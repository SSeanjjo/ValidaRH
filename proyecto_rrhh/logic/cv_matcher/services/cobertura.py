from . import tablas as tb

class Cobertura:
    """
    Matching en dos niveles para un término de búsqueda contra un CV tokenizado.

    Nivel 1 — Exacto
        Busca el término como substring en el texto normalizado verificando que
        los caracteres adyacentes al match no sean alfanuméricos (límite de
        palabra).  Aplica tanto a unigrams como a bigrams.  Peso = _PESO_EXACTO.

    Nivel 2 — Cobertura léxica por LCP  (solo unigrams)
        Calcula el Prefijo Común más Largo (LCP) entre el término y cada token
        del CV.  Si algún token comparte al menos _MIN_LCP caracteres iniciales
        con el término, se considera que el CV "cubre" ese concepto, aunque use
        una forma flexionada distinta.  Ejemplos con _MIN_LCP = 5:

            Término        CV token        LCP   ¿Cubre?
            ─────────────────────────────────────────────
            automatizacion automatizar     10     sí
            gestion        gestionando      7     sí
            liderazgo      liderar          5     sí
            analisis       analizar         5     sí
            python         python           6     sí (exacto)
            sql            sequel           1     no  (LCP < 5)
            arte           arteria          4     no  (LCP < 5)

        Peso = _PESO_COBERTURA.

    Los bigrams ('machine learning') no aplican cobertura léxica: si no se
    encuentran como frase exacta, su cobertura depende de sus unigrams
    individuales (que sí la aplican), evitando así falsos positivos.
    """

    @classmethod
    def buscar(cls, cv_norm: str, cv_tokens: frozenset,
               termino: str) -> tuple:
        """
        Busca termino en cv_norm con los dos niveles de matching.

        Parámetros
        ----------
        cv_norm    : texto del CV normalizado (minúsculas, sin diacríticos).
        cv_tokens  : conjunto de tokens del CV normalizados, de longitud ≥ _MIN_LCP
                     y excluidas las stopwords (precalculado para eficiencia).
        termino    : término de búsqueda ya normalizado (unigram o bigram).

        Retorno
        -------
        (tipo: str, pos: int, peso: float)
          tipo  — 'exacto' | 'cobertura' | 'ninguno'
          pos   — posición en cv_norm del match (-1 si no encontrado)
          peso  — _PESO_EXACTO | _PESO_COBERTURA | 0.0
        """
        # Nivel 1: match exacto con límite de palabra
        hallado, pos = cls._buscar_exacto(cv_norm, termino)
        if hallado:
            return 'exacto', pos, tb.PESO_EXACTO

        # Nivel 2: cobertura léxica por LCP (solo unigrams)
        if ' ' not in termino and len(termino) >= tb.MIN_LCP:
            for cv_tok in cv_tokens:
                if cls._lcp(termino, cv_tok) >= tb.MIN_LCP:
                    # Localizar el token en el texto para extraer contexto
                    pos_tok = cv_norm.find(cv_tok)
                    return 'cobertura', pos_tok, tb.PESO_COBERTURA

        return 'ninguno', -1, 0.0

    @staticmethod
    def _lcp(a: str, b: str) -> int:
        """
        Longitud del Prefijo Común más Largo (Longest Common Prefix) entre a y b.
        Recorre ambas cadenas en paralelo hasta la primera diferencia.
        """
        n = 0
        for ca, cb in zip(a, b):
            if ca != cb:
                break
            n += 1
        return n

    @staticmethod
    def _buscar_exacto(texto: str, termino: str) -> tuple:
        """
        Búsqueda de substring con verificación de límite de palabra.
        Un límite se define por un carácter no alfanumérico (o inicio/fin de texto).
        Retorna (encontrado: bool, posicion: int).
        """
        n    = len(termino)
        pos  = 0
        largo = len(texto)
        while pos <= largo - n:
            idx = texto.find(termino, pos)
            if idx == -1:
                return False, -1
            antes_ok   = (idx == 0        or not texto[idx - 1].isalnum())
            despues_ok = (idx + n >= largo or not texto[idx + n].isalnum())
            if antes_ok and despues_ok:
                return True, idx
            pos = idx + 1
        return False, -1