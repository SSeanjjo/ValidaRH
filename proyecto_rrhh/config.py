"""
config.py — Configuración global del sistema ValidaRH.
"""
import pathlib
import os.path
import dotenv as dotenv
dotenv.load_dotenv()  # Carga variables de entorno desde .env
BASE_DIR = pathlib.Path(__file__).parent
DB_PATH  = BASE_DIR / 'data' / 'validarh.db'

# ── SMTP para verificación de correo ─────────────────────────────────────────
# Si EMAIL_USER está vacío el sistema muestra el código en un diálogo.
EMAIL_HOST    = 'smtp.gmail.com'
EMAIL_PORT    = 587
EMAIL_USER    = os.getenv('EMAIL')
EMAIL_PASS    = os.getenv('EMAIL_PASS')
EMAIL_ENABLED = bool(EMAIL_USER)

VERIFICACION_DIGITOS = 6
