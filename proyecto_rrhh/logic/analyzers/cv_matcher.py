"""
cv_matcher.py — Motor ATS simplificado para compatibilidad CV ↔ Perfil.
Sin uso de la librería 're'.
"""


class CVMatcher:
    """
    Analiza la compatibilidad entre un CV y un perfil de vacante.
    Búsqueda con límite de palabra implementada manualmente.
    """

    STOPWORDS_ES = frozenset({
        'de', 'la', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las',
        'un', 'por', 'con', 'una', 'para', 'al', 'su', 'que', 'es',
        'o', 'e', 'lo', 'como', 'pero', 'si', 'sin', 'sobre', 'le',
        'me', 'ya', 'nos', 'yo', 'mi', 'tu', 'te', 'les', 'sus',
        'ha', 'he', 'han', 'hay', 'fue', 'ser', 'son', 'era',
        'este', 'esta', 'esto', 'estos', 'estas', 'ese', 'esa', 'eso',
        'no', 'ni', 'mas', 'muy', 'bien', 'mal', 'o', 'u',
        'cada', 'todo', 'todos', 'toda', 'todas', 'otro', 'otra',
        'mucho', 'poco', 'cuando', 'donde', 'quien', 'cual',
        'haber', 'estar', 'tener', 'hacer', 'poder', 'deber', 'ir',
        'dentro', 'fuera', 'antes', 'después', 'durante', 'entre',
        'hacia', 'hasta', 'desde', 'bajo', 'contra',
        'the', 'and', 'or', 'in', 'of', 'to', 'for', 'with', 'at', 'by',
        'conocimiento', 'conocimientos', 'experiencia', 'manejo',
        'habilidad', 'habilidades', 'capacidad', 'uso', 'nivel',
        'minimo', 'mínimo', 'minima', 'mínima', 'basico', 'básico',
        'avanzado', 'intermedio', 'deseable', 'requerido', 'requerida',
        'años', 'año', 'meses', 'mes', 'tiempo',
    })

    @staticmethod
    def _es_alnum(c: str) -> bool:
        return ('a' <= c.lower() <= 'z') or ('0' <= c <= '9')

    @staticmethod
    def _es_parte_termino(c: str) -> bool:
        return CVMatcher._es_alnum(c) or c in '+-#._'

    def _tokenizar(self, texto: str) -> list:
        tokens = []
        tok = ''
        for c in texto:
            if self._es_parte_termino(c):
                tok += c
            else:
                if tok:
                    tokens.append(tok)
                    tok = ''
        if tok:
            tokens.append(tok)
        return tokens

    def _extraer_keywords(self, linea: str) -> list:
        tokens = self._tokenizar(linea)
        resultado = []
        for t in tokens:
            tl = t.lower()
            if len(t) < 2:
                continue
            if all('0' <= c <= '9' for c in t):
                continue
            if tl not in self.STOPWORDS_ES:
                resultado.append(tl)
        return resultado

    def extraer_keywords_perfil(self, perfil_texto: str) -> list:
        """Extrae lista única de keywords de todo el texto del perfil."""
        lineas = [l.strip() for l in perfil_texto.splitlines() if l.strip()]
        todas = []
        vistos = set()
        for linea in lineas:
            for kw in self._extraer_keywords(linea):
                if kw not in vistos:
                    todas.append(kw)
                    vistos.add(kw)
        return todas

    def _buscar_en_cv(self, keyword: str, cv_lower: str, cv_orig: str) -> tuple:
        kw = keyword
        lk = len(kw)
        n  = len(cv_lower)
        i  = 0
        while i <= n - lk:
            pos = cv_lower.find(kw, i)
            if pos == -1:
                return False, ''
            antes_ok   = (pos == 0) or (not self._es_parte_termino(cv_lower[pos - 1]))
            despues_ok = (pos + lk >= n) or (not self._es_parte_termino(cv_lower[pos + lk]))
            if antes_ok and despues_ok:
                inicio = cv_orig.rfind('\n', 0, pos) + 1
                fin    = cv_orig.find('\n', pos)
                if fin == -1:
                    fin = len(cv_orig)
                contexto = cv_orig[inicio:fin].strip()[:80]
                return True, contexto
            i = pos + 1
        return False, ''

    def analizar(self, cv_texto: str, perfil_texto: str) -> dict:
        cv_lower = cv_texto.lower()
        lineas   = [l.strip() for l in perfil_texto.splitlines() if l.strip()]
        requisitos = []

        for linea in lineas:
            keywords = self._extraer_keywords(linea)
            if not keywords:
                continue
            encontrados    = []
            no_encontrados = []
            contextos      = {}
            for kw in keywords:
                hallado, ctx = self._buscar_en_cv(kw, cv_lower, cv_texto)
                if hallado:
                    encontrados.append(kw)
                    if ctx and kw not in contextos:
                        contextos[kw] = ctx
                else:
                    no_encontrados.append(kw)

            total_kw = len(keywords)
            n_enc    = len(encontrados)
            if n_enc == total_kw:
                estado = 'encontrado'
                score  = 100
            elif n_enc > 0:
                estado = 'parcial'
                score  = round((n_enc / total_kw) * 100)
            else:
                estado = 'no_encontrado'
                score  = 0

            ctx_display = ''
            for kw in encontrados:
                if kw in contextos:
                    ctx_display = contextos[kw]
                    break

            requisitos.append({
                'texto'         : linea,
                'keywords'      : keywords,
                'encontrados'   : encontrados,
                'no_encontrados': no_encontrados,
                'estado'        : estado,
                'score'         : score,
                'contexto'      : ctx_display,
            })

        total = len(requisitos)
        enc   = sum(1 for r in requisitos if r['estado'] == 'encontrado')
        par   = sum(1 for r in requisitos if r['estado'] == 'parcial')
        no    = sum(1 for r in requisitos if r['estado'] == 'no_encontrado')
        score_global = round(sum(r['score'] for r in requisitos) / total) if total > 0 else 0

        return {
            'requisitos'    : requisitos,
            'score_global'  : score_global,
            'encontrados'   : enc,
            'parciales'     : par,
            'no_encontrados': no,
            'total'         : total,
        }
