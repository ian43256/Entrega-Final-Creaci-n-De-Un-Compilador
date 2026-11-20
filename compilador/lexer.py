import ply.lex as lex

from .errores import ErrorLexico


reservadas = {
    "six": "VAR",
    "seven": "IMPRIMIR",
    "six_if": "SI",
    "seven_else": "SINO",
    "six_loop": "MIENTRAS",
    "six_true": "VERDADERO",
    "seven_false": "FALSO",
    "six_and": "Y",
    "seven_or": "O",
    "six_not": "NO",
}

tokens = (
    "ID", "NUM", "STR",
    "VAR", "IMPRIMIR", "SI", "SINO", "MIENTRAS",
    "VERDADERO", "FALSO", "Y", "O", "NO",
    "EQ", "NE", "LE", "GE", "LT", "GT", "ASSIGN",
    "PLUS", "MINUS", "TIMES", "DIVIDE", "MOD",
    "LPAREN", "RPAREN", "LBRACE", "RBRACE",
)

t_EQ = r"=="
t_NE = r"!="
t_LE = r"<="
t_GE = r">="
t_LT = r"<"
t_GT = r">"
t_ASSIGN = r"="
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_MOD = r"%"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_ignore = " \t\r"


def t_NUM(t):
    r"\d+(\.\d+)?"
    t.value = float(t.value) if "." in t.value else int(t.value)
    return t


def t_STR(t):
    r'"[^"\n]*"'
    t.value = t.value[1:-1]
    return t


def t_ID(t):
    r"[A-Za-zÁÉÍÓÚáéíóúÑñ_][A-Za-zÁÉÍÓÚáéíóúÑñ_0-9]*"
    t.type = reservadas.get(t.value, "ID")
    return t


def t_COMENTARIO(t):
    r"\#[^\n]*"
    pass


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    # Una comilla que llega hasta aquí no pudo casar con t_STR: no se cierra en su línea.
    if t.value[0] == '"':
        raise ErrorLexico("Cadena sin cerrar", t.lineno)
    raise ErrorLexico(f"Carácter no reconocido: {t.value[0]!r}", t.lineno)


def crear_lexer():
    lexer = lex.lex()
    lexer.lineno = 1
    return lexer


def tokenizar(codigo):
    lexer = crear_lexer()
    lexer.input(codigo)
    return list(iter(lexer.token, None))
