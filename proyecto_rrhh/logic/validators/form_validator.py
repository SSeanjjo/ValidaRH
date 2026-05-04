"""
form_validator.py — Validación de campos de formulario con autómatas manuales.
Sin uso de la librería 're'.
"""
from logic.validators.pattern_matcher import PatternMatcher


class FormValidator:
    """
    Capa entre la UI y PatternMatcher.
    Cada método retorna (bool, str): (válido, mensaje).
    """

    def __init__(self):
        self._matcher = PatternMatcher()

    def validar_nombre(self, valor: str) -> tuple:
        valor = valor.strip()
        if len(valor) < 5:
            return False, "El nombre debe tener al menos 5 caracteres."
        if len(valor) > 80:
            return False, "El nombre no puede superar los 80 caracteres."
        letras_validas = set('áéíóúÁÉÍÓÚñÑüÜ')
        for c in valor:
            if not (self._matcher._is_alpha(c) or c == ' ' or c in letras_validas):
                return False, f"Carácter no permitido: '{c}'. Solo letras y espacios."
        palabras = [p for p in valor.split(' ') if p]
        if len(palabras) < 2:
            return False, "Ingrese al menos nombre y apellido."
        for palabra in palabras:
            if len(palabra) < 2:
                return False, f"'{palabra}' es muy corto. Cada nombre debe tener mínimo 2 letras."
        return True, "Nombre válido."

    def validar_correo(self, valor: str) -> tuple:
        valor = valor.strip()
        if not valor:
            return False, "El correo no puede estar vacío."
        if '@' not in valor:
            return False, "El correo debe contener '@'."
        if valor.count('@') > 1:
            return False, "El correo no puede tener más de un '@'."
        if '.' not in valor.split('@')[-1]:
            return False, "El dominio debe contener al menos un punto."
        if self._matcher.es_correo(valor):
            return True, "Correo válido."
        return False, "Formato de correo inválido. Ejemplo: usuario@empresa.com"

    def validar_contrasena(self, valor: str) -> tuple:
        especiales = set('!@#$%&*_')
        tiene_longitud  = len(valor) >= 8
        tiene_mayuscula = False
        tiene_minuscula = False
        tiene_digito    = False
        tiene_especial  = False

        for c in valor:
            if c.isupper():
                tiene_mayuscula = True
            elif c.islower():
                tiene_minuscula = True
            elif self._matcher._is_digit(c):
                tiene_digito = True
            elif c in especiales:
                tiene_especial = True

        faltantes = []
        if not tiene_longitud:  faltantes.append("mínimo 8 caracteres")
        if not tiene_mayuscula: faltantes.append("una mayúscula")
        if not tiene_minuscula: faltantes.append("una minúscula")
        if not tiene_digito:    faltantes.append("un número")
        if not tiene_especial:  faltantes.append("un carácter especial (!@#$%&*_)")

        if not faltantes:
            return True, "Contraseña segura."
        return False, "Falta: " + ", ".join(faltantes) + "."

    def validar_telefono(self, valor: str) -> tuple:
        valor = valor.strip()
        if not valor:
            return False, "El teléfono no puede estar vacío."
        limpio = valor.replace(' ', '').replace('-', '').replace('+', '')
        if not all(self._matcher._is_digit(c) for c in limpio):
            return False, "El teléfono solo debe contener dígitos."
        if self._matcher.es_telefono_co(valor):
            return True, "Teléfono válido."
        return False, "Formato inválido. Use 10 dígitos (ej: 3001234567 o +573001234567)."

    def validar_cedula(self, valor: str) -> tuple:
        valor = valor.strip()
        if not valor:
            return False, "La cédula no puede estar vacía."
        limpio = valor.replace('.', '').replace(' ', '')
        if not all(self._matcher._is_digit(c) for c in limpio):
            return False, "La cédula solo debe contener números."
        if limpio.startswith('0'):
            return False, "La cédula no puede iniciar con cero."
        if len(limpio) < 6:
            return False, "La cédula debe tener al menos 6 dígitos."
        if len(limpio) > 10:
            return False, "La cédula no puede superar los 10 dígitos."
        return True, "Cédula válida."

    def validar_fecha(self, valor: str) -> tuple:
        import datetime
        valor = valor.strip()
        if not valor:
            return False, "La fecha no puede estar vacía."
        if not self._matcher.es_fecha(valor):
            return False, "Formato inválido. Use DD/MM/AAAA o DD-MM-AAAA."
        sep = '/' if '/' in valor else '-'
        d, m, a = [int(x) for x in valor.split(sep)]
        hoy = datetime.date.today()
        try:
            fecha = datetime.date(a, m, d)
        except ValueError:
            return False, "La fecha no existe en el calendario."
        if fecha > hoy:
            return False, "La fecha de nacimiento no puede ser futura."
        edad = (hoy - fecha).days // 365
        if edad < 18:
            return False, f"El candidato debe ser mayor de edad (edad detectada: {edad} años)."
        if edad > 100:
            return False, "Verifique el año ingresado."
        return True, f"Fecha válida. Edad: {edad} años."

    def validar_usuario(self, valor: str) -> tuple:
        valor = valor.strip()
        if len(valor) < 4:
            return False, "El usuario debe tener al menos 4 caracteres."
        if len(valor) > 20:
            return False, "El usuario no puede superar los 20 caracteres."
        permitidos = set('._')
        if valor[0] in permitidos or valor[-1] in permitidos:
            return False, "El usuario no puede iniciar ni terminar con '.' o '_'."
        estado = 1
        for c in valor:
            if self._matcher._is_alnum(c):
                estado = 1
            elif c in permitidos:
                if estado == 2:
                    return False, "No se permiten dos caracteres especiales consecutivos."
                estado = 2
            else:
                return False, f"Carácter no permitido: '{c}'. Use letras, números, '.' o '_'."
        return True, "Usuario válido."

    def validar_placa(self, valor: str) -> tuple:
        valor = valor.strip()
        if not valor:
            return True, "Campo opcional — sin placa registrada."
        if self._matcher.es_placa_co(valor):
            return True, "Placa válida."
        return False, "Formato inválido. Ejemplos: ABC123 (vehículo) o ABC12 (moto)."

    def validar_formulario(self, datos: dict) -> dict:
        validaciones = {
            'nombre':           self.validar_nombre,
            'correo':           self.validar_correo,
            'contrasena':       self.validar_contrasena,
            'telefono':         self.validar_telefono,
            'cedula':           self.validar_cedula,
            'fecha_nacimiento': self.validar_fecha,
            'usuario':          self.validar_usuario,
            'placa':            self.validar_placa,
        }
        resultado = {}
        todo_valido = True
        for campo, funcion in validaciones.items():
            valor = datos.get(campo, '')
            valido, mensaje = funcion(valor)
            resultado[campo] = {'valido': valido, 'mensaje': mensaje}
            if not valido:
                todo_valido = False
        resultado['formulario_valido'] = todo_valido
        return resultado
