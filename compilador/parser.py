import ply.yacc as yacc

from . import lexer as lexer_mod
from .errores import ErrorSintactico, ErroresSintacticos


tokens = lexer_mod.tokens

precedence = (
    ("left", "O"),
    ("left", "Y"),
    ("right", "NOT"),
    ("left", "EQ", "NE", "LT", "GT", "LE", "GE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("right", "UMINUS"),
)


# Estado del análisis en curso. Lo reinicia parsear() y lo llena p_error().
_errores = []          # errores de sintaxis acumulados
_ultima_linea = 1      # línea del último token del programa
_fuente = None         # tokens que se entregan al parser


def p_programa(p):
    "programa : sentencias_programa"
    p[0] = p[1]


# La lista de sentencias del programa y la de un bloque son dos reglas distintas
# (aunque iguales) a propósito: la regla "error" de cada una tiene así su propio
# conjunto de tokens de sincronización. En el programa una '}' no puede continuar
# el análisis; dentro de un bloque sí (cierra el bloque).
def p_sentencias_programa_varias(p):
    "sentencias_programa : sentencias_programa sentencia"
    p[0] = p[1] + [p[2]]


def p_sentencias_programa_vacia(p):
    "sentencias_programa :"
    p[0] = []


def p_sentencias_programa_error(p):
    "sentencias_programa : sentencias_programa error"
    p[0] = p[1]
    p.parser.errok()    # recuperado: el siguiente error también se informa


def p_sentencias_varias(p):
    "sentencias : sentencias sentencia"
    p[0] = p[1] + [p[2]]


def p_sentencias_vacia(p):
    "sentencias :"
    p[0] = []


def p_sentencias_error(p):
    "sentencias : sentencias error"
    p[0] = p[1]
    p.parser.errok()    # recuperado: el siguiente error también se informa


def p_sentencia_var(p):
    "sentencia : VAR ID ASSIGN expresion"
    p[0] = ("var", p[2], p[4], p.lineno(1))


def p_sentencia_asignacion(p):
    "sentencia : ID ASSIGN expresion"
    p[0] = ("asig", p[1], p[3], p.lineno(1))


def p_sentencia_imprimir(p):
    "sentencia : IMPRIMIR expresion"
    p[0] = ("imprimir", p[2], p.lineno(1))


def p_sentencia_si(p):
    "sentencia : SI expresion bloque"
    p[0] = ("si", p[2], p[3], [], p.lineno(1))


def p_sentencia_si_sino(p):
    "sentencia : SI expresion bloque SINO bloque"
    p[0] = ("si", p[2], p[3], p[5], p.lineno(1))


def p_sentencia_mientras(p):
    "sentencia : MIENTRAS expresion bloque"
    p[0] = ("mientras", p[2], p[3], p.lineno(1))


def p_bloque(p):
    "bloque : LBRACE sentencias RBRACE"
    p[0] = p[2]


def p_expresion_binaria(p):
    """expresion : expresion O expresion
                 | expresion Y expresion
                 | expresion EQ expresion
                 | expresion NE expresion
                 | expresion LT expresion
                 | expresion GT expresion
                 | expresion LE expresion
                 | expresion GE expresion
                 | expresion PLUS expresion
                 | expresion MINUS expresion
                 | expresion TIMES expresion
                 | expresion DIVIDE expresion
                 | expresion MOD expresion"""
    p[0] = ("bin", p[2], p[1], p[3], p.lineno(2))


def p_expresion_unaria(p):
    """expresion : NO expresion %prec NOT
                 | MINUS expresion %prec UMINUS"""
    p[0] = ("un", p[1], p[2], p.lineno(1))


def p_expresion_grupo(p):
    "expresion : LPAREN expresion RPAREN"
    p[0] = p[2]


def p_expresion_numero(p):
    "expresion : NUM"
    p[0] = ("num", p[1])


def p_expresion_texto(p):
    "expresion : STR"
    p[0] = ("str", p[1])


def p_expresion_booleano(p):
    """expresion : VERDADERO
                 | FALSO"""
    p[0] = ("bool", p.slice[1].type == "VERDADERO")


def p_expresion_variable(p):
    "expresion : ID"
    p[0] = ("id", p[1], p.lineno(1))


# Tokens con los que puede empezar una sentencia
_INICIO_DE_SENTENCIA = ("VAR", "ID", "IMPRIMIR", "SI", "MIENTRAS")


def p_error(token):
    """Registra el error y decide cómo se recupera el análisis (regla 'error' de PLY).

    Después de un error PLY descarta tokens hasta uno con el que pueda seguir. Para que
    ese punto sea predecible, aquí se decide dónde se reanuda:
      - si el token inesperado es una '}' que cierra un bloque, o abre una línea y puede
        iniciar una sentencia (la sentencia anterior quedó incompleta), se reanuda en él;
      - en cualquier otro caso se ignora lo que falte de la sentencia y se reanuda en la
        línea siguiente (ver _FuenteDeTokens).
    """
    if token is None:
        linea = _ultima_linea
        mensaje = "Sintaxis inválida al final del programa"
    else:
        linea = token.lineno
        mensaje = f"Sintaxis inválida cerca de {token.value!r}"
    # Se informa un solo error por línea: lo que sigue a un error en la misma
    # línea suele ser consecuencia de él y no un problema nuevo.
    if not _errores or _errores[-1].linea != linea:
        _errores.append(ErrorSintactico(linea, mensaje))

    if token is None:
        return
    previo = _fuente.previo
    abre_linea = previo is None or previo.lineno < linea
    if token.type == "RBRACE" or (abre_linea and token.type in _INICIO_DE_SENTENCIA):
        return
    if token.type == "LBRACE":
        _fuente.llave_descartada()
    else:
        # Un tipo que ninguna regla acepta hace que PLY descarte este token en lugar
        # de reanudar el análisis a mitad de la sentencia rota.
        token.type = "DESCARTADO"
    _fuente.recuperar(linea)


_parser = yacc.yacc(
    start="programa",
    write_tables=False,
    debug=False,
    errorlog=yacc.NullLogger(),
)
# Sin reducciones por defecto el parser consulta el token siguiente antes de reducir
# la regla 'error'; así descarta tokens hasta uno de sincronización en vez de ciclarse.
_parser.disable_defaulted_states()


class _FuenteDeTokens:
    """Entrega a PLY los tokens ya generados por el analizador léxico.

    También hace la parte de la recuperación de errores que PLY no resuelve bien en
    un lenguaje sin separadores: tras un error (ver recuperar) descarta tokens hasta la
    siguiente línea que empiece una sentencia, o hasta una '}' que cierre un bloque ya
    abierto. Así un identificador a mitad de una sentencia rota no se toma como el
    inicio de otra, y como se llevan las llaves, una '{' descartada (por ejemplo la de
    'six_if x = 3 {') arrastra a su '}' y no deja un bloque sin pareja.
    """
    def __init__(self, tokens):
        self._tokens = iter(tokens)
        self.previo = None            # token entregado antes del último
        self._ultimo = None
        self._llaves = []             # una por '{' sin cerrar: True si el parser la recibió
        self._recuperando = False
        self._linea_error = 0
        # PLY los lee (con tracking=True) igual que en un lexer real
        self.lineno = 1
        self.lexpos = 0

    def recuperar(self, linea):
        """Descarta tokens hasta una línea posterior a 'linea' que inicie una sentencia."""
        self._recuperando = True
        self._linea_error = linea

    def llave_descartada(self):
        """La '{' recién entregada era inesperada: PLY la descarta, y también su '}'."""
        self._llaves[-1] = False

    def token(self):
        for token in self._tokens:
            if self._se_entrega(token):
                self.previo, self._ultimo = self._ultimo, token
                self.lineno = token.lineno
                self.lexpos = token.lexpos
                return token
        return None

    def _se_entrega(self, token):
        if token.type == "LBRACE":
            entregar = not self._recuperando
            self._llaves.append(entregar)
            return entregar
        if token.type == "RBRACE":
            if not self._llaves:
                return True                       # '}' sobrante: PLY la informa o la descarta
            if self._llaves.pop():                # cierra un bloque abierto: se reanuda aquí
                self._recuperando = False
                return True
            return False                          # era la '}' de una '{' descartada
        if self._recuperando:
            if token.lineno > self._linea_error and token.type in _INICIO_DE_SENTENCIA:
                self._recuperando = False
                return True
            return False
        return True


def parsear(codigo):
    """Devuelve el árbol del programa.

    Lanza ErrorLexico si el código tiene un error léxico y ErroresSintacticos
    (con todos los errores encontrados) si tiene errores de sintaxis.
    """
    global _ultima_linea, _fuente
    tokens = lexer_mod.tokenizar(codigo)      # el análisis léxico termina primero
    _errores.clear()
    _ultima_linea = tokens[-1].lineno if tokens else 1
    _fuente = _FuenteDeTokens(tokens)
    arbol = _parser.parse(lexer=_fuente, tracking=True)
    if _errores:
        raise ErroresSintacticos(_errores)    # copia la lista en una tupla
    return arbol
