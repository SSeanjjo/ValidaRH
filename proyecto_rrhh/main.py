"""
main.py — Punto de entrada del sistema ValidaRH v2.0.

Flujo de inicio:
    1. Inicializar la base de datos SQLite (crea tablas si no existen)
    2. Mostrar ventana de login/registro (modal)
    3. Si el usuario cancela → cerrar aplicación
    4. Si el login es exitoso → construir la interfaz principal con las
       pestañas correspondientes al rol (reclutador / postulante)

Pestañas por rol:
    Reclutador : Panel Reclutador | Analizador | Formulario | Historial
    Postulante : Panel Postulante | Analizador | Formulario | Historial
"""

import sys
import pathlib
import tkinter as tk
from tkinter import ttk, messagebox

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, str(pathlib.Path(__file__).parent))

APP_TITULO    = 'ValidaRH — Sistema de Gestión de RRHH v2.0'
APP_ANCHO     = 1100
APP_ALTO      = 720
APP_MIN_ANCHO = 900
APP_MIN_ALTO  = 600


class ValidaRH(tk.Tk):

    def __init__(self):
        super().__init__()
        self._usuario = None
        self.withdraw()          # Ocultar hasta que el login sea exitoso

        self._init_bd()
        if not self._mostrar_login():
            self.destroy()
            return

        self._configurar_ventana()
        self._aplicar_tema()
        self._construir_barra_superior()
        self._construir_notebook()
        self._construir_barra_inferior()
        self._centrar_ventana()
        self.deiconify()

    # ── Inicialización ────────────────────────────────────────────────────────

    @staticmethod
    def _init_bd():
        from db.database import inicializar_bd
        inicializar_bd()

    def _mostrar_login(self) -> bool:
        from ui.login_window import LoginWindow
        login = LoginWindow(self)
        self.wait_window(login)
        self._usuario = login.get_usuario()
        return self._usuario is not None

    # ── Ventana ───────────────────────────────────────────────────────────────

    def _configurar_ventana(self):
        rol = self._usuario.get('rol', '')
        self.title(f"{APP_TITULO}  —  {self._usuario['nombre']}  [{rol}]")
        self.geometry(f'{APP_ANCHO}x{APP_ALTO}')
        self.minsize(APP_MIN_ANCHO, APP_MIN_ALTO)
        self.resizable(True, True)
        self.protocol('WM_DELETE_WINDOW', self._confirmar_salida)

    def _aplicar_tema(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg='#f5f5f5')

        self.style.configure('TNotebook',      background='#f5f5f5',
                             tabmargins=[4, 4, 0, 0])
        self.style.configure('TNotebook.Tab',  font=('Helvetica', 10),
                             padding=[14, 6], background='#e0e0e0',
                             foreground='#424242')
        self.style.map('TNotebook.Tab',
                       background=[('selected', '#ffffff')],
                       foreground=[('selected', '#1565c0')],
                       font=[('selected', ('Helvetica', 10, 'bold'))])

        self.style.configure('TFrame',      background='#f5f5f5')
        self.style.configure('TLabelframe', background='#f5f5f5')
        self.style.configure('TLabelframe.Label', background='#f5f5f5',
                             font=('Helvetica', 9, 'bold'),
                             foreground='#1565c0')
        self.style.configure('TLabel',  background='#f5f5f5',
                             foreground='#212121', font=('Helvetica', 9))
        self.style.configure('TButton', font=('Helvetica', 9), padding=[8, 4])
        self.style.configure('Accent.TButton', background='#1565c0',
                             foreground='white',
                             font=('Helvetica', 9, 'bold'), padding=[12, 5])
        self.style.map('Accent.TButton',
                       background=[('active', '#0d47a1'),
                                   ('pressed', '#0a3d8f')])
        self.style.configure('TEntry', fieldbackground='#ffffff',
                             foreground='#212121', padding=4)
        self.style.configure('Treeview', background='#ffffff',
                             fieldbackground='#ffffff', foreground='#212121',
                             rowheight=24, font=('Helvetica', 9))
        self.style.configure('Treeview.Heading',
                             font=('Helvetica', 9, 'bold'),
                             background='#e3f2fd', foreground='#1565c0')
        self.style.configure('TProgressbar', troughcolor='#e0e0e0',
                             background='#1565c0', thickness=8)

    # ── Interfaz ──────────────────────────────────────────────────────────────

    def _construir_barra_superior(self):
        frame = tk.Frame(self, bg='#1565c0', height=56)
        frame.pack(fill='x')
        frame.pack_propagate(False)

        tk.Label(frame, text='  ValidaRH',
                 font=('Helvetica', 15, 'bold'),
                 bg='#1565c0', fg='white').pack(side='left', padx=(8, 0), pady=10)
        tk.Label(frame, text='v2.0',
                 font=('Helvetica', 8), bg='#1565c0', fg='#90caf9').pack(
                     side='left', padx=(4, 0), pady=(18, 0))
        tk.Label(frame,
                 text='Sistema de Validación de Datos para Recursos Humanos',
                 font=('Helvetica', 9), bg='#1565c0', fg='#bbdefb').pack(
                     side='left', padx=20, pady=10)

        # Info del usuario en la esquina derecha
        rol = self._usuario.get('rol', '—')
        nombre = self._usuario['nombre'].split()[0]
        tk.Label(frame,
                 text=f"  {nombre}  [{rol}]  ",
                 font=('Helvetica', 9, 'bold'),
                 bg='#1565c0', fg='#ffffff').pack(side='right', padx=8)

    def _construir_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=8, pady=(8, 0))

        rol = self._usuario.get('rol', 'postulante')

        if rol == 'reclutador':
            self._agregar_pestanas_reclutador()
        else:
            self._agregar_pestanas_postulante()

    def _agregar_pestanas_reclutador(self):
        from ui.tab_reclutador import TabReclutador
        from ui.tab_analizador import TabAnalizador
        from ui.tab_historial  import TabHistorial
        from ui.tab_perfil     import TabPerfil

        tab_rec  = TabReclutador(self.notebook, self._usuario)
        tab_anal = TabAnalizador(self.notebook)
        tab_hist = TabHistorial(self.notebook, self._usuario)
        tab_perf = TabPerfil(self.notebook, self._usuario,
                             on_logout=self._cerrar_sesion)

        self.notebook.add(tab_rec,  text='📋  Panel Reclutador')
        self.notebook.add(tab_anal, text='📄  Analizador')
        self.notebook.add(tab_hist, text='📊  Historial')
        self.notebook.add(tab_perf, text='👤  Mi Perfil')

    def _agregar_pestanas_postulante(self):
        from ui.tab_postulante import TabPostulante
        from ui.tab_historial  import TabHistorial
        from ui.tab_perfil     import TabPerfil

        tab_post = TabPostulante(self.notebook, self._usuario)
        tab_hist = TabHistorial(self.notebook, self._usuario)
        tab_perf = TabPerfil(self.notebook, self._usuario,
                             on_logout=self._cerrar_sesion)

        self.notebook.add(tab_post, text='🎯  Mi espacio')
        self.notebook.add(tab_hist, text='📊  Historial')
        self.notebook.add(tab_perf, text='👤  Mi Perfil')

    def _construir_barra_inferior(self):
        frame = tk.Frame(self, bg='#e3f2fd', height=24)
        frame.pack(fill='x', side='bottom')
        frame.pack_propagate(False)

        tk.Label(frame,
                 text='Proyecto: Búsqueda y validación de patrones  '
                      '|  Python + tkinter  |  Motor manual sin librería re',
                 font=('Helvetica', 8), bg='#e3f2fd', fg='#1565c0').pack(
                     side='left', padx=12, pady=4)

        rol   = self._usuario.get('rol', '—')
        correo = self._usuario.get('correo', '—')
        tk.Label(frame, text=f"{correo}  [{rol}]",
                 font=('Helvetica', 8), bg='#e3f2fd',
                 fg='#1565c0').pack(side='right', padx=12, pady=4)

    # ── Utilidades ────────────────────────────────────────────────────────────

    def _centrar_ventana(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - APP_ANCHO) // 2
        y = (sh - APP_ALTO)  // 2
        self.geometry(f'{APP_ANCHO}x{APP_ALTO}+{x}+{y}')

    def _cerrar_sesion(self):
        """Destruye la interfaz activa, vuelve a mostrar el login y reconstruye."""
        for widget in self.winfo_children():
            widget.destroy()
        self._usuario = None
        self.withdraw()
        if not self._mostrar_login():
            self.destroy()
            return
        self._configurar_ventana()
        self._aplicar_tema()
        self._construir_barra_superior()
        self._construir_notebook()
        self._construir_barra_inferior()
        self._centrar_ventana()
        self.deiconify()

    def _confirmar_salida(self):
        if messagebox.askokcancel('Salir de ValidaRH',
                                  '¿Cerrar la aplicación?'):
            self.destroy()


def main():
    app = ValidaRH()
    if app._usuario is not None:
        app.mainloop()


if __name__ == '__main__':
    main()
