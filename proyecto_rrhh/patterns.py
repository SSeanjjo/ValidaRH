"""
patterns.py
===========
Patrones de expresiones regulares de referencia para ValidaRH.

Nota: La validación principal del sistema se realiza mediante autómatas
de estados finitos en PatternMatcher (sin uso de la librería re).
Este módulo documenta los patrones equivalentes en regex como referencia
académica y para búsqueda rápida en texto (find_all).
"""

import re

# ── Validadores (full-match) ──────────────────────────────────────────────────

VALIDATORS = {
    "correo":   re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'),
    "telefono": re.compile(r'^(\+57)?[0-9]{10}$'),
    "cedula":   re.compile(r'^[1-9][0-9]{4,9}$'),
    "fecha":    re.compile(r'^\d{2}[/\-]\d{2}[/\-]\d{4}$'),
    "url":      re.compile(r'^https?://[a-zA-Z0-9][a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}(/\S*)?$'),
    "placa":    re.compile(r'^[A-Z]{3}[0-9]{2,3}$'),
}

# ── Buscadores en texto libre ─────────────────────────────────────────────────

FINDERS = {
    "correos":   re.compile(r'[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'),
    "telefonos": re.compile(r'(?<!\d)(?:\+57)?[0-9]{10}(?!\d)'),
    "cedulas":   re.compile(r'(?<!\d)[1-9][0-9]{4,9}(?!\d)'),
    "fechas":    re.compile(r'\b\d{2}[/\-]\d{2}[/\-]\d{4}\b'),
    "urls":      re.compile(r'https?://[a-zA-Z0-9][a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}(?:/\S*)?'),
    "placas":    re.compile(r'\b[A-Z]{3}[0-9]{2,3}\b'),
}

# ── Etiquetas legibles ────────────────────────────────────────────────────────

LABELS = {
    "correo":   "Correo electrónico",
    "telefono": "Teléfono",
    "cedula":   "Cédula",
    "fecha":    "Fecha (dd/mm/aaaa)",
    "url":      "URL",
    "placa":    "Placa",
}
