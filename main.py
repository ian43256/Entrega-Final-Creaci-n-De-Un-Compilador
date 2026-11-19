import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtGui import QTextCursor

from ui_principal import Ui_MainWindow      # generado con: pyuic6 -o ui_principal.py interfaz.ui
from resaltador import ResaltadorSintaxis
from compilador import (
    ejecutar, analizar_codigo,
    ErrorLexico, ErroresSintacticos, ErroresSemanticos, LenguajeError,
)

MENSAJE_VALIDO = "✔ Código válido"

RUTA_ESTILOS = Path(__file__).with_name("estilos.qss")


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.archivo_actual = None
        self.resaltador = ResaltadorSintaxis(self.txtEditor.document())
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        # Botones
        self.btnEjecutar.clicked.connect(self.ejecutarCodigo)
        self.btnAnalizar.clicked.connect(self.analizarCodigo)
        self.btnAbrir.clicked.connect(self.abrirArchivo)
        self.btnGuardar.clicked.connect(self.guardarArchivo)
        self.btnLimpiar.clicked.connect(self.limpiarSalida)
        # Menú: cada acción usa el mismo método que su botón
        self.actionAbrir.triggered.connect(self.abrirArchivo)
        self.actionGuardar.triggered.connect(self.guardarArchivo)
        self.actionSalir.triggered.connect(self.close)
        self.actionAnalizar.triggered.connect(self.analizarCodigo)
        self.actionEjecutar.triggered.connect(self.ejecutarCodigo)

    def escribirSalida(self, texto):
        self.txtSalida.appendPlainText(texto)

    def limpiarSalida(self):
        self.txtSalida.clear()
        self.txtEditor.limpiarMarcasError()

    def analizarCodigo(self):
        """Solo análisis (léxico, sintáctico y semántico): no ejecuta el programa."""
        self._procesar(ejecutar_programa=False)

    def ejecutarCodigo(self):
        self._procesar(ejecutar_programa=True)

    def _procesar(self, ejecutar_programa):
        self.limpiarSalida()
        codigo = self.txtEditor.toPlainText()
        try:
            if ejecutar_programa:
                ejecutar(codigo, self.escribirSalida)
            else:
                analizar_codigo(codigo)
        except ErrorLexico as e:
            self.mostrarErrores("[ERROR LÉXICO]", [e])
        except ErroresSintacticos as e:
            self.mostrarErrores("[ERROR SINTÁCTICO]", e.errores)
        except ErroresSemanticos as e:
            self.mostrarErrores("[ERROR SEMÁNTICO]", e.errores)
        except LenguajeError as e:
            self.mostrarErrores("[ERROR]", [e])        # error de ejecución
        else:
            self.escribirSalida(MENSAJE_VALIDO)
            self.statusbar.showMessage(
                "Ejecución terminada" if ejecutar_programa else "Análisis terminado", 3000
            )

    def mostrarErrores(self, prefijo, errores):
        """Escribe cada error en la salida, marca sus líneas en el editor y salta a la primera."""
        for error in errores:
            ubicacion = f"Línea {error.linea}: " if error.linea else ""
            self.escribirSalida(f"{prefijo} {ubicacion}{error.mensaje}")
        lineas = [error.linea for error in errores if error.linea]
        self.txtEditor.marcarLineasError(lineas)
        if lineas:
            self.irALinea(lineas[0])
        self.statusbar.showMessage(f"Se encontraron {len(errores)} error(es)", 3000)

    def irALinea(self, linea):
        if not linea:
            return
        bloque = self.txtEditor.document().findBlockByLineNumber(linea - 1)
        cursor = QTextCursor(bloque)
        self.txtEditor.setTextCursor(cursor)
        self.txtEditor.setFocus()

    def abrirArchivo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Abrir", "", "Archivos de código (*.mini *.txt);;Todos (*)")
        if ruta:
            with open(ruta, encoding="utf-8") as f:
                self.txtEditor.setPlainText(f.read())
            self.txtEditor.limpiarMarcasError()     # las marcas eran del texto anterior
            self.archivo_actual = ruta

    def guardarArchivo(self):
        if not self.archivo_actual:
            ruta, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "Programas (*.mini)")
            if not ruta:
                return
            self.archivo_actual = ruta
        with open(self.archivo_actual, "w", encoding="utf-8") as f:
            f.write(self.txtEditor.toPlainText())
        self.statusbar.showMessage("Archivo guardado", 3000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(RUTA_ESTILOS.read_text(encoding="utf-8"))
    win = Window()
    win.show()
    sys.exit(app.exec())
