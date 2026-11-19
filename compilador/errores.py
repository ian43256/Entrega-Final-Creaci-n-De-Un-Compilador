from dataclasses import dataclass


class LenguajeError(Exception):
    """Error del lenguaje (léxico, sintáctico o de ejecución) con número de línea."""
    def __init__(self, mensaje, linea=None):
        self.mensaje = mensaje
        self.linea = linea
        super().__init__(f"Línea {linea}: {mensaje}" if linea else mensaje)


class ErrorLexico(LenguajeError):
    """Error del análisis léxico: carácter no reconocido o cadena sin cerrar."""


@dataclass(frozen=True)
class ErrorSintactico:
    linea: int
    mensaje: str


class ErroresSintacticos(Exception):
    """Conjunto de errores de sintaxis acumulados durante un mismo análisis."""
    def __init__(self, errores):
        self.errores = tuple(errores)
        super().__init__("\n".join(
            f"Línea {error.linea}: {error.mensaje}" for error in self.errores
        ))
