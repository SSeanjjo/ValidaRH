"""
date_analyzer.py — Análisis de fechas en lenguaje natural español.
"""


class DateAnalyzer:
    """
    Detecta y normaliza fechas escritas en español.
    Modos: es_fecha_textual | buscar_fechas_textuales | normalizar | describir
    """

    MESES = {
        'enero': 1,   'febrero': 2,  'marzo': 3,    'abril': 4,
        'mayo': 5,    'junio': 6,    'julio': 7,    'agosto': 8,
        'septiembre': 9, 'setiembre': 9, 'octubre': 10,
        'noviembre': 11, 'diciembre': 12,
        'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'ago': 8,
        'sep': 9, 'set': 9, 'oct': 10, 'nov': 11, 'dic': 12,
    }

    MESES_NOMBRE = {
        1: 'enero',    2: 'febrero',  3: 'marzo',    4: 'abril',
        5: 'mayo',     6: 'junio',    7: 'julio',     8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre',
    }

    _ARTICULOS  = frozenset({'el', 'del'})
    _CONECTORES = frozenset({'de', 'del'})

    @staticmethod
    def _limpiar(token: str) -> str:
        t = token.lower().strip()
        puntuacion = set('.,;:!?()"\'-_/')
        while t and t[0] in puntuacion:
            t = t[1:]
        while t and t[-1] in puntuacion:
            t = t[:-1]
        return t

    @staticmethod
    def _dias_en_mes(mes: int, anio: int) -> int:
        if mes in (1, 3, 5, 7, 8, 10, 12):
            return 31
        if mes in (4, 6, 9, 11):
            return 30
        if mes == 2:
            bisiesto = (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)
            return 29 if bisiesto else 28
        return 0

    def _parsear(self, tokens_norm: list, inicio: int) -> dict:
        n   = len(tokens_norm)
        i   = inicio
        dia  = None
        mes  = None
        anio = None

        if i < n and tokens_norm[i] in self._ARTICULOS:
            i += 1

        if i < n and tokens_norm[i].isdigit():
            d = int(tokens_norm[i])
            if 1 <= d <= 31:
                dia = d
                i += 1
                if i < n and tokens_norm[i] in self._CONECTORES:
                    i += 1

        if i >= n:
            return {'mes': None, 'longitud': 0}

        tok = tokens_norm[i]
        if tok not in self.MESES:
            return {'mes': None, 'longitud': 0}

        mes = self.MESES[tok]
        i += 1

        if i < n and tokens_norm[i] in self._CONECTORES:
            i += 1
            if i < n and tokens_norm[i].isdigit() and len(tokens_norm[i]) == 4:
                a = int(tokens_norm[i])
                if 1900 <= a <= 2100:
                    anio = a
                    i += 1
        elif i < n and tokens_norm[i].isdigit() and len(tokens_norm[i]) == 4:
            a = int(tokens_norm[i])
            if 1900 <= a <= 2100:
                anio = a
                i += 1

        if dia is not None and mes is not None:
            max_dias = self._dias_en_mes(mes, anio if anio else 2000)
            if not (1 <= dia <= max_dias):
                return {'mes': None, 'longitud': 0}

        return {'dia': dia, 'mes': mes, 'anio': anio, 'longitud': i - inicio}

    def es_fecha_textual(self, texto: str) -> bool:
        tokens = [self._limpiar(t) for t in texto.split() if t]
        tokens = [t for t in tokens if t]
        if not tokens:
            return False
        r = self._parsear(tokens, 0)
        return r['mes'] is not None and r['longitud'] == len(tokens)

    def normalizar(self, texto: str) -> str:
        tokens = [self._limpiar(t) for t in texto.split() if t]
        tokens = [t for t in tokens if t]
        r = self._parsear(tokens, 0)
        if r['mes'] is None or r['longitud'] != len(tokens):
            return ''
        dia, mes, anio = r['dia'], r['mes'], r['anio']
        if dia is not None and anio is not None:
            return f"{dia:02d}/{mes:02d}/{anio}"
        if anio is not None:
            return f"{mes:02d}/{anio}"
        if dia is not None:
            return f"{dia:02d}/{mes:02d}"
        return self.MESES_NOMBRE.get(mes, '')

    def buscar_fechas_textuales(self, texto: str) -> list:
        if not texto or not texto.strip():
            return []
        palabras_orig = texto.split()
        palabras_norm = [self._limpiar(t) for t in palabras_orig]
        n = len(palabras_orig)
        hallazgos = []
        vistos    = set()
        i = 0
        while i < n:
            r = self._parsear(palabras_norm, i)
            if (r['mes'] is not None and r['longitud'] >= 2 and
                    (r['dia'] is not None or r['anio'] is not None)):
                long = r['longitud']
                fecha_orig = ' '.join(palabras_orig[i:i+long])
                fecha_orig = fecha_orig.rstrip('.,;:!?)"\'')
                llave = fecha_orig.lower()
                if llave not in vistos:
                    hallazgos.append(fecha_orig)
                    vistos.add(llave)
                i += long
            else:
                i += 1
        return hallazgos

    def describir(self, texto: str) -> dict:
        tokens = [self._limpiar(t) for t in texto.split() if t]
        tokens = [t for t in tokens if t]
        r = self._parsear(tokens, 0)
        if r['mes'] is None or r['longitud'] != len(tokens):
            return {'dia': None, 'mes_num': None, 'mes_nombre': '',
                    'anio': None, 'normalizada': ''}
        return {
            'dia':         r['dia'],
            'mes_num':     r['mes'],
            'mes_nombre':  self.MESES_NOMBRE.get(r['mes'], ''),
            'anio':        r['anio'],
            'normalizada': self.normalizar(texto),
        }
