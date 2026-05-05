from . import tablas as tb

class Tokenizador:
    """
    Segmenta texto en tokens usando str.isalnum() para soporte Unicode completo.
    Los caracteres en _CHARS_EXTRA ('+', '#') se permiten dentro de un token
    para capturar términos como 'c++' o 'c#' sin partirlos.
    Los puntos de sufijo se eliminan (p.ej. un número de versión '3.0.' → '3.0').
    """

    @staticmethod
    def tokenizar(texto: str) -> list:
        tokens = []
        buf = []
        for c in texto:
            if c.isalnum() or c in tb.CHARS_EXTRA:
                buf.append(c)
            else:
                if buf:
                    tok = ''.join(buf).strip('.')
                    if tok:
                        tokens.append(tok)
                    buf = []
        if buf:
            tok = ''.join(buf).strip('.')
            if tok:
                tokens.append(tok)
        return tokens
