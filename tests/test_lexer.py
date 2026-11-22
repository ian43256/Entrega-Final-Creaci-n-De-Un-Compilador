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
        codigo = "six seven six_if seven_else six_loop six_true seven_false six_and seven_or six_not"
        self.assertEqual(
            tipos(codigo),
            ["VAR", "IMPRIMIR", "SI", "SINO", "MIENTRAS",
             "VERDADERO", "FALSO", "Y", "O", "NO"],
        )

    def test_palabras_anteriores_son_identificadores(self):
        codigo = "var imprimir si sino mientras verdadero falso y o no"
        self.assertEqual(tipos(codigo), ["ID"] * 10)

    def test_palabras_reservadas_distinguen_mayusculas(self):
        self.assertEqual(tipos("six Six SEVEN seven six_if Six_if"), [
            "VAR", "ID", "ID", "IMPRIMIR", "SI", "ID",
        ])

    def test_identificadores(self):
        tokens = tokenizar("contador _tmp x2 año")
        self.assertEqual([t.type for t in tokens], ["ID"] * 4)
        self.assertEqual([t.value for t in tokens], ["contador", "_tmp", "x2", "año"])

    def test_identificador_que_empieza_como_palabra_reservada(self):
        self.assertEqual(tipos("six_extra sevenish six_if_else"), ["ID", "ID", "ID"])

    def test_numeros_enteros_y_decimales(self):
        entero, decimal, entero_grande, decimal_grande = tokenizar(
            "42 3.14 12345678901234567890 12345678901234567890.0"
        )
        self.assertEqual((entero.type, entero.value), ("NUM", 42))
        self.assertIsInstance(entero.value, int)
        self.assertEqual((decimal.type, decimal.value), ("NUM", 3.14))
        self.assertIsInstance(decimal.value, float)
        self.assertEqual((entero_grande.type, entero_grande.value), ("NUM", 12345678901234567890))
        self.assertIsInstance(entero_grande.value, int)
        self.assertEqual(
            (decimal_grande.type, decimal_grande.value),
            ("NUM", 1.2345678901234567e19),
        )
        self.assertIsInstance(decimal_grande.value, float)

    def test_entero_fuera_de_limites_da_error_lexico(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar("six x = 1\n" + "9" * 5000)
        self.assertEqual(contexto.exception.mensaje, "Literal numérico fuera de límites")
        self.assertEqual(contexto.exception.linea, 2)

    def test_decimal_no_finito_da_error_lexico(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar("seven " + "9" * 400 + ".0")
        self.assertEqual(contexto.exception.mensaje, "Literal numérico fuera de límites")
        self.assertEqual(contexto.exception.linea, 1)

    def test_decimal_subdesbordado_da_error_lexico(self):
        literal = "0." + "0" * 400 + "1"
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar("seven " + literal)
        self.assertEqual(contexto.exception.mensaje, "Literal numérico fuera de límites")
        self.assertEqual(contexto.exception.linea, 1)

    def test_decimales_pequenos_representables_siguen_funcionando(self):
        for literal, esperado in (
            ("0." + "0" * 307 + "1", 1e-308),
            ("0." + "0" * 323 + "5", 5e-324),
        ):
            with self.subTest(literal=literal):
                (token,) = tokenizar(literal)
                self.assertEqual(token.value, esperado)
                self.assertNotEqual(token.value, 0.0)

    def test_decimal_normal_sigue_funcionando(self):
        (token,) = tokenizar("3.14")
        self.assertEqual((token.type, token.value), ("NUM", 3.14))

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
        self.assertEqual(tipos('six x # comentario con "comillas" y @\n'), ["VAR", "ID"])

    def test_comentario_dentro_de_cadena_no_es_comentario(self):
        (token,) = tokenizar('"a # b"')
        self.assertEqual((token.type, token.value), ("STR", "a # b"))

    def test_numero_de_linea_de_cada_token(self):
        tokens = tokenizar("six x\n\nseven x\n# comentario\nsix_if")
        self.assertEqual(
            [(t.type, t.lineno) for t in tokens],
            [("VAR", 1), ("ID", 1), ("IMPRIMIR", 3), ("ID", 3), ("SI", 5)],
        )

    def test_numero_de_linea_con_cr_lf_y_crlf(self):
        for salto in ("\r", "\n", "\r\n"):
            with self.subTest(salto=repr(salto)):
                tokens = tokenizar(f"six x{salto}seven x")
                self.assertEqual([token.lineno for token in tokens], [1, 1, 2, 2])

    def test_crlf_se_cuenta_como_un_solo_salto(self):
        tokens = tokenizar("six x\r\nseven x\r\nsix_if")
        self.assertEqual([token.lineno for token in tokens], [1, 1, 2, 2, 3])

    def test_comentario_termina_con_cr_aislado(self):
        tokens = tokenizar("six x # comentario\rsix_if six_true")
        self.assertEqual(
            [(token.type, token.lineno) for token in tokens],
            [("VAR", 1), ("ID", 1), ("SI", 2), ("VERDADERO", 2)],
        )

    def test_el_lexer_se_reinicia_en_cada_llamada(self):
        tokenizar("six\nsix\nsix")
        self.assertEqual(tokenizar("six")[0].lineno, 1)


class PruebasErroresLexicos(unittest.TestCase):
    def test_caracter_no_reconocido(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar("six x = 1\nsix y = @\n")
        self.assertEqual(contexto.exception.mensaje, "Carácter no reconocido: '@'")
        self.assertEqual(contexto.exception.linea, 2)

    def test_signo_de_exclamacion_solo_no_es_operador(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar("six_if x ! y")
        self.assertEqual(contexto.exception.mensaje, "Carácter no reconocido: '!'")

    def test_cadena_sin_cerrar(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar('seven "hola sin cerrar comillas')
        self.assertEqual(contexto.exception.mensaje, "Cadena sin cerrar")
        self.assertEqual(contexto.exception.linea, 1)

    def test_cadena_sin_cerrar_informa_su_linea(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar('six x = 1\nseven "hola\nseven "adios"\n')
        self.assertEqual(contexto.exception.mensaje, "Cadena sin cerrar")
        self.assertEqual(contexto.exception.linea, 2)

    def test_comilla_sola_al_final(self):
        with self.assertRaises(ErrorLexico) as contexto:
            tokenizar('seven "')
        self.assertEqual(contexto.exception.mensaje, "Cadena sin cerrar")

    def test_cadena_cerrada_no_da_error(self):
        self.assertEqual(tipos('seven "hola"'), ["IMPRIMIR", "STR"])

    def test_el_error_lexico_es_un_error_del_lenguaje(self):
        with self.assertRaises(LenguajeError) as contexto:
            tokenizar("$")
        self.assertEqual(str(contexto.exception), "Línea 1: Carácter no reconocido: '$'")


if __name__ == "__main__":
    unittest.main()
