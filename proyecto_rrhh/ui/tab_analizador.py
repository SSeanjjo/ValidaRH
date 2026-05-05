"""
tab_analizador.py
=================
Pestaña A — Analizador de documentos de texto.

Contexto: Sistema ValidaRH — Gestión de Recursos Humanos
Proyecto: Búsqueda y validación de patrones en textos y sistemas interactivos

Descripción:
    Implementa la interfaz gráfica de la pestaña de análisis de documentos.
    Permite al usuario cargar un archivo .txt, visualizar su contenido,
    ejecutar el análisis de patrones y exportar el reporte resultante.

Layout de la pestaña:
    ┌─────────────────────────────────────────────┐
    │  Barra de herramientas (cargar, analizar,   │
    │  exportar)                                  │
    ├───────────────────┬─────────────────────────┤
    │                   │  Panel de resultados    │
    │  Preview del      │  (árbol por categoría)  │
    │  documento        │                         │
    │                   ├─────────────────────────┤
    │                   │  Estadísticas           │
    ├───────────────────┴─────────────────────────┤
    │  Barra de estado                            │
    └─────────────────────────────────────────────┘

Autor: [Tu nombre]
Fecha: [Fecha]
Versión: 1.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from logic.analyzers.report_analyzer import ReportAnalyzer
from proyecto_rrhh.logic.cv_matcher.cv_matcher import CVMatcher


class TabAnalizador(ttk.Frame):
    """
    Pestaña A del Notebook — Analizador de documentos .txt.

    Orquesta la interacción entre el usuario y ReportAnalyzer:
        1. El usuario carga un archivo .txt
        2. Se previsualiza el contenido en el panel izquierdo
        3. Al analizar, los patrones aparecen en el árbol derecho
        4. Las estadísticas se muestran en el panel inferior derecho
        5. El usuario puede exportar el reporte a .txt

    Attributes:
        _analyzer : instancia de ReportAnalyzer que procesa el documento
        _ruta_actual : ruta del archivo actualmente cargado
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._analyzer    = ReportAnalyzer()
        self._cv_matcher  = CVMatcher()
        self._ruta_actual = ''
        self._construir_ui()

    # ── Construcción de la interfaz ───────────────────────────────────────────

    def _construir_ui(self):
        """
        Construye todos los elementos visuales de la pestaña.

        Estructura:
            - Barra de herramientas superior
            - Panel principal dividido: preview (izq) + resultados (der)
            - Barra de estado inferior
        """
        self._construir_barra_herramientas()
        self._construir_panel_principal()
        self._construir_barra_estado()

    def _construir_barra_herramientas(self):
        """
        Construye la barra superior con los botones de acción principal.

        Botones:
            - Cargar archivo  : abre el explorador de archivos
            - Analizar        : ejecuta el análisis (deshabilitado sin archivo)
            - Exportar reporte: guarda el reporte (deshabilitado sin análisis)
            - Limpiar         : resetea toda la pestaña
        """
        barra = ttk.Frame(self)
        barra.pack(fill='x', padx=12, pady=(12, 4))

        ttk.Label(
            barra,
            text='Analizador de Documentos',
            font=('Helvetica', 13, 'bold')
        ).pack(side='left')

        # Separador visual
        ttk.Separator(barra, orient='vertical').pack(
            side='left', fill='y', padx=12, pady=2)

        # Botones de acción
        self.btn_cargar = ttk.Button(
            barra,
            text='📂  Cargar archivo',
            command=self._cargar_archivo
        )
        self.btn_cargar.pack(side='left', padx=4)

        self.btn_analizar = ttk.Button(
            barra,
            text='🔍  Analizar',
            command=self._analizar,
            state='disabled'              # se habilita al cargar archivo
        )
        self.btn_analizar.pack(side='left', padx=4)

        self.btn_exportar = ttk.Button(
            barra,
            text='💾  Exportar reporte',
            command=self._exportar,
            state='disabled'              # se habilita tras el análisis
        )
        self.btn_exportar.pack(side='left', padx=4)

        ttk.Button(
            barra,
            text='✖  Limpiar',
            command=self._limpiar
        ).pack(side='left', padx=4)

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=12, pady=4)

    def _construir_panel_principal(self):
        """
        Construye el panel central dividido en dos secciones:
            - Izquierda: previsualización del texto del documento
            - Derecha:   árbol de resultados + tabla de estadísticas
        """
        panel = ttk.Frame(self)
        panel.pack(fill='both', expand=True, padx=12, pady=4)

        # ── Panel izquierdo: preview del documento ────────────────────────────
        frame_izq = ttk.LabelFrame(panel, text='Vista previa del documento')
        frame_izq.pack(side='left', fill='both', expand=True, padx=(0, 6))

        self.txt_preview = tk.Text(
            frame_izq,
            wrap='word',
            font=('Courier', 9),
            state='disabled',
            width=40
        )
        scroll_prev = ttk.Scrollbar(
            frame_izq, orient='vertical', command=self.txt_preview.yview)
        self.txt_preview.configure(yscrollcommand=scroll_prev.set)
        self.txt_preview.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        scroll_prev.pack(side='left', fill='y', pady=4)

        # ── Panel derecho: notebook resultados / compatibilidad ───────────────
        frame_der = ttk.Frame(panel)
        frame_der.pack(side='left', fill='both', expand=True, padx=(6, 0))

        self._nb_der = ttk.Notebook(frame_der)
        self._nb_der.pack(fill='both', expand=True)

        tab_pat = ttk.Frame(self._nb_der)
        tab_perf = ttk.Frame(self._nb_der)
        self._nb_der.add(tab_pat,  text='  Patrones encontrados  ')
        self._nb_der.add(tab_perf, text='  Compatibilidad con perfil  ')

        self._construir_arbol_resultados(tab_pat)
        self._construir_panel_estadisticas(tab_pat)
        self._construir_panel_perfil(tab_perf)

    def _construir_arbol_resultados(self, parent):
        """
        Construye el árbol (Treeview) que muestra los patrones encontrados
        organizados por categoría.

        Estructura del árbol:
            ▼ Correos electrónicos (2)
                juan@empresa.com
                rrhh@empresa.com
            ▼ Teléfonos (1)
                3001234567
            ...

        Args:
            parent: widget padre donde se inserta el árbol.
        """
        frame_arbol = ttk.LabelFrame(parent, text='Patrones encontrados')
        frame_arbol.pack(fill='both', expand=True, pady=(0, 6))

        self.arbol = ttk.Treeview(
            frame_arbol,
            columns=('valor',),
            show='tree headings',
            height=12
        )
        self.arbol.heading('#0',    text='Categoría')
        self.arbol.heading('valor', text='Valor encontrado')
        self.arbol.column('#0',    width=180)
        self.arbol.column('valor', width=220)

        # Colores por categoría
        self.arbol.tag_configure('categoria', font=('Helvetica', 9, 'bold'))
        self.arbol.tag_configure('item',      font=('Courier', 9))
        self.arbol.tag_configure('vacio',     foreground='gray')

        scroll_arbol = ttk.Scrollbar(
            frame_arbol, orient='vertical', command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=scroll_arbol.set)
        self.arbol.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        scroll_arbol.pack(side='left', fill='y', pady=4)

    def _construir_panel_estadisticas(self, parent):
        """
        Construye el panel inferior derecho con las estadísticas del documento.

        Muestra métricas calculadas por ReportAnalyzer:
            - Nombre del archivo
            - Fecha y hora del análisis
            - Total de líneas, palabras y caracteres
            - Total de datos encontrados y densidad

        Args:
            parent: widget padre donde se inserta el panel.
        """
        frame_est = ttk.LabelFrame(parent, text='Estadísticas del documento')
        frame_est.pack(fill='x', pady=(0, 4))

        # Grid de etiquetas: clave (izq) + valor (der)
        metricas = [
            ('Archivo:',          'lbl_archivo'),
            ('Fecha de análisis:','lbl_fecha'),
            ('Líneas:',           'lbl_lineas'),
            ('Palabras:',         'lbl_palabras'),
            ('Caracteres:',       'lbl_chars'),
            ('Datos encontrados:','lbl_datos'),
            ('Densidad de datos:','lbl_densidad'),
        ]

        self._labels_estadisticas = {}

        for i, (texto, attr) in enumerate(metricas):
            ttk.Label(
                frame_est,
                text=texto,
                font=('Helvetica', 8, 'bold')
            ).grid(row=i, column=0, sticky='w', padx=(8, 4), pady=1)

            lbl = ttk.Label(frame_est, text='—', font=('Helvetica', 8))
            lbl.grid(row=i, column=1, sticky='w', pady=1)
            self._labels_estadisticas[attr] = lbl

    def _construir_panel_perfil(self, parent):
        from tkinter.scrolledtext import ScrolledText

        frm_entrada = ttk.LabelFrame(parent, text='Descripción del perfil / vacante')
        frm_entrada.pack(fill='x', padx=4, pady=4)

        self.txt_perfil = ScrolledText(frm_entrada, wrap='word',
                                       font=('Courier', 9), height=7)
        self.txt_perfil.pack(fill='x', padx=4, pady=4)
        ttk.Label(frm_entrada, text='Ingrese los requisitos (uno por línea)',
                  foreground='gray', font=('Helvetica', 8)).pack(
                      anchor='w', padx=4, pady=(0, 4))

        frm_ctrl = ttk.Frame(parent)
        frm_ctrl.pack(fill='x', padx=4, pady=(0, 4))

        self.btn_compatibilidad = ttk.Button(
            frm_ctrl, text='Analizar compatibilidad',
            command=self._analizar_compatibilidad, state='disabled')
        self.btn_compatibilidad.pack(side='left', padx=(0, 12))

        ttk.Label(frm_ctrl, text='Compatibilidad:',
                  font=('Helvetica', 9, 'bold')).pack(side='left')
        self.lbl_score = ttk.Label(frm_ctrl, text='—',
                                   font=('Helvetica', 11, 'bold'))
        self.lbl_score.pack(side='left', padx=4)

        frame_tabla = ttk.LabelFrame(parent, text='Resultado por requisito')
        frame_tabla.pack(fill='both', expand=True, padx=4, pady=(0, 4))

        self.arbol_perfil = ttk.Treeview(
            frame_tabla,
            columns=('estado', 'keywords', 'contexto'),
            show='tree headings', height=10)
        self.arbol_perfil.heading('#0',       text='Requisito')
        self.arbol_perfil.heading('estado',   text='Estado')
        self.arbol_perfil.heading('keywords', text='Keywords OK')
        self.arbol_perfil.heading('contexto', text='Contexto en CV')
        self.arbol_perfil.column('#0',       width=150)
        self.arbol_perfil.column('estado',   width=80, anchor='center')
        self.arbol_perfil.column('keywords', width=140)
        self.arbol_perfil.column('contexto', width=200)
        self.arbol_perfil.tag_configure('encontrado',    foreground='#2e7d32')
        self.arbol_perfil.tag_configure('parcial',       foreground='#f57f17')
        self.arbol_perfil.tag_configure('no_encontrado', foreground='#c62828')

        sv = ttk.Scrollbar(frame_tabla, orient='vertical',
                           command=self.arbol_perfil.yview)
        self.arbol_perfil.configure(yscrollcommand=sv.set)
        self.arbol_perfil.pack(side='left', fill='both',
                               expand=True, padx=4, pady=4)
        sv.pack(side='right', fill='y', pady=4)

    def _analizar_compatibilidad(self):
        if not self._analyzer.get_contenido():
            messagebox.showwarning('Sin CV', 'Cargue un documento primero.')
            return
        perfil = self.txt_perfil.get('1.0', 'end').strip()
        if not perfil:
            messagebox.showwarning('Sin perfil',
                                   'Ingrese la descripción del perfil.')
            return

        resultado = self._cv_matcher.analizar(
            self._analyzer.get_contenido(), perfil)

        if resultado['total'] == 0:
            messagebox.showinfo('Sin requisitos',
                                'No se detectaron requisitos.\n'
                                'Ingrese los requisitos, uno por línea.')
            return

        for item in self.arbol_perfil.get_children():
            self.arbol_perfil.delete(item)

        etiquetas = {
            'encontrado':    '✓ Cumple',
            'parcial':       '~ Parcial',
            'no_encontrado': '✗ No cumple',
        }
        for r in resultado['requisitos']:
            kw_txt = ', '.join(r['encontrados'])
            req_txt = r['texto'][:45] + ('…' if len(r['texto']) > 45 else '')
            self.arbol_perfil.insert('', 'end',
                text=req_txt,
                values=(etiquetas.get(r['estado'], r['estado']),
                        kw_txt or '—', r['contexto'] or '—'),
                tags=(r['estado'],))

        score = resultado['score_global']
        color = '#2e7d32' if score >= 70 else '#f57f17' if score >= 40 else '#c62828'
        self.lbl_score.config(text=f"{score}%", foreground=color)
        self._set_estado(
            f"Compatibilidad: {score}% — "
            f"{resultado['encontrados']} cumplidos, "
            f"{resultado['parciales']} parciales, "
            f"{resultado['no_encontrados']} faltantes.")

    def _construir_barra_estado(self):
        """
        Construye la barra de estado inferior que informa al usuario
        sobre la acción más reciente ejecutada.
        """
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=12, pady=2)

        frame_estado = ttk.Frame(self)
        frame_estado.pack(fill='x', padx=12, pady=(0, 8))

        self.lbl_estado = ttk.Label(
            frame_estado,
            text='Cargue un archivo .txt o .pdf para comenzar.',
            foreground='gray',
            font=('Helvetica', 8)
        )
        self.lbl_estado.pack(side='left')

    # ── Acciones de los botones ───────────────────────────────────────────────

    def _cargar_archivo(self):
        """
        Abre el explorador de archivos para seleccionar un .txt.

        Tras la selección:
            1. Llama a ReportAnalyzer.cargar_archivo()
            2. Muestra el contenido en el panel de previsualización
            3. Habilita el botón Analizar
            4. Actualiza la barra de estado
        """
        ruta = filedialog.askopenfilename(
            title='Seleccionar documento',
            filetypes=[
                ('Documentos soportados', '*.txt *.pdf'),
                ('Archivos de texto',     '*.txt'),
                ('Archivos PDF',          '*.pdf'),
                ('Todos',                 '*.*'),
            ]
        )

        if not ruta:
            return  # El usuario canceló la selección

        exito, mensaje = self._analyzer.cargar_archivo(ruta)

        if not exito:
            messagebox.showerror('Error al cargar', mensaje)
            self._set_estado(mensaje, error=True)
            return

        self._ruta_actual = ruta

        # Mostrar contenido en el preview
        contenido = self._analyzer.get_contenido()
        self.txt_preview.config(state='normal')
        self.txt_preview.delete('1.0', 'end')
        self.txt_preview.insert('end', contenido)
        self.txt_preview.config(state='disabled')

        # Habilitar análisis y resetear resultados anteriores
        self.btn_analizar.config(state='normal')
        self.btn_exportar.config(state='disabled')
        self.btn_compatibilidad.config(state='normal')
        self._limpiar_resultados()
        self._set_estado(f"Archivo cargado: {mensaje}")

    def _analizar(self):
        """
        Ejecuta el análisis del documento cargado.

        Proceso:
            1. Llama a ReportAnalyzer.analyze()
            2. Puebla el árbol con los patrones encontrados
            3. Actualiza las estadísticas en el panel inferior
            4. Muestra advertencias si las hay
            5. Habilita el botón Exportar
        """
        resultados = self._analyzer.analyze()

        if not resultados:
            messagebox.showwarning('Sin contenido', 'No hay documento cargado.')
            return

        # Poblar árbol de resultados
        self._poblar_arbol(resultados['patrones'])

        # Actualizar estadísticas
        self._actualizar_estadisticas(resultados['estadisticas'])

        # Mostrar advertencias si existen
        advertencias = resultados.get('advertencias', [])
        if advertencias:
            messagebox.showwarning(
                'Advertencias del análisis',
                '\n'.join(f"⚠ {a}" for a in advertencias)
            )

        self.btn_exportar.config(state='normal')
        total = resultados['estadisticas']['total_datos_encontrados']
        self._set_estado(
            f"Análisis completado. {total} datos encontrados en el documento.")

    def _exportar(self):
        """
        Exporta el reporte del análisis a un archivo .txt.

        Abre un diálogo para que el usuario elija dónde guardar el archivo.
        Llama a ReportAnalyzer.export() con la ruta seleccionada.
        """
        if not self._analyzer.esta_analizado():
            messagebox.showwarning('Sin análisis', 'Ejecute el análisis primero.')
            return

        ruta_salida = filedialog.asksaveasfilename(
            title='Guardar reporte',
            defaultextension='.txt',
            filetypes=[('Archivos de texto', '*.txt')],
            initialfile=f"reporte_{self._ruta_actual.split('/')[-1]}"
        )

        if not ruta_salida:
            return  # El usuario canceló

        exito, resultado = self._analyzer.export(ruta_salida)

        if exito:
            messagebox.showinfo(
                'Reporte exportado',
                f"Reporte guardado correctamente en:\n{resultado}"
            )
            self._set_estado(f"Reporte exportado: {resultado}")
        else:
            messagebox.showerror('Error al exportar', resultado)
            self._set_estado(resultado, error=True)

    def _limpiar(self):
        """
        Resetea completamente la pestaña a su estado inicial.
        Borra el preview, el árbol, las estadísticas y el archivo cargado.
        """
        self.txt_preview.config(state='normal')
        self.txt_preview.delete('1.0', 'end')
        self.txt_preview.config(state='disabled')

        self._limpiar_resultados()
        self._ruta_actual = ''
        self.btn_analizar.config(state='disabled')
        self.btn_exportar.config(state='disabled')
        self.btn_compatibilidad.config(state='disabled')
        self._set_estado('Cargue un archivo .txt o .pdf para comenzar.')

    # ── Métodos de actualización visual ──────────────────────────────────────

    def _poblar_arbol(self, patrones: dict):
        """
        Llena el árbol de resultados con los patrones encontrados.

        Crea un nodo raíz por cada categoría y un hijo por cada
        valor encontrado. Si una categoría no tiene resultados,
        muestra '(ninguno)' en gris.

        Args:
            patrones (dict): Resultado de PatternMatcher.find_all()
        """
        # Limpiar árbol anterior
        for item in self.arbol.get_children():
            self.arbol.delete(item)

        etiquetas = {
            'correos'  : '📧 Correos electrónicos',
            'telefonos': '📞 Teléfonos',
            'cedulas'  : '🪪 Cédulas',
            'fechas'   : '📅 Fechas',
            'urls'     : '🔗 URLs',
            'placas'   : '🚗 Placas',
        }

        for clave, etiqueta in etiquetas.items():
            items = patrones.get(clave, [])
            texto_nodo = f"{etiqueta}  ({len(items)})"

            nodo = self.arbol.insert(
                '', 'end',
                text=texto_nodo,
                tags=('categoria',),
                open=True
            )

            if items:
                for valor in items:
                    self.arbol.insert(
                        nodo, 'end',
                        text='',
                        values=(valor,),
                        tags=('item',)
                    )
            else:
                self.arbol.insert(
                    nodo, 'end',
                    text='(ninguno)',
                    tags=('vacio',)
                )

    def _actualizar_estadisticas(self, estadisticas: dict):
        """
        Actualiza los labels del panel de estadísticas con los
        valores calculados por ReportAnalyzer.

        Args:
            estadisticas (dict): Diccionario de métricas del documento.
        """
        mapeo = {
            'lbl_archivo' : estadisticas.get('archivo', '—'),
            'lbl_fecha'   : estadisticas.get('fecha_analisis', '—'),
            'lbl_lineas'  : str(estadisticas.get('total_lineas', 0)),
            'lbl_palabras': str(estadisticas.get('total_palabras', 0)),
            'lbl_chars'   : str(estadisticas.get('total_caracteres', 0)),
            'lbl_datos'   : str(estadisticas.get('total_datos_encontrados', 0)),
            'lbl_densidad': f"{estadisticas.get('densidad_datos_pct', 0)}%",
        }

        for attr, valor in mapeo.items():
            self._labels_estadisticas[attr].config(text=valor)

    def _limpiar_resultados(self):
        """
        Borra el árbol de resultados y resetea las estadísticas a '—'.
        Se llama al cargar un nuevo archivo o al limpiar la pestaña.
        """
        for item in self.arbol.get_children():
            self.arbol.delete(item)

        for lbl in self._labels_estadisticas.values():
            lbl.config(text='—')

    def _set_estado(self, mensaje: str, error: bool = False):
        """
        Actualiza el texto de la barra de estado inferior.

        Args:
            mensaje (str): Texto a mostrar.
            error   (bool): True muestra el mensaje en rojo, False en gris.
        """
        color = '#c62828' if error else 'gray'
        self.lbl_estado.config(text=mensaje, foreground=color)