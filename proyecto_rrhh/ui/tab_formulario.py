"""
tab_formulario.py
=================
Pestaña B — Formulario interactivo de registro de candidatos/empleados.

Contexto: Sistema ValidaRH — Gestión de Recursos Humanos
Proyecto: Búsqueda y validación de patrones en textos y sistemas interactivos

Descripción:
    Implementa la interfaz gráfica del formulario de registro usando tkinter.
    Cada campo se valida en tiempo real mientras el usuario escribe, mostrando
    mensajes de retroalimentación inmediata (verde = válido, rojo = inválido).
    Al enviar, se ejecuta una validación completa antes de aceptar el registro.

Componentes:
    - CampoFormulario : widget reutilizable (label + entry + mensaje de estado)
    - TabFormulario   : frame principal que ensambla todos los campos

Autor: [Tu nombre]
Fecha: [Fecha]
Versión: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
from logic.validators.form_validator import FormValidator


# ─────────────────────────────────────────────────────────────────────────────
# Widget auxiliar: un campo completo con etiqueta, entrada y mensaje de estado
# ─────────────────────────────────────────────────────────────────────────────

class CampoFormulario(ttk.Frame):
    """
    Widget reutilizable que encapsula un campo del formulario.

    Contiene tres elementos apilados verticalmente:
        1. Etiqueta (label) con el nombre del campo
        2. Entry para la entrada del usuario
        3. Label de estado (verde si válido, rojo si inválido)

    Permite mostrar/ocultar el texto ingresado (útil para contraseñas)
    y expone métodos para obtener el valor y actualizar el estado visual.

    Args:
        parent     : widget padre (el frame del formulario)
        etiqueta   : texto de la etiqueta visible al usuario
        oculto     : True para campos de contraseña (muestra asteriscos)
        opcional   : True si el campo no es obligatorio
    """

    def __init__(self, parent, etiqueta: str,
                 oculto: bool = False, opcional: bool = False):
        super().__init__(parent)

        self.oculto = oculto
        self._ocultar = tk.BooleanVar(value=oculto)

        # ── Etiqueta del campo ────────────────────────────────────────────────
        texto_label = etiqueta + (' (opcional)' if opcional else ' *')
        ttk.Label(self, text=texto_label,
                  font=('Helvetica', 9, 'bold')).pack(anchor='w')

        # ── Frame para entry + botón mostrar/ocultar ──────────────────────────
        frame_entrada = ttk.Frame(self)
        frame_entrada.pack(fill='x')

        self.entrada = ttk.Entry(
            frame_entrada,
            show='●' if oculto else '',
            width=38
        )
        self.entrada.pack(side='left', fill='x', expand=True)

        # Botón para mostrar/ocultar contraseña
        if oculto:
            self.btn_ver = ttk.Button(
                frame_entrada,
                text='👁',
                width=3,
                command=self._toggle_visibilidad
            )
            self.btn_ver.pack(side='left', padx=(4, 0))

        # ── Label de estado (vacío hasta que el usuario escriba) ──────────────
        self.lbl_estado = ttk.Label(self, text='', font=('Helvetica', 8))
        self.lbl_estado.pack(anchor='w')

    def _toggle_visibilidad(self):
        """Alterna entre mostrar y ocultar el texto de la contraseña."""
        if self._ocultar.get():
            self.entrada.config(show='')
            self._ocultar.set(False)
        else:
            self.entrada.config(show='●')
            self._ocultar.set(True)

    def get(self) -> str:
        """Retorna el valor actual del campo."""
        return self.entrada.get()

    def set_estado(self, valido: bool, mensaje: str):
        """
        Actualiza el mensaje de estado del campo.

        Args:
            valido  : True muestra el mensaje en verde, False en rojo
            mensaje : texto descriptivo del resultado de la validación
        """
        color = '#2e7d32' if valido else '#c62828'
        icono = '✓' if valido else '✗'
        self.lbl_estado.config(
            text=f'{icono} {mensaje}',
            foreground=color
        )

    def limpiar_estado(self):
        """Borra el mensaje de estado (usado al resetear el formulario)."""
        self.lbl_estado.config(text='')

    def limpiar(self):
        """Borra el contenido del campo y su mensaje de estado."""
        self.entrada.delete(0, 'end')
        self.limpiar_estado()


# ─────────────────────────────────────────────────────────────────────────────
# Pestaña principal del formulario
# ─────────────────────────────────────────────────────────────────────────────

class TabFormulario(ttk.Frame):
    """
    Pestaña B del Notebook — Formulario de registro de candidatos.

    Construye el formulario completo con todos los campos requeridos,
    conecta cada campo a su validador correspondiente y gestiona
    el envío y reseteo del formulario.

    Campos del formulario:
        - Nombre completo     (obligatorio)
        - Correo electrónico  (obligatorio)
        - Contraseña          (obligatorio, oculto)
        - Teléfono            (obligatorio)
        - Cédula              (obligatorio)
        - Fecha de nacimiento (obligatorio)
        - Usuario del sistema (obligatorio)
        - Placa de vehículo   (opcional)
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.validator = FormValidator()
        self._construir_ui()
        self._conectar_validaciones()

    # ── Construcción de la interfaz ───────────────────────────────────────────

    def _construir_ui(self):
        """
        Construye todos los elementos visuales del formulario.

        Layout:
            - Título y subtítulo en la parte superior
            - Campos en dos columnas para aprovechar el espacio
            - Barra de progreso que indica campos completados
            - Botones Enviar y Limpiar en la parte inferior
        """

        # ── Encabezado ────────────────────────────────────────────────────────
        frame_header = ttk.Frame(self)
        frame_header.pack(fill='x', padx=20, pady=(16, 8))

        ttk.Label(
            frame_header,
            text='Registro de Candidato / Empleado',
            font=('Helvetica', 14, 'bold')
        ).pack(anchor='w')

        ttk.Label(
            frame_header,
            text='Complete todos los campos obligatorios (*) antes de enviar.',
            foreground='gray',
            font=('Helvetica', 9)
        ).pack(anchor='w')

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=20, pady=4)

        # ── Contenedor de campos en dos columnas ──────────────────────────────
        frame_campos = ttk.Frame(self)
        frame_campos.pack(fill='both', expand=True, padx=20, pady=8)

        columna_izq = ttk.Frame(frame_campos)
        columna_izq.pack(side='left', fill='both', expand=True, padx=(0, 10))

        columna_der = ttk.Frame(frame_campos)
        columna_der.pack(side='left', fill='both', expand=True, padx=(10, 0))

        # ── Instanciar campos ─────────────────────────────────────────────────
        # Columna izquierda
        self.campo_nombre = CampoFormulario(columna_izq, 'Nombre completo')
        self.campo_nombre.pack(fill='x', pady=6)

        self.campo_correo = CampoFormulario(columna_izq, 'Correo electrónico')
        self.campo_correo.pack(fill='x', pady=6)

        self.campo_contrasena = CampoFormulario(
            columna_izq, 'Contraseña', oculto=True)
        self.campo_contrasena.pack(fill='x', pady=6)

        self.campo_telefono = CampoFormulario(columna_izq, 'Teléfono')
        self.campo_telefono.pack(fill='x', pady=6)

        # Columna derecha
        self.campo_cedula = CampoFormulario(columna_der, 'Cédula de ciudadanía')
        self.campo_cedula.pack(fill='x', pady=6)

        self.campo_fecha = CampoFormulario(columna_der, 'Fecha de nacimiento')
        self.campo_fecha.pack(fill='x', pady=6)

        ttk.Label(
            columna_der,
            text='Formato: DD/MM/AAAA',
            foreground='gray',
            font=('Helvetica', 8)
        ).pack(anchor='w', pady=(0, 4))

        self.campo_usuario = CampoFormulario(columna_der, 'Usuario del sistema')
        self.campo_usuario.pack(fill='x', pady=6)

        self.campo_placa = CampoFormulario(
            columna_der, 'Placa de vehículo', opcional=True)
        self.campo_placa.pack(fill='x', pady=6)

        # ── Barra de progreso ─────────────────────────────────────────────────
        frame_progreso = ttk.Frame(self)
        frame_progreso.pack(fill='x', padx=20, pady=(4, 0))

        self.lbl_progreso = ttk.Label(
            frame_progreso,
            text='0 de 7 campos válidos',
            font=('Helvetica', 9),
            foreground='gray'
        )
        self.lbl_progreso.pack(anchor='w')

        self.barra_progreso = ttk.Progressbar(
            frame_progreso,
            maximum=7,
            value=0,
            mode='determinate'
        )
        self.barra_progreso.pack(fill='x', pady=(2, 8))

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=20, pady=4)

        # ── Botones ───────────────────────────────────────────────────────────
        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=12)

        self.btn_enviar = ttk.Button(
            frame_botones,
            text='Enviar registro',
            command=self._enviar,
            style='Accent.TButton'
        )
        self.btn_enviar.pack(side='left', padx=8)

        ttk.Button(
            frame_botones,
            text='Limpiar formulario',
            command=self._limpiar
        ).pack(side='left', padx=8)

    # ── Conexión de validaciones en tiempo real ───────────────────────────────

    def _conectar_validaciones(self):
        """
        Asocia cada campo a su función de validación mediante el evento
        <KeyRelease>. Esto dispara la validación cada vez que el usuario
        suelta una tecla, dando retroalimentación inmediata.
        """
        pares = [
            (self.campo_nombre,     self.validator.validar_nombre),
            (self.campo_correo,     self.validator.validar_correo),
            (self.campo_contrasena, self.validator.validar_contrasena),
            (self.campo_telefono,   self.validator.validar_telefono),
            (self.campo_cedula,     self.validator.validar_cedula),
            (self.campo_fecha,      self.validator.validar_fecha),
            (self.campo_usuario,    self.validator.validar_usuario),
            (self.campo_placa,      self.validator.validar_placa),
        ]

        for campo, funcion_validar in pares:
            # Closure para capturar campo y función correctamente
            def hacer_validador(c, f):
                def validar(event=None):
                    valor = c.get()
                    if valor:                        # solo valida si hay texto
                        valido, mensaje = f(valor)
                        c.set_estado(valido, mensaje)
                    else:
                        c.limpiar_estado()
                    self._actualizar_progreso()
                return validar

            campo.entrada.bind('<KeyRelease>', hacer_validador(campo, funcion_validar))

    # ── Lógica de envío ───────────────────────────────────────────────────────

    def _enviar(self):
        """
        Valida el formulario completo antes de aceptar el registro.

        Proceso:
            1. Recopila los valores de todos los campos
            2. Llama a FormValidator.validar_formulario()
            3. Si todo es válido → muestra confirmación
            4. Si hay errores → marca los campos inválidos y muestra resumen
        """
        datos = {
            'nombre':           self.campo_nombre.get(),
            'correo':           self.campo_correo.get(),
            'contrasena':       self.campo_contrasena.get(),
            'telefono':         self.campo_telefono.get(),
            'cedula':           self.campo_cedula.get(),
            'fecha_nacimiento': self.campo_fecha.get(),
            'usuario':          self.campo_usuario.get(),
            'placa':            self.campo_placa.get(),
        }

        resultado = self.validator.validar_formulario(datos)

        # Actualizar el estado visual de cada campo con el resultado
        campos_map = {
            'nombre':           self.campo_nombre,
            'correo':           self.campo_correo,
            'contrasena':       self.campo_contrasena,
            'telefono':         self.campo_telefono,
            'cedula':           self.campo_cedula,
            'fecha_nacimiento': self.campo_fecha,
            'usuario':          self.campo_usuario,
            'placa':            self.campo_placa,
        }

        for campo_key, campo_widget in campos_map.items():
            info = resultado[campo_key]
            campo_widget.set_estado(info['valido'], info['mensaje'])

        if resultado['formulario_valido']:
            messagebox.showinfo(
                'Registro exitoso',
                f"✓ El candidato '{datos['nombre']}' fue registrado correctamente.\n"
                f"Usuario asignado: {datos['usuario']}"
            )
            self._limpiar()
        else:
            errores = [
                k for k, v in resultado.items()
                if k != 'formulario_valido' and not v['valido']
            ]
            messagebox.showwarning(
                'Formulario incompleto',
                f"Corrija los siguientes campos antes de enviar:\n\n" +
                "\n".join(f"• {e.replace('_', ' ').capitalize()}"
                          for e in errores)
            )

    # ── Utilidades ────────────────────────────────────────────────────────────

    def _actualizar_progreso(self):
        """
        Recalcula cuántos campos obligatorios están válidos
        y actualiza la barra de progreso.

        Campos obligatorios considerados: 7 (excluye placa por ser opcional).
        """
        campos_obligatorios = [
            (self.campo_nombre,     self.validator.validar_nombre),
            (self.campo_correo,     self.validator.validar_correo),
            (self.campo_contrasena, self.validator.validar_contrasena),
            (self.campo_telefono,   self.validator.validar_telefono),
            (self.campo_cedula,     self.validator.validar_cedula),
            (self.campo_fecha,      self.validator.validar_fecha),
            (self.campo_usuario,    self.validator.validar_usuario),
        ]

        validos = sum(
            1 for campo, fn in campos_obligatorios
            if campo.get() and fn(campo.get())[0]
        )

        self.barra_progreso['value'] = validos
        self.lbl_progreso.config(
            text=f'{validos} de 7 campos válidos',
            foreground='#2e7d32' if validos == 7 else 'gray'
        )

    def _limpiar(self):
        """
        Resetea todos los campos del formulario a su estado inicial.
        Limpia tanto el contenido como los mensajes de estado.
        """
        for campo in [
            self.campo_nombre, self.campo_correo, self.campo_contrasena,
            self.campo_telefono, self.campo_cedula, self.campo_fecha,
            self.campo_usuario, self.campo_placa
        ]:
            campo.limpiar()

        self.barra_progreso['value'] = 0
        self.lbl_progreso.config(text='0 de 7 campos válidos', foreground='gray')