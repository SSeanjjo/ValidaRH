"""
tab_historial.py — Pestaña de historial de análisis con persistencia en BD.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json


class TabHistorial(ttk.Frame):
    """
    Muestra el historial de análisis del usuario actual.
    Los datos se cargan desde la tabla historial_analisis en SQLite.
    """

    def __init__(self, parent, usuario: dict):
        super().__init__(parent)
        self._usuario = usuario
        self._construir_ui()
        self.cargar_historial()

    # ── Construcción ─────────────────────────────────────────────────────────

    def _construir_ui(self):
        # Cabecera
        barra = ttk.Frame(self)
        barra.pack(fill='x', padx=12, pady=(12, 4))
        ttk.Label(barra, text='Historial de Análisis',
                  font=('Helvetica', 13, 'bold')).pack(side='left')
        ttk.Separator(barra, orient='vertical').pack(
            side='left', fill='y', padx=12, pady=2)
        ttk.Button(barra, text='Actualizar',
                   command=self.cargar_historial).pack(side='left', padx=4)
        ttk.Button(barra, text='Ver detalle',
                   command=self._ver_detalle).pack(side='left', padx=4)
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=12, pady=4)

        # Tabla principal
        frame_tabla = ttk.LabelFrame(self, text='Registros guardados')
        frame_tabla.pack(fill='both', expand=True, padx=12, pady=4)

        cols = ('fecha', 'candidato', 'archivo', 'perfil', 'score')
        self._tree = ttk.Treeview(frame_tabla, columns=cols,
                                  show='headings', height=18)

        cab = {
            'fecha':     ('Fecha',               130),
            'candidato': ('Candidato / Usuario',  160),
            'archivo':   ('Archivo analizado',    160),
            'perfil':    ('Perfil comparado',     160),
            'score':     ('Score',                70),
        }
        for c, (txt, w) in cab.items():
            self._tree.heading(c, text=txt,
                               command=lambda _c=c: self._ordenar(_c))
            self._tree.column(c, width=w,
                              anchor='center' if c == 'score' else 'w')

        self._tree.tag_configure('alto',  foreground='#2e7d32')
        self._tree.tag_configure('medio', foreground='#f57f17')
        self._tree.tag_configure('bajo',  foreground='#c62828')
        self._tree.tag_configure('sin',   foreground='gray')

        sv = ttk.Scrollbar(frame_tabla, orient='vertical',
                           command=self._tree.yview)
        self._tree.configure(yscrollcommand=sv.set)
        self._tree.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        sv.pack(side='right', fill='y', pady=4)

        self._tree.bind('<Double-1>', lambda e: self._ver_detalle())

        # Barra inferior de estado
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=12, pady=2)
        self.lbl_estado = ttk.Label(self, text='',
                                    foreground='gray', font=('Helvetica', 8))
        self.lbl_estado.pack(anchor='w', padx=14, pady=(0, 6))

    # ── Carga de datos ────────────────────────────────────────────────────────

    def cargar_historial(self):
        from db.repository import HistorialRepo
        for item in self._tree.get_children():
            self._tree.delete(item)

        registros = HistorialRepo.listar_por_usuario(self._usuario['id'])

        for r in registros:
            score = r['score_global']
            if score is None:
                tag  = 'sin'
                txt_score = '—'
            else:
                txt_score = f"{score}%"
                if score >= 70:   tag = 'alto'
                elif score >= 40: tag = 'medio'
                else:             tag = 'bajo'

            self._tree.insert('', 'end', iid=str(r['id']), tags=(tag,),
                values=(
                    r['fecha_analisis'],
                    r['nombre_candidato'] or '—',
                    r['nombre_archivo']   or '—',
                    r['titulo_perfil']    or '—',
                    txt_score,
                ))

        n = len(registros)
        self.lbl_estado.config(
            text=f"{n} análisis registrados para {self._usuario['nombre'].split()[0]}.")

    # ── Detalle ───────────────────────────────────────────────────────────────

    def _ver_detalle(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo('Sin selección',
                                'Seleccione un registro de la tabla.')
            return

        from db.repository import HistorialRepo
        id_analisis = int(sel[0])
        detalle = HistorialRepo.obtener_detalle(id_analisis)
        if not detalle:
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Detalle del análisis — {detalle['fecha_analisis']}")
        dlg.geometry('700x520')
        dlg.resizable(True, True)

        # Info general
        frm_info = ttk.LabelFrame(dlg, text='Información general')
        frm_info.pack(fill='x', padx=12, pady=8)

        info = [
            ('Fecha:',      detalle['fecha_analisis']),
            ('Candidato:',  detalle['nombre_candidato'] or '—'),
            ('Archivo:',    detalle['nombre_archivo']   or '—'),
            ('Perfil:',     detalle['titulo_perfil']    or '—'),
            ('Score global:', f"{detalle['score_global']}%"
             if detalle['score_global'] is not None else '—'),
        ]
        for i, (lbl, val) in enumerate(info):
            ttk.Label(frm_info, text=lbl,
                      font=('Helvetica', 8, 'bold')).grid(
                          row=i, column=0, sticky='w', padx=8, pady=1)
            ttk.Label(frm_info, text=val,
                      font=('Helvetica', 8)).grid(
                          row=i, column=1, sticky='w', padx=4, pady=1)

        # Resultado JSON
        frm_det = ttk.LabelFrame(dlg, text='Resultado detallado')
        frm_det.pack(fill='both', expand=True, padx=12, pady=(0, 8))

        txt = tk.Text(frm_det, wrap='word', font=('Courier', 8),
                      state='disabled')
        sv = ttk.Scrollbar(frm_det, orient='vertical', command=txt.yview)
        txt.configure(yscrollcommand=sv.set)
        txt.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        sv.pack(side='right', fill='y', pady=4)

        resultado = detalle.get('resultado', {})
        contenido = json.dumps(resultado, ensure_ascii=False, indent=2)

        txt.config(state='normal')
        txt.insert('end', contenido)
        txt.config(state='disabled')

    # ── Ordenamiento ──────────────────────────────────────────────────────────

    def _ordenar(self, col: str):
        items = [(self._tree.set(k, col), k) for k in self._tree.get_children()]
        items.sort(reverse=False)
        for idx, (_, k) in enumerate(items):
            self._tree.move(k, '', idx)
