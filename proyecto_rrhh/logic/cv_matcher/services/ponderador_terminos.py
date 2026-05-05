from . import tablas as tb

class PonderadorTerminos:
    """
    Asigna un peso de importancia a cada término según su categoría léxica.

    Categorías y criterio de clasificación
    ───────────────────────────────────────
    Verbo infinitivo (peso _PESO_TERM_VERBO = 0.5)
        Unigram que termina en 'ar', 'er' o 'ir', con longitud ≥ _MIN_LEN_VERBO
        y que NO está en _EXCEPCIONES_VERBO.
        Ejemplos: gestionar, desarrollar, implementar, analizar, coordinar,
                  establecer, producir, dirigir.
        Estos términos indican capacidad de acción pero no certifican el dominio
        de una herramienta concreta, por lo que su ausencia pesa menos.

    Bigram / término compuesto (peso _PESO_TERM_BIGRAM = 0.5)
        Cualquier término que contiene un espacio ('machine learning', 'power bi').
        Son bonus: si el CV los cita textualmente suma bastante, pero su ausencia
        no arrastra el score tanto como la de un sustantivo clave porque sus
        componentes (unigrams) ya están evaluados individualmente.

    Sustantivo / herramienta / skill (peso _PESO_TERM_NORMAL = 1.0)
        Todo lo que no sea verbo ni bigram: siglas (SQL, API), nombres de
        tecnologías (python, excel), sustantivos de habilidad (liderazgo,
        gestion, analisis, experiencia), etc.

    Nota: los tokens se reciben ya normalizados (minúsculas, sin diacríticos)
    dado que el ponderador opera después de la etapa de normalización.
    """

    # Sufijos de infinitivos españoles en las tres conjugaciones
    _SUFIJOS = ('ar', 'er', 'ir')

    @classmethod
    def peso(cls, termino: str) -> float:
        """
        Retorna el peso de importancia del término.

        Parámetros
        ----------
        termino : str — término normalizado (sin diacríticos, en minúsculas).

        Retorno
        -------
        float — _PESO_TERM_VERBO | _PESO_TERM_BIGRAM | _PESO_TERM_NORMAL
        """
        # Bigrams (contienen espacio): bonus con peso reducido
        if ' ' in termino:
            return tb.PESO_TERM_BIGRAM

        # Verbos en infinitivo: terminación -ar/-er/-ir con longitud mínima
        # y no en la lista de excepciones (adjetivos/sustantivos técnicos).
        if (len(termino) >= tb.MIN_LEN_VERBO
                and termino not in tb.EXCEPCIONES_VERBO
                and termino.endswith(cls._SUFIJOS)):
            return tb.PESO_TERM_VERBO

        # Sustantivos, siglas, herramientas, skills: peso completo
        return tb.PESO_TERM_NORMAL
