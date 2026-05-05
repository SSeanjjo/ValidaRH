"""
test_form_validator.py — Tests unitarios para FormValidator.

Ejecutar desde la raíz del proyecto:
    python -m pytest tests/test_form_validator.py -v
    python -m unittest tests/test_form_validator.py
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.validators.form_validator import FormValidator


class TestValidarNombre(unittest.TestCase):

    def setUp(self):
        self.fv = FormValidator()

    # ── Válidos ───────────────────────────────────────────────────────────────

    def test_nombre_simple_valido(self):
        ok, _ = self.fv.validar_nombre("Juan Pérez")
        self.assertTrue(ok)

    def test_nombre_compuesto_valido(self):
        ok, _ = self.fv.validar_nombre("María José López Romero")
        self.assertTrue(ok)

    def test_nombre_con_tildes(self):
        ok, _ = self.fv.validar_nombre("Andrés García")
        self.assertTrue(ok)

    # ── Inválidos ─────────────────────────────────────────────────────────────

    def test_nombre_muy_corto(self):
        ok, msg = self.fv.validar_nombre("A B")
        self.assertFalse(ok)

    def test_nombre_sin_apellido(self):
        ok, msg = self.fv.validar_nombre("Alejandro")
        self.assertFalse(ok)
        self.assertIn("apellido", msg.lower())

    def test_nombre_con_numeros(self):
        ok, _ = self.fv.validar_nombre("Juan123 Pérez")
        self.assertFalse(ok)

    def test_nombre_con_simbolos(self):
        ok, _ = self.fv.validar_nombre("Juan@ Pérez")
        self.assertFalse(ok)

    def test_nombre_palabra_muy_corta(self):
        ok, msg = self.fv.validar_nombre("J Pérez")
        self.assertFalse(ok)

    def test_nombre_vacio(self):
        ok, _ = self.fv.validar_nombre("")
        self.assertFalse(ok)

    def test_nombre_demasiado_largo(self):
        ok, _ = self.fv.validar_nombre("Juan " + "A" * 80)
        self.assertFalse(ok)


class TestValidarCorreo(unittest.TestCase):

    def setUp(self):
        self.fv = FormValidator()

    # ── Válidos ───────────────────────────────────────────────────────────────

    def test_correo_basico(self):
        ok, _ = self.fv.validar_correo("usuario@empresa.com")
        self.assertTrue(ok)

    def test_correo_con_subdominio(self):
        ok, _ = self.fv.validar_correo("user@mail.empresa.co")
        self.assertTrue(ok)

    def test_correo_con_punto_y_guion(self):
        ok, _ = self.fv.validar_correo("nombre.apellido@gmail.com")
        self.assertTrue(ok)

    def test_correo_con_mas(self):
        ok, _ = self.fv.validar_correo("user+tag@domain.org")
        self.assertTrue(ok)

    # ── Inválidos ─────────────────────────────────────────────────────────────

    def test_correo_sin_arroba(self):
        ok, msg = self.fv.validar_correo("usuarioempresa.com")
        self.assertFalse(ok)
        self.assertIn("@", msg)

    def test_correo_doble_arroba(self):
        ok, _ = self.fv.validar_correo("a@@b.com")
        self.assertFalse(ok)

    def test_correo_sin_dominio(self):
        ok, _ = self.fv.validar_correo("usuario@")
        self.assertFalse(ok)

    def test_correo_sin_tld(self):
        ok, _ = self.fv.validar_correo("usuario@empresa")
        self.assertFalse(ok)

    def test_correo_vacio(self):
        ok, _ = self.fv.validar_correo("")
        self.assertFalse(ok)

    def test_correo_tld_un_caracter(self):
        ok, _ = self.fv.validar_correo("user@dom.c")
        self.assertFalse(ok)


class TestValidarContrasena(unittest.TestCase):

    def setUp(self):
        self.fv = FormValidator()

    # ── Válidos ───────────────────────────────────────────────────────────────

    def test_contrasena_segura(self):
        ok, _ = self.fv.validar_contrasena("Segura#1")
        self.assertTrue(ok)

    def test_contrasena_larga_segura(self):
        ok, _ = self.fv.validar_contrasena("MiClave_Super99!")
        self.assertTrue(ok)

    # ── Inválidos ─────────────────────────────────────────────────────────────

    def test_contrasena_muy_corta(self):
        ok, msg = self.fv.validar_contrasena("Ab1#")
        self.assertFalse(ok)
        self.assertIn("8 caracteres", msg)

    def test_contrasena_sin_mayuscula(self):
        ok, msg = self.fv.validar_contrasena("clave123#a")
        self.assertFalse(ok)
        self.assertIn("mayúscula", msg)

    def test_contrasena_sin_minuscula(self):
        ok, msg = self.fv.validar_contrasena("CLAVE123#")
        self.assertFalse(ok)
        self.assertIn("minúscula", msg)

    def test_contrasena_sin_numero(self):
        ok, msg = self.fv.validar_contrasena("ClaveSegura#")
        self.assertFalse(ok)
        self.assertIn("número", msg)

    def test_contrasena_sin_especial(self):
        ok, msg = self.fv.validar_contrasena("ClaveSegura1")
        self.assertFalse(ok)
        self.assertIn("especial", msg)

    def test_contrasena_vacia(self):
        ok, _ = self.fv.validar_contrasena("")
        self.assertFalse(ok)


class TestValidarTelefono(unittest.TestCase):

    def setUp(self):
        self.fv = FormValidator()

    # ── Válidos ───────────────────────────────────────────────────────────────

    def test_movil_10_digitos(self):
        ok, _ = self.fv.validar_telefono("3001234567")
        self.assertTrue(ok)

    def test_movil_con_prefijo_internacional(self):
        ok, _ = self.fv.validar_telefono("+573001234567")
        self.assertTrue(ok)

    def test_fijo_bogota(self):
        ok, _ = self.fv.validar_telefono("6011234567")
        self.assertTrue(ok)

    # ── Inválidos ─────────────────────────────────────────────────────────────

    def test_telefono_con_letras(self):
        ok, _ = self.fv.validar_telefono("300ABC4567")
        self.assertFalse(ok)

    def test_telefono_muy_corto(self):
        ok, _ = self.fv.validar_telefono("30012345")
        self.assertFalse(ok)

    def test_telefono_vacio(self):
        ok, _ = self.fv.validar_telefono("")
        self.assertFalse(ok)

    def test_telefono_empieza_en_dos(self):
        ok, _ = self.fv.validar_telefono("2001234567")
        self.assertFalse(ok)


class TestValidarCedula(unittest.TestCase):

    def setUp(self):
        self.fv = FormValidator()

    # ── Válidos ───────────────────────────────────────────────────────────────

    def test_cedula_8_digitos(self):
        ok, _ = self.fv.validar_cedula("12345678")
        self.assertTrue(ok)

    def test_cedula_10_digitos(self):
        ok, _ = self.fv.validar_cedula("1098765432")
        self.assertTrue(ok)

    def test_cedula_6_digitos(self):
        ok, _ = self.fv.validar_cedula("123456")
        self.assertTrue(ok)

    def test_cedula_con_puntos(self):
        ok, _ = self.fv.validar_cedula("1.098.765.432")
        self.assertTrue(ok)

    # ── Inválidos ─────────────────────────────────────────────────────────────

    def test_cedula_empieza_en_cero(self):
        ok, msg = self.fv.validar_cedula("0123456789")
        self.assertFalse(ok)
        self.assertIn("cero", msg.lower())

    def test_cedula_muy_corta(self):
        ok, _ = self.fv.validar_cedula("12345")
        self.assertFalse(ok)

    def test_cedula_demasiado_larga(self):
        ok, _ = self.fv.validar_cedula("12345678901")
        self.assertFalse(ok)

    def test_cedula_con_letras(self):
        ok, _ = self.fv.validar_cedula("1234AB7890")
        self.assertFalse(ok)

    def test_cedula_vacia(self):
        ok, _ = self.fv.validar_cedula("")
        self.assertFalse(ok)


class TestValidarFecha(unittest.TestCase):

    def setUp(self):
        self.fv = FormValidator()

    # ── Válidos ───────────────────────────────────────────────────────────────

    def test_fecha_slash_valida(self):
        ok, msg = self.fv.validar_fecha("15/06/1995")
        self.assertTrue(ok)
        self.assertIn("años", msg)

    def test_fecha_guion_valida(self):
        ok, _ = self.fv.validar_fecha("20-03-1988")
        self.assertTrue(ok)

    def test_fecha_mayor_de_edad_justa(self):
        import datetime
        hace_18 = datetime.date.today().replace(year=datetime.date.today().year - 18)
        valor = hace_18.strftime("%d/%m/%Y")
        ok, _ = self.fv.validar_fecha(valor)
        self.assertTrue(ok)

    # ── Inválidos ─────────────────────────────────────────────────────────────

    def test_fecha_formato_incorrecto(self):
        ok, _ = self.fv.validar_fecha("1995-6-15")
        self.assertFalse(ok)

    def test_fecha_futura(self):
        ok, msg = self.fv.validar_fecha("01/01/2099")
        self.assertFalse(ok)
        self.assertIn("futura", msg.lower())

    def test_fecha_menor_de_edad(self):
        import datetime
        hace_10 = datetime.date.today().replace(year=datetime.date.today().year - 10)
        valor = hace_10.strftime("%d/%m/%Y")
        ok, msg = self.fv.validar_fecha(valor)
        self.assertFalse(ok)
        self.assertIn("mayor de edad", msg.lower())

    def test_fecha_inexistente(self):
        ok, _ = self.fv.validar_fecha("31/02/1990")
        self.assertFalse(ok)

    def test_fecha_vacia(self):
        ok, _ = self.fv.validar_fecha("")
        self.assertFalse(ok)

    def test_fecha_año_muy_antiguo(self):
        ok, _ = self.fv.validar_fecha("01/01/1890")
        self.assertFalse(ok)


class TestValidarUsuario(unittest.TestCase):

    def setUp(self):
        self.fv = FormValidator()

    # ── Válidos ───────────────────────────────────────────────────────────────

    def test_usuario_simple(self):
        ok, _ = self.fv.validar_usuario("juanperez")
        self.assertTrue(ok)

    def test_usuario_con_punto(self):
        ok, _ = self.fv.validar_usuario("juan.perez")
        self.assertTrue(ok)

    def test_usuario_con_guion_bajo(self):
        ok, _ = self.fv.validar_usuario("juan_perez")
        self.assertTrue(ok)

    def test_usuario_con_numeros(self):
        ok, _ = self.fv.validar_usuario("user123")
        self.assertTrue(ok)

    # ── Inválidos ─────────────────────────────────────────────────────────────

    def test_usuario_muy_corto(self):
        ok, _ = self.fv.validar_usuario("abc")
        self.assertFalse(ok)

    def test_usuario_empieza_con_punto(self):
        ok, msg = self.fv.validar_usuario(".usuario")
        self.assertFalse(ok)

    def test_usuario_termina_con_guion_bajo(self):
        ok, _ = self.fv.validar_usuario("usuario_")
        self.assertFalse(ok)

    def test_usuario_dos_especiales_consecutivos(self):
        ok, msg = self.fv.validar_usuario("ju..an")
        self.assertFalse(ok)
        self.assertIn("consecutivos", msg.lower())

    def test_usuario_caracter_no_permitido(self):
        ok, _ = self.fv.validar_usuario("juan@perez")
        self.assertFalse(ok)

    def test_usuario_demasiado_largo(self):
        ok, _ = self.fv.validar_usuario("a" * 21)
        self.assertFalse(ok)


class TestValidarPlaca(unittest.TestCase):

    def setUp(self):
        self.fv = FormValidator()

    # ── Válidos ───────────────────────────────────────────────────────────────

    def test_placa_vehiculo(self):
        ok, _ = self.fv.validar_placa("ABC123")
        self.assertTrue(ok)

    def test_placa_moto(self):
        ok, _ = self.fv.validar_placa("XYZ12")
        self.assertTrue(ok)

    def test_placa_con_guion(self):
        ok, _ = self.fv.validar_placa("ABC-123")
        self.assertTrue(ok)

    def test_placa_vacia_es_valida(self):
        ok, _ = self.fv.validar_placa("")
        self.assertTrue(ok)

    # ── Inválidos ─────────────────────────────────────────────────────────────

    def test_placa_solo_letras(self):
        ok, _ = self.fv.validar_placa("ABCDEF")
        self.assertFalse(ok)

    def test_placa_solo_numeros(self):
        ok, _ = self.fv.validar_placa("123456")
        self.assertFalse(ok)

    def test_placa_demasiado_corta(self):
        ok, _ = self.fv.validar_placa("AB1")
        self.assertFalse(ok)

    def test_placa_demasiado_larga(self):
        ok, _ = self.fv.validar_placa("ABCD1234")
        self.assertFalse(ok)


class TestValidarFormularioCompleto(unittest.TestCase):

    def setUp(self):
        self.fv = FormValidator()

    def test_formulario_completamente_valido(self):
        datos = {
            'nombre':           'Juan Carlos Pérez',
            'correo':           'juan@empresa.com',
            'contrasena':       'Clave_123!',
            'telefono':         '3001234567',
            'cedula':           '12345678',
            'fecha_nacimiento': '15/06/1990',
            'usuario':          'juan.perez',
            'placa':            '',
        }
        resultado = self.fv.validar_formulario(datos)
        self.assertTrue(resultado['formulario_valido'])

    def test_formulario_con_errores(self):
        datos = {
            'nombre':           'J',
            'correo':           'no-es-correo',
            'contrasena':       '1234',
            'telefono':         '123',
            'cedula':           '0',
            'fecha_nacimiento': '99/99/9999',
            'usuario':          'ab',
            'placa':            '',
        }
        resultado = self.fv.validar_formulario(datos)
        self.assertFalse(resultado['formulario_valido'])
        self.assertFalse(resultado['nombre']['valido'])
        self.assertFalse(resultado['correo']['valido'])
        self.assertFalse(resultado['contrasena']['valido'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
