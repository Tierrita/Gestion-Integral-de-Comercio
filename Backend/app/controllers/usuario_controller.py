"""
Controller de usuarios.

Se encarga de recibir las peticiones HTTP relacionadas
con usuarios y empleados del comercio.
"""

from flask import jsonify, g

from app.services.usuario_service import (
    listar_usuarios,
    obtener_usuario,
    crear_usuario,
    modificar_usuario,
    cambiar_estado_usuario,
    cambiar_rol_usuario,
    restablecer_password_usuario,

)

def obtener_usuarios_controller():
    """
    Obtiene todos los usuarios pertenecientes
    al comercio actualmente autenticado.
    """

    try:
        usuarios = listar_usuarios(g.id_comercio)

        return jsonify({
            "usuarios": usuarios
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


def obtener_usuario_controller(id_usuario):
    """
    Obtiene un usuario específico perteneciente
    al comercio actualmente autenticado.
    """

    try:
        usuario = obtener_usuario(
            id_usuario,
            g.id_comercio
        )

        return jsonify({
            "usuario": usuario
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500



def crear_usuario_controller():
    """
    Crea un nuevo empleado dentro del comercio
    actualmente autenticado.
    """

    try:
        from flask import request

        datos = request.get_json() or {}

        usuario = crear_usuario(
            datos,
            g.id_comercio
        )

        return jsonify({
            "message": "Usuario creado correctamente",
            "usuario": usuario
        }), 201

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500



def modificar_usuario_controller(id_usuario):
    """
    Modifica los datos básicos de un empleado.
    """

    try:
        from flask import request

        datos = request.get_json() or {}

        usuario = modificar_usuario(
            id_usuario=id_usuario,
            datos=datos,
            id_comercio=g.id_comercio,
            id_usuario_actual=g.id_usuario
        )

        return jsonify({
            "message": "Usuario actualizado correctamente",
            "usuario": usuario
        }), 200

    except PermissionError as e:
        return jsonify({
            "error": str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


def cambiar_estado_usuario_controller(id_usuario):
    """
    Activa o desactiva un empleado.
    """

    try:
        from flask import request

        datos = request.get_json() or {}

        if "estado" not in datos:
            raise ValueError(
                "El estado es obligatorio"
            )

        usuario = cambiar_estado_usuario(
            id_usuario=id_usuario,
            estado=datos["estado"],
            id_comercio=g.id_comercio,
            id_usuario_actual=g.id_usuario
        )

        return jsonify({
            "message": "Estado del usuario actualizado correctamente",
            "usuario": usuario
        }), 200

    except PermissionError as e:
        return jsonify({
            "error": str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500



def cambiar_rol_usuario_controller(id_usuario):
    """
    Cambia el rol de un empleado.
    """

    try:
        from flask import request

        datos = request.get_json() or {}

        if "id_rol" not in datos:
            raise ValueError(
                "El rol es obligatorio"
            )

        usuario = cambiar_rol_usuario(
            id_usuario=id_usuario,
            id_rol=datos["id_rol"],
            id_comercio=g.id_comercio
        )

        return jsonify({
            "message": "Rol del usuario actualizado correctamente",
            "usuario": usuario
        }), 200

    except PermissionError as e:
        return jsonify({
            "error": str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500



def restablecer_password_usuario_controller(id_usuario):
    """
    Restablece la contraseña de un empleado.
    """

    try:
        from flask import request

        datos = request.get_json() or {}

        if "password" not in datos:
            raise ValueError(
                "La nueva contraseña es obligatoria"
            )

        usuario = restablecer_password_usuario(
            id_usuario=id_usuario,
            nueva_password=datos["password"],
            id_comercio=g.id_comercio,
            id_usuario_actual=g.id_usuario
        )

        return jsonify({
            "message": "Contraseña del usuario restablecida correctamente",
            "usuario": usuario
        }), 200

    except PermissionError as e:
        return jsonify({
            "error": str(e)
        }), 403

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500