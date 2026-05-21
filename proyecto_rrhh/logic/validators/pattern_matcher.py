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
        DFA: q0 → prefijo(+57|57)? → q4 → (3|6) → q5..q14(aceptación)
        Estados:
          0: inicio
          1: leyó '+', espera '5'
          2: leyó '+5', espera '7'
          3: leyó '5' inicial (posible prefijo 57), espera '7'
          4: prefijo completo, espera '3' o '6'
          5: primer dígito válido leído, faltan 9
          6-13: dígitos 2-9
          14: décimo dígito — ACEPTACIÓN
        """
        t = texto.strip().replace(' ', '').replace('-', '')
        estado = 0

        for c in t:
            if estado == 0:
                if c == '+':
                    estado = 1
                elif c == '5':
                    estado = 3
                elif c in ('3', '6'):
                    estado = 5
                else:
                    return False
            elif estado == 1:
                if c == '5':
                    estado = 2
                else:
                    return False
            elif estado == 2:
                if c == '7':
                    estado = 4
                else:
                    return False
            elif estado == 3:
                if c == '7':
                    estado = 4
                else:
                    return False
            elif estado == 4:
                if c in ('3', '6'):
                    estado = 5
                else:
                    return False
            elif 5 <= estado <= 13:
                if PatternMatcher._is_digit(c):
                    estado += 1
                else:
                    return False
            else:
                return False

        return estado == 14

    @staticmethod
    def es_cedula(texto: str) -> bool:
        """
        DFA: q0 → (1-9) → q1 → dígito → q2 → ... → qn  (aceptación: 6 ≤ n ≤ 10)
        Estados 1-10 representan la cantidad de dígitos leídos.
        Cédula colombiana: 6–10 dígitos, sin ceros a la izquierda.
        """
        t = texto.strip().replace('.', '').replace(' ', '')
        estado = 0

        for c in t:
            if estado == 0:
                if PatternMatcher._is_digit(c) and c != '0':
                    estado = 1
                else:
                    return False
            elif 1 <= estado <= 9:
                if PatternMatcher._is_digit(c):
                    estado += 1
                else:
                    return False
            else:
                return False  # más de 10 dígitos

        return 6 <= estado <= 10

    @staticmethod
    def _cedula_es_ambigua(texto: str) -> bool:
        """True si el token es válido como teléfono Y como cédula a la vez."""
        t = texto.strip().replace('.', '').replace(' ', '')
        return (len(t) == 10 and t[0] in ('3', '6') and
                all(PatternMatcher._is_digit(c) for c in t))

    @staticmethod
    def es_fecha(texto: str) -> bool:
        """
        DFA: q0→q1(d1)→q2(d2)→q3(sep)→q4(m1)→q5(m2)→q6(sep)→q7(a1)→q8(a2)→q9(a3)→q10(a4)
        Formato DD/MM/AAAA o DD-MM-AAAA. El separador debe ser consistente.
        """
        t = texto.strip()
        estado = 0
        sep = None
        buf = ['', '', '']  # [dd, mm, aaaa]

        for c in t:
            if estado == 0:
                if PatternMatcher._is_digit(c):
                    buf[0] += c
                    estado = 1
                else:
                    return False
            elif estado == 1:
                if PatternMatcher._is_digit(c):
                    buf[0] += c
                    estado = 2
                else:
                    return False
            elif estado == 2:
                if c in ('/', '-'):
                    sep = c
                    estado = 3
                else:
                    return False
            elif estado == 3:
                if PatternMatcher._is_digit(c):
                    buf[1] += c
                    estado = 4
                else:
                    return False
            elif estado == 4:
                if PatternMatcher._is_digit(c):
                    buf[1] += c
                    estado = 5
                else:
                    return False
            elif estado == 5:
                if c == sep:
                    estado = 6
                else:
                    return False
            elif estado == 6:
                if PatternMatcher._is_digit(c):
                    buf[2] += c
                    estado = 7
                else:
                    return False
            elif estado == 7:
                if PatternMatcher._is_digit(c):
                    buf[2] += c
                    estado = 8
                else:
                    return False
            elif estado == 8:
                if PatternMatcher._is_digit(c):
                    buf[2] += c
                    estado = 9
                else:
                    return False
            elif estado == 9:
                if PatternMatcher._is_digit(c):
                    buf[2] += c
                    estado = 10
                else:
                    return False
            else:
                return False  # caracteres extra

        if estado != 10:
            return False

        d, m, a = int(buf[0]), int(buf[1]), int(buf[2])
        if not (1 <= m <= 12):
            return False
        dias_por_mes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if not (1 <= d <= dias_por_mes[m]):
            return False
        if not (1900 <= a <= 2100):
            return False
        return True

    @staticmethod
    def es_url(texto: str) -> bool:
        """
        DFA para http(s)://dominio.ext[/ruta]
        Estados:
          0-3 : leyendo 'http'
          4   : leyó 'http', espera 's' o ':'
          5   : leyó 'https', espera ':'
          6   : leyó ':', espera primer '/'
          7   : leyó primer '/', espera segundo '/'
          8   : inicio del dominio, espera alnum
          9   : interior del dominio (alnum | '-' | '_')
          10  : leyó '.', espera inicio de TLD/subdominio
          11  : dentro de TLD o ruta — ACEPTACIÓN
        """
        t = texto.strip()
        estado = 0
        _http = 'http'

        for c in t:
            if estado < 4:
                if c == _http[estado]:
                    estado += 1
                else:
                    return False
            elif estado == 4:
                if c == 's':
                    estado = 5
                elif c == ':':
                    estado = 6
                else:
                    return False
            elif estado == 5:
                if c == ':':
                    estado = 6
                else:
                    return False
            elif estado == 6:
                if c == '/':
                    estado = 7
                else:
                    return False
            elif estado == 7:
                if c == '/':
                    estado = 8
                else:
                    return False
            elif estado == 8:
                if PatternMatcher._is_alnum(c):
                    estado = 9
                else:
                    return False
            elif estado == 9:
                if PatternMatcher._is_alnum(c) or c in '-_':
                    pass
                elif c == '.':
                    estado = 10
                elif c == '/':
                    return False  # llegó '/' sin haber visto punto en el dominio
                else:
                    return False
            elif estado == 10:
                if PatternMatcher._is_alpha(c):
                    estado = 11
                else:
                    return False
            elif estado == 11:
                if PatternMatcher._is_alnum(c) or c in '-_./':
                    pass
                else:
                    return False

        return estado == 11

    @staticmethod
    def es_placa_co(texto: str) -> bool:
        """
        DFA: q0→q1(L)→q2(L)→q3(L)→q4(D)→q5(D)[moto]→q6(D)[vehículo]
        Placas colombianas:
          Vehículo: 3 letras + 3 dígitos  (ABC123) — acepta en q6
          Moto:     3 letras + 2 dígitos  (ABC12)  — acepta en q5
        """
        t = texto.strip().upper().replace('-', '').replace(' ', '')
        estado = 0

        for c in t:
            if estado == 0:
                if PatternMatcher._is_alpha(c):
                    estado = 1
                else:
                    return False
            elif estado == 1:
                if PatternMatcher._is_alpha(c):
                    estado = 2
                else:
                    return False
            elif estado == 2:
                if PatternMatcher._is_alpha(c):
                    estado = 3
                else:
                    return False
            elif estado == 3:
                if PatternMatcher._is_digit(c):
                    estado = 4
                else:
                    return False
            elif estado == 4:
                if PatternMatcher._is_digit(c):
                    estado = 5
                else:
                    return False
            elif estado == 5:
                if PatternMatcher._is_digit(c):
                    estado = 6
                else:
                    return False
            else:
                return False  # más de 6 caracteres

        return estado in (5, 6)  # 5=moto, 6=vehículo

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
