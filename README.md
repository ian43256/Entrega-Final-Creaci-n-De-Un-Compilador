# Proyecto Final:  Creación de un Compilador

## Descripción del proyecto

**Proyecto Final:  Creación de un Compilador** es un lenguaje de programación pequeño, con palabras reservadas en español, creado como proyecto final de la materia de Compiladores. Los programas se guardan en archivos con extensión `.mini`.

El proyecto incluye:

- Un **compilador/intérprete** en Python, construido con [PLY](https://www.dabeaz.com/ply/) (`lex` y `yacc`), que realiza análisis **léxico**, **sintáctico** y **semántico** y después **ejecuta** el programa.
- Un **editor gráfico** hecho con **PyQt6** (diseñado con Qt Designer) para escribir, analizar y ejecutar programas Proyecto Final:  Creación de un Compilador, con resaltado de sintaxis, numeración de líneas y marcado de las líneas con error.

Ejemplo de programa:

```text
# Mi primer programa
var x = 5
imprimir "x vale " + x

si x > 3 {
    imprimir "x es mayor que 3"
} sino {
    imprimir "x es pequeño"
}
```

## Requisitos e instalación

- Python 3 reciente (el proyecto se probó con Python 3.14).
- Las bibliotecas **PyQt6** y **PLY** (listadas en `requirements.txt`). Las pruebas usan solo la biblioteca estándar (`unittest`).

```bash
# (opcional pero recomendado) crear y activar un entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
```

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
python main.py
```

Se abre el editor. Escribe un programa (o ábrelo con **Abrir**, por ejemplo `ejemplo.mini`) y usa **Analizar** o **Ejecutar**. El detalle de la ventana está en el [manual de usuario](MANUAL_USUARIO.md).

Para probar solo el motor del lenguaje, sin interfaz gráfica:

```bash
python prueba_nucleo.py
```

## Estructura del proyecto

| Archivo / carpeta | Qué hace |
|---|---|
| `main.py` | Programa principal: ventana del editor. Conecta botones y menú con el compilador y muestra la salida y los errores. |
| `interfaz.ui` | Diseño de la ventana hecho en Qt Designer (botones, menú, editor, salida). |
| `ui_principal.py` | Código de la ventana **generado** con `pyuic6 -o ui_principal.py interfaz.ui`. No se edita a mano: si cambia `interfaz.ui`, se vuelve a generar. |
| `editor.py` | `EditorCodigo`: el cuadro de texto del código, con numeración de líneas y marcado de líneas con error. Es el widget `txtEditor` (promovido en `interfaz.ui`). |
| `resaltador.py` | `ResaltadorSintaxis`: resaltado de sintaxis (`QSyntaxHighlighter`). |
| `ejemplo.mini` | Programa de ejemplo válido. |
| `prueba_nucleo.py` | Prueba manual del motor: imprime tokens, árbol, errores semánticos y la ejecución de `ejemplo.mini`. |
| `requirements.txt` | Dependencias (PyQt6 y PLY). |
| `compilador/__init__.py` | Expone la API: `ejecutar`, `analizar_codigo` y las excepciones. |
| `compilador/errores.py` | Excepciones del lenguaje: `LenguajeError`, `ErrorLexico`, `ErroresSintacticos`. |
| `compilador/lexer.py` | Análisis léxico (tokens, palabras reservadas, errores léxicos). |
| `compilador/parser.py` | Análisis sintáctico (gramática) con recuperación de errores. Construye el árbol del programa. |
| `compilador/semantico.py` | Análisis semántico: variables, tipos, condiciones y división entre cero constante. |
| `compilador/interprete.py` | Intérprete que ejecuta el árbol (`ejecutar`) y análisis sin ejecutar (`analizar_codigo`). |
| `tests/` | Pruebas automáticas con `unittest`. |
| `docs/capturas/` | Carpeta para las capturas de pantalla del manual. |
| `MANUAL_USUARIO.md` | Manual de usuario del editor. |

El flujo de un programa es: **texto → analizador léxico → analizador sintáctico → analizador semántico → intérprete**. Cada fase solo se ejecuta si la anterior no encontró errores.

## Definición del lenguaje

### Tokens

Los espacios, tabuladores y saltos de línea separan tokens y se ignoran. Los comentarios empiezan con `#` y llegan hasta el final de la línea; también se ignoran.

| Token | Lexema | Ejemplos |
|---|---|---|
| `ID` | Letra (`A-Z`, `a-z`, vocales con tilde, `Ñ`, `ñ`) o `_`, seguida de letras, `_` o dígitos. Si coincide con una palabra reservada, es esa palabra. | `x`, `suma_total`, `año` |
| `NUM` | Entero o decimal: `\d+(\.\d+)?` | `42`, `3.14` |
| `STR` | Texto entre comillas dobles, en una sola línea y sin comillas dentro | `"Hola mundo"` |
| `VAR`, `IMPRIMIR`, `SI`, `SINO`, `MIENTRAS`, `VERDADERO`, `FALSO`, `Y`, `O`, `NO` | Palabras reservadas (ver abajo) | `var`, `si` |
| `ASSIGN` | `=` | |
| `EQ`, `NE` | `==`, `!=` | |
| `LT`, `GT`, `LE`, `GE` | `<`, `>`, `<=`, `>=` | |
| `PLUS`, `MINUS`, `TIMES`, `DIVIDE`, `MOD` | `+`, `-`, `*`, `/`, `%` | |
| `LPAREN`, `RPAREN` | `(`, `)` | |
| `LBRACE`, `RBRACE` | `{`, `}` | |

### Palabras reservadas

`var` · `imprimir` · `si` · `sino` · `mientras` · `verdadero` · `falso` · `y` · `o` · `no`

> Las palabras reservadas no pueden usarse como nombre de variable. Cuidado con `y` y `o`: son los operadores lógicos, así que `var y = 3` es un error de sintaxis.

### Tipos

| Tipo | Valores | Notas |
|---|---|---|
| `numero` | `5`, `3.14` | Enteros y decimales. Al imprimir, un decimal sin parte fraccionaria se muestra como entero (`4 / 2` imprime `2`). |
| `texto` | `"hola"` | Sin secuencias de escape: no puede contener comillas ni saltos de línea. |
| `booleano` | `verdadero`, `falso` | Se imprimen como `verdadero` / `falso`. |

El tipo de una variable lo fija su primer valor (`var n = 5` la hace numérica) y no puede cambiar después.

### Operadores y precedencia

De **menor** a **mayor** precedencia (los de una misma fila tienen igual precedencia):

| Nivel | Operadores | Asociatividad | Operandos | Resultado |
|---|---|---|---|---|
| 1 (menor) | `o` | izquierda | booleanos | booleano |
| 2 | `y` | izquierda | booleanos | booleano |
| 3 | `no` (prefijo) | derecha | booleano | booleano |
| 4 | `==` `!=` `<` `>` `<=` `>=` | izquierda | `==`/`!=`: ambos del mismo tipo; `<` `>` `<=` `>=`: numéricos | booleano |
| 5 | `+` `-` | izquierda | numéricos; `+` con algún texto concatena | numero (o texto) |
| 6 | `*` `/` `%` | izquierda | numéricos | numero |
| 7 (mayor) | `-` (prefijo, negativo) | derecha | numérico | numero |

Los paréntesis `( )` agrupan. Ejemplos: `no 1 == 2` se lee `no (1 == 2)`; `-2 * 3` se lee `(-2) * 3`. Los operadores `y` / `o` evalúan en cortocircuito. La división `/` siempre produce un valor decimal.

### Gramática

Producciones tal como las define `compilador/parser.py` (las palabras en MAYÚSCULAS son tokens; `ε` es la producción vacía):

```text
programa    → sentencias

sentencias  → sentencias sentencia
            | ε

sentencia   → VAR ID ASSIGN expresion                  declaración
            | ID ASSIGN expresion                      asignación
            | IMPRIMIR expresion                       salida
            | SI expresion bloque                      condicional
            | SI expresion bloque SINO bloque          condicional con alternativa
            | MIENTRAS expresion bloque                ciclo

bloque      → LBRACE sentencias RBRACE

expresion   → expresion O expresion       | expresion Y expresion
            | expresion EQ expresion      | expresion NE expresion
            | expresion LT expresion      | expresion GT expresion
            | expresion LE expresion      | expresion GE expresion
            | expresion PLUS expresion    | expresion MINUS expresion
            | expresion TIMES expresion   | expresion DIVIDE expresion
            | expresion MOD expresion
            | NO expresion                (prefijo, precedencia de NOT)
            | MINUS expresion             (prefijo, precedencia de UMINUS)
            | LPAREN expresion RPAREN
            | NUM | STR | VERDADERO | FALSO | ID
```

**Recuperación de errores.** Para poder informar varios errores de sintaxis a la vez, la implementación agrega a las listas de sentencias una producción con el símbolo especial `error` de PLY (`sentencias → sentencias error`). Como el programa y los bloques necesitan puntos de sincronización distintos, el programa usa una copia de la lista llamada `sentencias_programa`. Esas producciones no cambian el lenguaje, solo lo que ocurre después de un error.

### Reglas semánticas

El analizador semántico informa todos los errores que encuentra (no se detiene en el primero):

- Toda variable debe declararse con `var` antes de usarse o asignarse, y no puede declararse dos veces.
- Una asignación debe conservar el tipo de la variable.
- Los operadores exigen los tipos de la tabla de precedencia (por ejemplo, `"a" - 1` es un error).
- La condición de `si` y de `mientras` debe ser booleana.
- Dividir (`/` o `%`) entre una expresión constante igual a cero es un error (`8 / 0`, `2 / (1 - 1)`). Si el divisor es una variable, el error aparece al ejecutar.
- Las variables declaradas dentro de un bloque de `mientras` no existen fuera de él. En un `si … sino`, una variable declarada dentro solo existe después si se declara en **ambas** ramas y con el mismo tipo.
- Un `mientras` se detiene con un error de ejecución si pasa de 100 000 iteraciones (`MAX_ITERACIONES`), para evitar que un ciclo infinito congele la interfaz.

### Dos detalles importantes del lenguaje

**(a) Las sentencias no llevan separador.** No hay `;` ni obligación de saltos de línea: las sentencias se reconocen una tras otra. Por eso, una línea que empieza con `-` **continúa la expresión anterior** en lugar de empezar una sentencia nueva:

```text
var x = 4
imprimir x
-5
```

Esto se lee como `imprimir x - 5` y escribe `-1`, no `4` y luego `-5`. Si quieres imprimir un número negativo en una línea nueva, escribe `imprimir -5`.

**(b) `si … sino` no es ambiguo.** Los bloques siempre van entre llaves `{ }`, así que un `sino` pertenece siempre al `si` cuyo bloque se acaba de cerrar con `}`; no existe el problema clásico del "else colgante". Por eso la gramática **no tiene ningún conflicto shift/reduce** (ni reduce/reduce): PLY no reporta advertencias al construirla. Se puede comprobar con:

```bash
python -c "import ply.yacc as y, compilador.parser as p; y.yacc(module=p, start='programa', write_tables=False, debug=True, debugfile='parser.out', outputdir='.')"
```

Si hubiera conflictos, PLY imprimiría líneas `WARNING: ... shift/reduce conflict` (el comando también crea `parser.out` con las tablas LALR; puedes borrarlo). Un conflicto de este tipo solo aparecería si `si` aceptara una sentencia sin llaves. Ejemplo de asociación:

```text
si a { si b { imprimir 1 } sino { imprimir 2 } }     # el sino es del si interno (b)
si a { si b { imprimir 1 } } sino { imprimir 2 }     # el sino es del si externo (a)
```

## Ejemplos

La **salida esperada** es exactamente lo que aparece en el panel *Salida* del editor.

### Programas válidos

**1. `ejemplo.mini`** (se ejecuta con **Ejecutar**):

```text
# Mi primer programa
var x = 5
imprimir "Hola mundo"
imprimir "x vale " + x

si x > 3 {
    imprimir "x es mayor que 3"
} sino {
    imprimir "x es pequeño"
}

var suma = 0
mientras x > 0 {
    suma = suma + x
    x = x - 1
}
imprimir "Suma = " + suma
```

```text
Hola mundo
x vale 5
x es mayor que 3
Suma = 15
✔ Código válido
```

**2. Ciclo y operadores lógicos:**

```text
# Tabla del 3 y operadores lógicos
var n = 1
mientras n <= 5 {
    imprimir "3 x " + n + " = " + (3 * n)
    n = n + 1
}
var activo = verdadero
si activo y n > 5 {
    imprimir "Terminó"
}
```

```text
3 x 1 = 3
3 x 2 = 6
3 x 3 = 9
3 x 4 = 12
3 x 5 = 15
Terminó
✔ Código válido
```

**3. Factorial:**

```text
# Factorial de 5
var n = 5
var factorial = 1
mientras n > 1 {
    factorial = factorial * n
    n = n - 1
}
imprimir "5! = " + factorial
```

```text
5! = 120
✔ Código válido
```

**4. Operadores y formato de valores:**

```text
imprimir 10 / 4
imprimir 7 % 3
imprimir "Hola " + "mundo"
imprimir 3 > 2 y no (1 == 2)
imprimir -2 * 3 + 1
```

```text
2.5
1
Hola mundo
verdadero
-5
✔ Código válido
```

**5. Una línea que empieza con `-`** (detalle (a) de arriba):

```text
var x = 4
imprimir x
-5
```

```text
-1
✔ Código válido
```

### Programas con errores

Cuando hay errores no se ejecuta nada; cada error se escribe en la salida con su tipo y su línea, y la línea se marca en rojo en el editor. **Analizar** y **Ejecutar** muestran los mismos errores de análisis.

**6. Error léxico: carácter no reconocido**

```text
var precio = 100
var total = precio * 2 @ 3
imprimir total
```

```text
[ERROR LÉXICO] Línea 2: Carácter no reconocido: '@'
```

**7. Error léxico: cadena sin cerrar**

```text
var saludo = "Hola
imprimir saludo
```

```text
[ERROR LÉXICO] Línea 1: Cadena sin cerrar
```

**8. Varios errores de sintaxis** (se informan todos juntos):

```text
var = 5
imprimir "ok"
imprimir 2 2
var x = 3
x = = 4
```

```text
[ERROR SINTÁCTICO] Línea 1: Sintaxis inválida cerca de '='
[ERROR SINTÁCTICO] Línea 3: Sintaxis inválida cerca de 2
[ERROR SINTÁCTICO] Línea 5: Sintaxis inválida cerca de '='
```

**9. Error de sintaxis al final del programa** (falta cerrar un bloque; se señala la última línea con código):

```text
si verdadero {
    imprimir "falta cerrar el bloque"
```

```text
[ERROR SINTÁCTICO] Línea 2: Sintaxis inválida al final del programa
```

**10. Errores semánticos** (se informan todos):

```text
var edad = 18
var edad = 20
nombre = "Ana"
var texto = "hola"
texto = 5
si edad {
    imprimir texto
}
imprimir 8 / 0
```

```text
[ERROR SEMÁNTICO] Línea 2: Variable 'edad' ya declarada
[ERROR SEMÁNTICO] Línea 3: Variable 'nombre' no declarada
[ERROR SEMÁNTICO] Línea 5: Asignación incompatible para 'texto': se esperaba texto y se obtuvo numero
[ERROR SEMÁNTICO] Línea 6: La condición de 'si' debe ser booleana
[ERROR SEMÁNTICO] Línea 9: División entre cero con valor constante
```

**11. Error de ejecución: división entre una variable que vale cero** (prefijo `[ERROR]`) (lo impreso antes del error se conserva):

```text
var d = 0
imprimir "antes de dividir"
imprimir 10 / d
imprimir "no se llega aquí"
```

```text
antes de dividir
[ERROR] Línea 3: División entre cero
```

**12. Error de ejecución: ciclo infinito**

```text
var n = 0
mientras verdadero {
    n = n + 1
}
```

```text
[ERROR] Línea 2: Demasiadas iteraciones (¿bucle infinito?)
```

### Cómo se informan los errores de sintaxis

- El análisis **se recupera** después de cada error y sigue buscando más. Tras un error se ignora lo que falte de la sentencia y el análisis continúa en la siguiente línea que empiece una sentencia (si el token inesperado ya abre una línea y puede empezar una sentencia, continúa desde él). Las llaves se emparejan: si se ignora una `{`, también se ignora su `}`.
- Se informa **un solo error por línea**.
- La línea indicada es la del primer token que no encaja. Como las sentencias no llevan separador, una sentencia incompleta (por ejemplo `var x =`) se detecta al llegar a la sentencia siguiente, y el error se marca en esa línea.
- Un error puede provocar otros a continuación. Por ejemplo, en `si x = 3 { ... } sino { ... }` se informa el `=` (debía ser `==`) y además el `sino`, que quedó sin su `si`. Conviene corregir de arriba hacia abajo y volver a analizar.
- El análisis léxico termina antes de empezar el sintáctico: si hay un error **léxico**, se informa solo el primero de ellos y no se buscan errores de sintaxis hasta corregirlo.

## Pruebas

Las pruebas automáticas usan `unittest` (biblioteca estándar) y cubren el lexer, el parser, el analizador semántico y el intérprete:

```bash
python -m unittest discover tests
```

Deben terminar con `OK`. Además, `python prueba_nucleo.py` hace una prueba manual del motor completo.

Si modificas `interfaz.ui` en Qt Designer, regenera la ventana con:

```bash
pyuic6 -o ui_principal.py interfaz.ui
```

## Créditos

Proyecto final de Compiladores — **Ian Hernández Ibarra**.

Construido con Python, [PLY](https://www.dabeaz.com/ply/) y [PyQt6](https://www.riverbankcomputing.com/software/pyqt/).
