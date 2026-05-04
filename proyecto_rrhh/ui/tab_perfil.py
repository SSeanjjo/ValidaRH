"""
tab_perfil.py — Pestaña de gestión del perfil de usuario para ValidaRH.

Permite al usuario:
    - Ver datos de solo lectura (correo, cédula, rol, fecha de registro)
    - Editar campos permitidos: nombre, teléfono, nombre de usuario
    - Cambiar contraseña (requiere la contraseña actual)
    - Cerrar sesión mediante el callback on_logout
"""
import tkinter as tk
from tkinter import ttk, messagebox


class TabPerfil(ttk.Frame):

    def __init__(self, parent, usuario: dict, on_logout=None):
        super().__init__(parent)
        self._usuario   = usuario
        self._on_logout = on_logout
        self._construir_ui()

    # ── Construcción ──────────────────────────────────────────────────────────

    def _construir_ui(self):
        ttk.Label(self, text='Mi perfil',
                  font=('Helvetica', 13, 'bold')).pack(
                      anchor='w', padx=14, pady=(12, 4))
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=12, pady=4)

        contenedor = ttk.Frame(self)
        contenedor.pack(fill='both', expand=True, padx=20, pady=8)

        self._construir_datos_ro(contenedor)
        self._construir_datos_editables(contenedor)
        self._construir_cambio_pass(contenedor)
        self._construir_logout(contenedor)

    def _construir_datos_ro(self, parent):
        frm = ttk.LabelFrame(parent, text='Datos de la cuenta')
        frm.pack(fill='x', pady=(0, 12))

        campos = [
            ('Correo electrónico:', self._usuario.get('correo', '—')),
            ('Cédula:',             self._usuario.get('cedula', '—') or '—'),
            ('Rol:',                self._usuario.get('rol', '—').capitalize()),
            ('Miembro desde:',      self._usuario.get('fecha_registro', '—')),
        ]
        for i, (etiqueta, valor) in enumerate(campos):
            ttk.Label(frm, text=etiqueta,
                      font=('Helvetica', 9, 'bold')).grid(
                          row=i, column=0, sticky='w', padx=(12, 4), pady=4)
            ttk.Label(frm, text=valor,
                      foreground='#424242').grid(
                          row=i, column=1, sticky='w', padx=4, pady=4)

    def _construir_datos_editables(self, parent):
        frm = ttk.LabelFrame(parent, text='Editar perfil')
        frm.pack(fill='x', pady=(0, 12))

        campos = [
            ('Nombre completo:',    'ent_nombre',   self._usuario.get('nombre', '')),
            ('Teléfono:',           'ent_tel',       self._usuario.get('telefono', '') or ''),
            ('Nombre de usuario:',  'ent_usuario',   self._usuario.get('usuario', '') or ''),
        ]
        for i, (etiqueta, attr, valor) in enumerate(campos):
            ttk.Label(frm, text=etiqueta).grid(
                row=i, column=0, sticky='w', padx=(12, 4), pady=6)
            ent = ttk.Entry(frm, width=36)
            ent.insert(0, valor)
            ent.grid(row=i, column=1, sticky='ew', padx=(4, 12), pady=6)
            setattr(self, attr, ent)

        frm.columnconfigure(1, weight=1)

        self._lbl_ed = ttk.Label(frm, text='', font=('Helvetica', 8))
        self._lbl_ed.grid(row=len(campos), column=0, columnspan=2,
                          sticky='w', padx=14, pady=(0, 4))

        ttk.Button(frm, text='Guardar cambios',
                   command=self._guardar_perfil).grid(
                       row=len(campos) + 1, column=0, columnspan=2,
                       pady=(4, 12), ipadx=12, ipady=3)

    def _construir_cambio_pass(self, parent):
        frm = ttk.LabelFrame(parent, text='Cambiar contraseña')
        frm.pack(fill='x', pady=(0, 12))

        pass_campos = [
            ('Contraseña actual:',  'ent_pass_act'),
            ('Nueva contraseña:',   'ent_pass_nueva'),
            ('Confirmar nueva:',    'ent_pass_conf'),
        ]
        for i, (etiqueta, attr) in enumerate(pass_campos):
            ttk.Label(frm, text=etiqueta).grid(
                row=i, column=0, sticky='w', padx=(12, 4), pady=6)
            ent = ttk.Entry(frm, width=28, show='•')
            ent.grid(row=i, column=1, sticky='ew', padx=(4, 4), pady=6)
            btn_eye = ttk.Button(frm, text='👁', width=3)
            btn_eye.config(command=lambda e=ent, b=btn_eye: self._toggle_pass(e, b))
            btn_eye.grid(row=i, column=2, padx=(0, 12), pady=6)
            setattr(self, attr, ent)

        frm.columnconfigure(1, weight=1)

        self._lbl_pass = ttk.Label(frm, text='', font=('Helvetica', 8))
        self._lbl_pass.grid(row=len(pass_campos), column=0, columnspan=3,
                            sticky='w', padx=14, pady=(0, 4))

        ttk.Button(frm, text='Cambiar contraseña',
                   command=self._cambiar_contrasena).grid(
                       row=len(pass_campos) + 1, column=0, columnspan=3,
                       pady=(4, 12), ipadx=12, ipady=3)

    def _construir_logout(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill='x', pady=(4, 0))
        ttk.Separator(frm, orient='horizontal').pack(fill='x', pady=8)
        ttk.Button(frm, text='⏻  Cerrar sesión',
                   command=self._cerrar_sesion).pack(anchor='e',
                                                     ipadx=8, ipady=4)

    # ── Lógica ────────────────────────────────────────────────────────────────

    @staticmethod
    def _toggle_pass(entry: ttk.Entry, btn: ttk.Button) -> None:
        if entry.cget('show') == '•':
            entry.config(show='')
            btn.config(text='🙈')
        else:
            entry.config(show='•')
            btn.config(text='👁')

    def _guardar_perfil(self):
        from db.repository import UsuarioRepo
        nombre  = self.ent_nombre.get().strip()
        tel     = self.ent_tel.get().strip()
        usuario = self.ent_usuario.get().strip()

        if not nombre:
            self._lbl_ed.config(text='✗ El nombre no puede estar vacío.',
                                 foreground='#c62828')
            return

        ok, msg = UsuarioRepo.actualizar_perfil(
            self._usuario['id'], nombre, tel, usuario)

        if ok:
            self._usuario['nombre']   = nombre
            self._usuario['telefono'] = tel
            self._usuario['usuario']  = usuario
            self._lbl_ed.config(text=f'✓ {msg}', foreground='#2e7d32')
        else:
            self._lbl_ed.config(text=f'✗ {msg}', foreground='#c62828')

    def _cambiar_contrasena(self):
        from db.repository import UsuarioRepo
        actual = self.ent_pass_act.get()
        nueva  = self.ent_pass_nueva.get()
        conf   = self.ent_pass_conf.get()

        if not actual or not nueva:
            self._lbl_pass.config(text='✗ Complete todos los campos.',
                                   foreground='#c62828')
            return
        if nueva != conf:
            self._lbl_pass.config(text='✗ Las contraseñas nuevas no coinciden.',
                                   foreground='#c62828')
            return
        if len(nueva) < 6:
            self._lbl_pass.config(
                text='✗ La nueva contraseña debe tener al menos 6 caracteres.',
                foreground='#c62828')
            return

        ok, msg = UsuarioRepo.cambiar_contrasena(
            self._usuario['id'], actual, nueva)

        if ok:
            self._lbl_pass.config(text=f'✓ {msg}', foreground='#2e7d32')
            self.ent_pass_act.delete(0, 'end')
            self.ent_pass_nueva.delete(0, 'end')
            self.ent_pass_conf.delete(0, 'end')
        else:
            self._lbl_pass.config(text=f'✗ {msg}', foreground='#c62828')

    def _cerrar_sesion(self):
        if messagebox.askokcancel('Cerrar sesión',
                                  '¿Desea cerrar la sesión actual?'):
            if self._on_logout:
                self._on_logout()
