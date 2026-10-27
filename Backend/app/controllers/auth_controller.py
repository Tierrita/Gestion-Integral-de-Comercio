"""
Controller de autenticación.

Este módulo recibe las peticiones HTTP relacionadas
con la autenticación y delega la lógica de negocio
al servicio correspondiente.
"""

from flask import request, jsonify, g

from app.services.auth_service import iniciar_sesion


def login():
    """
    Inicia sesión utilizando email y contraseña.
    """

    try:
        datos = request.get_json(silent=True) or {}

        email = datos.get("email")
        password = datos.get("password")

        resultado = iniciar_sesion(email, password)

        return jsonify({
            "message": "Inicio de sesión correcto",
            **resultado
        }), 200

    except PermissionError as error:
        return jsonify({
            "error": str(error)
        }), 403

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        print(f"Error inesperado en login: {error}")

        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def obtener_perfil_actual():
    """
    Devuelve información del usuario autenticado
    y del comercio al que pertenece.
    """

    usuario = g.usuario_actual
    comercio = g.comercio_actual

    return jsonify({
        "usuario": {
            "id_usuario": usuario["id_usuario"],
            "id_comercio": usuario["id_comercio"],
            "id_rol": usuario.get("id_rol"),
            "nombre_completo": usuario.get("nombre_completo"),
            "email": usuario["email"],
            "telefono": usuario.get("telefono"),
            "direccion": usuario.get("direccion"),
            "dni": usuario.get("dni"),
            "es_propietario": usuario.get("es_propietario", False),
            "estado": usuario.get("estado")
        },
        "comercio": {
            "id_comercio": comercio["id_comercio"],
            "nombre_comercio": comercio["nombre_comercio"],
            "estado": comercio["estado"]
        }
    }), 200