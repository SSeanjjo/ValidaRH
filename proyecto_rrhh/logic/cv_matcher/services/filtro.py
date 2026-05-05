from . import tablas as tb

class Filtro:
    """
    Descarta:
      - Tokens de longitud < MIN_LEN (ruido tipográfico).
      - Tokens puramente numéricos (años, versiones, etc. no aportan semántica).
      - Stopwords en forma normalizada (compara contra _STOPWORDS).
    Espera tokens ya normalizados (sin tildes, en minúsculas).
    """

    _MIN_LEN = 3

    @classmethod
    def filtrar(cls, tokens: list) -> list:
        resultado = []
        for tok in tokens:
            if len(tok) < cls._MIN_LEN:
                continue
            if tok.isdigit():
                continue
            if tok.translate(tb.TABLA_NORM).lower() in tb.STOPWORDS:
                continue
            resultado.append(tok)
        return resultado