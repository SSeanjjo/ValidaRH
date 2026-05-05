"""
tab_postulante.py — Pestaña de espacio personal del postulante.

Sub-pestañas:
    1. Mis CVs     — CRUD de hojas de vida; muestra patrones extraídos al seleccionar
    2. Vacantes    — CRUD de vacantes guardadas; auto-extrae keywords del texto
    3. Analizador  — Selecciona CV y vacante de la BD, calcula compatibilidad
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class TabPostulante(ttk.Frame):

    def __init__(self, parent, usuario: dict):
        super().__init__(parent)
        self._usuario = usuario
        self._construir_ui()

    def _construir_ui(self):
        ttk.Label(self, text='Mi espacio de postulante',
                  font=('Helvetica', 13, 'bold')).pack(
                      anchor='w', padx=14, pady=(12, 4))
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=12, pady=4)

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=8, pady=4)

        tab_cvs  = ttk.Frame(nb)
        tab_vac  = ttk.Frame(nb)
        tab_anal = ttk.Frame(nb)
        nb.add(tab_cvs,  text='  📄  Mis CVs  ')
        nb.add(tab_vac,  text='  🏢  Vacantes  ')
        nb.add(tab_anal, text='  🎯  Analizador  ')

        self._construir_mis_cvs(tab_cvs)
        self._construir_vacantes(tab_vac)
        self._construir_analizador(tab_anal)

    # ── Sub-pestaña: Mis CVs ──────────────────────────────────────────────────

    def _construir_mis_cvs(self, parent):
        barra = ttk.Frame(parent)
        barra.pack(fill='x', padx=8, pady=8)
        ttk.Button(barra, text='➕  Nuevo CV',
                   command=self._nuevo_cv).pack(side='left', padx=4)
        ttk.Button(barra, text='🗑  Eliminar',
                   command=self._eliminar_cv).pack(side='left', padx=4)
        ttk.Button(barra, text='🔄  Actualizar',
                   command=self._cargar_lista_cvs).pack(side='left', padx=4)

        ttk.Separator(parent, orient='horizontal').pack(fill='x', padx=8, pady=2)

        pan = ttk.PanedWindow(parent, orient='horizontal')
        pan.pack(fill='both', expand=True, padx=8, pady=4)

        # Lista de CVs registrados
        frm_lista = ttk.LabelFrame(pan, text='Hojas de vida registradas')
        pan.add(frm_lista, weight=1)

        cols = ('nombre', 'archivo', 'fecha')
        self._tree_cvs = ttk.Treeview(frm_lista, columns=cols,
                                       show='headings', height=18)
        for c, t, w in [('nombre', 'Nombre', 160),
                         ('archivo', 'Archivo', 130),
                         ('fecha', 'Registro', 120)]:
            self._tree_cvs.heading(c, text=t)
            self._tree_cvs.column(c, width=w)

        sv = ttk.Scrollbar(frm_lista, orient='vertical',
                           command=self._tree_cvs.yview)
        self._tree_cvs.configure(yscrollcommand=sv.set)
        self._tree_cvs.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        sv.pack(side='right', fill='y', pady=4)
        self._tree_cvs.bind('<<TreeviewSelect>>', self._al_seleccionar_cv)

        # Patrones del CV seleccionado
        frm_pat = ttk.LabelFrame(pan, text='Patrones del CV seleccionado')
        pan.add(frm_pat, weight=1)

        self._arbol_pat_cv = ttk.Treeview(frm_pat, columns=('valor',),
                                           show='tree headings', height=18)
        self._arbol_pat_cv.heading('#0',    text='Categoría')
        self._arbol_pat_cv.heading('valor', text='Valor')
        self._arbol_pat_cv.column('#0',    width=140)
        self._arbol_pat_cv.column('valor', width=170)
        self._arbol_pat_cv.tag_configure('cat',   font=('Helvetica', 8, 'bold'))
        self._arbol_pat_cv.tag_configure('item',  font=('Courier', 8))
        self._arbol_pat_cv.tag_configure('vacio', foreground='gray')

        sv2 = ttk.Scrollbar(frm_pat, orient='vertical',
                            command=self._arbol_pat_cv.yview)
        self._arbol_pat_cv.configure(yscrollcommand=sv2.set)
        self._arbol_pat_cv.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        sv2.pack(side='right', fill='y', pady=4)

        self._cvs_map = {}
        self._cargar_lista_cvs()

    def _cargar_lista_cvs(self):
        from db.repository import HojaDeVidaRepo
        for item in self._tree_cvs.get_children():
            self._tree_cvs.delete(item)
        self._cvs_map = {}
        for cv in HojaDeVidaRepo.listar_por_usuario(self._usuario['id']):
            iid = self._tree_cvs.insert('', 'end', values=(
                cv['nombre'], cv['cv_nombre'] or '—', cv['fecha_registro']))
            self._cvs_map[iid] = cv['id']

    def _al_seleccionar_cv(self, _event=None):
        sel = self._tree_cvs.selection()
        if not sel:
            return
        id_cv = self._cvs_map.get(sel[0])
        if not id_cv:
            return

        from db.repository import HojaDeVidaRepo
        cv = HojaDeVidaRepo.obtener(id_cv)
        if not cv:
            return

        for item in self._arbol_pat_cv.get_children():
            self._arbol_pat_cv.delete(item)

        patrones = cv.get('patrones') or {}
        if not patrones:
            from logic.validators.pattern_matcher import PatternMatcher
            patrones = PatternMatcher().find_all(cv.get('cv_texto', ''))

        etiquetas = {
            'correos':   '📧 Correos',
            'telefonos': '📞 Teléfonos',
            'cedulas':   '🪪 Cédulas',
            'fechas':    '📅 Fechas',
            'urls':      '🔗 URLs',
            'placas':    '🚗 Placas',
        }
        for clave, etiqueta in etiquetas.items():
            items = patrones.get(clave, [])
            nodo = self._arbol_pat_cv.insert(
                '', 'end', text=f"{etiqueta} ({len(items)})",
                tags=('cat',), open=True)
            if items:
                for v in items:
                    self._arbol_pat_cv.insert(nodo, 'end', text='',
                                               values=(v,), tags=('item',))
            else:
                self._arbol_pat_cv.insert(nodo, 'end',
                                           text='(ninguno)', tags=('vacio',))

    def _nuevo_cv(self):
        _DialogNuevoCV(self, self._usuario['id'],
                       callback=self._cargar_lista_cvs)

    def _eliminar_cv(self):
        sel = self._tree_cvs.selection()
        if not sel:
            messagebox.showwarning('Selección', 'Seleccione un CV de la lista.')
            return
        id_cv = self._cvs_map.get(sel[0])
        if not messagebox.askokcancel('Eliminar CV',
                                      '¿Eliminar permanentemente este CV?'):
            return
        from db.repository import HojaDeVidaRepo
        HojaDeVidaRepo.eliminar(id_cv)
        self._cargar_lista_cvs()
        for item in self._arbol_pat_cv.get_children():
            self._arbol_pat_cv.delete(item)

    # ── Sub-pestaña: Vacantes ─────────────────────────────────────────────────

    def _construir_vacantes(self, parent):
        barra = ttk.Frame(parent)
        barra.pack(fill='x', padx=8, pady=8)
        ttk.Button(barra, text='➕  Registrar vacante',
                   command=self._nueva_vacante).pack(side='left', padx=4)
        ttk.Button(barra, text='🗑  Eliminar',
                   command=self._eliminar_vacante).pack(side='left', padx=4)
        ttk.Button(barra, text='🔄  Actualizar',
                   command=self._cargar_lista_vacantes).pack(side='left', padx=4)

        ttk.Separator(parent, orient='horizontal').pack(fill='x', padx=8, pady=2)

        pan = ttk.PanedWindow(parent, orient='horizontal')
        pan.pack(fill='both', expand=True, padx=8, pady=4)

        # Lista de vacantes
        frm_lista = ttk.LabelFrame(pan, text='Vacantes registradas')
        pan.add(frm_lista, weight=2)

        cols = ('titulo', 'empresa', 'ubicacion', 'modalidad', 'fecha')
        self._tree_vac = ttk.Treeview(frm_lista, columns=cols,
                                       show='headings', height=18)
        for c, t, w in [('titulo', 'Título', 180), ('empresa', 'Empresa', 130),
                         ('ubicacion', 'Ubicación', 100),
                         ('modalidad', 'Modalidad', 90),
                         ('fecha', 'Registro', 110)]:
            self._tree_vac.heading(c, text=t)
            self._tree_vac.column(c, width=w)

        sv = ttk.Scrollbar(frm_lista, orient='vertical',
                           command=self._tree_vac.yview)
        self._tree_vac.configure(yscrollcommand=sv.set)
        self._tree_vac.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        sv.pack(side='right', fill='y', pady=4)
        self._tree_vac.bind('<<TreeviewSelect>>', self._al_seleccionar_vacante)

        # Keywords de la vacante seleccionada
        frm_kw = ttk.LabelFrame(pan, text='Keywords extraídas')
        pan.add(frm_kw, weight=1)

        self._txt_kw_vac = tk.Text(frm_kw, wrap='word', font=('Courier', 8),
                                    state='disabled', width=30)
        sv2 = ttk.Scrollbar(frm_kw, orient='vertical',
                            command=self._txt_kw_vac.yview)
        self._txt_kw_vac.configure(yscrollcommand=sv2.set)
        self._txt_kw_vac.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        sv2.pack(side='right', fill='y', pady=4)

        self._vac_map = {}
        self._cargar_lista_vacantes()

    def _cargar_lista_vacantes(self):
        from db.repository import VacanteRepo
        for item in self._tree_vac.get_children():
            self._tree_vac.delete(item)
        self._vac_map = {}
        for v in VacanteRepo.listar_por_usuario(self._usuario['id']):
            iid = self._tree_vac.insert('', 'end', values=(
                v['titulo'], v['empresa'] or '—',
                v['ubicacion'] or '—', v['modalidad'] or '—',
                v['fecha_registro']))
            self._vac_map[iid] = v['id']

    def _al_seleccionar_vacante(self, _event=None):
        sel = self._tree_vac.selection()
        if not sel:
            return
        id_vac = self._vac_map.get(sel[0])
        if not id_vac:
            return

        from db.repository import VacanteRepo
        vac = VacanteRepo.obtener(id_vac)
        if not vac:
            return

        kws = vac.get('keywords') or []
        self._txt_kw_vac.config(state='normal')
        self._txt_kw_vac.delete('1.0', 'end')
        self._txt_kw_vac.insert('end', '\n'.join(kws) if kws else '(sin keywords)')
        self._txt_kw_vac.config(state='disabled')

    def _nueva_vacante(self):
        _DialogNuevaVacante(self, self._usuario['id'],
                            callback=self._cargar_lista_vacantes)

    def _eliminar_vacante(self):
        sel = self._tree_vac.selection()
        if not sel:
            messagebox.showwarning('Selección', 'Seleccione una vacante.')
            return
        id_vac = self._vac_map.get(sel[0])
        if not messagebox.askokcancel('Eliminar vacante',
                                      '¿Eliminar esta vacante?'):
            return
        from db.repository import VacanteRepo
        VacanteRepo.eliminar(id_vac)
        self._cargar_lista_vacantes()
        self._txt_kw_vac.config(state='normal')
        self._txt_kw_vac.delete('1.0', 'end')
        self._txt_kw_vac.config(state='disabled')

    # ── Sub-pestaña: Analizador ───────────────────────────────────────────────

    def _construir_analizador(self, parent):
        frm_sel = ttk.LabelFrame(parent, text='Selección de CV y vacante')
        frm_sel.pack(fill='x', padx=8, pady=8)

        ttk.Label(frm_sel, text='Mi CV:').grid(
            row=0, column=0, padx=8, pady=8, sticky='w')
        self._var_cv_anal = tk.StringVar()
        self._combo_cv_anal = ttk.Combobox(
            frm_sel, textvariable=self._var_cv_anal,
            state='readonly', width=38)
        self._combo_cv_anal.grid(row=0, column=1, padx=4, pady=8)

        ttk.Label(frm_sel, text='Vacante:').grid(
            row=1, column=0, padx=8, pady=4, sticky='w')
        self._var_vac_anal = tk.StringVar()
        self._combo_vac_anal = ttk.Combobox(
            frm_sel, textvariable=self._var_vac_anal,
            state='readonly', width=38)
        self._combo_vac_anal.grid(row=1, column=1, padx=4, pady=4)

        frm_btns = ttk.Frame(frm_sel)
        frm_btns.grid(row=0, column=2, rowspan=2, padx=12, pady=4)
        ttk.Button(frm_btns, text='🔄  Actualizar',
                   command=self._actualizar_combos_anal).pack(pady=2)
        ttk.Button(frm_btns, text='🎯  Analizar compatibilidad',
                   command=self._analizar).pack(pady=2, ipadx=4)

        # Score
        frm_sc = ttk.Frame(parent)
        frm_sc.pack(fill='x', padx=8, pady=(0, 4))
        ttk.Label(frm_sc, text='Compatibilidad:',
                  font=('Helvetica', 10, 'bold')).pack(side='left', padx=8)
        self._lbl_score_anal = ttk.Label(frm_sc, text='—',
                                          font=('Helvetica', 16, 'bold'))
        self._lbl_score_anal.pack(side='left', padx=4)
        self._lbl_resumen_anal = ttk.Label(frm_sc, text='',
                                            font=('Helvetica', 9),
                                            foreground='gray')
        self._lbl_resumen_anal.pack(side='left', padx=12)

        # Tabla de resultados
        frame_res = ttk.LabelFrame(parent, text='Detalle por requisito')
        frame_res.pack(fill='both', expand=True, padx=8, pady=(0, 8))

        rcols = ('estado', 'requisito', 'encontradas', 'faltantes', 'contexto')
        self._tree_anal = ttk.Treeview(frame_res, columns=rcols,
                                        show='headings', height=14)
        for c, t, w, anc in [
            ('estado',      'Estado',      80,  'center'),
            ('requisito',   'Requisito',   180, 'w'),
            ('encontradas', 'Encontradas', 130, 'w'),
            ('faltantes',   'Faltantes',   130, 'w'),
            ('contexto',    'Contexto CV', 200, 'w'),
        ]:
            self._tree_anal.heading(c, text=t)
            self._tree_anal.column(c, width=w, anchor=anc)

        self._tree_anal.tag_configure('encontrado',    foreground='#2e7d32')
        self._tree_anal.tag_configure('parcial',       foreground='#f57f17')
        self._tree_anal.tag_configure('no_encontrado', foreground='#c62828')

        sv = ttk.Scrollbar(frame_res, orient='vertical',
                           command=self._tree_anal.yview)
        self._tree_anal.configure(yscrollcommand=sv.set)
        self._tree_anal.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        sv.pack(side='right', fill='y', pady=4)

        self._cvs_anal_map  = {}
        self._vacs_anal_map = {}
        self._actualizar_combos_anal()

    def _actualizar_combos_anal(self):
        from db.repository import HojaDeVidaRepo, VacanteRepo

        cvs = HojaDeVidaRepo.listar_por_usuario(self._usuario['id'])
        self._cvs_anal_map = {}
        vals_cv = []
        for cv in cvs:
            clave = f"{cv['nombre']} ({cv['cv_nombre'] or 'sin archivo'})"
            vals_cv.append(clave)
            self._cvs_anal_map[clave] = cv['id']
        self._combo_cv_anal['values'] = vals_cv
        if vals_cv:
            self._combo_cv_anal.current(0)

        vacs = VacanteRepo.listar_por_usuario(self._usuario['id'])
        self._vacs_anal_map = {}
        vals_vac = []
        for v in vacs:
            clave = f"{v['titulo']} — {v['empresa'] or '?'}"
            vals_vac.append(clave)
            self._vacs_anal_map[clave] = v['id']
        self._combo_vac_anal['values'] = vals_vac
        if vals_vac:
            self._combo_vac_anal.current(0)

    def _analizar(self):
        cv_key  = self._var_cv_anal.get()
        vac_key = self._var_vac_anal.get()

        if not cv_key:
            messagebox.showwarning('Sin CV',
                                   'Registre y seleccione un CV en "Mis CVs".')
            return
        if not vac_key:
            messagebox.showwarning('Sin vacante',
                                   'Registre y seleccione una vacante en "Vacantes".')
            return

        from db.repository import HojaDeVidaRepo, VacanteRepo, HistorialRepo
        from logic.cv_matcher.cv_matcher import CVMatcher

        cv  = HojaDeVidaRepo.obtener(self._cvs_anal_map[cv_key])
        vac = VacanteRepo.obtener(self._vacs_anal_map[vac_key])

        if not cv or not vac:
            messagebox.showerror('Error', 'No se encontró el registro en la base de datos.')
            return

        resultado = CVMatcher().analizar(cv['cv_texto'], vac['descripcion'])

        for item in self._tree_anal.get_children():
            self._tree_anal.delete(item)

        etiquetas = {
            'encontrado':    '✓ Cumple',
            'parcial':       '~ Parcial',
            'no_encontrado': '✗ No cumple',
        }
        for r in resultado['requisitos']:
            self._tree_anal.insert('', 'end', tags=(r['estado'],),
                values=(
                    etiquetas.get(r['estado'], r['estado']),
                    r['texto'][:50] + ('…' if len(r['texto']) > 50 else ''),
                    ', '.join(r['encontrados']) or '—',
                    ', '.join(r['no_encontrados']) or '—',
                    r['contexto'] or '—',
                ))

        score = resultado['score_global']
        color = '#2e7d32' if score >= 70 else '#f57f17' if score >= 40 else '#c62828'
        self._lbl_score_anal.config(text=f"{score}%", foreground=color)
        self._lbl_resumen_anal.config(
            text=f"✓ {resultado['encontrados']}  "
                 f"~ {resultado['parciales']}  "
                 f"✗ {resultado['no_encontrados']}  "
                 f"de {resultado['total']} requisitos")

        HistorialRepo.guardar(
            id_usuario       = self._usuario['id'],
            nombre_candidato = self._usuario['nombre'],
            nombre_archivo   = cv['cv_nombre'] or '—',
            id_perfil        = None,
            titulo_perfil    = vac['titulo'],
            score_global     = score,
            resultado        = resultado,
        )


# ── Diálogos modales ──────────────────────────────────────────────────────────

class _DialogNuevoCV(tk.Toplevel):
    """Diálogo para registrar un nuevo CV: carga desde archivo o texto pegado."""

    def __init__(self, parent, id_usuario: int, callback=None):
        super().__init__(parent)
        self._id_usuario = id_usuario
        self._callback   = callback
        self._cv_nombre  = ''
        self._construir_ui()
        self.grab_set()
        self.focus_force()
        self._centrar(parent)

    def _construir_ui(self):
        self.title('Nuevo CV')
        self.resizable(False, False)
        self.configure(bg='#f5f5f5')

        frm = ttk.Frame(self)
        frm.pack(fill='both', expand=True, padx=16, pady=12)

        ttk.Label(frm, text='Nombre del CV:').grid(
            row=0, column=0, sticky='w', pady=(0, 2))
        self.ent_nombre = ttk.Entry(frm, width=38)
        self.ent_nombre.grid(row=1, column=0, columnspan=2,
                             sticky='ew', pady=(0, 8))

        ttk.Label(frm, text='Descripción (opcional):').grid(
            row=2, column=0, sticky='w', pady=(0, 2))
        self.ent_desc = ttk.Entry(frm, width=38)
        self.ent_desc.grid(row=3, column=0, columnspan=2,
                           sticky='ew', pady=(0, 8))

        ttk.Label(frm, text='Contenido del CV:').grid(
            row=4, column=0, sticky='w', pady=(0, 2))
        ttk.Button(frm, text='📂  Cargar desde archivo (.txt/.pdf)',
                   command=self._cargar_archivo).grid(
                       row=4, column=1, sticky='e', pady=(0, 2))

        self.txt_cv = tk.Text(frm, width=50, height=12, wrap='word',
                              font=('Courier', 8))
        sv = ttk.Scrollbar(frm, orient='vertical', command=self.txt_cv.yview)
        self.txt_cv.configure(yscrollcommand=sv.set)
        self.txt_cv.grid(row=5, column=0, sticky='nsew', pady=4)
        sv.grid(row=5, column=1, sticky='ns', pady=4)

        self._lbl_arch = ttk.Label(frm, text='(sin archivo cargado)',
                                    foreground='gray', font=('Helvetica', 8))
        self._lbl_arch.grid(row=6, column=0, columnspan=2, sticky='w')

        self._lbl_err = ttk.Label(frm, text='', foreground='#c62828',
                                   font=('Helvetica', 8))
        self._lbl_err.grid(row=7, column=0, columnspan=2,
                           sticky='w', pady=(4, 0))

        frm_btns = ttk.Frame(frm)
        frm_btns.grid(row=8, column=0, columnspan=2, pady=12)
        ttk.Button(frm_btns, text='Guardar',
                   command=self._guardar).pack(side='left', padx=8,
                                               ipadx=12, ipady=4)
        ttk.Button(frm_btns, text='Cancelar',
                   command=self.destroy).pack(side='left', padx=8,
                                              ipadx=12, ipady=4)

        frm.columnconfigure(0, weight=1)
        frm.rowconfigure(5, weight=1)

    def _cargar_archivo(self):
        from logic.analyzers.report_analyzer import ReportAnalyzer
        ruta = filedialog.askopenfilename(
            title='Seleccionar CV',
            filetypes=[('Documentos', '*.txt *.pdf'),
                       ('Texto', '*.txt'), ('PDF', '*.pdf'),
                       ('Todos', '*.*')])
        if not ruta:
            return
        ra = ReportAnalyzer()
        ok, msg = ra.cargar_archivo(ruta)
        if not ok:
            messagebox.showerror('Error', msg, parent=self)
            return
        self._cv_nombre = ruta.replace('\\', '/').split('/')[-1]
        self.txt_cv.delete('1.0', 'end')
        self.txt_cv.insert('end', ra.get_contenido())
        self._lbl_arch.config(text=f"Archivo: {self._cv_nombre}",
                               foreground='#1565c0')
        if not self.ent_nombre.get():
            self.ent_nombre.insert(0, self._cv_nombre)

    def _guardar(self):
        from db.repository import HojaDeVidaRepo
        from logic.validators.pattern_matcher import PatternMatcher

        nombre = self.ent_nombre.get().strip()
        if not nombre:
            self._lbl_err.config(text='✗ Ingrese un nombre para el CV.')
            return

        cv_texto = self.txt_cv.get('1.0', 'end').strip()
        if not cv_texto:
            self._lbl_err.config(
                text='✗ Ingrese o cargue el contenido del CV.')
            return

        patrones = PatternMatcher().find_all(cv_texto)

        ok, msg = HojaDeVidaRepo.crear(
            id_usuario  = self._id_usuario,
            nombre      = nombre,
            cv_texto    = cv_texto,
            cv_nombre   = self._cv_nombre,
            descripcion = self.ent_desc.get().strip(),
            patrones    = patrones,
        )
        if ok:
            if self._callback:
                self._callback()
            self.destroy()
        else:
            self._lbl_err.config(text=f'✗ {msg}')

    def _centrar(self, parent):
        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width() // 2
        ph = parent.winfo_rooty() + parent.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f'+{pw - w // 2}+{ph - h // 2}')


class _DialogNuevaVacante(tk.Toplevel):
    """Diálogo para registrar una nueva vacante con PDF o texto pegado."""

    def __init__(self, parent, id_usuario: int, callback=None):
        super().__init__(parent)
        self._id_usuario = id_usuario
        self._callback   = callback
        self._construir_ui()
        self.grab_set()
        self.focus_force()
        self._centrar(parent)

    def _construir_ui(self):
        self.title('Registrar vacante')
        self.resizable(False, False)
        self.configure(bg='#f5f5f5')

        frm = ttk.Frame(self)
        frm.pack(fill='both', expand=True, padx=16, pady=12)

        campos_texto = [
            ('Título del cargo *:', 'ent_titulo'),
            ('Empresa:',            'ent_empresa'),
            ('Ubicación:',          'ent_ubicacion'),
        ]
        for i, (label, attr) in enumerate(campos_texto):
            ttk.Label(frm, text=label).grid(
                row=i, column=0, sticky='w', pady=(4, 0))
            ent = ttk.Entry(frm, width=40)
            ent.grid(row=i, column=1, columnspan=2, sticky='ew',
                     padx=(4, 0), pady=(4, 0))
            setattr(self, attr, ent)

        r = len(campos_texto)
        ttk.Label(frm, text='Modalidad:').grid(
            row=r, column=0, sticky='w', pady=(4, 0))
        self._var_modal = tk.StringVar(value='Presencial')
        ttk.Combobox(frm, textvariable=self._var_modal,
                     values=['Presencial', 'Remoto', 'Híbrido'],
                     state='readonly', width=20).grid(
                         row=r, column=1, sticky='w', padx=(4, 0), pady=(4, 0))

        r += 1
        ttk.Label(frm, text='Descripción de la vacante *:').grid(
            row=r, column=0, columnspan=2, sticky='w', pady=(8, 2))
        ttk.Button(frm, text='📂  Cargar desde PDF/TXT',
                   command=self._cargar_archivo).grid(
                       row=r, column=2, sticky='e', pady=(8, 2))

        r += 1
        self.txt_desc = tk.Text(frm, width=50, height=10, wrap='word',
                                font=('Courier', 8))
        sv = ttk.Scrollbar(frm, orient='vertical', command=self.txt_desc.yview)
        self.txt_desc.configure(yscrollcommand=sv.set)
        self.txt_desc.grid(row=r, column=0, columnspan=2, sticky='nsew', pady=4)
        sv.grid(row=r, column=2, sticky='ns', pady=4)

        r += 1
        self._lbl_arch = ttk.Label(frm, text='', foreground='gray',
                                    font=('Helvetica', 8))
        self._lbl_arch.grid(row=r, column=0, columnspan=3, sticky='w')

        r += 1
        self._lbl_err = ttk.Label(frm, text='', foreground='#c62828',
                                   font=('Helvetica', 8))
        self._lbl_err.grid(row=r, column=0, columnspan=3,
                           sticky='w', pady=(4, 0))

        r += 1
        frm_btns = ttk.Frame(frm)
        frm_btns.grid(row=r, column=0, columnspan=3, pady=12)
        ttk.Button(frm_btns, text='Guardar',
                   command=self._guardar).pack(side='left', padx=8,
                                               ipadx=12, ipady=4)
        ttk.Button(frm_btns, text='Cancelar',
                   command=self.destroy).pack(side='left', padx=8,
                                              ipadx=12, ipady=4)

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(len(campos_texto) + 2, weight=1)

    def _cargar_archivo(self):
        from logic.analyzers.report_analyzer import ReportAnalyzer
        ruta = filedialog.askopenfilename(
            title='Seleccionar descripción de la vacante',
            filetypes=[('Documentos', '*.txt *.pdf'),
                       ('Texto', '*.txt'), ('PDF', '*.pdf'),
                       ('Todos', '*.*')])
        if not ruta:
            return
        ra = ReportAnalyzer()
        ok, msg = ra.cargar_archivo(ruta)
        if not ok:
            messagebox.showerror('Error', msg, parent=self)
            return
        self.txt_desc.delete('1.0', 'end')
        self.txt_desc.insert('end', ra.get_contenido())
        nombre = ruta.replace('\\', '/').split('/')[-1]
        self._lbl_arch.config(text=f"Archivo: {nombre}",
                               foreground='#1565c0')

    def _guardar(self):
        from db.repository import VacanteRepo
        from logic.cv_matcher.cv_matcher import CVMatcher

        titulo = self.ent_titulo.get().strip()
        if not titulo:
            self._lbl_err.config(
                text='✗ El título del cargo es obligatorio.')
            return

        desc = self.txt_desc.get('1.0', 'end').strip()
        if not desc:
            self._lbl_err.config(
                text='✗ Ingrese o cargue la descripción de la vacante.')
            return

        matcher  = CVMatcher()
        desc     = matcher.preparar_descripcion(desc)
        keywords = matcher.extraer_keywords_perfil(desc)

        ok, msg = VacanteRepo.crear(
            id_usuario  = self._id_usuario,
            titulo      = titulo,
            empresa     = self.ent_empresa.get().strip(),
            ubicacion   = self.ent_ubicacion.get().strip(),
            modalidad   = self._var_modal.get(),
            descripcion = desc,
            keywords    = keywords,
        )
        if ok:
            if self._callback:
                self._callback()
            self.destroy()
        else:
            self._lbl_err.config(text=f'✗ {msg}')

    def _centrar(self, parent):
        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width() // 2
        ph = parent.winfo_rooty() + parent.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f'+{pw - w // 2}+{ph - h // 2}')
