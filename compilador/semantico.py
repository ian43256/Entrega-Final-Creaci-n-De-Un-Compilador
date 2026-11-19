from dataclasses import dataclass


NUMERO = "numero"
TEXTO = "texto"
BOOLEANO = "booleano"


@dataclass(frozen=True)
class ErrorSemantico:
    linea: int
    mensaje: str


class ErroresSemanticos(Exception):
    def __init__(self, errores):
        self.errores = tuple(errores)
        super().__init__("\n".join(
            f"Línea {error.linea}: {error.mensaje}" for error in self.errores
        ))


class AnalizadorSemantico:
    def __init__(self):
        self.variables = {}
        self.errores = []

    def analizar(self, sentencias):
        self._bloque(sentencias)
        return self.errores

    def _error(self, linea, mensaje):
        self.errores.append(ErrorSemantico(linea, mensaje))

    def _bloque(self, sentencias):
        for sentencia in sentencias:
            self._sentencia(sentencia)

    def _sentencia(self, sentencia):
        tipo = sentencia[0]
        if tipo == "var":
            _, nombre, expresion, linea = sentencia
            tipo_valor = self._expresion(expresion)
            if nombre in self.variables:
                self._error(linea, f"Variable '{nombre}' ya declarada")
            elif tipo_valor is not None:
                self.variables[nombre] = tipo_valor
        elif tipo == "asig":
            _, nombre, expresion, linea = sentencia
            tipo_valor = self._expresion(expresion)
            tipo_variable = self.variables.get(nombre)
            if tipo_variable is None:
                self._error(linea, f"Variable '{nombre}' no declarada")
            elif tipo_valor is not None and tipo_valor != tipo_variable:
                self._error(
                    linea,
                    f"Asignación incompatible para '{nombre}': "
                    f"se esperaba {tipo_variable} y se obtuvo {tipo_valor}",
                )
        elif tipo == "imprimir":
            self._expresion(sentencia[1])
        elif tipo == "si":
            _, condicion, entonces, sino, linea = sentencia
            tipo_condicion = self._expresion(condicion)
            if tipo_condicion is not None and tipo_condicion != BOOLEANO:
                self._error(linea, "La condición de 'si' debe ser booleana")
            iniciales = self.variables.copy()
            self.variables = iniciales.copy()
            self._bloque(entonces)
            variables_entonces = self.variables
            self.variables = iniciales.copy()
            self._bloque(sino)
            variables_sino = self.variables
            self.variables = self._unir_ramas(
                iniciales, variables_entonces, variables_sino, linea
            )
        elif tipo == "mientras":
            _, condicion, cuerpo, linea = sentencia
            tipo_condicion = self._expresion(condicion)
            if tipo_condicion is not None and tipo_condicion != BOOLEANO:
                self._error(linea, "La condición de 'mientras' debe ser booleana")
            iniciales = self.variables
            self.variables = iniciales.copy()
            self._bloque(cuerpo)
            self.variables = iniciales

    def _unir_ramas(self, iniciales, entonces, sino, linea):
        resultado = iniciales.copy()
        for nombre in entonces.keys() & sino.keys():
            if nombre in iniciales:
                continue
            if entonces[nombre] == sino[nombre]:
                resultado[nombre] = entonces[nombre]
            else:
                self._error(
                    linea,
                    f"La variable '{nombre}' tiene tipos distintos en las ramas de 'si'",
                )
        return resultado

    def _expresion(self, expresion):
        tipo = expresion[0]
        if tipo == "num":
            return NUMERO
        if tipo == "str":
            return TEXTO
        if tipo == "bool":
            return BOOLEANO
        if tipo == "id":
            _, nombre, linea = expresion
            tipo_variable = self.variables.get(nombre)
            if tipo_variable is None:
                self._error(linea, f"Variable '{nombre}' no declarada")
            return tipo_variable
        if tipo == "un":
            _, operador, operando, linea = expresion
            tipo_operando = self._expresion(operando)
            tipo_esperado = BOOLEANO if operador == "no" else NUMERO
            if tipo_operando is not None and tipo_operando != tipo_esperado:
                self._error(linea, f"El operador '{operador}' requiere {tipo_esperado}")
            return tipo_esperado
        if tipo == "bin":
            _, operador, izquierda, derecha, linea = expresion
            tipo_izquierda = self._expresion(izquierda)
            tipo_derecha = self._expresion(derecha)
            return self._binaria(
                operador, izquierda, derecha, tipo_izquierda, tipo_derecha, linea
            )
        return None

    def _binaria(self, operador, izquierda, derecha, tipo_izquierda, tipo_derecha, linea):
        if operador in ("y", "o"):
            if tipo_izquierda not in (None, BOOLEANO) or tipo_derecha not in (None, BOOLEANO):
                self._error(linea, f"El operador '{operador}' requiere valores booleanos")
            return BOOLEANO

        if operador in ("==", "!="):
            if (tipo_izquierda is not None and tipo_derecha is not None
                    and tipo_izquierda != tipo_derecha):
                self._error(linea, f"El operador '{operador}' requiere operandos del mismo tipo")
            return BOOLEANO

        if operador in ("<", ">", "<=", ">="):
            self._requiere_numeros(operador, tipo_izquierda, tipo_derecha, linea)
            return BOOLEANO

        if operador == "+" and TEXTO in (tipo_izquierda, tipo_derecha):
            return TEXTO

        self._requiere_numeros(operador, tipo_izquierda, tipo_derecha, linea)
        if operador in ("/", "%"):
            conocido, valor = _valor_constante(derecha)
            if conocido and type(valor) in (int, float) and valor == 0:
                self._error(linea, "División entre cero con valor constante")
        return NUMERO

    def _requiere_numeros(self, operador, izquierda, derecha, linea):
        if izquierda not in (None, NUMERO) or derecha not in (None, NUMERO):
            self._error(linea, f"El operador '{operador}' requiere operandos numéricos")


def _valor_constante(expresion):
    tipo = expresion[0]
    if tipo in ("num", "str", "bool"):
        return True, expresion[1]
    if tipo == "id":
        return False, None
    if tipo == "un":
        conocido, valor = _valor_constante(expresion[2])
        if not conocido:
            return False, None
        if expresion[1] == "no":
            return True, not valor
        return True, -valor
    if tipo != "bin":
        return False, None

    _, operador, izquierda, derecha, _ = expresion
    es_constante_izq, valor_izq = _valor_constante(izquierda)
    es_constante_der, valor_der = _valor_constante(derecha)
    if not es_constante_izq or not es_constante_der:
        return False, None
    try:
        operaciones = {
            "+": lambda: valor_izq + valor_der,
            "-": lambda: valor_izq - valor_der,
            "*": lambda: valor_izq * valor_der,
            "/": lambda: valor_izq / valor_der,
            "%": lambda: valor_izq % valor_der,
            "==": lambda: valor_izq == valor_der,
            "!=": lambda: valor_izq != valor_der,
            "<": lambda: valor_izq < valor_der,
            ">": lambda: valor_izq > valor_der,
            "<=": lambda: valor_izq <= valor_der,
            ">=": lambda: valor_izq >= valor_der,
            "y": lambda: bool(valor_izq) and bool(valor_der),
            "o": lambda: bool(valor_izq) or bool(valor_der),
        }
        operacion = operaciones.get(operador)
        return (True, operacion()) if operacion is not None else (False, None)
    except (ArithmeticError, TypeError):
        return False, None


def analizar(sentencias):
    return AnalizadorSemantico().analizar(sentencias)
