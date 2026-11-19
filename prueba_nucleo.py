from pprint import pprint

from compilador import ErroresSemanticos, LenguajeError, ejecutar
from compilador.lexer import tokenizar
from compilador.parser import parsear
from compilador.semantico import analizar


def main():
    with open("ejemplo.mini", encoding="utf-8") as archivo:
        codigo = archivo.read()

    print("=== Análisis léxico: tokens ===")
    for token in tokenizar(codigo):
        print(f"{token.type}: {token.value!r} (línea {token.lineno})")

    print("\n=== Análisis sintáctico: árbol ===")
    arbol = parsear(codigo)
    pprint(arbol)

    print("\n=== Análisis semántico: errores de ejemplo ===")
    codigo_con_errores = """
var a = 1
var a = 2
b = 3
var texto = "hola"
texto = 2
si 4 {
    imprimir "no es una condición booleana"
}
var division = 2 / (1 - 1)
"""
    errores = analizar(parsear(codigo_con_errores))
    if errores:
        for error in errores:
            print(f"Línea {error.linea}: {error.mensaje}")
    else:
        print("Sin errores semánticos")

    print("\n=== Ejecución del programa de ejemplo ===")
    try:
        ejecutar(codigo)
    except ErroresSemanticos as error:
        for problema in error.errores:
            print(f"[ERROR SEMÁNTICO] Línea {problema.linea}: {problema.mensaje}")
    except LenguajeError as error:
        print(f"[ERROR] {error}")


if __name__ == "__main__":
    main()
