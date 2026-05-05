"""
test_report_analyzer.py — Tests unitarios para ReportAnalyzer.

Ejecutar desde la raíz del proyecto:
    python -m pytest tests/test_report_analyzer.py -v
    python -m unittest tests/test_report_analyzer.py
"""
import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.analyzers.report_analyzer import ReportAnalyzer


# ── Contenido de ejemplo con datos variados ───────────────────────────────────
TEXTO_CV = """
Juan Carlos Pérez López
CC: 12345678
Celular: 3001234567
Correo: juan.perez@empresa.com
Fecha de nacimiento: 15/06/1990
Placa: ABC123

EXPERIENCIA
Desarrollador backend en TechCorp (2018-2022)
Python, Django, PostgreSQL

EDUCACIÓN
Universidad Nacional — Ingeniería de Sistemas
"""

TEXTO_SIN_CONTACTO = """
Perfil profesional con experiencia en gestión de proyectos.
Conocimientos en metodologías ágiles y liderazgo de equipos.
"""

TEXTO_MUCHAS_CEDULAS = """
CC: 11111111
CC: 22222222
CC: 33333333
CC: 44444444
Correo: info@empresa.com
Tel: 3009876543
"""


def _crear_txt(contenido: str) -> str:
    """Crea un archivo .txt temporal y retorna su ruta."""
    f = tempfile.NamedTemporaryFile(
        mode='w', suffix='.txt', encoding='utf-8', delete=False)
    f.write(contenido)
    f.close()
    return f.name


class TestCargarArchivo(unittest.TestCase):

    def setUp(self):
        self.ra = ReportAnalyzer()
        self._temps = []

    def tearDown(self):
        for ruta in self._temps:
            try:
                os.unlink(ruta)
            except OSError:
                pass

    def _tmp(self, contenido='hola mundo'):
        ruta = _crear_txt(contenido)
        self._temps.append(ruta)
        return ruta

    # ── Válidos ───────────────────────────────────────────────────────────────

    def test_cargar_txt_valido(self):
        ruta = self._tmp(TEXTO_CV)
        ok, msg = self.ra.cargar_archivo(ruta)
        self.assertTrue(ok)
        self.assertIn("cargado", msg.lower())

    def test_contenido_disponible_tras_carga(self):
        ruta = self._tmp("correo: test@mail.com")
        self.ra.cargar_archivo(ruta)
        self.assertIn("test@mail.com", self.ra.get_contenido())

    def test_estado_no_analizado_tras_carga(self):
        ruta = self._tmp(TEXTO_CV)
        self.ra.cargar_archivo(ruta)
        self.assertFalse(self.ra.esta_analizado())

    # ── Inválidos ─────────────────────────────────────────────────────────────

    def test_archivo_inexistente(self):
        ok, msg = self.ra.cargar_archivo("/ruta/que/no/existe.txt")
        self.assertFalse(ok)
        self.assertIn("no existe", msg.lower())

    def test_extension_no_soportada(self):
        f = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        f.write(b"contenido")
        f.close()
        self._temps.append(f.name)
        ok, msg = self.ra.cargar_archivo(f.name)
        self.assertFalse(ok)
        self.assertIn(".pdf", msg)

    def test_archivo_vacio(self):
        f = tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False)
        f.close()
        self._temps.append(f.name)
        ok, msg = self.ra.cargar_archivo(f.name)
        self.assertFalse(ok)
        self.assertIn("vacío", msg.lower())


class TestAnalyze(unittest.TestCase):

    def setUp(self):
        self._temps = []

    def tearDown(self):
        for ruta in self._temps:
            try:
                os.unlink(ruta)
            except OSError:
                pass

    def _cargar(self, contenido: str) -> ReportAnalyzer:
        ra = ReportAnalyzer()
        ruta = _crear_txt(contenido)
        self._temps.append(ruta)
        ra.cargar_archivo(ruta)
        return ra

    # ── Sin contenido ─────────────────────────────────────────────────────────

    def test_analyze_sin_cargar_retorna_vacio(self):
        ra = ReportAnalyzer()
        resultado = ra.analyze()
        self.assertEqual(resultado, {})

    # ── Estructura del resultado ──────────────────────────────────────────────

    def test_analyze_retorna_claves_esperadas(self):
        ra = self._cargar(TEXTO_CV)
        resultado = ra.analyze()
        self.assertIn('patrones', resultado)
        self.assertIn('estadisticas', resultado)
        self.assertIn('advertencias', resultado)

    def test_estadisticas_contienen_conteos(self):
        ra = self._cargar(TEXTO_CV)
        est = ra.analyze()['estadisticas']
        self.assertGreater(est['total_palabras'], 0)
        self.assertGreater(est['total_lineas'], 0)
        self.assertGreater(est['total_caracteres'], 0)

    def test_estado_analizado_tras_analyze(self):
        ra = self._cargar(TEXTO_CV)
        ra.analyze()
        self.assertTrue(ra.esta_analizado())

    # ── Detección de patrones ─────────────────────────────────────────────────

    def test_detecta_correo(self):
        ra = self._cargar(TEXTO_CV)
        patrones = ra.analyze()['patrones']
        self.assertIn('juan.perez@empresa.com', patrones['correos'])

    def test_detecta_telefono(self):
        ra = self._cargar(TEXTO_CV)
        patrones = ra.analyze()['patrones']
        self.assertIn('3001234567', patrones['telefonos'])

    def test_detecta_cedula(self):
        ra = self._cargar("CC: 12345678 — datos del candidato.")
        patrones = ra.analyze()['patrones']
        self.assertIn('12345678', patrones['cedulas'])

    def test_detecta_placa(self):
        ra = self._cargar("Mi vehículo tiene placa ABC123 asignada.")
        patrones = ra.analyze()['patrones']
        self.assertIn('ABC123', patrones['placas'])

    def test_texto_sin_datos_patrones_vacios(self):
        ra = self._cargar("texto sin ningún dato estructurado aquí")
        patrones = ra.analyze()['patrones']
        self.assertEqual(patrones['correos'], [])
        self.assertEqual(patrones['telefonos'], [])

    def test_patrones_sin_duplicados(self):
        contenido = ("correo: test@mail.com y también test@mail.com "
                     "y de nuevo test@mail.com")
        ra = self._cargar(contenido)
        patrones = ra.analyze()['patrones']
        correos = patrones['correos']
        self.assertEqual(len(correos), len(set(correos)))


class TestAdvertencias(unittest.TestCase):

    def setUp(self):
        self._temps = []

    def tearDown(self):
        for ruta in self._temps:
            try:
                os.unlink(ruta)
            except OSError:
                pass

    def _cargar_y_analizar(self, contenido: str) -> list:
        ra = ReportAnalyzer()
        ruta = _crear_txt(contenido)
        self._temps.append(ruta)
        ra.cargar_archivo(ruta)
        return ra.analyze()['advertencias']

    def test_advertencia_sin_correo(self):
        adv = self._cargar_y_analizar(TEXTO_SIN_CONTACTO)
        textos = ' '.join(adv).lower()
        self.assertIn("correo", textos)

    def test_advertencia_sin_telefono(self):
        adv = self._cargar_y_analizar(TEXTO_SIN_CONTACTO)
        textos = ' '.join(adv).lower()
        self.assertIn("teléfono", textos)

    def test_advertencia_muchas_cedulas(self):
        adv = self._cargar_y_analizar(TEXTO_MUCHAS_CEDULAS)
        textos = ' '.join(adv).lower()
        self.assertIn("cédulas", textos)

    def test_sin_advertencias_en_cv_completo(self):
        adv = self._cargar_y_analizar(TEXTO_CV)
        # CV completo no debe disparar advertencias de contacto faltante
        textos = ' '.join(adv).lower()
        self.assertNotIn("no se encontró ningún correo", textos)
        self.assertNotIn("no se encontró ningún número", textos)


class TestExport(unittest.TestCase):

    def setUp(self):
        self._temps = []

    def tearDown(self):
        for ruta in self._temps:
            try:
                os.unlink(ruta)
            except OSError:
                pass

    def test_export_sin_analyze_falla(self):
        ra = ReportAnalyzer()
        ruta = _crear_txt(TEXTO_CV)
        self._temps.append(ruta)
        ra.cargar_archivo(ruta)
        ok, msg = ra.export("salida_prueba.txt")
        self.assertFalse(ok)
        self.assertIn("analyze", msg.lower())

    def test_export_tras_analyze_crea_archivo(self):
        ra = ReportAnalyzer()
        ruta = _crear_txt(TEXTO_CV)
        self._temps.append(ruta)
        ra.cargar_archivo(ruta)
        ra.analyze()

        salida = tempfile.mktemp(suffix='.txt')
        self._temps.append(salida)

        ok, ruta_out = ra.export(salida)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(ruta_out))

    def test_export_contiene_seccion_patrones(self):
        ra = ReportAnalyzer()
        ruta = _crear_txt(TEXTO_CV)
        self._temps.append(ruta)
        ra.cargar_archivo(ruta)
        ra.analyze()

        salida = tempfile.mktemp(suffix='.txt')
        self._temps.append(salida)
        ra.export(salida)

        with open(salida, encoding='utf-8') as f:
            contenido_reporte = f.read()

        self.assertIn("PATRONES ENCONTRADOS", contenido_reporte)
        self.assertIn("ValidaRH", contenido_reporte)

    def test_export_sin_analyze_no_crea_archivo(self):
        ra = ReportAnalyzer()
        salida = tempfile.mktemp(suffix='.txt')
        self._temps.append(salida)
        ra.export(salida)
        self.assertFalse(os.path.exists(salida))


if __name__ == '__main__':
    unittest.main(verbosity=2)
