"""
Utilidades de autenticación y autorización.

Este módulo se encarga de:
- Generar tokens JWT.
- Validar tokens JWT.
- Obtener el usuario autenticado.
- Validar que el usuario continúe activo.
- Validar que el comercio continúe activo.
- Proteger endpoints que requieren autenticación.
- Proteger operaciones exclusivas del propietario.
- Validar permisos según el rol del usuario.

El frontend nunca decide a qué comercio pertenece una operación.
El comercio se obtiene desde el usuario autenticado.
"""

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, request, jsonify, g

from app.models.usuario_model import (
    obtener_usuario_por_id,
    obtener_comercio_usuario,
)

from core.supabase_client import get_client


def generar_token(usuario):
    """
    Genera un token JWT para un usuario autenticado.

    El token identifica al usuario.
    Los datos actuales del usuario, comercio, rol y permisos
    se consultan nuevamente en cada petición protegida.
    """

    ahora = datetime.now(timezone.utc)

    payload = {
        "id_usuario": usuario["id_usuario"],
        "iat": ahora,
        "exp": ahora + timedelta(hours=24)
    }

    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256"
    )

    return token


def decodificar_token(token):
    """
    Valida y decodifica un token JWT.
    """

    return jwt.decode(
        token,
        current_app.config["JWT_SECRET_KEY"],
        algorithms=["HS256"]
    )


def login_requerido(func):
    """
    Protege un endpoint mediante JWT.

    Además de validar el token, consulta nuevamente al usuario
    y al comercio para verificar su estado actual.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        authorization = request.headers.get("Authorization")

        if not authorization:
            return jsonify({
                "error": "Token de autenticación requerido"
            }), 401

        partes = authorization.split()

        if len(partes) != 2 or partes[0].lower() != "bearer":
            return jsonify({
                "error": "Formato de token inválido"
            }), 401

        token = partes[1]

        try:
            payload = decodificar_token(token)

        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "La sesión ha expirado"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Token inválido"
            }), 401

        id_usuario = payload.get("id_usuario")

        if not id_usuario:
            return jsonify({
                "error": "Token inválido"
            }), 401

        # Consultar nuevamente al usuario.
        usuario = obtener_usuario_por_id(id_usuario)

        if not usuario:
            return jsonify({
                "error": "Usuario no encontrado"
            }), 401

        if not usuario.get("estado", False):
            return jsonify({
                "error": "El usuario se encuentra inactivo"
            }), 403

        id_comercio = usuario.get("id_comercio")

        if not id_comercio:
            return jsonify({
                "error": "El usuario no posee un comercio asociado"
            }), 403

        # Validar estado actual del comercio.
        comercio = obtener_comercio_usuario(id_comercio)

        if not comercio:
            return jsonify({
                "error": "Comercio no encontrado"
            }), 403

        if not comercio.get("estado", False):
            return jsonify({
                "error": "El comercio se encuentra inactivo"
            }), 403

        # Contexto disponible para los endpoints protegidos.
        g.usuario_actual = usuario
        g.comercio_actual = comercio

        g.id_usuario = usuario["id_usuario"]
        g.id_comercio = usuario["id_comercio"]
        g.id_rol = usuario.get("id_rol")
        g.es_propietario = usuario.get("es_propietario", False)

        return func(*args, **kwargs)

    return wrapper


def solo_propietario(func):
    """
    Permite acceder al endpoint únicamente al propietario
    del comercio autenticado.

    Debe utilizarse después de @login_requerido.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not getattr(g, "es_propietario", False):
            return jsonify({
                "error": "Esta operación es exclusiva del propietario"
            }), 403

        return func(*args, **kwargs)

    return wrapper


def permiso_requerido(codigo_permiso):
    """
    Verifica que el usuario autenticado tenga
    el permiso requerido para ejecutar una operación.

    El propietario tiene acceso automático a todos
    los permisos del sistema.

    Debe utilizarse después de @login_requerido.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            # El propietario tiene acceso total.
            if getattr(g, "es_propietario", False):
                return func(*args, **kwargs)

            id_rol = getattr(g, "id_rol", None)
            id_comercio = getattr(g, "id_comercio", None)

            # Un empleado sin rol no tiene permisos.
            if not id_rol:
                return jsonify({
                    "error": "No tiene permisos para realizar esta operación"
                }), 403

            supabase = get_client()

            # Validar que el rol exista, pertenezca al comercio
            # y continúe activo.
            rol_response = (
                supabase
                .table("roles")
                .select("id_rol")
                .eq("id_rol", id_rol)
                .eq("id_comercio", id_comercio)
                .eq("estado", True)
                .limit(1)
                .execute()
            )

            if not rol_response.data:
                return jsonify({
                    "error": "El rol del usuario no está activo"
                }), 403

            # Buscar el permiso solicitado en el catálogo.
            permiso_response = (
                supabase
                .table("permisos")
                .select("id_permiso")
                .eq("codigo", codigo_permiso)
                .limit(1)
                .execute()
            )

            if not permiso_response.data:
                return jsonify({
                    "error": "Permiso no configurado"
                }), 403

            id_permiso = permiso_response.data[0]["id_permiso"]

            # Verificar que el rol tenga asignado el permiso.
            relacion_response = (
                supabase
                .table("rol_permiso")
                .select("id_rol")
                .eq("id_rol", id_rol)
                .eq("id_permiso", id_permiso)
                .limit(1)
                .execute()
            )

            if not relacion_response.data:
                return jsonify({
                    "error": "No tiene permisos para realizar esta operación"
                }), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator




def usuario_tiene_permiso(codigo_permiso):
    """
    Verifica si el usuario autenticado posee un permiso específico.

    A diferencia de permiso_requerido(), esta función no bloquea
    la petición. Devuelve True o False y permite decidir qué
    información mostrar dentro de un endpoint.

    El propietario siempre tiene acceso.
    """

    # El propietario posee todos los permisos.
    if getattr(g, "es_propietario", False):
        return True

    id_rol = getattr(g, "id_rol", None)
    id_comercio = getattr(g, "id_comercio", None)

    if not id_rol or not id_comercio:
        return False

    supabase = get_client()

    # Verificar que el rol pertenezca al comercio
    # y continúe activo.
    rol_response = (
        supabase
        .table("roles")
        .select("id_rol")
        .eq("id_rol", id_rol)
        .eq("id_comercio", id_comercio)
        .eq("estado", True)
        .limit(1)
        .execute()
    )

    if not rol_response.data:
        return False

    # Buscar el permiso solicitado.
    permiso_response = (
        supabase
        .table("permisos")
        .select("id_permiso")
        .eq("codigo", codigo_permiso)
        .limit(1)
        .execute()
    )

    if not permiso_response.data:
        return False

    id_permiso = permiso_response.data[0]["id_permiso"]

    # Verificar relación rol → permiso.
    relacion_response = (
        supabase
        .table("rol_permiso")
        .select("id_rol")
        .eq("id_rol", id_rol)
        .eq("id_permiso", id_permiso)
        .limit(1)
        .execute()
    )

    return bool(relacion_response.data)