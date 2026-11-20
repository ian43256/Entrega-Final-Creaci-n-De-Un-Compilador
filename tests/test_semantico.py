import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from compilador import ErroresSemanticos, analizar_codigo
from compilador.parser import parsear
from compilador.semantico import analizar


def errores_de(codigo):
    """Devuelve [(línea, mensaje), ...] de los errores semánticos del código."""
    return [(error.linea, error.mensaje) for error in analizar(parsear(codigo))]


class PruebasProgramaValido(unittest.TestCase):
    def test_ejemplo_mini_no_tiene_errores(self):
        with open(os.path.join(RAIZ, "ejemplo.mini"), encoding="utf-8") as archivo:
            self.assertEqual(errores_de(archivo.read()), [])

    def test_programa_con_todos_los_tipos(self):
        codigo = (
            'six n = 2\n'
            'six t = "a" + n\n'
            'six b = n > 1 six_and six_not (t == "a")\n'
            'six_if b { seven n } seven_else { seven t }\n'
        )
        self.assertEqual(errores_de(codigo), [])


class PruebasVariables(unittest.TestCase):
    def test_variable_no_declarada_en_una_expresion(self):
        self.assertEqual(
            errores_de('seven total\n'),
            [(1, "Variable 'total' no declarada")],
        )

    def test_asignacion_a_variable_no_declarada(self):
        self.assertEqual(
            errores_de('six a = 1\nb = 3\n'),
            [(2, "Variable 'b' no declarada")],
        )

    def test_variable_declarada_dos_veces(self):
        self.assertEqual(
            errores_de('six a = 1\nsix a = 2\n'),
            [(2, "Variable 'a' ya declarada")],
        )

    def test_variable_declarada_dentro_de_un_bloque_no_existe_fuera(self):
        codigo = 'six_loop seven_false {\n    six adentro = 1\n}\nseven adentro\n'
        self.assertEqual(errores_de(codigo), [(4, "Variable 'adentro' no declarada")])


class PruebasTipos(unittest.TestCase):
    def test_asignacion_de_tipo_incompatible(self):
        self.assertEqual(
            errores_de('six texto = "hola"\ntexto = 2\n'),
            [(2, "Asignación incompatible para 'texto': "
                 "se esperaba texto y se obtuvo numero")],
        )

    def test_operacion_aritmetica_con_texto(self):
        self.assertEqual(
            errores_de('seven "a" - 1\n'),
            [(1, "El operador '-' requiere operandos numéricos")],
        )

    def test_operador_logico_con_numeros(self):
        self.assertEqual(
            errores_de('seven 1 six_and 2\n'),
            [(1, "El operador 'six_and' requiere valores booleanos")],
        )

    def test_igualdad_entre_tipos_distintos(self):
        self.assertEqual(
            errores_de('seven 1 == "1"\n'),
            [(1, "El operador '==' requiere operandos del mismo tipo")],
        )

    def test_no_requiere_booleano(self):
        self.assertEqual(
            errores_de('seven six_not 5\n'),
            [(1, "El operador 'six_not' requiere booleano")],
        )

    def test_la_suma_con_texto_concatena(self):
        self.assertEqual(errores_de('seven "n = " + 5\nseven 5 + "!"\n'), [])


class PruebasCondiciones(unittest.TestCase):
    def test_condicion_de_si_no_booleana(self):
        self.assertEqual(
            errores_de('six_if 4 {\n    seven "x"\n}\n'),
            [(1, "La condición de 'six_if' debe ser booleana")],
        )

    def test_condicion_de_mientras_no_booleana(self):
        self.assertEqual(
            errores_de('six texto = "a"\nsix_loop texto {\n}\n'),
            [(2, "La condición de 'six_loop' debe ser booleana")],
        )

    def test_condicion_booleana_es_valida(self):
        self.assertEqual(errores_de('six_if 1 < 2 { }\nsix_loop seven_false { }\n'), [])


class PruebasDivisionEntreCero(unittest.TestCase):
    MENSAJE = "División entre cero con valor constante"

    def test_division_entre_cero_literal(self):
        self.assertEqual(errores_de('seven 8 / 0\n'), [(1, self.MENSAJE)])

    def test_division_entre_expresion_constante_que_vale_cero(self):
        self.assertEqual(errores_de('six d = 2 / (1 - 1)\n'), [(1, self.MENSAJE)])

    def test_modulo_entre_cero(self):
        self.assertEqual(errores_de('seven 8 % 0\n'), [(1, self.MENSAJE)])

    def test_division_entre_variable_no_se_detecta_en_el_analisis(self):
        # Solo se detecta cuando el divisor es constante; el resto falla al ejecutar.
        self.assertEqual(errores_de('six d = 0\nseven 1 / d\n'), [])

    def test_division_entre_distinto_de_cero_es_valida(self):
        self.assertEqual(errores_de('seven 8 / 2\n'), [])


class PruebasVariosErrores(unittest.TestCase):
    CODIGO = (
        'six a = 1\n'
        'six a = 2\n'
        "b = 3\n"
        'six texto = "hola"\n'
        "texto = 2\n"
        'six_if 4 {\n'
        '    seven "no es una condición booleana"\n'
        "}\n"
        'six division = 2 / (1 - 1)\n'
    )

    def test_se_informan_todos_en_orden(self):
        self.assertEqual(
            [linea for linea, _ in errores_de(self.CODIGO)], [2, 3, 5, 6, 9]
        )

    def test_analizar_codigo_los_agrupa_en_una_excepcion(self):
        with self.assertRaises(ErroresSemanticos) as contexto:
            analizar_codigo(self.CODIGO)
        self.assertEqual(len(contexto.exception.errores), 5)
        self.assertTrue(str(contexto.exception).startswith("Línea 2: Variable 'a' ya declarada"))


if __name__ == "__main__":
    unittest.main()
