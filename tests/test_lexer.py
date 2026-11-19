import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compilador import ErrorLexico, LenguajeError
from compilador.lexer import tokenizar


def tipos(codigo):
    return [token.type for token in tokenizar(codigo)]


class PruebasTokens(unittest.TestCase):
    def test_palabras_reservadas(self):
        codigo = "var imprimir si sino mientras verdadero falso y o no"
        self.assertEqual(
            tipos(codigo),
            ["VAR", "IMPRIMIR", "SI", "SINO", "MIENTRAS",
             "VERDADERO", "FALSO", "Y", "O", "NO"],
        )

    def test_identificadores(self):
        tokens = tokenizar("contador _tmp x2 año")
        self.assertEqual([t.type for t in tokens], ["ID"] * 4)
        self.assertEqual([t.value for t in tokens], ["contador", "_tmp", "x2", "año"])

    def test_identificador_que_empieza_como_palabra_reservada(self):
        self.assertEqual(tipos("variable silla yo"), ["ID", "ID", "ID"])

    def test_numeros_enteros_y_decimales(self):
        entero, decimal = tokenizar("42 3.14")
        self.assertEqual((entero.type, entero.value), ("NUM", 42))
        self.assertIsInstance(entero.value, int)
        self.assertEqual((decimal.type, decimal.value), ("NUM", 3.14))
        self.assertIsInstance(decimal.value, float)

    def test_cadena_sin_las_comillas(self):
        (token,) = tokenizar('"hola mundo"')
        self.assertEqual((token.type, token.value), ("STR", "hola mundo"))

    def test_cadena_vacia(self):
        (token,) = tokenizar('""')
        self.assertEqual((token.type, token.value), ("STR", ""))

    def test_operadores_y_simbolos(self):
        self.assertEqual(
            tipos("== != <= >= < > = + - * / % ( ) { }"),
            ["EQ", "NE", "LE", "GE", "LT", "GT", "ASSIGN",
             "PLUS", "MINUS", "TIMES", "DIVIDE", "MOD",
             "LPAREN", "RPAREN", "LBRACE", "RBRACE"],
        )

    def test_comentarios_y_espacios_se_ignoran(self):
        self.assertEqual(tipos("  # solo un comentario\n\t"), [])
        self.assertEqual(tipos("var x # comentario con \"comillas\" y @\n"), ["VAR", "ID"])

    def test_comentario_dentro_de_cadena_no_es_comentario(self):
        (token,) = tokenizar('"a # b"')
        self.assertEqual((token.type, token.value), ("STR", "a # b"))

    def test_numero_de_linea_de_cada_token(self):
        tokens = tokenizar("var x\n\nimprimir x\n# comentario\nsi")
        self.assertEqual(
            [(t.type, t.lineno) for t in tokens],
            [("VAR", 1), ("ID", 1), ("IMPRIMIR", 3), ("ID", 3), ("SI", 5)],
        )

    def test_el_lexer_se_reinicia_en_cada_llamada(self):
        tokenizar("var\nvar\nvar")
        self.assertEqual(tokenizar("var")[0].lineno, 1)


class PruebasErroresLexicos(unittest.TestCase):
    def test_caracter_no_reconocido(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar("var x = 1\nvar y = @\n")
        self.assertEqual(contexto.exception.mensaje, "Carácter no reconocido: '@'")
        self.assertEqual(contexto.exception.linea, 2)

    def test_signo_de_exclamacion_solo_no_es_operador(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar("si x ! y")
        self.assertEqual(contexto.exception.mensaje, "Carácter no reconocido: '!'")

    def test_cadena_sin_cerrar(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar('imprimir "hola sin cerrar comillas')
        self.assertEqual(contexto.exception.mensaje, "Cadena sin cerrar")
        self.assertEqual(contexto.exception.linea, 1)

    def test_cadena_sin_cerrar_informa_su_linea(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar('var x = 1\nimprimir "hola\nimprimir "adios"\n')
        self.assertEqual(contexto.exception.mensaje, "Cadena sin cerrar")
        self.assertEqual(contexto.exception.linea, 2)

    def test_comilla_sola_al_final(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar('imprimir "')
        self.assertEqual(contexto.exception.mensaje, "Cadena sin cerrar")

    def test_cadena_cerrada_no_da_error(self):
        self.assertEqual(tipos('imprimir "hola"'), ["IMPRIMIR", "STR"])

    def test_el_error_lexico_es_un_error_del_lenguaje(self):
        with self.assertRaises(LenguajeError) as contexto:
            tokenizar("$")
        self.assertEqual(str(contexto.exception), "Línea 1: Carácter no reconocido: '$'")


if __name__ == "__main__":
    unittest.main()
