"""
tab_pruebas.py
==============
Pestaña C — Casos de prueba del sistema ValidaRH.

Contexto: Sistema ValidaRH — Gestión de Recursos Humanos
Proyecto: Búsqueda y validación de patrones en textos y sistemas interactivos

Descripción:
    Implementa la interfaz gráfica de la pestaña de pruebas automatizadas.
    Carga los casos de prueba desde data/casos_prueba.csv, ejecuta cada
    validación contra PatternMatcher y muestra los resultados en una tabla
    con codificación visual (verde = OK, rojo = FALLO).

    Esta pestaña sirve como evidencia visual de funcionamiento para la
    rúbrica del proyecto, complementando las pruebas automáticas de
    la carpeta tests/.

Layout:
    ┌─────────────────────────────────────────────┐
    │  Encabezado + botón Ejecutar pruebas        │
    ├─────────────────────────────────────────────┤
    │  Filtros por tipo de patrón                 │
    ├─────────────────────────────────────────────┤
    │  Tabla de resultados (scrollable)           │
    │  Tipo | Entrada | Esperado | Obtenido |     │
    │  Estado | Descripción                       │
    ├─────────────────────────────────────────────┤
    │  Barra de resumen: X/Y casos pasados        │
    └─────────────────────────────────────────────┘

Autor: [Tu nombre]
Fecha: [Fecha]
Versión: 1.0
"""

import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox
from logic.pattern_matcher import PatternMatcher


class TabPruebas(ttk.Frame):
    """
    Pestaña C del Notebook — Visualizador de casos de prueba.

    Carga casos desde data/casos_prueba.csv, los ejecuta contra
    PatternMatcher y muestra los resultados con codificación de color.
    Incluye filtros por tipo de patrón y resumen estadístico.

    Attributes:
        _matcher      : instancia de PatternMatcher para ejecutar validaciones
        _todos_casos  : lista completa de casos cargados del CSV
        _filtro_actual: tipo de patrón actualmente filtrado ('todos' por defecto)
    """

    # Mapeo de clave CSV → función validadora de PatternMatcher
    _VALIDADORES = {
        'correo'  : 'es_correo',
        'telefono': 'es_telefono_co',
        'cedula'  : 'es_cedula',
        'fecha'   : 'es_fecha',
        'url'     : 'es_url',
        'placa'   : 'es_placa_co',
    }

    # Etiquetas legibles por tipo
    _ETIQUETAS = {
        'correo'  : '📧 Correo',
        'telefono': '📞 Teléfono',
        'cedula'  : '🪪 Cédula',
        'fecha'   : '📅 Fecha',
        'url'     : '🔗 URL',
        'placa'   : '🚗 Placa',
    }

    def __init__(self, parent):
        super().__init__(parent)
        self._matcher       = PatternMatcher()
        self._todos_casos   = []
        self._filtro_actual = 'todos'
        self._construir_ui()

    # ── Construcción de la interfaz ───────────────────────────────────────────

    def _construir_ui(self):
        """
        Construye todos los elementos visuales de la pestaña en orden:
            1. Encabezado con título y botón principal
            2. Barra de filtros por tipo
            3. Tabla de resultados
            4. Barra de resumen inferior
        """
        self._construir_encabezado()
        self._construir_filtros()
        self._construir_tabla()
        self._construir_barra_resumen()

    def _construir_encabezado(self):
        """
        Construye el encabezado con título, descripción y botón
        para ejecutar todas las pruebas.
        """
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=16, pady=(14, 6))

        # Columna izquierda: títulos
        frame_texto = ttk.Frame(frame)
        frame_texto.pack(side='left', fill='x', expand=True)

        ttk.Label(
            frame_texto,
            text='Casos de Prueba — PatternMatcher',
            font=('Helvetica', 13, 'bold')
        ).pack(anchor='w')

        ttk.Label(
            frame_texto,
            text='Casos cargados desde data/casos_prueba.csv',
            foreground='gray',
            font=('Helvetica', 9)
        ).pack(anchor='w')

        # Columna derecha: botón principal
        self.btn_ejecutar = ttk.Button(
            frame,
            text='▶  Ejecutar todas las pruebas',
            command=self._ejecutar_pruebas
        )
        self.btn_ejecutar.pack(side='right', padx=4)

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=16, pady=6)

    def _construir_filtros(self):
        """
        Construye la barra de filtros que permite mostrar solo los casos
        de un tipo de patrón específico.

        Botones de filtro:
            Todos | Correo | Teléfono | Cédula | Fecha | URL | Placa
        """
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=16, pady=(0, 6))

        ttk.Label(
            frame,
            text='Filtrar por tipo:',
            font=('Helvetica', 9, 'bold')
        ).pack(side='left', padx=(0, 8))

        self._botones_filtro = {}

        # Botón "Todos"
        btn_todos = ttk.Button(
            frame,
            text='Todos',
            command=lambda: self._aplicar_filtro('todos')
        )
        btn_todos.pack(side='left', padx=2)
        self._botones_filtro['todos'] = btn_todos

        # Un botón por cada tipo de patrón
        for clave, etiqueta in self._ETIQUETAS.items():
            btn = ttk.Button(
                frame,
                text=etiqueta,
                command=lambda c=clave: self._aplicar_filtro(c)
            )
            btn.pack(side='left', padx=2)
            self._botones_filtro[clave] = btn

    def _construir_tabla(self):
        """
        Construye la tabla principal (Treeview) que muestra los resultados
        de cada caso de prueba con las columnas:
            Tipo | Entrada | Esperado | Obtenido | Estado | Descripción

        Codificación de color:
            Verde claro → caso pasado (OK)
            Rojo claro  → caso fallido (FALLO)
        """
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True, padx=16, pady=4)

        columnas = ('tipo', 'entrada', 'esperado', 'obtenido', 'estado', 'descripcion')

        self.tabla = ttk.Treeview(
            frame,
            columns=columnas,
            show='headings',
            height=16
        )

        # Configurar encabezados y anchos
        config_columnas = {
            'tipo'       : ('Tipo',        90),
            'entrada'    : ('Entrada',     160),
            'esperado'   : ('Esperado',    80),
            'obtenido'   : ('Obtenido',    80),
            'estado'     : ('Estado',      70),
            'descripcion': ('Descripción', 220),
        }

        for col, (titulo, ancho) in config_columnas.items():
            self.tabla.heading(col, text=titulo,
                               command=lambda c=col: self._ordenar_por(c))
            self.tabla.column(col, width=ancho, anchor='center'
                              if col != 'descripcion' else 'w')

        # Tags de color por resultado
        self.tabla.tag_configure(
            'ok',
            background='#e8f5e9',
            foreground='#1b5e20'
        )
        self.tabla.tag_configure(
            'fallo',
            background='#ffebee',
            foreground='#b71c1c'
        )
        self.tabla.tag_configure(
            'sin_validador',
            background='#fff8e1',
            foreground='#e65100'
        )

        # Scrollbars
        scroll_v = ttk.Scrollbar(frame, orient='vertical',
                                  command=self.tabla.yview)
        scroll_h = ttk.Scrollbar(frame, orient='horizontal',
                                  command=self.tabla.xview)
        self.tabla.configure(
            yscrollcommand=scroll_v.set,
            xscrollcommand=scroll_h.set
        )

        self.tabla.pack(side='left', fill='both', expand=True)
        scroll_v.pack(side='left', fill='y')

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=16, pady=2)

    def _construir_barra_resumen(self):
        """
        Construye la barra inferior que muestra el resumen de resultados:
            - Total de casos ejecutados
            - Casos pasados y fallidos
            - Porcentaje de éxito
            - Barra de progreso visual
        """
        frame = ttk.Frame(self)
        frame.pack(fill='x', padx=16, pady=(4, 12))

        # Label de resumen textual
        self.lbl_resumen = ttk.Label(
            frame,
            text='Ejecute las pruebas para ver el resumen.',
            foreground='gray',
            font=('Helvetica', 9)
        )
        self.lbl_resumen.pack(anchor='w')

        # Barra de progreso
        self.barra_resumen = ttk.Progressbar(
            frame,
            maximum=100,
            value=0,
            mode='determinate',
            length=400
        )
        self.barra_resumen.pack(anchor='w', pady=(2, 0))

    # ── Lógica de ejecución ───────────────────────────────────────────────────

    def _cargar_casos_csv(self) -> list:
        """
        Carga los casos de prueba desde data/casos_prueba.csv.

        Returns:
            list: Lista de dicts con claves:
                  tipo, entrada, esperado (bool), descripcion.
                  Lista vacía si el archivo no existe o tiene errores.
        """
        ruta = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'casos_prueba.csv')

        if not os.path.exists(ruta):
            messagebox.showerror(
                'Archivo no encontrado',
                f'No se encontró el archivo de casos:\n{ruta}\n\n'
                'Verifique que data/casos_prueba.csv exista.'
            )
            return []

        casos = []
        try:
            with open(ruta, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for fila in reader:
                    casos.append({
                        'tipo'       : fila['tipo'].strip(),
                        'entrada'    : fila['entrada'].strip(),
                        'esperado'   : fila['esperado'].strip() == 'True',
                        'descripcion': fila['descripcion'].strip(),
                    })
        except Exception as e:
            messagebox.showerror('Error al leer CSV', str(e))
            return []

        return casos

    def _ejecutar_caso(self, caso: dict) -> dict:
        """
        Ejecuta un único caso de prueba contra el validador correspondiente.

        Busca el método validador en PatternMatcher según el tipo del caso.
        Si no existe validador para el tipo, marca el caso como advertencia.

        Args:
            caso (dict): Caso con claves tipo, entrada, esperado, descripcion.

        Returns:
            dict: Caso original enriquecido con:
                  - 'obtenido' (bool): resultado real del validador
                  - 'ok'       (bool): True si obtenido == esperado
                  - 'tag'      (str) : 'ok' | 'fallo' | 'sin_validador'
        """
        nombre_metodo = self._VALIDADORES.get(caso['tipo'])

        if not nombre_metodo:
            return {**caso, 'obtenido': None, 'ok': False, 'tag': 'sin_validador'}

        funcion = getattr(self._matcher, nombre_metodo, None)

        if not funcion:
            return {**caso, 'obtenido': None, 'ok': False, 'tag': 'sin_validador'}

        obtenido = funcion(caso['entrada'])
        ok       = obtenido == caso['esperado']

        return {**caso, 'obtenido': obtenido, 'ok': ok,
                'tag': 'ok' if ok else 'fallo'}

    def _ejecutar_pruebas(self):
        """
        Carga y ejecuta todos los casos de prueba del CSV.

        Proceso:
            1. Carga casos desde CSV
            2. Ejecuta cada caso con _ejecutar_caso()
            3. Guarda todos los resultados en _todos_casos
            4. Aplica el filtro actual para mostrar en tabla
            5. Actualiza el resumen con estadísticas globales
        """
        casos = self._cargar_casos_csv()

        if not casos:
            return

        # Ejecutar todos los casos
        self._todos_casos = [self._ejecutar_caso(c) for c in casos]

        # Mostrar con el filtro activo
        self._aplicar_filtro(self._filtro_actual)

        # Actualizar resumen global (siempre sobre el total, no el filtro)
        self._actualizar_resumen(self._todos_casos)

    # ── Filtrado y visualización ──────────────────────────────────────────────

    def _aplicar_filtro(self, tipo: str):
        """
        Filtra la tabla para mostrar solo los casos del tipo indicado.

        Args:
            tipo (str): Clave de tipo ('todos', 'correo', 'telefono', etc.)
        """
        self._filtro_actual = tipo

        if tipo == 'todos':
            casos_filtrados = self._todos_casos
        else:
            casos_filtrados = [c for c in self._todos_casos if c['tipo'] == tipo]

        self._poblar_tabla(casos_filtrados)

    def _poblar_tabla(self, casos: list):
        """
        Llena la tabla con la lista de casos proporcionada.

        Borra las filas anteriores y reconstruye la tabla con
        los casos filtrados, aplicando el tag de color correspondiente.

        Args:
            casos (list): Lista de casos con resultados ejecutados.
        """
        # Limpiar tabla
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        if not casos:
            self.tabla.insert('', 'end', values=(
                '—', 'Sin casos para mostrar', '—', '—', '—', '—'
            ))
            return

        for caso in casos:
            esperado_txt = 'Válido'   if caso['esperado']  else 'Inválido'
            obtenido_txt = '—'
            estado_txt   = '—'

            if caso.get('obtenido') is not None:
                obtenido_txt = 'Válido' if caso['obtenido'] else 'Inválido'
                estado_txt   = '✓ OK'  if caso['ok']       else '✗ FALLO'
            elif caso['tag'] == 'sin_validador':
                obtenido_txt = 'Sin validador'
                estado_txt   = '⚠ N/A'

            self.tabla.insert('', 'end', values=(
                self._ETIQUETAS.get(caso['tipo'], caso['tipo']),
                caso['entrada'],
                esperado_txt,
                obtenido_txt,
                estado_txt,
                caso['descripcion'],
            ), tags=(caso['tag'],))

    def _actualizar_resumen(self, casos: list):
        """
        Calcula y muestra las estadísticas globales de la ejecución.

        Calcula:
            - Total de casos ejecutados
            - Casos pasados (ok == True)
            - Casos fallidos
            - Porcentaje de éxito
        Actualiza la barra de progreso y el label de resumen.

        Args:
            casos (list): Lista completa de casos con resultados.
        """
        total    = len(casos)
        pasados  = sum(1 for c in casos if c.get('ok'))
        fallidos = total - pasados
        pct      = round((pasados / total) * 100, 1) if total else 0

        self.barra_resumen['value'] = pct

        color = '#1b5e20' if pct == 100 else ('#e65100' if pct < 50 else '#1a237e')

        self.lbl_resumen.config(
            text=(
                f"Total: {total} casos  |  "
                f"✓ Pasados: {pasados}  |  "
                f"✗ Fallidos: {fallidos}  |  "
                f"Éxito: {pct}%"
            ),
            foreground=color,
            font=('Helvetica', 9, 'bold')
        )

    def _ordenar_por(self, columna: str):
        """
        Ordena las filas de la tabla al hacer clic en un encabezado.

        Alterna entre orden ascendente y descendente en cada clic.
        Funciona sobre los casos actualmente visibles (respeta el filtro).

        Args:
            columna (str): Nombre de la columna por la que ordenar.
        """
        items = [
            (self.tabla.set(item, columna), item)
            for item in self.tabla.get_children()
        ]

        # Detectar orden actual y alternar
        reverso = getattr(self, f'_orden_{columna}', False)
        items.sort(reverse=reverso)
        setattr(self, f'_orden_{columna}', not reverso)

        for index, (_, item) in enumerate(items):
            self.tabla.move(item, '', index)