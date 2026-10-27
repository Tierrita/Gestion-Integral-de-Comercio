"""
Utilidades de autenticación.

Este módulo se encarga de:
- Generar tokens JWT.
- Validar tokens JWT.
- Obtener el usuario autenticado.
- Proteger endpoints que requieren autenticación.

El frontend nunca decide a qué comercio pertenece una operación.
El comercio se obtiene desde el token del usuario autenticado.
"""

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, request, jsonify, g


def generar_token(usuario):
    """
    Genera un token JWT para un usuario autenticado.
    """

    ahora = datetime.now(timezone.utc)

    payload = {
        "id_usuario": usuario["id_usuario"],
        "id_comercio": usuario["id_comercio"],
        "es_propietario": usuario.get("es_propietario", False),
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


"""
Utilidades de autenticación.

Este módulo se encarga de:
- Generar tokens JWT.
- Validar tokens JWT.
- Obtener el usuario autenticado.
- Validar que el usuario continúe activo.
- Validar que el comercio continúe activo.
- Proteger endpoints que requieren autenticación.
"""

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, request, jsonify, g

from app.models.usuario_model import (
    obtener_usuario_por_id,
    obtener_comercio_usuario,
)


def generar_token(usuario):
    """
    Genera un token JWT para un usuario autenticado.
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

        # Contexto disponible para el endpoint protegido.
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