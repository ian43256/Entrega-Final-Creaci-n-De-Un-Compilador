"""Editor de código con numeración de líneas y marcado de líneas con error.

En interfaz.ui, txtEditor es un QPlainTextEdit "promovido" a esta clase.
"""
from PyQt6.QtCore import QEvent, QRect, QSize, Qt
from PyQt6.QtGui import QColor, QPainter, QPalette, QTextCursor, QTextFormat
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

# Rojo claro con transparencia: se ve como un fondo rosado sobre tema claro
# y como un fondo rojizo (sin tapar el texto) sobre tema oscuro.
COLOR_LINEA_CON_ERROR = QColor(255, 80, 80, 70)


class AreaNumeros(QWidget):
    """Franja a la izquierda del editor donde se dibujan los números de línea."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.anchoAreaNumeros(), 0)

    def paintEvent(self, evento):
        self.editor.pintarNumeros(evento)


class EditorCodigo(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._area = AreaNumeros(self)
        self.blockCountChanged.connect(self._actualizarMargen)
        self.updateRequest.connect(self._actualizarArea)   # al escribir y al hacer scroll
        self._actualizarMargen()

    # ---------- numeración de líneas ----------

    def anchoAreaNumeros(self):
        digitos = max(2, len(str(self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance("9") * digitos

    def _actualizarMargen(self, *_):
        self.setViewportMargins(self.anchoAreaNumeros(), 0, 0, 0)

    def _actualizarArea(self, rect, dy):
        if dy:
            self._area.scroll(0, dy)
        else:
            self._area.update(0, rect.y(), self._area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._actualizarMargen()

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        contenido = self.contentsRect()
        self._area.setGeometry(
            QRect(contenido.left(), contenido.top(), self.anchoAreaNumeros(), contenido.height())
        )

    def changeEvent(self, evento):
        super().changeEvent(evento)
        if evento.type() == QEvent.Type.FontChange and hasattr(self, "_area"):
            self._actualizarMargen()
            self._area.update()

    def pintarNumeros(self, evento):
        paleta = self.palette()
        pintor = QPainter(self._area)
        pintor.fillRect(evento.rect(), paleta.color(QPalette.ColorRole.Window))
        pintor.setPen(paleta.color(QPalette.ColorRole.Mid))
        pintor.drawLine(self._area.width() - 1, evento.rect().top(),
                        self._area.width() - 1, evento.rect().bottom())
        pintor.setFont(self.font())
        pintor.setPen(paleta.color(QPalette.ColorRole.PlaceholderText))

        bloque = self.firstVisibleBlock()
        numero = bloque.blockNumber()
        arriba = round(self.blockBoundingGeometry(bloque).translated(self.contentOffset()).top())
        abajo = arriba + round(self.blockBoundingRect(bloque).height())
        while bloque.isValid() and arriba <= evento.rect().bottom():
            if bloque.isVisible() and abajo >= evento.rect().top():
                pintor.drawText(
                    0, arriba, self._area.width() - 6, self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, str(numero + 1),
                )
            bloque = bloque.next()
            arriba = abajo
            abajo = arriba + round(self.blockBoundingRect(bloque).height())
            numero += 1

    # ---------- líneas con error ----------

    def marcarLineasError(self, lineas):
        """Resalta con fondo rojo claro las líneas indicadas (numeradas desde 1)."""
        selecciones = []
        for linea in sorted(set(lineas)):
            if not linea:
                continue
            bloque = self.document().findBlockByLineNumber(linea - 1)
            if not bloque.isValid():
                continue
            seleccion = QTextEdit.ExtraSelection()
            seleccion.format.setBackground(COLOR_LINEA_CON_ERROR)
            seleccion.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            seleccion.cursor = QTextCursor(bloque)
            selecciones.append(seleccion)
        self.setExtraSelections(selecciones)

    def limpiarMarcasError(self):
        self.setExtraSelections([])
