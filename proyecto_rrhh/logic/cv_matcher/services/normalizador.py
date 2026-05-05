from . import tablas as tb

class Normalizador:
    """
    Convierte texto a minúsculas eliminando diacríticos (tildes/acentos).
    La transformación es 1-a-1: len(normalizar(t)) == len(t) siempre,
    lo que permite alinear posiciones entre el texto normalizado y el original.
    """

    @staticmethod
    def normalizar(texto: str) -> str:
        return texto.translate(tb.TABLA_NORM).lower()