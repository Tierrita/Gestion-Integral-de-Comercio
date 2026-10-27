"""
Controller de roles.

Recibe las peticiones HTTP relacionadas con roles y permisos
y delega la lógica de negocio al servicio correspondiente.
"""

from flask import request, jsonify, g

from app.services.rol_service import (
    listar_roles,
    listar_permisos,
    obtener_detalle_rol,
    crear_rol,
    modificar_rol,
    cambiar_estado_rol
)


def obtener_roles_controller():
    """
    Devuelve los roles del comercio autenticado.
    """

    try:
        roles = listar_roles(g.id_comercio)

        return jsonify({
            "roles": roles
        }), 200

    except Exception as e:
        print(f"Error al obtener roles: {e}")

        return jsonify({
            "error": "Error interno al obtener los roles"
        }), 500


def obtener_permisos_controller():
    """
    Devuelve el catálogo de permisos disponibles.
    """

    try:
        permisos = listar_permisos()

        return jsonify({
            "permisos": permisos
        }), 200

    except Exception as e:
        print(f"Error al obtener permisos: {e}")

        return jsonify({
            "error": "Error interno al obtener los permisos"
        }), 500


def obtener_rol_controller(id_rol):
    """
    Devuelve un rol específico del comercio autenticado.
    """

    try:
        rol = obtener_detalle_rol(
            id_rol,
            g.id_comercio
        )

        return jsonify({
            "rol": rol
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404

    except Exception as e:
        print(f"Error al obtener rol: {e}")

        return jsonify({
            "error": "Error interno al obtener el rol"
        }), 500


def crear_rol_controller():
    """
    Crea un rol dentro del comercio autenticado.
    """

    try:
        datos = request.get_json(silent=True) or {}

        rol = crear_rol(
            datos,
            g.id_comercio
        )

        return jsonify({
            "message": "Rol creado correctamente",
            "rol": rol
        }), 201

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        print(f"Error al crear rol: {e}")

        return jsonify({
            "error": "Error interno al crear el rol"
        }), 500



def modificar_rol_controller(id_rol):
    """
    Modifica el nombre y/o los permisos de un rol
    perteneciente al comercio autenticado.
    """

    try:
        datos = request.get_json(silent=True) or {}

        rol = modificar_rol(
            id_rol,
            datos,
            g.id_comercio
        )

        return jsonify({
            "message": "Rol actualizado correctamente",
            "rol": rol
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        print(f"Error al modificar rol: {e}")

        return jsonify({
            "error": "Error interno al modificar el rol"
        }), 500


def cambiar_estado_rol_controller(id_rol):
    """
    Activa o desactiva un rol del comercio autenticado.
    """

    try:
        datos = request.get_json(silent=True) or {}

        rol = cambiar_estado_rol(
            id_rol,
            datos,
            g.id_comercio
        )

        return jsonify({
            "message": "Estado del rol actualizado correctamente",
            "rol": rol
        }), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        print(f"Error al cambiar estado del rol: {e}")

        return jsonify({
            "error": "Error interno al cambiar el estado del rol"
        }), 500