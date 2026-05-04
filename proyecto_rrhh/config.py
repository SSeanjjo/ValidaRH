"""
config.py — Configuración global del sistema ValidaRH.
"""
import pathlib

BASE_DIR = pathlib.Path(__file__).parent
DB_PATH  = BASE_DIR / 'data' / 'validarh.db'

# ── SMTP para verificación de correo ─────────────────────────────────────────
# Si EMAIL_USER está vacío el sistema muestra el código en un diálogo.
EMAIL_HOST    = 'smtp.gmail.com'
EMAIL_PORT    = 587
EMAIL_USER    = ''   # ej: 'validarh.app@gmail.com'
EMAIL_PASS    = ''   # App Password de Gmail (no la contraseña de la cuenta)
EMAIL_ENABLED = bool(EMAIL_USER)

VERIFICACION_DIGITOS = 6
