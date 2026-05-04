class PatternMatcher:
    """
    Motor de búsqueda y validación de patrones sin librería re.
    Implementa autómatas de estados finitos por segmentos.
    """

    # ── Primitivas del motor ──────────────────────────────────────────────────

    @staticmethod
    def _is_alpha(c: str) -> bool:
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z')

    @staticmethod
    def _is_digit(c: str) -> bool:
        return '0' <= c <= '9'

    @staticmethod
    def _is_alnum(c: str) -> bool:
        return PatternMatcher._is_alpha(c) or PatternMatcher._is_digit(c)

    # ── Validadores atómicos ──────────────────────────────────────────────────

    @staticmethod
    def es_correo(texto: str) -> bool:
        """Autómata: q0→q1(usuario)→q2(@)→q3(dominio)→q4(extensión)"""
        texto = texto.strip()
        estado = 0
        i = 0
        n = len(texto)
        chars_usuario = set('._+-')
        chars_dominio = set('-')
        tld_len = 0

        while i < n:
            c = texto[i]
            if estado == 0:
                if PatternMatcher._is_alnum(c):
                    estado = 1
                else:
                    return False
            elif estado == 1:
                if PatternMatcher._is_alnum(c) or c in chars_usuario:
                    pass
                elif c == '@':
                    estado = 2
                else:
                    return False
            elif estado == 2:
                if PatternMatcher._is_alnum(c):
                    estado = 3
                else:
                    return False
            elif estado == 3:
                if PatternMatcher._is_alnum(c) or c in chars_dominio:
                    pass
                elif c == '.':
                    estado = 4
                    tld_len = 0
                else:
                    return False
            elif estado == 4:
                if PatternMatcher._is_alpha(c):
                    tld_len += 1
                elif c == '.':
                    if tld_len < 2:
                        return False
                    tld_len = 0
                else:
                    return False
            i += 1

        return estado == 4 and tld_len >= 2

    @staticmethod
    def es_telefono_co(texto: str) -> bool:
        """
        Formatos: 3001234567 | +573001234567 | 6011234567
        Móvil: 10 dígitos empezando en 3.  Fijo: 10 dígitos empezando en 6.
        """
        t = texto.strip().replace(' ', '').replace('-', '')
        if t.startswith('+57'):
            t = t[3:]
        elif t.startswith('57') and len(t) == 12:
            t = t[2:]

        digitos = 0
        for c in t:
            if not PatternMatcher._is_digit(c):
                return False
            digitos += 1

        if digitos == 10 and t[0] == '3':
            return True
        if digitos == 10 and t[0] == '6':
            return True
        return False

    @staticmethod
    def es_cedula(texto: str) -> bool:
        """
        Cédula colombiana: 6–10 dígitos, sin ceros a la izquierda.
        Nota: números de 10 dígitos que empiezan en 3 o 6 son ambiguos
        con teléfonos; la resolución se hace en find_all() por contexto.
        """
        t = texto.strip().replace('.', '').replace(' ', '')
        if not (6 <= len(t) <= 10):
            return False
        if t[0] == '0':
            return False
        return all(PatternMatcher._is_digit(c) for c in t)

    @staticmethod
    def _cedula_es_ambigua(texto: str) -> bool:
        """True si el token es válido como teléfono Y como cédula a la vez."""
        t = texto.strip().replace('.', '').replace(' ', '')
        return (len(t) == 10 and t[0] in ('3', '6') and
                all(PatternMatcher._is_digit(c) for c in t))

    @staticmethod
    def es_fecha(texto: str) -> bool:
        """Formato DD/MM/AAAA o DD-MM-AAAA con validación de rangos."""
        t = texto.strip()
        sep = None
        if '/' in t:
            sep = '/'
        elif '-' in t:
            sep = '-'
        else:
            return False

        partes = t.split(sep)
        if len(partes) != 3:
            return False

        d_str, m_str, a_str = partes
        if not (len(d_str) == 2 and len(m_str) == 2 and len(a_str) == 4):
            return False
        if not all(PatternMatcher._is_digit(c) for c in d_str + m_str + a_str):
            return False

        d, m, a = int(d_str), int(m_str), int(a_str)
        if not (1 <= m <= 12):
            return False
        dias_por_mes = [0,31,29,31,30,31,30,31,31,30,31,30,31]
        if not (1 <= d <= dias_por_mes[m]):
            return False
        if not (1900 <= a <= 2100):
            return False
        return True

    @staticmethod
    def es_url(texto: str) -> bool:
        """Valida URLs: http(s)://dominio.ext[/ruta]"""
        t = texto.strip()
        i = 0
        n = len(t)

        for p in ('https://', 'http://'):
            if t.startswith(p):
                i = len(p)
                break
        else:
            return False

        start = i
        while i < n and (PatternMatcher._is_alnum(t[i]) or t[i] in '-_.'):
            i += 1
        if i == start:
            return False
        if i >= n or '.' not in t[start:i]:
            return False
        return True

    @staticmethod
    def es_placa_co(texto: str) -> bool:
        """
        Placas colombianas:
          Vehículo: 3 letras + 3 dígitos (ABC123)
          Moto:     3 letras + 2 dígitos (ABC12)
        """
        t = texto.strip().upper().replace('-', '').replace(' ', '')
        if len(t) not in (5, 6):
            return False
        letras = t[:3]
        numeros = t[3:]
        return (all(PatternMatcher._is_alpha(c) for c in letras) and
                all(PatternMatcher._is_digit(c) for c in numeros))

    # ── Motor de búsqueda con desambiguación telefono/cédula ─────────────────

    # Palabras que indican que el token siguiente es un teléfono
    _CTX_TELEFONO = frozenset({
        'cel:', 'celular:', 'movil:', 'móvil:', 'tel:', 'telefono:',
        'teléfono:', 'fono:', 'cell:', 'mobile:', 'contacto:', 'cel',
        'celular', 'teléfono', 'telefono',
    })

    # Palabras que indican que el token siguiente es una cédula
    _CTX_CEDULA = frozenset({
        'cc:', 'c.c.:', 'cedula:', 'cédula:', 'documento:', 'dni:',
        'id:', 'identificacion:', 'identificación:', 'c.c', 'cc',
        'cedula', 'cédula', 'documento',
    })

    def find_all(self, texto: str) -> dict:
        """
        Recorre el texto token por token y retorna todas las coincidencias.
        Desambigua números de 10 dígitos que inician en 3/6 usando el
        contexto (token anterior): si hay indicador de cédula → cédula,
        si hay indicador de teléfono o ninguno → teléfono.
        """
        resultados = {
            'correos': [], 'telefonos': [], 'cedulas': [],
            'fechas': [], 'urls': [], 'placas': [],
        }

        tokens = texto.split()

        for idx, token in enumerate(tokens):
            t = token.rstrip('.,;:!?)"\'')
            t_prev = tokens[idx - 1].lower().rstrip('.,;:!?)"\'') if idx > 0 else ''

            ctx_tel = t_prev in self._CTX_TELEFONO
            ctx_ced = t_prev in self._CTX_CEDULA

            es_tel = self.es_telefono_co(t)
            es_ced = self.es_cedula(t)
            ambiguo = self._cedula_es_ambigua(t)

            if ambiguo:
                if ctx_ced:
                    resultados['cedulas'].append(t)
                else:
                    resultados['telefonos'].append(t)
            else:
                if es_tel:
                    resultados['telefonos'].append(t)
                if es_ced:
                    resultados['cedulas'].append(t)

            if self.es_correo(t):
                resultados['correos'].append(t)
            if self.es_fecha(t):
                resultados['fechas'].append(t)
            if self.es_url(t):
                resultados['urls'].append(t)
            if self.es_placa_co(t):
                resultados['placas'].append(t)

        from logic.analyzers.date_analyzer import DateAnalyzer
        _da = DateAnalyzer()
        resultados['fechas'].extend(_da.buscar_fechas_textuales(texto))

        for k in resultados:
            seen = set()
            resultados[k] = [x for x in resultados[k]
                             if not (x in seen or seen.add(x))]
        return resultados

    def search(self, texto: str, tipo: str) -> list:
        return self.find_all(texto).get(tipo, [])
