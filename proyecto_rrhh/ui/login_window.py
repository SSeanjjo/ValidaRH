"""
login_window.py — Ventana de inicio de sesión y registro para ValidaRH.

Flujo:
    1. Usuario ingresa correo + contraseña → Login
    2. Si no tiene cuenta → formulario de registro con todos los campos
    3. Al registrarse → se envía código al correo (o se muestra en diálogo)
    4. Usuario ingresa código → cuenta verificada → puede ingresar
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import datetime
import json
import pathlib

# Archivo donde se guardan los correos usados recientemente
_RECIENTES_PATH = pathlib.Path(__file__).parent.parent / 'data' / 'login_recientes.json'


def _cargar_recientes() -> list:
    try:
        if _RECIENTES_PATH.exists():
            return json.loads(_RECIENTES_PATH.read_text(encoding='utf-8'))
    except Exception:
        pass
    return []


def _guardar_reciente(correo: str) -> None:
    recientes = _cargar_recientes()
    if correo in recientes:
        recientes.remove(correo)
    recientes.insert(0, correo)        # El más reciente primero
    recientes = recientes[:10]         # Máximo 10 sugerencias
    try:
        _RECIENTES_PATH.parent.mkdir(parents=True, exist_ok=True)
        _RECIENTES_PATH.write_text(
            json.dumps(recientes, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    except Exception:
        pass


def _generar_codigo(n: int = 6) -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(n))


def _enviar_codigo(correo: str, codigo: str) -> tuple:
    """Intenta enviar el código por SMTP. Retorna (True,'') o (False, error)."""
    from config import EMAIL_ENABLED, EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS
    if not EMAIL_ENABLED:
        return False, 'Email no configurado'
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To']   = correo
        msg['Subject'] = 'ValidaRH — Código de verificación'
        cuerpo = (
            f"Bienvenido a ValidaRH.\n\n"
            f"Su código de verificación es: {codigo}\n\n"
            f"Si no solicitó este código, ignore este mensaje."
        )
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10) as s:
            s.starttls()
            s.login(EMAIL_USER, EMAIL_PASS)
            s.send_message(msg)
        return True, ''
    except Exception as e:
        return False, str(e)


class LoginWindow(tk.Toplevel):
    """
    Ventana modal de autenticación.
    Tras login exitoso, self._usuario contiene los datos del usuario.
    Se accede con get_usuario().
    """

    ANCHO = 480
    ALTO  = 620

    def __init__(self, parent):
        super().__init__(parent)
        self._usuario = None
        self._construir_ui()
        self._centrar()
        self.grab_set()
        self.focus_force()
        self.protocol('WM_DELETE_WINDOW', self._cancelar)

    def get_usuario(self) -> dict | None:
        return self._usuario

    # ── Construcción ─────────────────────────────────────────────────────────

    def _construir_ui(self):
        self.title('ValidaRH — Acceso al sistema')
        self.resizable(False, False)
        self.configure(bg='#f5f5f5')

        # Cabecera azul
        cab = tk.Frame(self, bg='#1565c0', height=60)
        cab.pack(fill='x')
        cab.pack_propagate(False)
        tk.Label(cab, text='  ValidaRH', font=('Helvetica', 16, 'bold'),
                 bg='#1565c0', fg='white').pack(side='left', padx=8, pady=12)
        tk.Label(cab, text='Sistema de Gestión de RRHH',
                 font=('Helvetica', 9), bg='#1565c0', fg='#bbdefb').pack(
                     side='left', padx=4, pady=(20, 0))

        # Notebook login / registro
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill='both', expand=True, padx=16, pady=12)

        self._frame_login = ttk.Frame(self._nb)
        self._frame_reg   = ttk.Frame(self._nb)

        self._nb.add(self._frame_login, text='  Iniciar sesión  ')
        self._nb.add(self._frame_reg,   text='  Registrarse  ')

        self._construir_login(self._frame_login)
        self._construir_registro(self._frame_reg)

        # Al volver a "Iniciar sesión", copiar el correo ya escrito en Registro
        self._nb.bind('<<NotebookTabChanged>>', self._al_cambiar_tab)

        # Barra de estado
        self.lbl_estado = ttk.Label(self, text='', foreground='gray',
                                    font=('Helvetica', 8))
        self.lbl_estado.pack(pady=(0, 8))

    # ── Panel Login ───────────────────────────────────────────────────────────

    # ── Utilidad: alternar visibilidad de contraseña ──────────────────────────

    @staticmethod
    def _toggle_pass(entry: ttk.Entry, btn: ttk.Button) -> None:
        """Alterna entre mostrar y ocultar el texto de una entrada de contraseña."""
        if entry.cget('show') == '•':
            entry.config(show='')
            btn.config(text='🙈')
        else:
            entry.config(show='•')
            btn.config(text='👁')

    def _construir_login(self, parent):
        frm = ttk.LabelFrame(parent, text='Credenciales de acceso')
        frm.pack(fill='both', expand=True, padx=16, pady=16)

        ttk.Label(frm, text='Correo electrónico:').grid(
            row=0, column=0, columnspan=2, sticky='w', padx=12, pady=(16, 4))
        self._recientes = _cargar_recientes()
        self.ent_login_correo = ttk.Combobox(frm, width=30, values=self._recientes)
        self.ent_login_correo.grid(row=1, column=0, columnspan=2,
                                   padx=12, sticky='ew')
        self.ent_login_correo.bind('<KeyRelease>', self._filtrar_correos)

        ttk.Label(frm, text='Contraseña:').grid(
            row=2, column=0, columnspan=2, sticky='w', padx=12, pady=(12, 4))

        # Entry + botón de mostrar/ocultar en la misma fila
        self.ent_login_pass = ttk.Entry(frm, width=28, show='•')
        self.ent_login_pass.grid(row=3, column=0, padx=(12, 2), sticky='ew')
        btn_eye = ttk.Button(frm, text='👁', width=3)
        btn_eye.config(command=lambda: self._toggle_pass(
            self.ent_login_pass, btn_eye))
        btn_eye.grid(row=3, column=1, padx=(0, 12))

        frm.columnconfigure(0, weight=1)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text='Ingresar',
                   command=self._hacer_login).pack(ipadx=16, ipady=4)

        self.ent_login_correo.bind('<Return>', lambda e: self.ent_login_pass.focus())
        self.ent_login_pass.bind('<Return>', lambda e: self._hacer_login())

    def _hacer_login(self):
        from db.repository import UsuarioRepo
        correo = self.ent_login_correo.get().strip()
        passwd = self.ent_login_pass.get()

        if not correo or not passwd:
            self._set_estado('Complete todos los campos.', error=True)
            return

        cuentas = UsuarioRepo.verificar_credenciales_multi(correo, passwd)
        if not cuentas:
            self._set_estado('Correo o contraseña incorrectos.', error=True)
            return

        verificadas = [c for c in cuentas if c['verificado']]

        if not verificadas:
            self._set_estado('Cuenta sin verificar. Revise su correo.', error=True)
            self._solicitar_verificacion(correo)
            return

        if len(verificadas) == 1:
            self._usuario = verificadas[0]
            _guardar_reciente(correo)
            self._set_estado(f"Bienvenido, {verificadas[0]['nombre'].split()[0]}.")
            self.after(400, self.destroy)
        else:
            # El correo tiene cuentas en ambos roles — preguntar cuál usar
            self._seleccionar_rol(verificadas, correo)

    def _seleccionar_rol(self, cuentas: list, correo: str = ''):
        """Diálogo para elegir con qué rol ingresar cuando hay dos cuentas."""
        dialogo = tk.Toplevel(self)
        dialogo.title('Seleccionar rol')
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.configure(bg='#f5f5f5')

        ttk.Label(dialogo,
                  text='Tienes cuenta con ambos roles.\n¿Con cuál deseas ingresar?',
                  font=('Helvetica', 10), justify='center').pack(
                      padx=28, pady=(20, 12))

        iconos = {'reclutador': '📋  Reclutador', 'postulante': '🎯  Postulante'}
        for cuenta in cuentas:
            texto = iconos.get(cuenta['rol'], cuenta['rol'].capitalize())
            ttk.Button(dialogo, text=texto,
                       command=lambda c=cuenta, e=correo: self._confirmar_rol(
                           c, dialogo, e)).pack(pady=4, ipadx=24, ipady=6)

        ttk.Button(dialogo, text='Cancelar',
                   command=dialogo.destroy).pack(pady=(8, 16))

        dialogo.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width()  - dialogo.winfo_width())  // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialogo.winfo_height()) // 2
        dialogo.geometry(f'+{x}+{y}')

    def _confirmar_rol(self, cuenta: dict, dialogo: tk.Toplevel, correo: str = ''):
        dialogo.destroy()
        self._usuario = cuenta
        if correo:
            _guardar_reciente(correo)
        self._set_estado(f"Bienvenido, {cuenta['nombre'].split()[0]}.")
        self.after(400, self.destroy)

    def _al_cambiar_tab(self, _event=None):
        """Si el usuario vuelve a 'Iniciar sesión', copia el correo del registro."""
        if self._nb.index('current') == 0:
            correo_reg = getattr(self, 'ent_reg_correo', None)
            if correo_reg and correo_reg.get().strip():
                self.ent_login_correo.delete(0, 'end')
                self.ent_login_correo.insert(0, correo_reg.get().strip())
                self._filtrar_correos()

    def _filtrar_correos(self, _event=None):
        """Filtra las sugerencias del combobox según lo que el usuario esté escribiendo."""
        typed = self.ent_login_correo.get().strip().lower()
        if typed:
            filtrados = [r for r in self._recientes if typed in r.lower()]
        else:
            filtrados = self._recientes
        self.ent_login_correo['values'] = filtrados

    # ── Panel Registro ────────────────────────────────────────────────────────

    def _construir_registro(self, parent):
        # Scrollbar debe empacarse ANTES que el canvas para reservar su espacio
        sb = ttk.Scrollbar(parent, orient='vertical')
        canvas = tk.Canvas(parent, bg='#f5f5f5', highlightthickness=0,
                           yscrollcommand=sb.set)
        sb.configure(command=canvas.yview)
        sb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        inner = ttk.Frame(canvas)
        win_id = canvas.create_window((0, 0), window=inner, anchor='nw')

        # inner.Configure actualiza el scrollregion cuando crece el contenido
        inner.bind('<Configure>',
                   lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        # canvas.Configure actualiza el ancho del frame interno cuando cambia el canvas
        canvas.bind('<Configure>',
                    lambda e: canvas.itemconfig(win_id, width=e.width))

        # Rol
        frm_rol = ttk.LabelFrame(inner, text='Tipo de cuenta')
        frm_rol.pack(fill='x', padx=12, pady=(12, 4))
        self._var_rol = tk.StringVar(value='postulante')
        ttk.Radiobutton(frm_rol, text='Postulante (candidato)',
                        variable=self._var_rol, value='postulante').pack(
                            side='left', padx=16, pady=6)
        ttk.Radiobutton(frm_rol, text='Reclutador (empresa)',
                        variable=self._var_rol, value='reclutador').pack(
                            side='left', padx=8, pady=6)

        frm = ttk.LabelFrame(inner, text='Datos personales')
        frm.pack(fill='x', padx=12, pady=4)

        campos_config = [
            ('Nombre completo *',      'ent_reg_nombre',      False),
            ('Correo electrónico *',   'ent_reg_correo',      False),
            ('Contraseña *',           'ent_reg_pass',        True),
            ('Confirmar contraseña *', 'ent_reg_pass2',       True),
            ('Cédula *',               'ent_reg_cedula',      False),
            ('Teléfono *',             'ent_reg_tel',         False),
            ('Nombre de usuario *',    'ent_reg_usuario',     False),
            ('Fecha de nacimiento *',  'ent_reg_fecha',       False),
        ]

        self._reg_entries   = {}
        self._reg_labels    = {}
        self._campos_validos = {}  # {attr: bool} para la barra de progreso

        # Campos obligatorios para el progreso (excluye confirmar contraseña)
        self._CAMPOS_REQ = ['ent_reg_nombre', 'ent_reg_correo', 'ent_reg_pass',
                            'ent_reg_cedula', 'ent_reg_tel',
                            'ent_reg_usuario', 'ent_reg_fecha']

        # 3 filas por campo: etiqueta / entry (+toggle si es pass) / mensaje
        for i, (label, attr, es_pass) in enumerate(campos_config):
            ttk.Label(frm, text=label).grid(
                row=i*3, column=0, columnspan=2,
                sticky='w', padx=12, pady=(8, 1))

            ent = ttk.Entry(frm, width=38, show='•' if es_pass else '')
            ent.grid(row=i*3+1, column=0, padx=(12, 2), sticky='ew')

            if es_pass:
                btn_e = ttk.Button(frm, text='👁', width=3)
                btn_e.config(command=lambda e=ent, b=btn_e: self._toggle_pass(e, b))
                btn_e.grid(row=i*3+1, column=1, padx=(0, 12))
            else:
                ttk.Label(frm, text='').grid(row=i*3+1, column=1)

            lbl_v = ttk.Label(frm, text='', font=('Helvetica', 8), wraplength=360)
            lbl_v.grid(row=i*3+2, column=0, columnspan=2,
                       sticky='w', padx=14, pady=(1, 0))

            setattr(self, attr, ent)
            self._reg_entries[attr] = ent
            self._reg_labels[attr]  = lbl_v
            ent.bind('<FocusOut>', lambda e, a=attr: self._validar_campo_reg(a))

        ttk.Label(frm, text='Formato fecha: DD/MM/AAAA', foreground='gray',
                  font=('Helvetica', 8)).grid(
                      row=len(campos_config)*3, column=0, columnspan=2,
                      sticky='w', padx=14, pady=(0, 4))
        frm.columnconfigure(0, weight=1)

        # ── Barra de progreso ─────────────────────────────────────────────────
        frm_prog = ttk.LabelFrame(inner, text='Progreso del formulario')
        frm_prog.pack(fill='x', padx=12, pady=(8, 4))

        self._prog_reg = ttk.Progressbar(
            frm_prog, maximum=len(self._CAMPOS_REQ),
            length=400, mode='determinate')
        self._prog_reg.pack(padx=8, pady=(6, 2), fill='x')

        self._lbl_prog = ttk.Label(
            frm_prog,
            text=f'0 / {len(self._CAMPOS_REQ)} campos válidos',
            font=('Helvetica', 8))
        self._lbl_prog.pack(anchor='w', padx=10, pady=(0, 6))

        ttk.Button(inner, text='Crear cuenta',
                   command=self._hacer_registro).pack(
                       pady=16, ipadx=20, ipady=4)

    def _validar_campo_reg(self, attr: str) -> bool:
        from logic.validators.form_validator import FormValidator
        fv = FormValidator()
        mapa = {
            'ent_reg_nombre':  fv.validar_nombre,
            'ent_reg_correo':  fv.validar_correo,
            'ent_reg_pass':    fv.validar_contrasena,
            'ent_reg_cedula':  fv.validar_cedula,
            'ent_reg_tel':     fv.validar_telefono,
            'ent_reg_usuario': fv.validar_usuario,
            'ent_reg_fecha':   fv.validar_fecha,
        }
        if attr not in mapa:
            return True
        valor = getattr(self, attr).get()
        valido, msg = mapa[attr](valor)
        lbl = self._reg_labels.get(attr)
        if lbl:
            texto = f"✓ {msg}" if valido else f"✗ {msg}"
            lbl.config(text=texto,
                       foreground='#2e7d32' if valido else '#c62828')
        # Actualizar barra de progreso
        if attr in self._CAMPOS_REQ:
            self._campos_validos[attr] = valido
            n_validos = sum(1 for v in self._campos_validos.values() if v)
            self._prog_reg['value'] = n_validos
            total = len(self._CAMPOS_REQ)
            self._lbl_prog.config(text=f'{n_validos} / {total} campos válidos')
        return valido

    def _hacer_registro(self):
        from db.repository import UsuarioRepo
        from logic.validators.form_validator import FormValidator

        # Validar campos básicos
        todos_ok = True
        for attr in ['ent_reg_nombre', 'ent_reg_correo', 'ent_reg_pass',
                     'ent_reg_cedula', 'ent_reg_tel', 'ent_reg_usuario',
                     'ent_reg_fecha']:
            if not self._validar_campo_reg(attr):
                todos_ok = False

        if not todos_ok:
            self._set_estado('Corrija los campos marcados en rojo.', error=True)
            return

        if self.ent_reg_pass.get() != self.ent_reg_pass2.get():
            self._set_estado('Las contraseñas no coinciden.', error=True)
            return

        codigo = _generar_codigo(6)
        exito_mail, err = _enviar_codigo(self.ent_reg_correo.get().strip(), codigo)

        ok, msg = UsuarioRepo.crear(
            nombre          = self.ent_reg_nombre.get().strip(),
            correo          = self.ent_reg_correo.get().strip(),
            contrasena      = self.ent_reg_pass.get(),
            rol             = self._var_rol.get(),
            cedula          = self.ent_reg_cedula.get().strip(),
            telefono        = self.ent_reg_tel.get().strip(),
            usuario         = self.ent_reg_usuario.get().strip(),
            fecha_nacimiento= self.ent_reg_fecha.get().strip(),
            codigo          = codigo,
        )

        if not ok:
            self._set_estado(msg, error=True)
            return

        # Si el correo no se pudo enviar, pasar el código directamente al diálogo
        codigo_local = codigo if not exito_mail else None
        self._solicitar_verificacion(self.ent_reg_correo.get().strip(),
                                     codigo_local=codigo_local)

    # ── Verificación ──────────────────────────────────────────────────────────

    def _solicitar_verificacion(self, correo: str, codigo_local: str = None):
        from db.repository import UsuarioRepo
        dialogo = tk.Toplevel(self)
        dialogo.title('Verificación de correo')
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.configure(bg='#f5f5f5')

        if codigo_local:
            ttk.Label(dialogo,
                      text='No se pudo enviar el correo. Tu código es:',
                      font=('Helvetica', 9), foreground='gray').pack(
                          padx=24, pady=(20, 4))
            ttk.Label(dialogo, text=codigo_local,
                      font=('Courier', 26, 'bold'),
                      foreground='#1565c0').pack(padx=24, pady=(0, 4))
            ttk.Label(dialogo, text='(ya está llenado abajo — solo haz clic en Verificar)',
                      font=('Helvetica', 8), foreground='gray').pack(padx=24, pady=(0, 8))
        else:
            ttk.Label(dialogo,
                      text='Ingrese el código de 6 dígitos enviado a:',
                      font=('Helvetica', 9)).pack(padx=24, pady=(20, 4))
            ttk.Label(dialogo, text=correo,
                      font=('Helvetica', 9, 'bold'),
                      foreground='#1565c0').pack(padx=24, pady=(0, 12))

        ent_cod = ttk.Entry(dialogo, width=14,
                            font=('Courier', 16), justify='center')
        ent_cod.pack(padx=24, pady=4)
        if codigo_local:
            ent_cod.insert(0, codigo_local)   # Pre-llenado, solo confirmar
        ent_cod.focus()

        lbl_err = ttk.Label(dialogo, text='', foreground='#c62828',
                            font=('Helvetica', 8))
        lbl_err.pack()

        def _verificar():
            u = UsuarioRepo.buscar_por_correo(correo)
            if not u:
                lbl_err.config(text='Usuario no encontrado.')
                return
            if ent_cod.get().strip() == u['codigo_verificacion']:
                UsuarioRepo.marcar_verificado(correo)
                dialogo.destroy()
                messagebox.showinfo('Verificado',
                                    'Cuenta verificada correctamente.\n'
                                    'Ya puede iniciar sesión.')
                self._nb.select(0)
                self.ent_login_correo.delete(0, 'end')
                self.ent_login_correo.insert(0, correo)
            else:
                lbl_err.config(text='Código incorrecto. Inténtelo de nuevo.')

        ttk.Button(dialogo, text='Verificar', command=_verificar).pack(
            pady=16, ipadx=12, ipady=4)
        ent_cod.bind('<Return>', lambda e: _verificar())

        # Centrar sobre el login
        dialogo.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialogo.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialogo.winfo_height()) // 2
        dialogo.geometry(f'+{x}+{y}')

    # ── Utilidades ────────────────────────────────────────────────────────────

    def _set_estado(self, msg: str, error: bool = False):
        self.lbl_estado.config(text=msg,
                               foreground='#c62828' if error else '#2e7d32')

    def _cancelar(self):
        self._usuario = None
        self.destroy()

    def _centrar(self):
        self.update_idletasks()
        w, h = self.ANCHO, self.ALTO
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')
