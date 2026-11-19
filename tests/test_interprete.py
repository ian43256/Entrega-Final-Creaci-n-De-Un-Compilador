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
            "imprimir 10 / 4\nimprimir 4 / 2\nimprimir verdadero\n"
            "imprimir 1 > 2\nimprimir 7 % 3\nimprimir \"a\" + falso\n"
        )
        self.assertEqual(salida, ["2.5", "2", "verdadero", "falso", "1", "afalso"])

    def test_si_sino_elige_la_rama(self):
        self.assertEqual(
            correr('si 1 > 2 { imprimir "a" } sino { imprimir "b" }'), ["b"]
        )

    def test_una_linea_que_empieza_con_menos_continua_la_expresion_anterior(self):
        # Las sentencias no llevan separador: "imprimir x" y "-5" se leen como x - 5.
        self.assertEqual(correr("var x = 4\nimprimir x\n-5\n"), ["-1"])

    def test_analizar_codigo_no_ejecuta_el_programa(self):
        arbol = analizar_codigo('imprimir "hola"')
        self.assertEqual(arbol, [("imprimir", ("str", "hola"), 1)])


class PruebasErroresAntesDeEjecutar(unittest.TestCase):
    def test_con_errores_no_se_imprime_nada(self):
        salida = []
        with self.assertRaises(ErroresSintacticos):
            ejecutar('imprimir "antes"\nvar = 1\n', salida.append)
        with self.assertRaises(ErroresSemanticos):
            ejecutar('imprimir "antes"\nimprimir b\n', salida.append)
        with self.assertRaises(ErrorLexico):
            ejecutar('imprimir "antes"\n@\n', salida.append)
        self.assertEqual(salida, [])

    def test_analizar_codigo_lanza_el_error_de_cada_fase(self):
        with self.assertRaises(ErrorLexico):
            analizar_codigo("var x = #\n@")
        with self.assertRaises(ErroresSintacticos):
            analizar_codigo("var = 1")
        with self.assertRaises(ErroresSemanticos):
            analizar_codigo("imprimir z")


class PruebasErroresDeEjecucion(unittest.TestCase):
    def test_division_entre_variable_igual_a_cero(self):
        with self.assertRaises(LenguajeError) as contexto:
            correr("var d = 0\nimprimir 1 / d\n")
        self.assertEqual(contexto.exception.mensaje, "División entre cero")
        self.assertEqual(contexto.exception.linea, 2)

    def test_lo_impreso_antes_del_error_se_conserva(self):
        salida = []
        with self.assertRaises(LenguajeError):
            ejecutar('imprimir "uno"\nvar d = 0\nimprimir 1 % d\n', salida.append)
        self.assertEqual(salida, ["uno"])


class PruebasLimiteDeIteraciones(unittest.TestCase):
    def test_valor_del_limite(self):
        self.assertEqual(MAX_ITERACIONES, 100_000)

    def test_bucle_infinito_se_detiene(self):
        with self.assertRaises(LenguajeError) as contexto:
            correr("var n = 0\nmientras verdadero {\n    n = n + 1\n}\n")
        self.assertEqual(
            contexto.exception.mensaje, "Demasiadas iteraciones (¿bucle infinito?)"
        )
        self.assertEqual(contexto.exception.linea, 2)

    def test_exactamente_el_limite_si_se_permite(self):
        codigo = f"var i = 0\nmientras i < {MAX_ITERACIONES} {{\n    i = i + 1\n}}\nimprimir i\n"
        self.assertEqual(correr(codigo), [str(MAX_ITERACIONES)])

    def test_una_iteracion_mas_del_limite_falla(self):
        codigo = f"var i = 0\nmientras i < {MAX_ITERACIONES + 1} {{\n    i = i + 1\n}}\n"
        with self.assertRaises(LenguajeError):
            correr(codigo)


if __name__ == "__main__":
    unittest.main()
