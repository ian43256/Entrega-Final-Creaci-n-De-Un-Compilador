from .errores import LenguajeError
from .parser import parsear
from .semantico import ErroresSemanticos, analizar

MAX_ITERACIONES = 100_000  # evita que un 'mientras' infinito congele la interfaz


def formatear(v):
    if v is True:  return "verdadero"
    if v is False: return "falso"
    if isinstance(v, float) and v.is_integer(): return str(int(v))
    return str(v)


class Interprete:
    def __init__(self, salida):
        self.vars = {}
        self.salida = salida          # función que recibe cada línea de texto
        self.iteraciones = 0

    def ejecutar_bloque(self, sentencias):
        for s in sentencias:
            self.ejecutar(s)

    def ejecutar(self, s):
        tipo = s[0]
        if tipo == "var":
            self.vars[s[1]] = self.evaluar(s[2])
        elif tipo == "asig":
            if s[1] not in self.vars:
                raise LenguajeError(f"Variable '{s[1]}' no declarada (usa 'var')", s[3])
            self.vars[s[1]] = self.evaluar(s[2])
        elif tipo == "imprimir":
            self.salida(formatear(self.evaluar(s[1])))
        elif tipo == "si":
            self.ejecutar_bloque(s[2] if self.evaluar(s[1]) else s[3])
        elif tipo == "mientras":
            while self.evaluar(s[1]):
                self.iteraciones += 1
                if self.iteraciones > MAX_ITERACIONES:
                    raise LenguajeError("Demasiadas iteraciones (¿bucle infinito?)", s[3])
                self.ejecutar_bloque(s[2])

    def evaluar(self, e):
        tipo = e[0]
        if tipo in ("num", "str", "bool"):
            return e[1]
        if tipo == "id":
            if e[1] not in self.vars:
                raise LenguajeError(f"Variable '{e[1]}' no definida", e[2])
            return self.vars[e[1]]
        if tipo == "un":
            v = self.evaluar(e[2])
            if e[1] == "no": return not v
            self._num(v, e[3]); return -v
        if tipo == "bin":
            return self.binario(e)

    def _num(self, v, linea):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise LenguajeError("Se esperaba un número", linea)

    def binario(self, e):
        _, op, ie, de, linea = e
        if op == "y":  return bool(self.evaluar(ie)) and bool(self.evaluar(de))
        if op == "o":  return bool(self.evaluar(ie)) or bool(self.evaluar(de))
        a, b = self.evaluar(ie), self.evaluar(de)
        if op == "==": return a == b
        if op == "!=": return a != b
        if op == "+" and (isinstance(a, str) or isinstance(b, str)):
            return formatear(a) + formatear(b)
        self._num(a, linea); self._num(b, linea)
        if op == "+": return a + b
        if op == "-": return a - b
        if op == "*": return a * b
        if op in ("/", "%") and b == 0:
            raise LenguajeError("División entre cero", linea)
        if op == "/": return a / b
        if op == "%": return a % b
        if op == "<": return a < b
        if op == ">": return a > b
        if op == "<=": return a <= b
        if op == ">=": return a >= b


def analizar_codigo(codigo):
    """Análisis léxico, sintáctico y semántico, sin ejecutar el programa.

    Devuelve el árbol del programa. Si hay errores lanza la excepción de la fase
    que los encontró (léxica, sintáctica o semántica).
    """
    ast = parsear(codigo)
    errores = analizar(ast)
    if errores:
        raise ErroresSemanticos(errores)
    return ast


def ejecutar(codigo, salida=print):
    """Compila, valida semánticamente y ejecuta el programa."""
    ast = analizar_codigo(codigo)
    Interprete(salida).ejecutar_bloque(ast)
