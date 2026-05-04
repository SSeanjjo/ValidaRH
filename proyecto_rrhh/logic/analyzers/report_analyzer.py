"""
report_analyzer.py — Extracción de datos estructurados desde documentos .txt/.pdf.
"""
import os
import datetime
from logic.validators.pattern_matcher import PatternMatcher


class ReportAnalyzer:

    def __init__(self):
        self._matcher        = PatternMatcher()
        self._contenido      = ''
        self._nombre_archivo = ''
        self._resultados     = {}
        self._estadisticas   = {}
        self._analizado      = False

    def cargar_archivo(self, ruta: str) -> tuple:
        if not os.path.exists(ruta):
            return False, f"El archivo no existe: {ruta}"
        ext = os.path.splitext(ruta.lower())[1]
        if ext not in ('.txt', '.pdf'):
            return False, "Solo se aceptan archivos .txt o .pdf"
        if os.path.getsize(ruta) == 0:
            return False, "El archivo está vacío."

        if ext == '.pdf':
            ok, resultado = self._extraer_texto_pdf(ruta)
            if not ok:
                return False, resultado
            self._contenido = resultado
        else:
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    self._contenido = f.read()
            except UnicodeDecodeError:
                try:
                    with open(ruta, 'r', encoding='latin-1') as f:
                        self._contenido = f.read()
                except Exception as e:
                    return False, f"Error al leer el archivo: {str(e)}"
            except Exception as e:
                return False, f"Error inesperado: {str(e)}"

        self._nombre_archivo = os.path.basename(ruta)
        self._analizado = False
        return True, f"Archivo '{self._nombre_archivo}' cargado correctamente."

    def _extraer_texto_pdf(self, ruta: str) -> tuple:
        try:
            import pdfplumber
        except ImportError:
            return False, "Instale pdfplumber: pip install pdfplumber"
        try:
            with pdfplumber.open(ruta) as pdf:
                paginas = []
                for num, pagina in enumerate(pdf.pages, start=1):
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        paginas.append(f"[Página {num}]\n{texto_pagina}")
                texto = "\n\n".join(paginas)
            if not texto.strip():
                return False, "No se pudo extraer texto del PDF. Puede ser una imagen escaneada."
            return True, texto
        except Exception as e:
            return False, f"Error al procesar el PDF: {str(e)}"

    def analyze(self) -> dict:
        if not self._contenido:
            return {}
        patrones = self._matcher.find_all(self._contenido)
        lineas   = self._contenido.splitlines()
        palabras = self._contenido.split()
        chars    = len(self._contenido)
        total_datos = sum(len(v) for v in patrones.values())
        densidad    = round((total_datos / len(palabras)) * 100, 2) if palabras else 0
        self._estadisticas = {
            'archivo'                : self._nombre_archivo,
            'fecha_analisis'         : datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'total_lineas'           : len(lineas),
            'total_palabras'         : len(palabras),
            'total_caracteres'       : chars,
            'total_datos_encontrados': total_datos,
            'densidad_datos_pct'     : densidad,
        }
        advertencias = self._generar_advertencias(patrones)
        self._resultados = {
            'patrones'    : patrones,
            'estadisticas': self._estadisticas,
            'advertencias': advertencias,
        }
        self._analizado = True
        return self._resultados

    def _generar_advertencias(self, patrones: dict) -> list:
        adv = []
        if len(patrones.get('cedulas', [])) > 3:
            adv.append(f"Se encontraron {len(patrones['cedulas'])} cédulas. El documento puede tener múltiples perfiles.")
        if not patrones.get('correos'):
            adv.append("No se encontró ningún correo electrónico en el documento.")
        if not patrones.get('telefonos'):
            adv.append("No se encontró ningún número de teléfono en el documento.")
        if len(patrones.get('correos', [])) > 5:
            adv.append(f"Se encontraron {len(patrones['correos'])} correos. Verifique que corresponda a un solo candidato.")
        return adv

    def get_resultados(self) -> dict:
        return self._resultados

    def get_contenido(self) -> str:
        return self._contenido

    def esta_analizado(self) -> bool:
        return self._analizado

    def export(self, ruta_salida: str = '') -> tuple:
        if not self._analizado:
            return False, "Debe ejecutar analyze() antes de exportar."
        if not ruta_salida:
            nombre_base = self._nombre_archivo.replace('.txt', '')
            ruta_salida = f"reporte_{nombre_base}.txt"
        try:
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                f.write(self._formatear_reporte())
            return True, ruta_salida
        except Exception as e:
            return False, f"Error al exportar: {str(e)}"

    def _formatear_reporte(self) -> str:
        sep  = '=' * 60
        sep2 = '-' * 40
        est  = self._estadisticas
        pat  = self._resultados.get('patrones', {})
        adv  = self._resultados.get('advertencias', [])
        lineas = [
            sep, '   REPORTE DE ANÁLISIS — ValidaRH', sep, '',
            '[ INFORMACIÓN DEL DOCUMENTO ]', sep2,
            f"Archivo         : {est.get('archivo', '-')}",
            f"Fecha de análisis: {est.get('fecha_analisis', '-')}",
            f"Total líneas    : {est.get('total_lineas', 0)}",
            f"Total palabras  : {est.get('total_palabras', 0)}",
            f"Total caracteres: {est.get('total_caracteres', 0)}",
            f"Datos encontrados: {est.get('total_datos_encontrados', 0)}",
            f"Densidad de datos: {est.get('densidad_datos_pct', 0)}%",
            '', '[ PATRONES ENCONTRADOS ]', sep2,
        ]
        etiquetas = {
            'correos': 'Correos', 'telefonos': 'Teléfonos',
            'cedulas': 'Cédulas', 'fechas': 'Fechas',
            'urls': 'URLs', 'placas': 'Placas',
        }
        for clave, etiqueta in etiquetas.items():
            items = pat.get(clave, [])
            lineas.append(f"\n{etiqueta} ({len(items)} encontrados):")
            if items:
                for item in items:
                    lineas.append(f"    - {item}")
            else:
                lineas.append("    (ninguno)")
        if adv:
            lineas += ['', '[ ADVERTENCIAS ]', sep2]
            for a in adv:
                lineas.append(f"  ! {a}")
        lineas += ['', sep, '  Generado por ValidaRH v2.0', sep]
        return '\n'.join(lineas)
