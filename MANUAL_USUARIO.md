# Manual de usuario — Editor Proyecto Final:  Creación de un Compilador

Este manual explica cómo usar el editor gráfico de **Proyecto Final:  Creación de un Compilador** para escribir, analizar y ejecutar programas `.mini`. Para la definición completa del lenguaje y la instalación consulta el [README](README.md).

> Los textos `[AQUÍ VA CAPTURA: ...]` marcan los lugares donde se insertarán capturas de pantalla (guárdalas en `docs/capturas/`).

## 1. Iniciar el editor

1. Abre una terminal en la carpeta del proyecto.
2. Instala las dependencias (solo la primera vez): `pip install -r requirements.txt`
3. Inicia el editor: `python main.py`

[AQUÍ VA CAPTURA: ventana principal del editor recién abierta, con el editor de código vacío y el panel de salida vacío]

## 2. Descripción de la ventana

La ventana tiene cinco zonas, de arriba hacia abajo:

| Zona | Para qué sirve |
|---|---|
| **Barra de menús** | Menús **Archivo** (Abrir, Guardar, Salir) y **Ejecutar** (Analizar, Ejecutar). |
| **Botones** | Accesos rápidos: **Abrir**, **Guardar**, **Analizar**, **▶ Ejecutar** y **Limpiar salida**. |
| **Código** | El editor donde se escribe el programa. A la izquierda muestra la **numeración de líneas** y colorea el código (resaltado de sintaxis). |
| **Salida** | Panel de solo lectura donde aparecen los resultados de `imprimir`, el mensaje `✔ Código válido` y los mensajes de error. |
| **Barra de estado** | Mensajes breves que desaparecen solos a los 3 segundos (por ejemplo "Archivo guardado" o "Se encontraron 2 error(es)"). |

[AQUÍ VA CAPTURA: ventana principal con ejemplo.mini cargado, señalando con números la barra de menús, los botones, el editor con numeración, el panel de salida y la barra de estado]

## 3. Botones y opciones de menú

Cada opción del menú hace lo mismo que su botón.

| Acción | Botón | Menú | Atajo | Qué hace |
|---|---|---|---|---|
| **Abrir** | Abrir | Archivo ▸ Abrir | `Ctrl+O` | Muestra un cuadro para elegir un archivo (`*.mini` o `*.txt`) y carga su contenido en el editor. |
| **Guardar** | Guardar | Archivo ▸ Guardar | `Ctrl+S` | Guarda el programa. La primera vez pide el nombre del archivo (`.mini`); después sobrescribe ese mismo archivo. |
| **Analizar** | Analizar | Ejecutar ▸ Analizar | `F6` | Revisa el programa (léxico, sintaxis y semántica) **sin ejecutarlo**. Muestra `✔ Código válido` o la lista de errores. |
| **Ejecutar** | ▶ Ejecutar | Ejecutar ▸ Ejecutar | `F5` | Analiza el programa y, si no hay errores, lo ejecuta. Muestra lo que imprime el programa y al final `✔ Código válido`; si hay errores, muestra la lista y no ejecuta nada. |
| **Limpiar salida** | Limpiar salida | — | — | Borra el panel de salida y quita el marcado rojo de las líneas con error. |
| **Salir** | — | Archivo ▸ Salir | `Ctrl+Q` | Cierra el editor. |

[AQUÍ VA CAPTURA: menú Archivo desplegado, mostrando Abrir, Guardar y Salir]

[AQUÍ VA CAPTURA: menú Ejecutar desplegado, mostrando Analizar y Ejecutar]

Notas importantes:

- **Abrir** reemplaza el contenido del editor **sin preguntar** si hay cambios sin guardar. Guarda antes de abrir otro archivo.
- Después de **Abrir** o de la primera vez que **Guardas**, el botón **Guardar** siempre sobrescribe ese archivo (no hay "Guardar como"). Para crear una copia, copia el texto y guárdalo en un editor nuevo.
- **Analizar** y **Ejecutar** borran la salida anterior antes de empezar.
- Cerrar la ventana no avisa de cambios sin guardar.

## 4. Escribir y guardar un programa `.mini`

1. Haz clic en el área **Código** y escribe tu programa. Por ejemplo:

   ```text
   # Mi primer programa
   var nombre = "Ana"
   imprimir "Hola, " + nombre
   ```

   [AQUÍ VA CAPTURA: el programa de ejemplo escrito en el editor, mostrando el resaltado de colores y la numeración de líneas]

2. Pulsa **Analizar** (`F6`) para comprobar que no tiene errores, o **Ejecutar** (`F5`) para correrlo.
3. Pulsa **Guardar** (`Ctrl+S`). En el cuadro que aparece elige la carpeta y escribe un nombre terminado en `.mini` (por ejemplo `saludo.mini`).

   [AQUÍ VA CAPTURA: cuadro de diálogo "Guardar" con el nombre saludo.mini escrito]

4. Para volver a trabajar con él más tarde, usa **Abrir** y selecciona el archivo.

   [AQUÍ VA CAPTURA: cuadro de diálogo "Abrir" con un archivo .mini seleccionado]

### Ayudas visuales del editor

**Resaltado de sintaxis.** El editor colorea el código mientras escribes:

| Elemento | Color | Ejemplos |
|---|---|---|
| Palabras reservadas | Azul, en negrita | `var` `imprimir` `si` `sino` `mientras` `verdadero` `falso` `y` `o` `no` |
| Números | Naranja | `42` `3.14` |
| Cadenas de texto | Verde | `"Hola"` |
| Comentarios | Gris, en cursiva | `# esto es un comentario` |

**Numeración de líneas.** Los números de la izquierda se actualizan al escribir y siguen el desplazamiento (scroll). Los mensajes de error usan estos mismos números de línea.

**Líneas con error.** Cuando el análisis encuentra errores, las líneas afectadas se marcan con fondo rojo y el cursor salta a la primera de ellas. Las marcas desaparecen al volver a **Analizar** o **Ejecutar**, o al pulsar **Limpiar salida**.

## 5. Cómo interpretar los resultados

### El mensaje `✔ Código válido`

Aparece como última línea de la salida cuando todo salió bien:

- Con **Analizar**: el programa no tiene errores léxicos, de sintaxis ni semánticos. No se ejecutó nada.
- Con **Ejecutar**: además de estar libre de errores, el programa terminó de ejecutarse sin fallar. Las líneas anteriores son lo que imprimió el programa.

Un programa sin `imprimir` también muestra `✔ Código válido`: no habrá nada más en la salida porque el programa no imprime nada.

```text
Hola, Ana
✔ Código válido
```

[AQUÍ VA CAPTURA: salida del programa ejemplo.mini ejecutado, mostrando las líneas impresas y "✔ Código válido" al final, con "Ejecución terminada" en la barra de estado]

`✔ Código válido` solo dice que el programa es correcto para el lenguaje; no garantiza que haga lo que tú querías.

### Mensajes de error

Todos tienen la forma `[ERROR TIPO] Línea N: descripción` (`[ERROR LÉXICO]`, `[ERROR SINTÁCTICO]`, `[ERROR SEMÁNTICO]`; los de ejecución llevan solo `[ERROR]`), donde `N` es el número de línea del editor. Se muestran **todos** los errores que se encuentran en la misma fase.

| Tipo | Cuándo ocurre | Se detecta con |
|---|---|---|
| **LÉXICO** | Hay un carácter o una cadena de texto que el lenguaje no reconoce. | Analizar / Ejecutar |
| **SINTÁCTICO** | El programa no tiene la forma correcta (falta una llave, hay una expresión incompleta…). | Analizar / Ejecutar |
| **SEMÁNTICO** | La estructura es correcta pero no tiene sentido (variable sin declarar, tipos que no coinciden…). | Analizar / Ejecutar |
| **Ejecución** (prefijo `[ERROR]`) | El programa falla mientras se ejecuta (división entre cero, ciclo infinito). | Solo Ejecutar |

El análisis se hace por fases y solo pasa a la siguiente si la anterior no encontró errores. Por eso, al corregir los errores léxicos pueden aparecer errores de sintaxis, y al corregir estos, errores semánticos. Es normal.

#### Errores léxicos

| Mensaje | Causa y solución |
|---|---|
| `[ERROR LÉXICO] Línea 2: Carácter no reconocido: '@'` | Hay un carácter que no existe en Proyecto Final:  Creación de un Compilador (`@`, `$`, `!` suelto, `.`…). Bórralo o corrígelo. Solo se informa el primero que se encuentre. |
| `[ERROR LÉXICO] Línea 1: Cadena sin cerrar` | Falta la comilla `"` de cierre en esa línea. Los textos deben abrir y cerrar en la misma línea. |

[AQUÍ VA CAPTURA: error léxico "Cadena sin cerrar" en la salida, con la línea 1 marcada en rojo en el editor]

#### Errores sintácticos

| Mensaje | Causa y solución |
|---|---|
| `[ERROR SINTÁCTICO] Línea 3: Sintaxis inválida cerca de 2` | El programa no sigue la forma del lenguaje cerca de ese elemento (aquí, `imprimir 2 2`). Revisa esa línea **y la anterior**: en Proyecto Final:  Creación de un Compilador una sentencia incompleta (como `var x =`) se detecta al llegar a la siguiente. |
| `[ERROR SINTÁCTICO] Línea 2: Sintaxis inválida al final del programa` | El programa termina antes de lo esperado, casi siempre por una `{` sin su `}`, un paréntesis abierto o una expresión sin terminar. La línea es la última que tiene código. |

Todos los errores de sintaxis se muestran juntos, uno por línea. Un error puede provocar otros justo después (por ejemplo, un `si` con un error en su condición y con `sino` informa también el `sino`), así que corrige de arriba hacia abajo y vuelve a **Analizar**.

[AQUÍ VA CAPTURA: salida con varios errores sintácticos y las líneas correspondientes marcadas en rojo en el editor]

#### Errores semánticos

| Mensaje | Causa y solución |
|---|---|
| `Variable 'x' no declarada` | Usas o asignas una variable que nunca declaraste. Declárala antes con `var x = ...`. |
| `Variable 'x' ya declarada` | Declaraste dos veces la misma variable con `var`. Para cambiar su valor usa `x = ...` sin `var`. |
| `Asignación incompatible para 'x': se esperaba texto y se obtuvo numero` | Intentas guardar un valor de otro tipo (una variable de texto no puede recibir un número). |
| `La condición de 'si' debe ser booleana` / `... de 'mientras' ...` | La condición debe dar `verdadero` o `falso` (por ejemplo `x > 3`), no un número ni un texto. |
| `El operador '-' requiere operandos numéricos` | Operas con tipos incorrectos (por ejemplo `"a" - 1`). Los operadores `<` `>` `<=` `>=` `+` `-` `*` `/` `%` piden números (`+` también permite unir texto). |
| `El operador 'y' requiere valores booleanos` / `El operador 'no' requiere booleano` | Los operadores lógicos solo trabajan con `verdadero` / `falso`. |
| `El operador '==' requiere operandos del mismo tipo` | No se pueden comparar con `==` o `!=` valores de tipos distintos. |
| `División entre cero con valor constante` | Divides (`/` o `%`) entre una expresión que vale cero, como `8 / 0`. |
| `La variable 'x' tiene tipos distintos en las ramas de 'si'` | Declaras la misma variable en el `si` y en el `sino` con tipos diferentes. |

[AQUÍ VA CAPTURA: salida con varios errores semánticos, con sus líneas marcadas en rojo]

#### Errores de ejecución

| Mensaje | Causa y solución |
|---|---|
| `[ERROR] Línea 3: División entre cero` | Una variable valía cero en el momento de dividir. Lo que el programa alcanzó a imprimir antes del error se conserva en la salida. |
| `[ERROR] Línea 2: Demasiadas iteraciones (¿bucle infinito?)` | Un `mientras` repitió más de 100 000 veces. Revisa que su condición pueda volverse falsa. La línea indicada es la del `mientras`. |

[AQUÍ VA CAPTURA: salida de un error de ejecución, mostrando lo impreso antes del error y el mensaje de división entre cero]

## 6. Guía rápida del lenguaje Proyecto Final:  Creación de un Compilador

**Comentarios.** Empiezan con `#` y llegan al final de la línea.

```text
# esto es un comentario
```

**Variables.** Se declaran con `var` y un valor inicial; después se asignan con `=`. El tipo lo fija el primer valor.

```text
var edad = 18
edad = edad + 1
```

**Tipos.** `numero` (`5`, `3.14`), `texto` (`"hola"`) y `booleano` (`verdadero`, `falso`).

**Salida.** `imprimir` muestra un valor en el panel de salida. Con `+` se unen textos y valores.

```text
imprimir "Tengo " + edad + " años"
```

**Operadores.**

| Tipo | Operadores |
|---|---|
| Aritméticos | `+` `-` `*` `/` `%` |
| Comparación | `==` `!=` `<` `>` `<=` `>=` |
| Lógicos | `y` `o` `no` |
| Agrupar | `( )` |

**Condicional.** La condición debe ser booleana y los bloques van entre llaves.

```text
si edad >= 18 {
    imprimir "Mayor de edad"
} sino {
    imprimir "Menor de edad"
}
```

**Ciclo.**

```text
var i = 1
mientras i <= 3 {
    imprimir i
    i = i + 1
}
```

**Palabras reservadas** (no se pueden usar como nombres de variable): `var` `imprimir` `si` `sino` `mientras` `verdadero` `falso` `y` `o` `no`.

## 7. Problemas frecuentes

| Situación | Explicación |
|---|---|
| `var y = 3` da error de sintaxis. | `y` (y también `o`, `no`) es palabra reservada. Usa otro nombre, por ejemplo `var ye = 3`. |
| Una línea que empieza con `-` no se comporta como esperaba. | En Proyecto Final:  Creación de un Compilador no hay separador entre sentencias, así que `imprimir x` seguido de `-5` en la línea siguiente se lee como `imprimir x - 5`. Escribe `imprimir -5` si quieres imprimir el número negativo. |
| El error dice una línea distinta de la que esperaba. | Una sentencia incompleta (por ejemplo `var x =`) se detecta en el siguiente elemento del programa, que suele estar en la línea de abajo. Revisa también la línea anterior. |
| Aparecen varios errores por una sola equivocación. | Un error de sintaxis puede arrastrar otros (por ejemplo, el `sino` de un `si` cuya condición tenía el error). Corrige el primero y vuelve a **Analizar**. |
| Escribí `si x = 3 { ... }` y da error de sintaxis. | Para comparar se usa `==` (dos signos). Un solo `=` es asignación y no puede ir en una condición. |
| Un texto con comillas dentro da error. | Proyecto Final:  Creación de un Compilador no admite comillas ni saltos de línea dentro de un texto. |
| Escribí algo con `ü` y da "Carácter no reconocido". | Los nombres de variable aceptan letras sin diéresis, vocales con tilde y `ñ`; evita la `ü`. (Dentro de un texto entre comillas sí puedes usar cualquier carácter.) |
| Ejecutar tarda y luego dice "Demasiadas iteraciones". | Un ciclo `mientras` nunca terminó. El editor lo detiene automáticamente después de 100 000 vueltas. |
