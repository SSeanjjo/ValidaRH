
# ─── Tabla de normalización de diacríticos ───────────────────────────────────
# Se usan escapes Unicode (\uXXXX) para evitar ambigüedad con caracteres
# visualmente similares de otros bloques Unicode (p.ej. cirílico).
# La tabla es 1-a-1: cada carácter fuente → exactamente un carácter destino,
# preservando la longitud del string y la alineación de posiciones.
FUENTE_NORM = (
    'áéíóú'   # á é í ó ú  (agudas min.)
    'àèìòù'   # à è ì ò ù  (graves min.)
    'âêîôû'   # â ê î ô û  (circunflejas min.)
    'äëïöü'   # ä ë ï ö ü  (diéresis min.)
    'ñç'                     # ñ ç
    'ÁÉÍÓÚ'   # Á É Í Ó Ú  (agudas may.)
    'ÀÈÌÒÙ'   # À È Ì Ò Ù  (graves may.)
    'ÂÊÎÔÛ'   # Â Ê Î Ô Û  (circunflejas may.)
    'ÄËÏÖÜ'   # Ä Ë Ï Ö Ü  (diéresis may.)
    'ÑÇ'                     # Ñ Ç
)
DESTINO_NORM = (
    'aeiou' 'aeiou' 'aeiou' 'aeiou' 'nc'   # 22 minúsculas
    'AEIOU' 'AEIOU' 'AEIOU' 'AEIOU' 'NC'   # 22 mayúsculas
)
TABLA_NORM = str.maketrans(FUENTE_NORM, DESTINO_NORM)


# ─── Stopwords en forma normalizada (sin tildes, minúsculas) ─────────────────
STOPWORDS = frozenset({
    'a', 'al', 'algo', 'algunas', 'algunos', 'ante', 'antes', 'como',
    'con', 'contra', 'cual', 'cuando', 'de', 'del', 'desde', 'donde',
    'durante', 'e', 'el', 'ella', 'ello', 'ellos', 'en', 'entre',
    'es', 'esa', 'esas', 'ese', 'eso', 'esos', 'esta', 'estar', 'este',
    'estos', 'fue', 'gran', 'ha', 'haber', 'hay', 'he', 'la', 'las',
    'le', 'les', 'lo', 'los', 'mas', 'me', 'mi', 'mis', 'mismo',
    'mucho', 'muchos', 'muy', 'nada', 'ni', 'no', 'nos', 'o', 'otro',
    'otros', 'para', 'pero', 'poco', 'por', 'que', 'quien', 'quienes',
    'se', 'sea', 'ser', 'si', 'sin', 'sobre', 'su', 'sus', 'tan',
    'tambien', 'te', 'todo', 'todos', 'tu', 'un', 'una', 'unas',
    'uno', 'unos', 'y', 'ya', 'yo',
})

# Caracteres técnicos válidos dentro de un token (p.ej. 'c++', 'c#')
CHARS_EXTRA = frozenset('+#')

# Chars a cada lado del match para el fragmento de contexto
VENTANA_CTX = 60

# ─── Constantes de matching por cobertura ────────────────────────────────────
# Ajustables sin modificar la lógica de las clases.

MIN_LCP           = 5    # Prefijo compartido mínimo para cobertura léxica
PESO_EXACTO       = 1.0  # Peso del match exacto con límite de palabra
PESO_COBERTURA    = 0.7  # Peso del match por cobertura léxica (LCP)
UMBRAL_ENCONTRADO = 0.5  # Ratio ponderado mínimo para estado 'encontrado'

# ─── Constantes de ponderación por categoría léxica ──────────────────────────
# Los sustantivos/herramientas pesan más que los verbos de acción.
MIN_LEN_VERBO    = 7    # Longitud mínima para clasificar un token como verbo
PESO_TERM_NORMAL = 1.0  # Importancia: sustantivos, siglas, herramientas, skills
PESO_TERM_VERBO  = 0.5  # Importancia: verbos en infinitivo (-ar/-er/-ir)
PESO_TERM_BIGRAM = 0.5  # Importancia: bigrams — bonus si encontrados, no penalizan fuerte

# Tokens que terminan en -ar/-er/-ir pero NO son verbos (adjetivos, sustantivos
# técnicos en inglés, etc.).  Se comparan contra el token ya normalizado.
EXCEPCIONES_VERBO = frozenset({
    # Adjetivos españoles que terminan en -ar (7+ chars)
    'popular',    'similar',    'familiar',   'regular',    'modular',
    'nuclear',    'circular',   'singular',   'particular', 'muscular',
    'secular',    'escolar',    'molecular',  'calendar',   'angular',
    'tubular',    'celular',    'vascular',   'laboral',    'doctoral',
    # Sustantivos técnicos en inglés que terminan en -er/-ar (7+ chars)
    'cluster',    'manager',    'container',  'provider',   'adapter',
    'register',   'transformer','observer',   'publisher',  'subscriber',
    'modifier',   'handler',    'scanner',    'builder',    'compiler',
    'debugger',   'profiler',   'dispatcher', 'scheduler',  'controller',
    'wrapper',    'tracker',    'listener',   'renderer',   'injector',
    'selector',   'inspector',  'optimizer',  'converter',  'formatter',
    'router',     'broker',     'worker',     'iterator',   'generator',
})