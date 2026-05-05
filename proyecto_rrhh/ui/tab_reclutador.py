"""
tab_reclutador.py — Pestaña exclusiva para el rol Reclutador.

Sub-pestañas:
    1. Perfiles laborales  — CRUD de perfiles de vacante con extracción de keywords
    2. Candidatos          — Registro de candidatos + análisis de compatibilidad
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


class TabReclutador(ttk.Frame):

    def __init__(self, parent, usuario: dict):
        super().__init__(parent)
        self._usuario = usuario
        self._construir_ui()

    def _construir_ui(self):
        ttk.Label(self, text='Panel del Reclutador',
                  font=('Helvetica', 13, 'bold')).pack(
                      anchor='w', padx=14, pady=(12, 4))
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=12, pady=4)

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=8, pady=4)

        tab_perf = ttk.Frame(nb)
        tab_cand = ttk.Frame(nb)
        nb.add(tab_perf, text='  📋  Perfiles laborales  ')
        nb.add(tab_cand, text='  👥  Candidatos  ')

        self._construir_perfiles(tab_perf)
        self._construir_candidatos(tab_cand)

    # ─────────────────────────────────────────────────────────────────────────
    # Sub-pestaña: Perfiles laborales
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_perfiles(self, parent):
        # Barra de herramientas
        barra = ttk.Frame(parent)
        barra.pack(fill='x', padx=8, pady=8)
        ttk.Button(barra, text='+ Nuevo perfil',
                   command=self._nuevo_perfil).pack(side='left', padx=4)
        ttk.Button(barra, text='Eliminar seleccionado',
                   command=self._eliminar_perfil).pack(side='left', padx=4)
        ttk.Button(barra, text='Actualizar',
                   command=self._cargar_perfiles).pack(side='left', padx=4)

        # Tabla de perfiles
        frame_tabla = ttk.LabelFrame(parent, text='Perfiles registrados')
        frame_tabla.pack(fill='both', expand=True, padx=8, pady=4)

        cols = ('titulo', 'keywords', 'fecha', 'reclutador')
        self._tree_perfiles = ttk.Treeview(
            frame_tabla, columns=cols, show='headings', height=12)

        cabeceras = {
            'titulo':     ('Título del perfil',  200),
            'keywords':   ('Keywords detectadas', 300),
            'fecha':      ('Fecha de creación',   130),
            'reclutador': ('Creado por',           120),
        }
        for c, (txt, w) in cabeceras.items():
            self._tree_perfiles.heading(c, text=txt)
            self._tree_perfiles.column(c, width=w)

        sv = ttk.Scrollbar(frame_tabla, orient='vertical',
                           command=self._tree_perfiles.yview)
        self._tree_perfiles.configure(yscrollcommand=sv.set)
        self._tree_perfiles.pack(side='left', fill='both',
                                 expand=True, padx=4, pady=4)
        sv.pack(side='right', fill='y', pady=4)

        self._cargar_perfiles()

    def _cargar_perfiles(self):
        from db.repository import PerfilRepo
        for item in self._tree_perfiles.get_children():
            self._tree_perfiles.delete(item)
        for p in PerfilRepo.listar_activos():
            kw_txt = ', '.join(p['keywords'][:8])
            if len(p['keywords']) > 8:
                kw_txt += f' (+{len(p["keywords"])-8})'
            self._tree_perfiles.insert('', 'end', iid=str(p['id']),
                values=(p['titulo'], kw_txt, p['fecha_creacion'],
                        p.get('reclutador', '—')))

    def _nuevo_perfil(self):
        dlg = tk.Toplevel(self)
        dlg.title('Nuevo perfil laboral')
        dlg.geometry('520x480')
        dlg.resizable(False, True)
        dlg.grab_set()

        ttk.Label(dlg, text='Título del perfil:',
                  font=('Helvetica', 9, 'bold')).pack(
                      anchor='w', padx=16, pady=(16, 4))
        ent_titulo = ttk.Entry(dlg, width=52)
        ent_titulo.pack(padx=16, fill='x')

        ttk.Label(dlg,
                  text='Descripción / Requisitos (uno por línea):',
                  font=('Helvetica', 9, 'bold')).pack(
                      anchor='w', padx=16, pady=(12, 4))
        txt_desc = ScrolledText(dlg, height=12, wrap='word',
                                font=('Courier', 9))
        txt_desc.pack(padx=16, fill='both', expand=True)

        ttk.Label(dlg,
                  text='Las keywords se extraen automáticamente al guardar.',
                  foreground='gray', font=('Helvetica', 8)).pack(
                      anchor='w', padx=16, pady=(4, 0))

        frm_bot = ttk.Frame(dlg)
        frm_bot.pack(fill='x', padx=16, pady=12)
        lbl_err = ttk.Label(frm_bot, text='', foreground='#c62828',
                            font=('Helvetica', 8))
        lbl_err.pack(side='left')

        def _guardar():
            from db.repository import PerfilRepo
            from proyecto_rrhh.logic.cv_matcher.cv_matcher import CVMatcher
            titulo = ent_titulo.get().strip()
            desc   = txt_desc.get('1.0', 'end').strip()
            if not titulo:
                lbl_err.config(text='El título no puede estar vacío.')
                return
            if not desc:
                lbl_err.config(text='La descripción no puede estar vacía.')
                return
            matcher  = CVMatcher()
            desc     = matcher.preparar_descripcion(desc)
            keywords = matcher.extraer_keywords_perfil(desc)
            ok, msg = PerfilRepo.crear(self._usuario['id'], titulo, desc, keywords)
            if ok:
                dlg.destroy()
                self._cargar_perfiles()
                messagebox.showinfo('Perfil creado',
                                    f"Perfil '{titulo}' creado con "
                                    f"{len(keywords)} keywords detectadas.")
            else:
                lbl_err.config(text=msg)

        ttk.Button(frm_bot, text='Guardar perfil',
                   command=_guardar).pack(side='right', ipadx=12, ipady=4)

    def _eliminar_perfil(self):
        sel = self._tree_perfiles.selection()
        if not sel:
            messagebox.showinfo('Sin selección', 'Seleccione un perfil.')
            return
        if not messagebox.askyesno('Confirmar',
                                   '¿Eliminar el perfil seleccionado?'):
            return
        from db.repository import PerfilRepo
        PerfilRepo.eliminar(int(sel[0]))
        self._cargar_perfiles()

    # ─────────────────────────────────────────────────────────────────────────
    # Sub-pestaña: Candidatos
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_candidatos(self, parent):
        # Panel izquierdo: lista de postulantes registrados
        pan = ttk.PanedWindow(parent, orient='horizontal')
        pan.pack(fill='both', expand=True, padx=8, pady=8)

        # Lista
        frame_lista = ttk.LabelFrame(pan, text='Postulantes registrados')
        pan.add(frame_lista, weight=1)

        cols = ('nombre', 'correo', 'cedula', 'fecha')
        self._tree_cand = ttk.Treeview(
            frame_lista, columns=cols, show='headings', height=16)
        for c, txt, w in [('nombre','Nombre',130),('correo','Correo',150),
                           ('cedula','Cédula',90),('fecha','Registro',110)]:
            self._tree_cand.heading(c, text=txt)
            self._tree_cand.column(c, width=w)
        sv = ttk.Scrollbar(frame_lista, orient='vertical',
                           command=self._tree_cand.yview)
        self._tree_cand.configure(yscrollcommand=sv.set)
        self._tree_cand.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        sv.pack(side='right', fill='y', pady=4)
        self._tree_cand.bind('<<TreeviewSelect>>', self._al_seleccionar_candidato)

        ttk.Button(frame_lista, text='Actualizar lista',
                   command=self._cargar_candidatos).pack(pady=4)

        # Panel derecho: análisis
        frame_analisis = ttk.LabelFrame(pan, text='Analizar candidato')
        pan.add(frame_analisis, weight=2)

        ttk.Label(frame_analisis,
                  text='Candidato seleccionado:',
                  font=('Helvetica', 8, 'bold')).grid(
                      row=0, column=0, sticky='w', padx=8, pady=(8, 2))
        self.lbl_cand_sel = ttk.Label(frame_analisis, text='—',
                                      foreground='#1565c0')
        self.lbl_cand_sel.grid(row=0, column=1, sticky='w', padx=4, pady=(8, 2))

        ttk.Label(frame_analisis,
                  text='Perfil a comparar:',
                  font=('Helvetica', 8, 'bold')).grid(
                      row=1, column=0, sticky='w', padx=8, pady=(8, 2))
        self._var_perfil = tk.StringVar()
        self._combo_perfiles = ttk.Combobox(
            frame_analisis, textvariable=self._var_perfil,
            state='readonly', width=30)
        self._combo_perfiles.grid(row=1, column=1, sticky='w',
                                  padx=4, pady=(8, 2))

        ttk.Button(frame_analisis, text='Actualizar perfiles',
                   command=self._actualizar_combo_perfiles).grid(
                       row=1, column=2, padx=4)

        ttk.Button(frame_analisis, text='Analizar compatibilidad',
                   command=self._analizar_candidato).grid(
                       row=2, column=0, columnspan=3,
                       pady=12, ipadx=12, ipady=4)

        # Score
        frm_score = ttk.Frame(frame_analisis)
        frm_score.grid(row=3, column=0, columnspan=3, pady=(0, 8))
        ttk.Label(frm_score, text='Compatibilidad:',
                  font=('Helvetica', 10, 'bold')).pack(side='left')
        self.lbl_score_cand = ttk.Label(frm_score, text='—',
                                        font=('Helvetica', 14, 'bold'))
        self.lbl_score_cand.pack(side='left', padx=8)

        # Tabla de requisitos
        frame_res = ttk.LabelFrame(frame_analisis, text='Resultado por requisito')
        frame_res.grid(row=4, column=0, columnspan=3,
                       sticky='nsew', padx=8, pady=4)
        frame_analisis.rowconfigure(4, weight=1)
        frame_analisis.columnconfigure(1, weight=1)

        rcols = ('estado', 'requisito', 'encontradas', 'contexto')
        self._tree_res = ttk.Treeview(
            frame_res, columns=rcols, show='headings', height=10)

        rcab = {
            'estado':     ('Estado',       80),
            'requisito':  ('Requisito',    180),
            'encontradas':('Keywords OK',  140),
            'contexto':   ('Contexto CV',  200),
        }
        for c, (txt, w) in rcab.items():
            self._tree_res.heading(c, text=txt)
            self._tree_res.column(c, width=w,
                                  anchor='center' if c == 'estado' else 'w')

        self._tree_res.tag_configure('encontrado',    foreground='#2e7d32')
        self._tree_res.tag_configure('parcial',       foreground='#f57f17')
        self._tree_res.tag_configure('no_encontrado', foreground='#c62828')

        sv2 = ttk.Scrollbar(frame_res, orient='vertical',
                            command=self._tree_res.yview)
        self._tree_res.configure(yscrollcommand=sv2.set)
        self._tree_res.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        sv2.pack(side='right', fill='y', pady=4)

        self._candidatos_data = {}
        self._cargar_candidatos()
        self._actualizar_combo_perfiles()

    def _cargar_candidatos(self):
        from db.repository import UsuarioRepo
        for item in self._tree_cand.get_children():
            self._tree_cand.delete(item)
        self._candidatos_data = {}
        for u in UsuarioRepo.listar_postulantes():
            self._tree_cand.insert('', 'end', iid=str(u['id']),
                values=(u['nombre'], u['correo'],
                        u['cedula'] or '—', u['fecha_registro']))
            self._candidatos_data[str(u['id'])] = u

    def _al_seleccionar_candidato(self, _event):
        sel = self._tree_cand.selection()
        if not sel:
            return
        u = self._candidatos_data.get(sel[0])
        if u:
            self.lbl_cand_sel.config(
                text=f"{u['nombre']}  ({u['correo']})")

    def _actualizar_combo_perfiles(self):
        from db.repository import PerfilRepo
        self._perfiles_map = {}
        perfiles = PerfilRepo.listar_activos()
        valores  = []
        for p in perfiles:
            clave = f"{p['titulo']} (ID:{p['id']})"
            valores.append(clave)
            self._perfiles_map[clave] = p
        self._combo_perfiles['values'] = valores
        if valores:
            self._combo_perfiles.current(0)

    def _analizar_candidato(self):
        sel = self._tree_cand.selection()
        if not sel:
            messagebox.showwarning('Sin candidato',
                                   'Seleccione un candidato de la lista.')
            return
        perfil_key = self._var_perfil.get()
        if not perfil_key:
            messagebox.showwarning('Sin perfil',
                                   'Seleccione un perfil laboral.')
            return

        u = self._candidatos_data.get(sel[0])
        if not u or not u.get('cv_texto'):
            messagebox.showwarning('Sin CV',
                                   'El candidato no tiene CV registrado.')
            return

        perfil = self._perfiles_map[perfil_key]

        from proyecto_rrhh.logic.cv_matcher.cv_matcher import CVMatcher
        from db.repository import HistorialRepo

        resultado = CVMatcher().analizar(u['cv_texto'], perfil['descripcion'])

        # Poblar tabla de resultados
        for item in self._tree_res.get_children():
            self._tree_res.delete(item)

        etiquetas = {
            'encontrado':    '✓ Cumple',
            'parcial':       '~ Parcial',
            'no_encontrado': '✗ No cumple',
        }
        for r in resultado['requisitos']:
            enc_txt = ', '.join(r['encontrados']) or '—'
            self._tree_res.insert('', 'end', tags=(r['estado'],),
                values=(
                    etiquetas.get(r['estado'], r['estado']),
                    r['texto'][:50] + ('…' if len(r['texto']) > 50 else ''),
                    enc_txt,
                    r['contexto'] or '—',
                ))

        score = resultado['score_global']
        color = '#2e7d32' if score >= 70 else '#f57f17' if score >= 40 else '#c62828'
        self.lbl_score_cand.config(text=f"{score}%", foreground=color)

        # Guardar en historial
        HistorialRepo.guardar(
            id_usuario      = self._usuario['id'],
            nombre_candidato= u['nombre'],
            nombre_archivo  = u.get('cv_nombre') or '—',
            id_perfil       = perfil['id'],
            titulo_perfil   = perfil['titulo'],
            score_global    = score,
            resultado       = resultado,
        )
