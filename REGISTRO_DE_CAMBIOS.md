# Registro de Cambios en el Código del Compilador

**Proyecto:** Entrega Final - Creación de un Compilador  
**Repositorio:** https://github.com/ian43256/Entrega-Final-Creaci-n-De-Un-Compilador.git  
**Rama de trabajo:** interfaz-bonita  
**Fecha de las sesiones:** 19 de noviembre de 2026  

---

## Resumen

Este documento registra paso a paso todos los cambios realizados al código del proyecto durante las sesiones de desarrollo asistido con Junie (asistente de programación de JetBrains). Los cambios se centraron exclusivamente en la **mejora visual de la interfaz gráfica** del compilador de MiniLang, sin modificar la lógica del compilador ni los tests.

---

## Sesión 1: Mejora de la Interfaz Gráfica

### Paso 1: Preparación del entorno

**Acción:** Se creó un entorno virtual de Python y se instalaron las dependencias del proyecto.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Resultado:** Entorno virtual creado exitosamente con PyQt6, PLY y demás dependencias instaladas.

---

### Paso 2: Clonación del repositorio

**Acción:** Se clonó el repositorio desde GitHub para obtener el código base.

```powershell
git clone https://github.com/ian43256/Entrega-Final-Creaci-n-De-Un-Compilador.git temp-clone
```

**Resultado:** Repositorio clonado y archivos movidos al directorio de trabajo.

---

### Paso 3: Creación de rama de trabajo

**Acción:** Se creó una rama dedicada para los cambios de interfaz, siguiendo las buenas prácticas de Git.

```powershell
git switch -c interfaz-bonita
```

**Resultado:** Rama `interfaz-bonita` creada y activa.

---

### Paso 4: Verificación inicial

**Acción:** Se ejecutaron los tests unitarios para confirmar que el código base funcionaba correctamente antes de hacer cambios.

```powershell
python -m unittest discover tests
```

**Resultado:** 86 tests ejecutados, todos pasaron (OK).

---

### Paso 5: Análisis de archivos existentes

**Acción:** Se revisaron los archivos clave del proyecto para entender la estructura antes de modificar:
- `main.py`: Punto de entrada de la aplicación, carga la interfaz y conecta los botones.
- `interfaz.ui`: Diseño XML de la ventana principal generado con Qt Designer.
- `editor.py`: Editor de código con numeración de líneas y marcado de errores.
- `resaltador.py`: Resaltado de sintaxis con diccionario FORMATOS y colores.
- `ui_principal.py`: Código Python generado automáticamente desde `interfaz.ui` con pyuic6.

---

### Paso 6: Creación de la hoja de estilos (estilos.qss)

**Acción:** Se creó el archivo `estilos.qss` desde cero con **309 líneas** de código QSS (Qt Style Sheets, equivalente a CSS para Qt).

**Archivo creado:** `estilos.qss`

**Contenido de los estilos:**

| Sección | Widgets afectados | Descripción |
|---------|-------------------|-------------|
| Ventana principal | QMainWindow | Fondo gris claro (#f5f5f5) |
| Barra de menú | QMenuBar, QMenu | Fondo blanco, texto oscuro, bordes redondeados, hover azul claro |
| Barra de estado | QStatusBar | Fondo blanco, borde superior, texto gris |
| Etiquetas | QLabel#lblEditor, QLabel#lblSalida | Fuente 14px, negrita, padding |
| Botones secundarios | btnAbrir, btnGuardar, btnAnalizar, btnLimpiar | Fondo blanco, borde gris, bordes redondeados, hover y pressed |
| Botón principal | btnEjecutar | Azul (#2563eb), texto blanco, negrita, hover y pressed más oscuro |
| Editor y salida | QPlainTextEdit, QPlainTextEdit#txtEditor, QPlainTextEdit#txtSalida | Borde suave, fuente monoespaciada, padding |
| Layouts | QVBoxLayout, QHBoxLayout#layoutBotones | Espaciado de 8px entre botones |
| Diálogos | QFileDialog, QMessageBox | Tema claro coherente con la ventana principal |
| Barras de desplazamiento | QScrollBar:vertical, QScrollBar:horizontal | Personalizadas con colores del tema |

**Colores originales de los botones:**
- Botones secundarios: Fondo blanco (#ffffff), borde gris (#c0c0c0)
- Botón Ejecutar: Azul (#2563eb), texto blanco

---

### Paso 7: Modificación del diseño de la ventana (interfaz.ui)

**Acción:** Se modificó `interfaz.ui` para mejorar las dimensiones de la ventana.

**Archivo modificado:** `interfaz.ui`

**Cambios realizados:**

| Propiedad | Antes | Después |
|-----------|-------|---------|
| Tamaño mínimo | No definido | 800 x 550 píxeles |
| Tamaño predeterminado | 900 x 650 píxeles | 1000 x 700 píxeles |

**Código agregado (XML):**
```xml
<property name="minimumSize">
    <size>
        <width>800</width>
        <height>550</height>
    </size>
</property>
```

**Motivo:** Evitar que la ventana se haga demasiado pequeña y proporcionar más espacio para el editor y la salida.

---

### Paso 8: Modificación de main.py (primera edición)

**Acción:** Se agregaron las importaciones y la constante para cargar la hoja de estilos.

**Archivo modificado:** `main.py`

**Cambios realizados:**

1. **Importación agregada:**
```python
from pathlib import Path
```

2. **Constante agregada:**
```python
RUTA_ESTILOS = Path(__file__).with_name("estilos.qss")
```

**Motivo:** Permitir que la aplicación cargue los estilos QSS al iniciar.

---

### Paso 9: Modificación de main.py (segunda edición)

**Acción:** Se agregó la línea que aplica la hoja de estilos a la aplicación.

**Archivo modificado:** `main.py`

**Cambio realizado:**
```python
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(RUTA_ESTILOS.read_text(encoding="utf-8"))  # ← Línea agregada
    win = Window()
    win.show()
    sys.exit(app.exec())
```

**Motivo:** Cargar los estilos definidos en `estilos.qss` al iniciar la aplicación.

---

### Paso 10: Regeneración de ui_principal.py

**Acción:** Se regeneró el archivo Python desde el archivo UI modificado.

```powershell
.venv\Scripts\pyuic6 -o ui_principal.py interfaz.ui
```

**Archivo regenerado:** `ui_principal.py`

**Motivo:** `ui_principal.py` es código generado automáticamente desde `interfaz.ui`. Cada vez que se modifica el archivo `.ui`, se debe regenerar para que los cambios reflejen en la aplicación.

**Verificación:** La primera línea de `ui_principal.py` confirma que fue generado desde `interfaz.ui`.

---

### Paso 11: Verificación intermedia

**Acción:** Se ejecutaron los tests unitarios después de los cambios iniciales.

```powershell
python -m unittest discover tests
```

**Resultado:** 86 tests ejecutados, todos pasaron (OK). La interfaz no se rompió.

---

### Paso 12: Cambio a paleta de colores pastel

**Acción:** Se solicitó cambiar el diseño de los botones a una paleta de colores pastel, manteniendo todas las funcionalidades.

**Archivo modificado:** `estilos.qss`

**Cambios realizados:** Se reemplazaron los estilos genéricos de botones por estilos individuales con colores pastel únicos.

| Botón | Color pastel | Código hexadecimal | Estado hover | Estado pressed |
|-------|-------------|-------------------|--------------|----------------|
| Abrir | Azul pastel | #C5D9F7 | #B0C8F0 | #9AB8E6 |
| Guardar | Verde pastel | #A8F0C6 | #93E6BA | #7DDCAE |
| Analizar | Durazno pastel | #FFCBA4 | #FFBE8E | #FFB078 |
| Ejecutar | Rosa pastel | #FF8FA3 | #FF7A96 | #FF6588 |
| Limpiar | Amarillo pastel | #E8F8C5 | #D8F0B0 | #C8E898 |

**Cambios técnicos:**
- Se eliminaron los selectores grupales (ej. `QPushButton#btnAbrir, QPushButton#btnGuardar, ...`)
- Se crearon selectores individuales para cada botón
- Cada botón tiene ahora 3 estados: normal, `:hover` y `:pressed`
- Bordes cambiados de 1px a 2px solid
- Border-radius aumentado de 6px a 8px
- El botón Ejecutar mantiene `font-weight: bold` como botón principal destacado

**Estadísticas del cambio:** +82 líneas agregadas, -26 líneas eliminadas.

---

### Paso 13: Verificación final

**Acción:** Se ejecutaron los tests unitarios por última vez para confirmar que todos los cambios funcionan correctamente.

```powershell
python -m unittest discover tests
```

**Resultado:** 86 tests ejecutados, todos pasaron (OK).

**Verificación de archivos modificados:**
```
On branch interfaz-bonita
Changes not staged for commit:
  modified:   interfaz.ui
  modified:   main.py
  modified:   ui_principal.py

Untracked files:
  estilos.qss
```

**Confirmación:** Solo se modificaron los archivos permitidos. No se tocaron: `compilador/`, `tests/`, `README.md`, `MANUAL_USUARIO.md`, `requirements.txt`, `.gitignore`.

---

## Sesión 2: Solución de Problemas de Git y GitHub

### Problema identificado

La cuenta de GitHub del usuario (`ian43256`) estaba marcada (flagged) por el sistema de seguridad de GitHub, lo que impedía autorizar aplicaciones de terceros (OAuth). Esto bloqueaba la autenticación desde PyCharm.

**Mensaje de error:**
> "This account is flagged, and therefore cannot authorize a third party application."

### Diagnóstico realizado

1. **Verificación del repositorio remoto:**
```powershell
git remote -v
```
Resultado: Repositorio configurado correctamente con HTTPS.

2. **Verificación del estado del repositorio:**
```powershell
git status
```
Resultado: Rama `interfaz-bonita` activa, sin cambios pendientes, árbol de trabajo limpio.

3. **Intento de push:**
```powershell
git push origin interfaz-bonita
```
Resultado: El push se interrumpió por exceder el tiempo de espera (esperando credenciales).

4. **Verificación de configuración de Git:**
```powershell
git config --global --list
```
Resultado: Usuario configurado como `JD953` con correo `estudiosj953@gmail.com`, sin credenciales guardadas ni SSH configurado.

5. **Verificación de claves SSH:**
```powershell
Test-Path "$env:USERPROFILE\.ssh"
```
Resultado: No existen claves SSH configuradas.

### Solución propuesta

Se propuso crear un **Personal Access Token (token personal)** en GitHub y usarlo como contraseña al hacer push desde la terminal:

```powershell
git push https://ian43256:TU_TOKEN@github.com/ian43256/Entrega-Final-Creaci-n-De-Un-Compilador.git interfaz-bonita
```

### Comandos de commit propuestos

Se proporcionaron 18 comandos de commit atómicos para distribuir los cambios de forma lógica:

| # | Commit | Archivo(s) |
|---|--------|-----------|
| 1 | Crea rama interfaz-bonita | --allow-empty |
| 2 | Agrega tamaño mínimo de ventana | interfaz.ui |
| 3 | Aumenta tamaño predeterminado a 1000x700 | interfaz.ui |
| 4 | Regenera ui_principal.py con pyuic6 | ui_principal.py |
| 5 | Agrega importación de Path y RUTA_ESTILOS | main.py |
| 6 | Carga hoja de estilos QSS al iniciar | main.py |
| 7 | Agrega estilos base (ventana, menú, barra de estado) | estilos.qss |
| 8 | Estiliza etiquetas Código y Salida | estilos.qss |
| 9 | Estiliza botón Abrir (azul pastel) | estilos.qss |
| 10 | Estiliza botón Guardar (verde pastel) | estilos.qss |
| 11 | Estiliza botón Analizar (durazno pastel) | estilos.qss |
| 12 | Estiliza botón Ejecutar (rosa pastel) | estilos.qss |
| 13 | Estiliza botón Limpiar (amarillo pastel) | estilos.qss |
| 14 | Estiliza layouts, editor y área de salida | estilos.qss |
| 15 | Estiliza diálogos QFileDialog | estilos.qss |
| 16 | Personaliza barras de desplazamiento | estilos.qss |
| 17 | Estiliza QMessageBox | estilos.qss |
| 18 | Verifica que todos los tests pasan | --allow-empty |

---

## Resumen de Archivos Modificados

| Archivo | Acción | Líneas cambiadas | Descripción |
|---------|--------|-----------------|-------------|
| `estilos.qss` | **Creado** | +309 (primera edición) | Hoja de estilos QSS completa con tema claro profesional |
| `estilos.qss` | **Modificado** | +82, -26 (segunda edición) | Cambio a paleta de colores pastel para botones |
| `interfaz.ui` | **Modificado** | +8, -2 | Tamaño mínimo y tamaño predeterminado de ventana |
| `main.py` | **Modificado** | +5 | Importación de Path, constante RUTA_ESTILOS, carga de estilos |
| `ui_principal.py` | **Regenerado** | +5, -2 | Código generado automáticamente desde interfaz.ui |

**Total de archivos modificados:** 4 archivos (1 creado, 3 modificados/regenerados)

---

## Archivos NO Modificados

Los siguientes archivos **no fueron tocados** durante las sesiones, respetando las restricciones del proyecto:

- `compilador/` (carpeta completa con la lógica del compilador)
- `tests/` (carpeta completa con los tests unitarios)
- `README.md`
- `MANUAL_USUARIO.md`
- `requirements.txt`
- `.gitignore`
- `editor.py` (no requirió cambios)
- `resaltador.py` (no requirió cambios)

---

## Sesión 3: Mejoras Visuales Adicionales a la Interfaz

**Fecha:** 22 de noviembre de 2026  
**Objetivo:** Realizar cambios puramente visuales en la interfaz gráfica para enriquecer el diseño sin añadir ni modificar funcionalidades.

---

### Paso 1: Etiquetas "Código:" y "Salida:" con fondo pastel y borde decorativo

**Archivo modificado:** `estilos.qss`

**Cambios realizados:** Se separaron los selectores grupales en dos individuales, uno por etiqueta, y se agregó fondo de color pastel con borde lateral decorativo.

| Propiedad | lblEditor (Código) | lblSalida (Salida) |
|-----------|---------------------|---------------------|
| Fondo | Azul pastel #C5D9F7 | Durazno pastel #FFCBA4 |
| Borde izquierdo | 4px sólido #7BAFD4 | 4px sólido #E8A070 |
| Padding | 6px 10px 4px 12px | 6px 10px 4px 12px |
| Min-height | 24px | 24px |
| Color de texto | #2c3e50 | #2c3e50 |

**Motivo:** Dar jerarquía visual a cada sección y coordinar los colores con los botones de la paleta pastel.

---

### Paso 2: Botones con efecto de sombra 3D y transición

**Archivo modificado:** `estilos.qss`

**Cambios realizados:** Todos los botones ahora simulan un efecto de elevación mediante `border-bottom` más grueso (3px en tono más oscuro) y "se hunden" al presionar reduciendo ese borde a 2px.

| Mejora | Detalle |
|--------|---------|
| Border-radius | Aumentado de 8px a 10px |
| Padding | Aumentado de 6px 16px a 8px 18px (botones secundarios) |
| Font-weight | 600 (semibold) para secundarios, bold para Ejecutar |
| Border-bottom normal | 3px en tono más oscuro del color base |
| Border-bottom pressed | 2px en tono aún más oscuro, simulando hundimiento |
| btnEjecutar font-size | Aumentado a 14px para mayor prominencia |

**Estados de cada botón:**

| Botón | Normal | Hover | Pressed (hundido) |
|-------|--------|-------|-------------------|
| Abrir | #C5D9F7 / borde #8BB0D8 | #B0C8F0 / borde #7AA0C8 | #9AB8E6 / borde #6A90B8 |
| Guardar | #A8F0C6 / borde #6EC89A | #93E6BA / borde #5DB88A | #7DDCAE / borde #4DA87A |
| Analizar | #FFCBA4 / borde #E89A6E | #FFBE8E / borde #D88A5E | #FFB078 / borde #C87A4E |
| Ejecutar | #FF8FA3 / borde #D06080 | #FF7A96 / borde #C05070 | #FF6588 / borde #B04060 |
| Limpiar | #E8F8C5 / borde #B0D888 | #D8F0B0 / borde #A0C878 | #C8E898 / borde #90B868 |

---

### Paso 3: Editor de código con borde de acento y estado focus

**Archivo modificado:** `estilos.qss`

**Cambios realizados:**

| Propiedad | Antes | Después |
|-----------|-------|---------|
| Border | 1px solid #d0d0d0 | 2px solid #d0d0d0 |
| Border-top | (sin acento) | 3px solid #C5D9F7 (azul pastel) |
| Border-radius | 6px | 8px |
| Padding | 8px | 10px |
| Font-size | (heredado) | 12px explícito |

**Nuevo estado `:focus`:** Cuando el editor recibe el foco, el borde cambia a azul más intenso (#A8C4E8) y el borde superior a #7BAFD4, indicando visualmente dónde está el cursor.

---

### Paso 4: Área de salida con borde de acento y fondo más suave

**Archivo modificado:** `estilos.qss`

**Cambios realizados:**

| Propiedad | Antes | Después |
|-----------|-------|---------|
| Background | #1e1e1e (negro puro) | #2d2d2d (gris oscuro suave) |
| Border | 1px solid #d0d0d0 | 2px solid #555555 |
| Border-top | (sin acento) | 3px solid #FFCBA4 (durazno pastel) |
| Border-radius | 6px | 8px |
| Padding | 8px | 10px |

**Motivo:** El fondo #2d2d2d es menos agresivo que #1e1e1e y los bordes coordinados con la paleta pastel unifican el diseño.

---

### Paso 5: Barra de estado mejorada

**Archivo modificado:** `estilos.qss`

**Cambios realizados:**

| Propiedad | Antes | Después |
|-----------|-------|---------|
| Border-top | 1px solid #d0d0d0 | 2px solid #e0e8f0 |
| Font-weight | (normal) | 500 (medium) |
| Padding | 2px 4px | 4px 8px |

**Nuevo selector `QStatusBar::item`:** Elimina bordes internos y agrega padding de 2px 8px a cada elemento de la barra.

---

### Paso 6: Tooltips personalizados

**Archivo modificado:** `estilos.qss`

**Nuevo selector `QToolTip`:**

| Propiedad | Valor |
|-----------|-------|
| Background | #ffffff (blanco) |
| Color | #333333 |
| Border | 2px solid #C5D9F7 (azul pastel) |
| Border-radius | 6px |
| Padding | 6px 10px |
| Font-size | 11px |

---

### Paso 7: Separadores del menú con gradiente pastel

**Archivo modificado:** `estilos.qss`

**Cambios realizados:** El separador del menú ahora es un gradiente horizontal de 2px de alto que recorre los colores pastel: azul (#C5D9F7) → durazno (#FFCBA4) → rosa (#FF8FA3).

| Propiedad | Antes | Después |
|-----------|-------|---------|
| Height | 1px | 2px |
| Background | #d0d0d0 sólido | Gradiente horizontal pastel |
| Margin | 4px 12px | 6px 12px |

---

### Paso 8: Layouts con más espaciado

**Archivo modificado:** `estilos.qss`

**Cambios realizados:**

| Layout | Propiedad | Antes | Después |
|--------|-----------|-------|---------|
| layoutBotones | spacing | 8px | 10px |
| layoutBotones | margin | 8px 8px 4px 8px | 10px 10px 6px 10px |
| verticalLayout | spacing | 6px | 8px |
| verticalLayout | margin | 8px | 10px |

---

### Paso 9: Tooltips descriptivos en los botones (interfaz.ui)

**Archivo modificado:** `interfaz.ui`

**Cambios realizados:** Se agregó la propiedad `toolTip` a cada botón con un texto descriptivo en español.

| Botón | Tooltip |
|-------|---------|
| btnAbrir | "Abrir archivo de código" |
| btnGuardar | "Guardar archivo actual" |
| btnAnalizar | "Analizar sintaxis del código" |
| btnEjecutar | "Ejecutar el programa" |
| btnLimpiar | "Limpiar el área de salida" |

**Placeholder del editor:** Cambiado de "Escribe aquí tu programa..." a "Escribe aquí tu programa en MiniLang...".

---

### Paso 10: Regeneración de ui_principal.py

**Comando ejecutado:**
```powershell
.venv\Scripts\pyuic6 -o ui_principal.py interfaz.ui
```

**Archivo regenerado:** `ui_principal.py` con los nuevos tooltips y el placeholder actualizado.

---

### Paso 11: Verificación final

**Comando ejecutado:**
```powershell
python -m unittest discover tests
```

**Resultado:** 86 tests ejecutados, todos pasaron (OK) en 0.618s.

---

## Resumen de Archivos Modificados (Sesión 3)

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `estilos.qss` | **Modificado** | Etiquetas con fondo pastel, botones 3D, editor/salida con borde de acento, barra de estado, tooltips, separadores con gradiente, layouts con más espaciado |
| `interfaz.ui` | **Modificado** | Tooltips en 5 botones, placeholder del editor actualizado |
| `ui_principal.py` | **Regenerado** | Código generado automáticamente desde interfaz.ui |

**Total de archivos modificados en esta sesión:** 3 archivos

---

## Archivos NO Modificados

Los siguientes archivos **no fueron tocados** durante esta sesión:

- `compilador/` (carpeta completa con la lógica del compilador)
- `tests/` (carpeta completa con los tests unitarios)
- `README.md`
- `MANUAL_USUARIO.md`
- `requirements.txt`
- `.gitignore`
- `editor.py`
- `resaltador.py`
- `main.py`

---

## Estado Final

- **Rama:** `interfaz-bonita`
- **Tests:** 86 tests pasando (OK)
- **Archivos pendientes de commit:** estilos.qss, interfaz.ui, ui_principal.py
- **Funcionalidad:** Sin cambios, solo mejoras visuales.

---

## Sesión 4: Etiquetas "Código:" y "Salida:" cambiadas a gris neutro

**Fecha:** 22 de noviembre de 2026  
**Objetivo:** Cambiar los separadores visuales entre el área de código y el área de salida de colores pastel a un tono gris neutro, manteniendo los botones de arriba con sus colores pastel.

---

### Paso 1: Cambio de colores de etiquetas a gris neutro

**Archivo modificado:** `estilos.qss`

**Cambios realizados:** Se reemplazaron los fondos y bordes de color pastel de ambas etiquetas por un gris neutro uniforme.

| Propiedad | lblEditor (Código) - Antes | lblEditor (Código) - Después | lblSalida (Salida) - Antes | lblSalida (Salida) - Después |
|-----------|---------------------------|-----------------------------|--------------------------|----------------------------|
| Fondo | Azul pastel #C5D9F7 | Gris #e0e0e0 | Durazno pastel #FFCBA4 | Gris #e0e0e0 |
| Borde izquierdo | 4px sólido #7BAFD4 (azul) | 4px sólido #9e9e9e (gris) | 4px sólido #E8A070 (durazno) | 4px sólido #9e9e9e (gris) |

**Motivo:** El usuario prefirió un aspecto más neutro y sobrio para los separadores de sección, manteniendo los botones de acción con colores pastel para destacar las funciones.

---

### Paso 2: Verificación final

**Comando ejecutado:**
```powershell
python -m unittest discover tests
```

**Resultado:** 86 tests ejecutados, todos pasaron (OK) en 0.540s.

---

## Resumen de Archivos Modificados (Sesión 4)

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `estilos.qss` | **Modificado** | Etiquetas lblEditor y lblSalida cambiadas de colores pastel a gris neutro (#e0e0e0 con borde #9e9e9e) |

**Total de archivos modificados en esta sesión:** 1 archivo

---

## Archivos NO Modificados

Los siguientes archivos **no fueron tocados** durante esta sesión:

- `compilador/` (carpeta completa con la lógica del compilador)
- `tests/` (carpeta completa con los tests unitarios)
- `README.md`
- `MANUAL_USUARIO.md`
- `requirements.txt`
- `.gitignore`
- `editor.py`
- `resaltador.py`
- `main.py`
- `interfaz.ui`
- `ui_principal.py`

---

## Estado Final

- **Rama:** `interfaz-bonita`
- **Tests:** 86 tests pasando (OK)
- **Archivos pendientes de commit:** estilos.qss
- **Funcionalidad:** Sin cambios, solo mejoras visuales.
