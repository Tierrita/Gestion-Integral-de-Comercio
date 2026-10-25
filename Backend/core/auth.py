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


def login_requerido(func):
    """
    Decorador para proteger endpoints.

    Lee:
        Authorization: Bearer <token>

    Si el token es válido, guarda los datos básicos del usuario
    autenticado en flask.g.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        authorization = request.headers.get("Authorization")

        if not authorization:
            return jsonify({
                "mensaje": "Token de autenticación requerido"
            }), 401

        partes = authorization.split()

        if len(partes) != 2 or partes[0].lower() != "bearer":
            return jsonify({
                "mensaje": "Formato de token inválido"
            }), 401

        token = partes[1]

        try:
            payload = decodificar_token(token)

            g.id_usuario = payload["id_usuario"]
            g.id_comercio = payload["id_comercio"]
            g.es_propietario = payload.get("es_propietario", False)

        except jwt.ExpiredSignatureError:
            return jsonify({
                "mensaje": "La sesión ha expirado"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "mensaje": "Token inválido"
            }), 401

        return func(*args, **kwargs)

    return wrapper
