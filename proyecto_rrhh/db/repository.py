"""
repository.py — Operaciones CRUD para todas las entidades de ValidaRH.
"""
import hashlib
import datetime
import json
from db.database import get_conn


# ── Utilidades ────────────────────────────────────────────────────────────────

def _hash(contrasena: str) -> str:
    return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

def _ahora() -> str:
    return datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')


# ── Repositorio de usuarios ───────────────────────────────────────────────────

class UsuarioRepo:

    @staticmethod
    def crear(nombre: str, correo: str, contrasena: str, rol: str,
              cedula: str = '', telefono: str = '', usuario: str = '',
              fecha_nacimiento: str = '', codigo: str = '') -> tuple:
        try:
            with get_conn() as conn:
                conn.execute(
                    """INSERT INTO usuarios
                       (nombre, correo, contrasena_hash, rol, cedula, telefono,
                        usuario, fecha_nacimiento, fecha_registro,
                        verificado, codigo_verificacion)
                       VALUES (?,?,?,?,?,?,?,?,?,0,?)""",
                    (nombre, correo, _hash(contrasena), rol,
                     cedula, telefono, usuario, fecha_nacimiento,
                     _ahora(), codigo)
                )
            return True, 'Usuario creado correctamente.'
        except Exception as e:
            if 'UNIQUE' in str(e):
                err = str(e).lower()
                if 'correo' in err and 'rol' in err:
                    return False, 'Ya tienes una cuenta con este correo para ese rol.'
                if 'usuario' in err:
                    return False, 'El nombre de usuario ya está en uso.'
            return False, f'Error al crear usuario: {e}'

    @staticmethod
    def buscar_por_correo(correo: str) -> dict | None:
        with get_conn() as conn:
            row = conn.execute(
                'SELECT * FROM usuarios WHERE correo = ?', (correo,)
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def verificar_credenciales(correo: str, contrasena: str) -> dict | None:
        u = UsuarioRepo.buscar_por_correo(correo)
        if u and u['contrasena_hash'] == _hash(contrasena):
            return u
        return None

    @staticmethod
    def verificar_credenciales_multi(correo: str, contrasena: str) -> list:
        """Retorna todas las cuentas con ese correo cuya contraseña coincida."""
        with get_conn() as conn:
            rows = conn.execute(
                'SELECT * FROM usuarios WHERE correo=? AND contrasena_hash=?',
                (correo, _hash(contrasena))
            ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def marcar_verificado(correo: str) -> None:
        with get_conn() as conn:
            conn.execute(
                "UPDATE usuarios SET verificado=1, codigo_verificacion='' WHERE correo=?",
                (correo,)
            )

    @staticmethod
    def actualizar_codigo(correo: str, codigo: str) -> None:
        with get_conn() as conn:
            conn.execute(
                'UPDATE usuarios SET codigo_verificacion=? WHERE correo=?',
                (codigo, correo)
            )

    @staticmethod
    def guardar_cv(id_usuario: int, cv_texto: str, cv_nombre: str) -> None:
        with get_conn() as conn:
            conn.execute(
                'UPDATE usuarios SET cv_texto=?, cv_nombre=? WHERE id=?',
                (cv_texto, cv_nombre, id_usuario)
            )

    @staticmethod
    def listar_postulantes() -> list:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT id, nombre, correo, cedula, telefono, cv_nombre, fecha_registro "
                "FROM usuarios WHERE rol='postulante' ORDER BY fecha_registro DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def actualizar_perfil(id_usuario: int, nombre: str, telefono: str,
                          usuario: str) -> tuple:
        """Actualiza los campos editables del perfil (no correo ni cédula)."""
        try:
            with get_conn() as conn:
                conn.execute(
                    'UPDATE usuarios SET nombre=?, telefono=?, usuario=? WHERE id=?',
                    (nombre, telefono, usuario, id_usuario)
                )
            return True, 'Perfil actualizado correctamente.'
        except Exception as e:
            if 'UNIQUE' in str(e):
                return False, 'El nombre de usuario ya está en uso.'
            return False, f'Error: {e}'

    @staticmethod
    def actualizar_candidato(id_usuario: int, nombre: str, correo: str,
                             cedula: str, telefono: str) -> tuple:
        try:
            with get_conn() as conn:
                conn.execute(
                    'UPDATE usuarios SET nombre=?, correo=?, cedula=?, telefono=? WHERE id=?',
                    (nombre, correo, cedula, telefono, id_usuario)
                )
            return True, 'Candidato actualizado correctamente.'
        except Exception as e:
            if 'UNIQUE' in str(e):
                return False, 'Ya existe un postulante con ese correo.'
            return False, f'Error: {e}'

    @staticmethod
    def eliminar_candidato(id_usuario: int) -> None:
        with get_conn() as conn:
            conn.execute(
                'DELETE FROM historial_analisis WHERE id_usuario=?', (id_usuario,))
            conn.execute(
                'DELETE FROM hojas_de_vida WHERE id_usuario=?', (id_usuario,))
            conn.execute(
                'DELETE FROM vacantes_postulante WHERE id_usuario=?', (id_usuario,))
            conn.execute(
                'DELETE FROM usuarios WHERE id=?', (id_usuario,))

    @staticmethod
    def cambiar_contrasena(id_usuario: int, actual: str, nueva: str) -> tuple:
        """Verifica la contraseña actual y actualiza a la nueva."""
        with get_conn() as conn:
            row = conn.execute(
                'SELECT contrasena_hash FROM usuarios WHERE id=?', (id_usuario,)
            ).fetchone()
        if not row or row['contrasena_hash'] != _hash(actual):
            return False, 'La contraseña actual es incorrecta.'
        with get_conn() as conn:
            conn.execute(
                'UPDATE usuarios SET contrasena_hash=? WHERE id=?',
                (_hash(nueva), id_usuario)
            )
        return True, 'Contraseña actualizada correctamente.'


# ── Repositorio de perfiles laborales ────────────────────────────────────────

class PerfilRepo:

    @staticmethod
    def crear(id_reclutador: int, titulo: str, descripcion: str,
              keywords: list) -> tuple:
        try:
            with get_conn() as conn:
                conn.execute(
                    """INSERT INTO perfiles_laborales
                       (id_reclutador, titulo, descripcion, keywords, fecha_creacion)
                       VALUES (?,?,?,?,?)""",
                    (id_reclutador, titulo, descripcion,
                     json.dumps(keywords, ensure_ascii=False), _ahora())
                )
            return True, 'Perfil creado correctamente.'
        except Exception as e:
            return False, f'Error: {e}'

    @staticmethod
    def listar_activos() -> list:
        with get_conn() as conn:
            rows = conn.execute(
                """SELECT p.id, p.titulo, p.descripcion, p.keywords,
                          p.fecha_creacion, u.nombre AS reclutador
                   FROM perfiles_laborales p
                   JOIN usuarios u ON u.id = p.id_reclutador
                   WHERE p.activo=1
                   ORDER BY p.fecha_creacion DESC"""
            ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d['keywords'] = json.loads(d['keywords']) if d['keywords'] else []
            result.append(d)
        return result

    @staticmethod
    def listar_por_reclutador(id_reclutador: int) -> list:
        with get_conn() as conn:
            rows = conn.execute(
                """SELECT * FROM perfiles_laborales
                   WHERE id_reclutador=? AND activo=1
                   ORDER BY fecha_creacion DESC""",
                (id_reclutador,)
            ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d['keywords'] = json.loads(d['keywords']) if d['keywords'] else []
            result.append(d)
        return result

    @staticmethod
    def eliminar(id_perfil: int) -> None:
        with get_conn() as conn:
            conn.execute(
                'UPDATE perfiles_laborales SET activo=0 WHERE id=?', (id_perfil,)
            )

    @staticmethod
    def obtener(id_perfil: int) -> dict | None:
        with get_conn() as conn:
            row = conn.execute(
                'SELECT * FROM perfiles_laborales WHERE id=?', (id_perfil,)
            ).fetchone()
        if not row:
            return None
        d = dict(row)
        d['keywords'] = json.loads(d['keywords']) if d['keywords'] else []
        return d


# ── Repositorio de historial ──────────────────────────────────────────────────

class HistorialRepo:

    @staticmethod
    def guardar(id_usuario: int, nombre_candidato: str, nombre_archivo: str,
                id_perfil: int | None, titulo_perfil: str,
                score_global: int, resultado: dict) -> None:
        with get_conn() as conn:
            conn.execute(
                """INSERT INTO historial_analisis
                   (id_usuario, nombre_candidato, nombre_archivo,
                    id_perfil, titulo_perfil, score_global,
                    resultado_json, fecha_analisis)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (id_usuario, nombre_candidato, nombre_archivo,
                 id_perfil, titulo_perfil, score_global,
                 json.dumps(resultado, ensure_ascii=False), _ahora())
            )

    @staticmethod
    def listar_por_usuario(id_usuario: int) -> list:
        with get_conn() as conn:
            rows = conn.execute(
                """SELECT id, nombre_candidato, nombre_archivo, titulo_perfil,
                          score_global, fecha_analisis
                   FROM historial_analisis
                   WHERE id_usuario=?
                   ORDER BY fecha_analisis DESC""",
                (id_usuario,)
            ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def obtener_detalle(id_analisis: int) -> dict | None:
        with get_conn() as conn:
            row = conn.execute(
                'SELECT * FROM historial_analisis WHERE id=?', (id_analisis,)
            ).fetchone()
        if not row:
            return None
        d = dict(row)
        d['resultado'] = json.loads(d['resultado_json']) if d['resultado_json'] else {}
        return d


# ── Repositorio de hojas de vida (postulante) ─────────────────────────────────

class HojaDeVidaRepo:
    """CRUD para los CVs registrados por cada postulante."""

    @staticmethod
    def crear(id_usuario: int, nombre: str, cv_texto: str,
              cv_nombre: str, descripcion: str, patrones: dict) -> tuple:
        """Guarda un nuevo CV junto con sus patrones extraídos."""
        try:
            with get_conn() as conn:
                conn.execute(
                    """INSERT INTO hojas_de_vida
                       (id_usuario, nombre, cv_texto, cv_nombre, descripcion,
                        patrones_json, fecha_registro)
                       VALUES (?,?,?,?,?,?,?)""",
                    (id_usuario, nombre, cv_texto, cv_nombre, descripcion,
                     json.dumps(patrones, ensure_ascii=False), _ahora())
                )
            return True, 'CV registrado correctamente.'
        except Exception as e:
            return False, f'Error: {e}'

    @staticmethod
    def listar_por_usuario(id_usuario: int) -> list:
        """Retorna todos los CVs de un usuario, sin el texto completo."""
        with get_conn() as conn:
            rows = conn.execute(
                """SELECT id, nombre, cv_nombre, descripcion, fecha_registro
                   FROM hojas_de_vida WHERE id_usuario=?
                   ORDER BY fecha_registro DESC""",
                (id_usuario,)
            ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def obtener(id_cv: int) -> dict | None:
        """Retorna un CV completo (incluyendo texto y patrones)."""
        with get_conn() as conn:
            row = conn.execute(
                'SELECT * FROM hojas_de_vida WHERE id=?', (id_cv,)
            ).fetchone()
        if not row:
            return None
        d = dict(row)
        d['patrones'] = json.loads(d['patrones_json']) if d['patrones_json'] else {}
        return d

    @staticmethod
    def eliminar(id_cv: int) -> None:
        with get_conn() as conn:
            conn.execute('DELETE FROM hojas_de_vida WHERE id=?', (id_cv,))


# ── Repositorio de vacantes del postulante ────────────────────────────────────

class VacanteRepo:
    """CRUD para las vacantes que el postulante guarda para comparar."""

    @staticmethod
    def crear(id_usuario: int, titulo: str, empresa: str, ubicacion: str,
              modalidad: str, descripcion: str, keywords: list) -> tuple:
        """Guarda una nueva vacante con sus keywords extraídas."""
        try:
            with get_conn() as conn:
                conn.execute(
                    """INSERT INTO vacantes_postulante
                       (id_usuario, titulo, empresa, ubicacion, modalidad,
                        descripcion, keywords, fecha_registro)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (id_usuario, titulo, empresa, ubicacion, modalidad,
                     descripcion, json.dumps(keywords, ensure_ascii=False),
                     _ahora())
                )
            return True, 'Vacante registrada correctamente.'
        except Exception as e:
            return False, f'Error: {e}'

    @staticmethod
    def listar_por_usuario(id_usuario: int) -> list:
        """Retorna las vacantes activas del usuario."""
        with get_conn() as conn:
            rows = conn.execute(
                """SELECT id, titulo, empresa, ubicacion, modalidad,
                          keywords, fecha_registro
                   FROM vacantes_postulante
                   WHERE id_usuario=? AND activo=1
                   ORDER BY fecha_registro DESC""",
                (id_usuario,)
            ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d['keywords'] = json.loads(d['keywords']) if d['keywords'] else []
            result.append(d)
        return result

    @staticmethod
    def obtener(id_vac: int) -> dict | None:
        """Retorna una vacante completa incluyendo descripción."""
        with get_conn() as conn:
            row = conn.execute(
                'SELECT * FROM vacantes_postulante WHERE id=?', (id_vac,)
            ).fetchone()
        if not row:
            return None
        d = dict(row)
        d['keywords'] = json.loads(d['keywords']) if d['keywords'] else []
        return d

    @staticmethod
    def eliminar(id_vac: int) -> None:
        with get_conn() as conn:
            conn.execute(
                'UPDATE vacantes_postulante SET activo=0 WHERE id=?', (id_vac,)
            )
