"""
Servicio de autenticación.

Este módulo contiene la lógica de negocio relacionada
con el inicio de sesión de los usuarios.
"""

from werkzeug.security import check_password_hash

from app.models.usuario_model import (
    obtener_usuario_por_email,
    obtener_comercio_usuario,
)

from core.auth import generar_token


def iniciar_sesion(email, password):
    """
    Valida las credenciales del usuario y genera un token JWT.
    """

    # Validar datos obligatorios
    if not email or not email.strip():
        raise ValueError("El email es obligatorio")

    if not password:
        raise ValueError("La contraseña es obligatoria")

    email = email.strip().lower()

    # Buscar usuario
    usuario = obtener_usuario_por_email(email)

    if not usuario:
        raise ValueError("Email o contraseña incorrectos")

    # Validar estado del usuario
    if not usuario.get("estado", False):
        raise PermissionError("El usuario se encuentra inactivo")

    # Validar contraseña
    password_hash = usuario.get("password")

    if not password_hash:
        raise ValueError("Email o contraseña incorrectos")

    try:
        password_valida = check_password_hash(
            password_hash,
            password
        )
    except (ValueError, TypeError):
        password_valida = False

    if not password_valida:
        raise ValueError("Email o contraseña incorrectos")

    # Validar comercio
    id_comercio = usuario.get("id_comercio")

    if not id_comercio:
        raise PermissionError(
            "El usuario no se encuentra asociado a un comercio"
        )

    comercio = obtener_comercio_usuario(id_comercio)

    if not comercio:
        raise PermissionError("Comercio no encontrado")

    if not comercio.get("estado", False):
        raise PermissionError("El comercio se encuentra inactivo")

    # Generar JWT
    token = generar_token(usuario)

    # Nunca devolver el hash de la contraseña
    usuario_publico = {
        "id_usuario": usuario["id_usuario"],
        "id_comercio": usuario["id_comercio"],
        "id_rol": usuario.get("id_rol"),
        "nombre_completo": usuario.get("nombre_completo"),
        "email": usuario["email"],
        "telefono": usuario.get("telefono"),
        "es_propietario": usuario.get("es_propietario", False),
    }

    comercio_publico = {
        "id_comercio": comercio["id_comercio"],
        "nombre_comercio": comercio["nombre_comercio"],
    }

    return {
        "token": token,
        "usuario": usuario_publico,
        "comercio": comercio_publico,
    }