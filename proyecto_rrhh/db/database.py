"""
database.py — Inicialización y conexión SQLite para ValidaRH.
"""
import sqlite3
import pathlib
from config import DB_PATH


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def inicializar_bd() -> None:
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre              TEXT    NOT NULL,
            correo              TEXT    UNIQUE NOT NULL,
            contrasena_hash     TEXT    NOT NULL,
            rol                 TEXT    NOT NULL CHECK(rol IN ('reclutador','postulante')),
            cedula              TEXT,
            telefono            TEXT,
            usuario             TEXT    UNIQUE,
            fecha_nacimiento    TEXT,
            fecha_registro      TEXT    NOT NULL,
            verificado          INTEGER DEFAULT 0,
            codigo_verificacion TEXT,
            cv_texto            TEXT,
            cv_nombre           TEXT
        );

        CREATE TABLE IF NOT EXISTS perfiles_laborales (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            id_reclutador   INTEGER NOT NULL,
            titulo          TEXT    NOT NULL,
            descripcion     TEXT    NOT NULL,
            keywords        TEXT,
            fecha_creacion  TEXT    NOT NULL,
            activo          INTEGER DEFAULT 1,
            FOREIGN KEY (id_reclutador) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS historial_analisis (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario       INTEGER NOT NULL,
            nombre_candidato TEXT,
            nombre_archivo   TEXT,
            id_perfil        INTEGER,
            titulo_perfil    TEXT,
            score_global     INTEGER,
            resultado_json   TEXT,
            fecha_analisis   TEXT    NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
        );

        -- CVs registrados por el postulante (puede tener varios)
        CREATE TABLE IF NOT EXISTS hojas_de_vida (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario      INTEGER NOT NULL,
            nombre          TEXT    NOT NULL,
            cv_texto        TEXT    NOT NULL,
            cv_nombre       TEXT,
            descripcion     TEXT,
            patrones_json   TEXT,
            fecha_registro  TEXT    NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
        );

        -- Vacantes guardadas por el postulante para comparar con sus CVs
        CREATE TABLE IF NOT EXISTS vacantes_postulante (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario      INTEGER NOT NULL,
            titulo          TEXT    NOT NULL,
            empresa         TEXT,
            ubicacion       TEXT,
            modalidad       TEXT,
            descripcion     TEXT    NOT NULL,
            keywords        TEXT,
            fecha_registro  TEXT    NOT NULL,
            activo          INTEGER DEFAULT 1,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
        );
        """)
