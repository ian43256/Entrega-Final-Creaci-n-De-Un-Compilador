import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from compilador import (ErrorLexico, ErroresSemanticos, ErroresSintacticos,
                        LenguajeError, analizar_codigo, ejecutar)
from compilador.interprete import MAX_ITERACIONES


def correr(codigo):
    """Ejecuta el código y devuelve la lista de líneas que imprimió."""
    salida = []
    ejecutar(codigo, salida.append)
    return salida


class PruebasProgramaValido(unittest.TestCase):
    def test_ejemplo_mini(self):
        with open(os.path.join(RAIZ, "ejemplo.mini"), encoding="utf-8") as archivo:
            salida = correr(archivo.read())
        self.assertEqual(
            salida, ["Hola mundo", "x vale 5", "x es mayor que 3", "Suma = 15"]
        )

    def test_formato_de_los_valores(self):
        salida = correr(
            'seven 10 / 4\nseven 4 / 2\nseven six_true\n'
            'seven 1 > 2\nseven 7 % 3\nseven "a" + seven_false\n'
        )
        self.assertEqual(salida, ["2.5", "2", "six_true", "seven_false", "1", "aseven_false"])

    def test_operaciones_aritmeticas_normales(self):
        codigo = (
            "seven 2 + 3\n"
            "seven 7 - 2\n"
            "seven 3 * 4\n"
            "seven 10 / 4\n"
            "seven 7 % 4\n"
            "seven 1.5 * 2\n"
        )
        self.assertEqual(correr(codigo), ["5", "5", "12", "2.5", "3", "3"])

    def test_operaciones_normales_con_enteros_y_decimales(self):
        codigo = (
            "seven 7 + 1.5\n"
            "seven 7 - 1.5\n"
            "seven 7 * 1.5\n"
            "seven 7 % 1.5\n"
        )
        self.assertEqual(correr(codigo), ["8.5", "5.5", "10.5", "1"])

    def test_operadores_logicos_sixseven(self):
        codigo = (
            "seven six_not six_true\n"
            "seven six_true six_and seven_false\n"
            "seven six_true seven_or seven_false\n"
        )
        self.assertEqual(correr(codigo), ["seven_false", "seven_false", "six_true"])

    def test_precedencia_combinada_y_parentesis_de_operadores_logicos(self):
        codigo = (
            "seven six_not seven_false six_and six_true seven_or seven_false\n"
            "seven six_true seven_or seven_false six_and seven_false\n"
            "seven (six_true seven_or seven_false) six_and seven_false\n"
        )
        self.assertEqual(correr(codigo), ["six_true", "six_true", "seven_false"])

    def test_palabras_anteriores_se_pueden_usar_como_identificadores(self):
        codigo = "six var = 4\nsix imprimir = var + 1\nseven imprimir\n"
        self.assertEqual(correr(codigo), ["5"])

    def test_si_sino_elige_la_rama(self):
        self.assertEqual(
            correr('six_if 1 > 2 { seven "a" } seven_else { seven "b" }'), ["b"]
        )

    def test_una_linea_que_empieza_con_menos_continua_la_expresion_anterior(self):
        # Las sentencias no llevan separador: "seven x" y "-5" se leen como x - 5.
        self.assertEqual(correr('six x = 4\nseven x\n-5\n'), ["-1"])

    def test_analizar_codigo_no_ejecuta_el_programa(self):
        arbol = analizar_codigo('seven "hola"')
        self.assertEqual(arbol, [("imprimir", ("str", "hola"), 1)])


class PruebasErroresAntesDeEjecutar(unittest.TestCase):
    def test_con_errores_no_se_imprime_nada(self):
        salida = []
        with self.assertRaises(ErroresSintacticos):
            ejecutar('seven "antes"\nsix = 1\n', salida.append)
        with self.assertRaises(ErroresSemanticos):
            ejecutar('seven "antes"\nseven b\n', salida.append)
        with self.assertRaises(ErrorLexico):
            ejecutar('seven "antes"\n@\n', salida.append)
        self.assertEqual(salida, [])

    def test_analizar_codigo_lanza_el_error_de_cada_fase(self):
        with self.assertRaises(ErrorLexico):
            analizar_codigo('six x = #\n@')
        with self.assertRaises(ErroresSintacticos):
            analizar_codigo('six = 1')
        with self.assertRaises(ErroresSemanticos):
            analizar_codigo("seven z")


class PruebasErroresDeEjecucion(unittest.TestCase):
    def test_desbordamiento_decimal_da_error_controlado(self):
        operando = "1" + "0" * 200 + ".0"
        codigo = f"six a = {operando}\nsix b = {operando}\nseven a * b\n"
        with self.assertRaises(LenguajeError) as contexto:
            correr(codigo)
        self.assertEqual(contexto.exception.mensaje, "Resultado numérico fuera de límites")
        self.assertEqual(contexto.exception.linea, 3)

    def test_imprimir_entero_extremadamente_grande_da_error_controlado(self):
        literal = "9" * 2200
        with self.assertRaises(LenguajeError) as contexto:
            correr(f"seven {literal} * {literal}")
        self.assertEqual(contexto.exception.mensaje, "Resultado numérico fuera de límites")
        self.assertEqual(contexto.exception.linea, 1)

    def test_division_de_entero_grande_da_error_controlado(self):
        codigo = f"seven {'9' * 400} / 1"
        with self.assertRaises(LenguajeError) as contexto:
            correr(codigo)
        self.assertEqual(contexto.exception.mensaje, "Resultado numérico fuera de límites")
        self.assertEqual(contexto.exception.linea, 1)

    def test_operaciones_con_entero_grande_y_decimal_da_error_controlado(self):
        entero_grande = "9" * 400
        for operador in ("+", "-", "*", "%"):
            with self.subTest(operador=operador):
                codigo = f"seven {entero_grande} {operador} 1.0"
                with self.assertRaises(LenguajeError) as contexto:
                    correr(codigo)
                self.assertEqual(
                    contexto.exception.mensaje, "Resultado numérico fuera de límites"
                )
                self.assertEqual(contexto.exception.linea, 1)

    def test_divisiones_normales_siguen_funcionando(self):
        self.assertEqual(correr("seven 10 / 4\nseven 4 / 2"), ["2.5", "2"])

    def test_division_entre_variable_igual_a_cero(self):
        with self.assertRaises(LenguajeError) as contexto:
            correr('six d = 0\nseven 1 / d\n')
        self.assertEqual(contexto.exception.mensaje, "División entre cero")
        self.assertEqual(contexto.exception.linea, 2)

    def test_lo_impreso_antes_del_error_se_conserva(self):
        salida = []
        with self.assertRaises(LenguajeError):
            ejecutar('seven "uno"\nsix d = 0\nseven 1 % d\n', salida.append)
        self.assertEqual(salida, ["uno"])


class PruebasLimiteDeIteraciones(unittest.TestCase):
    def test_valor_del_limite(self):
        self.assertEqual(MAX_ITERACIONES, 100_000)

    def test_bucle_infinito_se_detiene(self):
        with self.assertRaises(LenguajeError) as contexto:
            correr('six n = 0\nsix_loop six_true {\n    n = n + 1\n}\n')
        self.assertEqual(
            contexto.exception.mensaje, "Demasiadas iteraciones (¿bucle infinito?)"
        )
        self.assertEqual(contexto.exception.linea, 2)

    def test_exactamente_el_limite_si_se_permite(self):
        codigo = f"six i = 0\nsix_loop i < {MAX_ITERACIONES} {{\n    i = i + 1\n}}\nseven i\n"
        self.assertEqual(correr(codigo), [str(MAX_ITERACIONES)])

    def test_una_iteracion_mas_del_limite_falla(self):
        codigo = f"six i = 0\nsix_loop i < {MAX_ITERACIONES + 1} {{\n    i = i + 1\n}}\n"
        with self.assertRaises(LenguajeError):
            correr(codigo)


if __name__ == "__main__":
    unittest.main()
