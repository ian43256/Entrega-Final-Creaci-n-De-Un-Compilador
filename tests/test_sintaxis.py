import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from compilador import ErrorLexico, ErroresSintacticos
from compilador.parser import parsear


def errores_de(codigo):
    """Devuelve [(línea, mensaje), ...] de los errores de sintaxis del código."""
    try:
        parsear(codigo)
    except ErroresSintacticos as error:
        return [(e.linea, e.mensaje) for e in error.errores]
    raise AssertionError("se esperaba ErroresSintacticos y el código no tiene errores")


class PruebasProgramaValido(unittest.TestCase):
    def test_programa_vacio(self):
        self.assertEqual(parsear(""), [])
        self.assertEqual(parsear("# solo un comentario\n\n"), [])

    def test_arbol_de_una_declaracion(self):
        self.assertEqual(parsear("var x = 1\n"), [("var", "x", ("num", 1), 1)])

    def test_ejemplo_mini(self):
        with open(os.path.join(RAIZ, "ejemplo.mini"), encoding="utf-8") as archivo:
            arbol = parsear(archivo.read())
        self.assertEqual(
            [sentencia[0] for sentencia in arbol],
            ["var", "imprimir", "imprimir", "si", "var", "mientras", "imprimir"],
        )

    def test_precedencia_de_operadores(self):
        (sentencia,) = parsear("imprimir 1 + 2 * 3")
        self.assertEqual(
            sentencia[1],
            ("bin", "+", ("num", 1), ("bin", "*", ("num", 2), ("num", 3), 1), 1),
        )

    def test_las_sentencias_no_llevan_separador(self):
        # Una línea que empieza con '-' continúa la expresión anterior.
        arbol = parsear("imprimir x\n-5")
        self.assertEqual(len(arbol), 1)
        self.assertEqual(arbol[0][1][:2], ("bin", "-"))

    def test_sino_se_asocia_con_el_si_cuyo_bloque_se_acaba_de_cerrar(self):
        # El 'sino' va después de la '}' de un 'si': no hay ambigüedad posible.
        (si_externo,) = parsear("si a { si b { imprimir 1 } sino { imprimir 2 } }")
        _, _, cuerpo, sino_externo, _ = si_externo
        self.assertEqual(sino_externo, [])
        (si_interno,) = cuerpo
        self.assertEqual(si_interno[3], [("imprimir", ("num", 2), 1)])

        (si_externo,) = parsear("si a { si b { imprimir 1 } } sino { imprimir 2 }")
        _, _, cuerpo, sino_externo, _ = si_externo
        self.assertEqual(sino_externo, [("imprimir", ("num", 2), 1)])
        (si_interno,) = cuerpo
        self.assertEqual(si_interno[3], [])


class PruebasErroresDeSintaxis(unittest.TestCase):
    def test_un_error(self):
        self.assertEqual(
            errores_de("var = 5\nimprimir 1\n"),
            [(1, "Sintaxis inválida cerca de '='")],
        )

    def test_el_mensaje_incluye_el_token_y_la_linea(self):
        with self.assertRaises(ErroresSintacticos) as contexto:
            parsear("var x = 1\nimprimir 2 3\n")
        self.assertEqual(
            str(contexto.exception), "Línea 2: Sintaxis inválida cerca de 3"
        )
        (error,) = contexto.exception.errores
        self.assertEqual((error.linea, error.mensaje), (2, "Sintaxis inválida cerca de 3"))

    def test_varios_errores_se_acumulan_con_su_linea(self):
        codigo = (
            "var = 5\n"            # 1: error
            "imprimir 1\n"         # 2: correcta
            "imprimir 2 2\n"       # 3: error
            "var x = 3\n"          # 4: correcta
            "x = = 4\n"            # 5: error
            "imprimir x\n"         # 6: correcta
        )
        self.assertEqual(
            errores_de(codigo),
            [
                (1, "Sintaxis inválida cerca de '='"),
                (3, "Sintaxis inválida cerca de 2"),
                (5, "Sintaxis inválida cerca de '='"),
            ],
        )

    def test_errores_en_lineas_consecutivas(self):
        lineas = [linea for linea, _ in errores_de("var = 1\nvar = 2\nvar = 3\n")]
        self.assertEqual(lineas, [1, 2, 3])

    def test_un_solo_error_por_linea(self):
        # Todo lo que sigue al primer error de una línea es consecuencia suya.
        lineas = [linea for linea, _ in errores_de("imprimir 1 + * a b\nimprimir 2\n")]
        self.assertEqual(lineas, [1])

    def test_un_error_mas_en_la_misma_linea_no_se_repite(self):
        # 'var' abre la línea 2 y es donde se reanuda; el '=' que sigue es de la misma línea.
        self.assertEqual(
            errores_de("imprimir\nvar = 3\n"),
            [(2, "Sintaxis inválida cerca de 'var'")],
        )

    def test_el_token_inesperado_a_mitad_de_linea_no_inicia_otra_sentencia(self):
        # Sin esto 'imprimir' (línea 1) se tomaría como una sentencia nueva
        # y fallaría de nuevo al encontrar el 'imprimir' de la línea 2.
        self.assertEqual(
            errores_de("si verdadero imprimir 1\nimprimir 2\n"),
            [(1, "Sintaxis inválida cerca de 'imprimir'")],
        )

    def test_tras_un_error_se_ignora_el_resto_de_la_linea(self):
        # El 'a' de la línea 1 parece el inicio de una sentencia, pero es parte de la
        # sentencia rota: si se tomara como nueva, el '3' de la línea 2 daría otro error.
        self.assertEqual(
            errores_de("imprimir 1 + * a\n3\n"),
            [(1, "Sintaxis inválida cerca de '*'")],
        )

    def test_se_reanuda_en_el_inicio_de_linea_que_cierra_una_sentencia_incompleta(self):
        # El 'si' que delata la sentencia incompleta se conserva completo, con su 'sino'.
        codigo = (
            "imprimir 1 +\n"          # 1: incompleta
            "si verdadero {\n"        # 2: aquí se detecta el error y se reanuda
            "    imprimir 2\n"
            "} sino {\n"
            "    imprimir 3\n"
            "}\n"
        )
        self.assertEqual(
            errores_de(codigo), [(2, "Sintaxis inválida cerca de 'si'")]
        )

    def test_error_en_el_encabezado_de_un_si_no_deja_llaves_sin_pareja(self):
        # El clásico '=' en lugar de '==': la '{' se descarta junto con su '}'.
        codigo = (
            "si x = 3 {\n"         # 1: error en la condición
            "    imprimir 1\n"     # 2
            "}\n"                  # 3: no debe dar un error por '}' sobrante
            "imprimir 2 2\n"       # 4: error aparte
        )
        self.assertEqual(
            errores_de(codigo),
            [
                (1, "Sintaxis inválida cerca de '='"),
                (4, "Sintaxis inválida cerca de 2"),
            ],
        )

    def test_llave_de_apertura_en_su_propia_linea(self):
        codigo = "si x = 3\n{\n    imprimir 1\n}\nimprimir 2\n"
        self.assertEqual(errores_de(codigo), [(1, "Sintaxis inválida cerca de '='")])

    def test_condicion_incompleta_antes_de_la_llave(self):
        for codigo in ("si x > {\n    imprimir 1\n}\n", "mientras {\n    imprimir 1\n}\n"):
            with self.subTest(codigo=codigo):
                self.assertEqual(
                    errores_de(codigo), [(1, "Sintaxis inválida cerca de '{'")]
                )

    def test_error_en_el_encabezado_de_un_bloque_anidado(self):
        codigo = (
            "si verdadero {\n"
            "    mientras x > {\n"      # 2: error
            "        imprimir 1\n"
            "    }\n"
            "    imprimir 2\n"
            "}\n"                       # cierra el 'si' exterior: no hay error al final
        )
        self.assertEqual(errores_de(codigo), [(2, "Sintaxis inválida cerca de '{'")])

    def test_error_dentro_de_un_bloque_escrito_en_una_sola_linea(self):
        # La '}' de la misma línea sigue cerrando el bloque y el análisis continúa.
        self.assertEqual(
            errores_de("si verdadero { var = 5 }\nimprimir 1 2\n"),
            [
                (1, "Sintaxis inválida cerca de '='"),
                (2, "Sintaxis inválida cerca de 2"),
            ],
        )

    def test_errores_en_bloques_anidados_se_informan_todos(self):
        codigo = (
            "si verdadero {\n"
            "    si verdadero {\n"
            "        var = 1\n"        # 3
            "    }\n"
            "    var = 2\n"            # 5
            "}\n"
            "var = 3\n"                # 7
        )
        self.assertEqual([linea for linea, _ in errores_de(codigo)], [3, 5, 7])

    def test_llave_de_cierre_sobrante_despues_de_un_bloque(self):
        self.assertEqual(
            errores_de("si verdadero {\n    imprimir 1\n}\n}\n"),
            [(4, "Sintaxis inválida cerca de '}'")],
        )

    def test_se_recupera_dentro_de_un_bloque(self):
        codigo = (
            "si verdadero {\n"     # 1
            "    var = 1\n"        # 2: error dentro del bloque
            "    imprimir 2\n"     # 3: correcta
            "}\n"                  # 4: cierra el bloque sin error adicional
            "imprimir 3 3\n"       # 5: error fuera del bloque
        )
        self.assertEqual(
            errores_de(codigo),
            [
                (2, "Sintaxis inválida cerca de '='"),
                (5, "Sintaxis inválida cerca de 3"),
            ],
        )

    def test_sentencia_incompleta_se_informa_en_el_token_siguiente(self):
        # Sin separadores, la falta se detecta al llegar a la siguiente sentencia.
        self.assertEqual(
            errores_de("var x =\nimprimir x\n"),
            [(2, "Sintaxis inválida cerca de 'imprimir'")],
        )

    def test_llave_de_cierre_sobrante(self):
        self.assertEqual(
            errores_de("imprimir 1\n}\nimprimir 2\n"),
            [(2, "Sintaxis inválida cerca de '}'")],
        )

    def test_sino_sin_si(self):
        self.assertEqual(
            errores_de("sino { imprimir 1 }\nimprimir 2\n"),
            [(1, "Sintaxis inválida cerca de 'sino'")],
        )

    def test_error_al_final_del_programa_incluye_la_ultima_linea(self):
        self.assertEqual(
            errores_de("si verdadero {\n    imprimir 1\n"),
            [(2, "Sintaxis inválida al final del programa")],
        )
        self.assertEqual(
            errores_de("var x = 1 +"),
            [(1, "Sintaxis inválida al final del programa")],
        )

    def test_el_final_del_programa_ignora_lineas_vacias_y_comentarios(self):
        codigo = "var x = 1\nvar z = x +\n\n\n# fin del archivo\n\n"
        self.assertEqual(
            errores_de(codigo), [(2, "Sintaxis inválida al final del programa")]
        )

    def test_error_al_final_junto_con_errores_anteriores(self):
        codigo = "var = 1\nsi verdadero {\n    imprimir 2\n"
        self.assertEqual(
            errores_de(codigo),
            [
                (1, "Sintaxis inválida cerca de '='"),
                (3, "Sintaxis inválida al final del programa"),
            ],
        )

    def test_el_error_lexico_se_informa_antes_que_los_de_sintaxis(self):
        with self.assertRaises(ErrorLexico) as contexto:
            parsear("var = 1\nvar y = @\n")
        self.assertEqual(contexto.exception.linea, 2)

    def test_cadena_sin_cerrar_llega_como_error_lexico(self):
        with self.assertRaises(ErrorLexico) as contexto:
            parsear('imprimir "hola\n')
        self.assertEqual(contexto.exception.mensaje, "Cadena sin cerrar")

    def test_un_programa_correcto_despues_de_uno_con_errores(self):
        # El estado de los errores no debe filtrarse de un análisis al siguiente.
        errores_de("var = 1")
        self.assertEqual(parsear("var x = 1"), [("var", "x", ("num", 1), 1)])

    def test_cualquier_prefijo_del_ejemplo_termina_sin_fallar(self):
        with open(os.path.join(RAIZ, "ejemplo.mini"), encoding="utf-8") as archivo:
            codigo = archivo.read()
        for fin in range(len(codigo) + 1):
            try:
                parsear(codigo[:fin])
            except (ErroresSintacticos, ErrorLexico):
                pass


if __name__ == "__main__":
    unittest.main()
