
class ConstructorNgrams:
    """
    Genera la lista de términos de búsqueda combinando:
      - Unigrams: cada token individual.
      - Bigrams (si bigrams=True): pares consecutivos separados por espacio,
        para capturar términos compuestos como 'power bi', 'machine learning',
        'google ads', 'ciencia datos', etc.
    El resultado preserva el orden de aparición.
    """

    @staticmethod
    def construir(tokens: list, bigrams: bool = True) -> list:
        terminos = list(tokens)
        if bigrams and len(tokens) >= 2:
            for i in range(len(tokens) - 1):
                terminos.append(tokens[i] + ' ' + tokens[i + 1])
        return terminos