"""Resaltado de sintaxis de Proyecto Final:  Creación de un Compilador para el editor de código."""
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat

from compilador.lexer import reservadas


def _formato(color, negrita=False, cursiva=False):
    formato = QTextCharFormat()
    formato.setForeground(QColor(color))
    if negrita:
        formato.setFontWeight(QFont.Weight.Bold)
    if cursiva:
        formato.setFontItalic(True)
    return formato


# Colores de tono medio: se leen bien tanto sobre fondo claro como oscuro.
FORMATOS = {
    "reservada": _formato("#1f6feb", negrita=True),
    "numero": _formato("#d9730d"),
    "cadena": _formato("#2a9d4b"),
    "comentario": _formato("#8a8f98", cursiva=True),
}

# Una sola expresión con alternativas: se recorre cada línea de izquierda a derecha
# y la primera coincidencia gana, así un '#' dentro de una cadena no es comentario
# ni una palabra reservada dentro de un comentario se pinta como tal.
_PATRON = QRegularExpression(
    r'(?<comentario>#[^\n]*)'
    r'|(?<cadena>"[^"\n]*"?)'        # también pinta la cadena sin cerrar hasta fin de línea
    r'|(?<numero>\b\d+(?:\.\d+)?)'
    r'|(?<reservada>\b(?:' + "|".join(reservadas) + r')\b)',
    QRegularExpression.PatternOption.UseUnicodePropertiesOption,
)


class ResaltadorSintaxis(QSyntaxHighlighter):
    """Colorea palabras reservadas, números, cadenas y comentarios (# ...)."""

    def highlightBlock(self, texto):
        coincidencias = _PATRON.globalMatch(texto)
        while coincidencias.hasNext():
            coincidencia = coincidencias.next()
            for grupo, formato in FORMATOS.items():
                if coincidencia.hasCaptured(grupo):
                    self.setFormat(
                        coincidencia.capturedStart(grupo),
                        coincidencia.capturedLength(grupo),
                        formato,
                    )
                    break
