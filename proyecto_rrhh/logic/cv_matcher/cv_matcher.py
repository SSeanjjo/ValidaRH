"""
cv_matcher.py — Motor ATS para compatibilidad CV ↔ Perfil laboral.
Sin uso de la librería 're'.

Pipeline de análisis léxico
────────────────────────────
  1. Normalización  — minúsculas + sustitución de diacríticos mediante tabla
                      de traducción 1-a-1; preserva la longitud del string.
  2. Limpieza       — collapsado de líneas vacías y espacios redundantes.
  3. Tokenización   — segmentación con str.isalnum() (soporte Unicode completo).
  4. Filtrado       — descarte de stopwords, tokens cortos y tokens numéricos.
  5. N-grams        — unigrams siempre; bigrams opcionales para términos compuestos.
  6. Cobertura      — matching en dos niveles para cada término del requisito:
                        a) Exacto  : coincidencia con límite de palabra  (peso 1.0).
                        b) Cobertura léxica: prefijo común mínimo (LCP ≥ MIN_LCP
                           caracteres) entre el término y algún token del CV.
                           Captura formas flexionadas del mismo lexema:
                             'automatizacion' cubre 'automatizar' (LCP=10)
                             'gestion'        cubre 'gestionando' (LCP= 7)
                             'liderazgo'      cubre 'liderar'     (LCP= 5)
                             'analisis'       cubre 'analizar'    (LCP= 5)
                           peso 0.7 — inferior al exacto para no sobreestimar.
                        Para bigrams ('machine learning') solo se aplica exacto.
  7. Ponderación    — cada término tiene un peso de importancia según su categoría:
                        • Sustantivo / herramienta / skill  (peso 1.0): Python, SQL,
                          gestión, liderazgo, análisis, AWS, Power BI, etc.
                        • Verbo infinitivo en -ar/-er/-ir    (peso 0.5): gestionar,
                          desarrollar, analizar, implementar, etc.  Los verbos
                          indican capacidad pero no certifican el dominio de una
                          herramienta, por lo que ponderan la mitad.
                        • Bigram (término compuesto)         (peso 0.5): los bigrams
                          son bonus — si se encuentran exactos suman, pero su ausencia
                          no penaliza tanto como la de un sustantivo clave.
                      Score del requisito = Σ(match_peso × importancia) / Σ(importancia)
                      Score global = promedio ponderado de requisitos
                      (encontrado=1.0, parcial=0.5, no_encontrado=0).

Constantes de ajuste (module-level)
────────────────────────────────────
  _MIN_LCP           : mínimo de chars compartidos para cobertura léxica (default 5).
  _PESO_EXACTO       : peso del match exacto (default 1.0).
  _PESO_COBERTURA    : peso del match por cobertura LCP (default 0.7).
  _UMBRAL_ENCONTRADO : ratio mínimo para estado 'encontrado' (default 0.5).
  _MIN_LEN_VERBO     : longitud mínima para clasificar un token como verbo (default 7).
  _PESO_TERM_NORMAL  : importancia de sustantivos/herramientas/skills (default 1.0).
  _PESO_TERM_VERBO   : importancia de verbos en infinitivo (default 0.5).
  _PESO_TERM_BIGRAM  : importancia de bigrams/términos compuestos (default 0.5).

Clases
──────
  _Normalizador      : Etapa 1 — normalización de texto.
  _Limpiador         : Etapa 2 — limpieza tipográfica.
  _Tokenizador       : Etapa 3 — segmentación en tokens.
  _Filtro            : Etapa 4 — filtrado de tokens irrelevantes.
  _ConstructorNgrams : Etapa 5 — construcción de términos compuestos.
  _Cobertura         : Etapa 6 — matching exacto y por prefijo común (LCP).
  _PonderadorTerminos: Etapa 7 — asignación de pesos por categoría léxica.
  CVMatcher          : Orquestador del pipeline completo.
"""

from .services import tablas as tb
from .services.normalizador import Normalizador
from .services.limpiador import Limpiador
from .services.tokenizador import Tokenizador
from .services.filtro import Filtro
from .services.constructorNgrams import ConstructorNgrams
from .services.cobertura import Cobertura
from .services.ponderador_terminos import PonderadorTerminos

# ─── Orquestador ─────────────────────────────────────────────────────────────

class CVMatcher:
    """
    Motor ATS que mide la compatibilidad entre un CV y un perfil laboral.

    Orquesta el pipeline completo:
        _Normalizador → _Limpiador → _Tokenizador → _Filtro
        → _ConstructorNgrams → _Cobertura

    Para cada requisito del perfil:
      1. Extrae sus términos clave con el pipeline (unigrams + bigrams).
      2. Busca cada término en el CV con _Cobertura (exacto o por LCP).
      3. Calcula un ratio ponderado: peso_exacto=1.0, peso_cobertura=0.7.
      4. Determina el estado: 'encontrado' (ratio ≥ 0.5), 'parcial' (>0), 'no_encontrado'.

    El score global es el promedio ponderado de los estados de requisitos
    (encontrado=1.0, parcial=0.5, no_encontrado=0), expresado en porcentaje.

    Uso típico
    ----------
        matcher  = CVMatcher()
        resultado = matcher.analizar(cv_texto, perfil_texto)
        keywords  = matcher.extraer_keywords_perfil(desc_perfil)
        desc_ok   = matcher.preparar_descripcion(desc_raw)
    """

    def __init__(self):
        self._norm      = Normalizador()
        self._limp      = Limpiador()
        self._tok       = Tokenizador()
        self._filt      = Filtro()
        self._ngram     = ConstructorNgrams()
        self._cobertura = Cobertura()

    # ── API pública ───────────────────────────────────────────────────────────

    def preparar_descripcion(self, texto: str) -> str:
        """
        Limpia el espaciado tipográfico de una descripción antes de almacenarla.
        Colapsa líneas vacías múltiples y espacios redundantes; no normaliza
        caracteres para mantener la legibilidad del texto almacenado.
        """
        return self._limp.limpiar(texto)

    def extraer_keywords_perfil(self, desc: str) -> list:
        """
        Extrae keywords significativas de la descripción de un perfil laboral.
        Aplica el pipeline completo y retorna los términos deduplicados.
        """
        texto_norm = self._norm.normalizar(self._limp.limpiar(desc))
        tokens     = self._filt.filtrar(self._tok.tokenizar(texto_norm))
        terminos   = self._ngram.construir(tokens, bigrams=True)
        return list(dict.fromkeys(terminos))

    def analizar(self, cv_texto: str, perfil_texto: str) -> dict:
        """
        Compara un CV contra un perfil laboral línea a línea usando matching
        por cobertura léxica (ver _Cobertura).

        Parámetros
        ----------
        cv_texto     : texto completo del CV (raw; se limpia y normaliza internamente).
        perfil_texto : descripción del perfil / requisitos.  Las líneas en
                       MAYÚSCULAS (encabezados de sección) se ignoran;
                       cada línea restante es tratada como un requisito.

        Retorno
        -------
        {
            'total'         : int,
            'encontrados'   : int,   # requisitos con estado 'encontrado'
            'parciales'     : int,   # requisitos con estado 'parcial'
            'no_encontrados': int,   # requisitos con estado 'no_encontrado'
            'score_global'  : int,   # 0–100, promedio ponderado de requisitos
            'requisitos'    : [
                {
                    'texto'         : str,
                    'estado'        : 'encontrado' | 'parcial' | 'no_encontrado',
                    'score_req'     : float,  # ratio ponderado del requisito (0–1)
                    'encontrados'   : list[str],  # términos cubiertos (exacto o LCP)
                    'no_encontrados': list[str],  # términos no cubiertos
                    'contexto'      : str,        # fragmento del CV donde aparecen
                },
                ...
            ]
        }
        """
        # Limpiar el CV colapsa artefactos de PDFs (dobles espacios, etc.).
        # Normalizar preserva la longitud → len(cv_norm) == len(cv_limp),
        # lo que permite extraer contexto de cv_limp por posición.
        cv_limp = self._limp.limpiar(cv_texto)
        cv_norm = self._norm.normalizar(cv_limp)

        # Precomputar tokens del CV para el matching por LCP.
        # Se filtran tokens cortos y stopwords para reducir falsos positivos.
        cv_tokens = frozenset(
            tok for tok in self._tok.tokenizar(cv_norm)
            if len(tok) >= tb.MIN_LCP and tok not in tb.STOPWORDS
        )

        requisitos_raw = self._parsear_requisitos(perfil_texto)
        if not requisitos_raw:
            return self._vacio()

        detalle = [
            self._evaluar_requisito(req, cv_norm, cv_limp, cv_tokens)
            for req in requisitos_raw
        ]

        encontrados    = sum(1 for r in detalle if r['estado'] == 'encontrado')
        parciales      = sum(1 for r in detalle if r['estado'] == 'parcial')
        no_encontrados = sum(1 for r in detalle if r['estado'] == 'no_encontrado')
        total          = len(detalle)

        score_global = (
            round((encontrados * 1.0 + parciales * 0.5) / total * 100)
            if total else 0
        )

        return {
            'total'         : total,
            'encontrados'   : encontrados,
            'parciales'     : parciales,
            'no_encontrados': no_encontrados,
            'score_global'  : score_global,
            'requisitos'    : detalle,
        }

    # ── Métodos internos ──────────────────────────────────────────────────────

    @staticmethod
    def _vacio() -> dict:
        return {
            'total': 0, 'encontrados': 0, 'parciales': 0,
            'no_encontrados': 0, 'score_global': 0, 'requisitos': [],
        }

    def _parsear_requisitos(self, texto: str) -> list:
        """
        Extrae líneas de requisito de un perfil de texto libre.
        Descarta encabezados de sección (solo letras mayúsculas), separadores
        (---, ===) y líneas demasiado cortas (< 5 chars).
        Elimina los prefijos de listas (guion, viñeta, número).
        """
        reqs = []
        for linea in texto.splitlines():
            linea = linea.strip()
            if not linea:
                continue
            if all(c in '-=_*~' for c in linea):
                continue
            letras = [c for c in linea if c.isalpha()]
            if letras and all(c.isupper() for c in letras):
                continue
            for pfx in ('•', '–', '—', '·', '-', '*', '▪'):
                if linea.startswith(pfx):
                    linea = linea[len(pfx):].strip()
                    break
            if linea and linea[0].isdigit():
                i = 0
                while i < len(linea) and linea[i].isdigit():
                    i += 1
                if i < len(linea) and linea[i] in '.)':
                    linea = linea[i + 1:].strip()
            if len(linea) >= 5:
                reqs.append(linea)
        return reqs

    def _evaluar_requisito(self, req_txt: str, cv_norm: str,
                           cv_original: str, cv_tokens: frozenset) -> dict:
        """
        Evalúa la cobertura de un requisito sobre el CV con ponderación léxica.

        Para cada término del requisito:
          1. _Cobertura.buscar  → tipo ('exacto'|'cobertura'|'ninguno') + match_peso.
          2. _PonderadorTerminos.peso → importancia del término (sustantivo=1.0,
             verbo=0.5, bigram=0.5).
          3. Contribución = match_peso × importancia.

        Score del requisito (media ponderada normalizada):
          score_req = Σ(match_peso × importancia) / Σ(1.0 × importancia)

        El denominador usa siempre el peso exacto máximo (1.0) escalado por
        importancia, de modo que el score refleja "qué fracción del valor total
        del requisito está cubierta en el CV".

        Estado derivado del score_req:
          ≥ _UMBRAL_ENCONTRADO  →  'encontrado'
          >  0                  →  'parcial'
          == 0                  →  'no_encontrado'
        """
        req_norm = self._norm.normalizar(req_txt)
        tokens   = self._filt.filtrar(self._tok.tokenizar(req_norm))
        terminos = list(dict.fromkeys(self._ngram.construir(tokens, bigrams=True)))

        if not terminos:
            return {
                'texto': req_txt, 'estado': 'no_encontrado', 'score_req': 0.0,
                'encontrados': [], 'no_encontrados': [], 'contexto': '',
            }

        encontrados    = []
        no_encontrados = []
        suma_pond      = 0.0   # Σ (match_peso × importancia)
        suma_max       = 0.0   # Σ (1.0 × importancia)  — denominador normalizado
        primer_pos     = -1

        for termino in terminos:
            imp               = PonderadorTerminos.peso(termino)
            tipo, pos, m_peso = Cobertura.buscar(cv_norm, cv_tokens, termino)
            suma_pond += m_peso * imp
            suma_max  += tb.PESO_EXACTO * imp
            if tipo != 'ninguno':
                encontrados.append(termino)
                if primer_pos == -1:
                    primer_pos = pos
            else:
                no_encontrados.append(termino)

        score_req = suma_pond / suma_max if suma_max > 0 else 0.0

        if score_req >= tb.UMBRAL_ENCONTRADO:
            estado = 'encontrado'
        elif score_req > 0:
            estado = 'parcial'
        else:
            estado = 'no_encontrado'

        contexto = ''
        if primer_pos >= 0:
            ini      = max(0, primer_pos - tb.VENTANA_CTX)
            fin      = min(len(cv_original), primer_pos + tb.VENTANA_CTX)
            fragmento = cv_original[ini:fin].replace('\n', ' ').strip()
            if ini > 0:
                fragmento = '…' + fragmento
            if fin < len(cv_original):
                fragmento = fragmento + '…'
            contexto = fragmento

        return {
            'texto'         : req_txt,
            'estado'        : estado,
            'score_req'     : round(score_req, 3),
            'encontrados'   : encontrados,
            'no_encontrados': no_encontrados,
            'contexto'      : contexto,
        }
