"""
Rutas de roles y permisos.

Todas las rutas requieren autenticación.
La administración de roles y permisos es exclusiva
del propietario del comercio.
"""

from flask import Blueprint

from app.controllers.rol_controller import (
    obtener_roles_controller,
    obtener_permisos_controller,
    obtener_rol_controller,
    crear_rol_controller,
    modificar_rol_controller,
    cambiar_estado_rol_controller
)

from core.auth import login_requerido, solo_propietario


rol_bp = Blueprint(
    "roles",
    __name__,
    url_prefix="/roles"
)


@rol_bp.route("", methods=["GET"])
@login_requerido
@solo_propietario
def obtener_roles():
    """
    Lista los roles del comercio autenticado.
    """
    return obtener_roles_controller()


@rol_bp.route("/permisos", methods=["GET"])
@login_requerido
@solo_propietario
def obtener_permisos():
    """
    Lista el catálogo de permisos disponibles.
    """
    return obtener_permisos_controller()


@rol_bp.route("/<int:id_rol>", methods=["GET"])
@login_requerido
@solo_propietario
def obtener_rol(id_rol):
    """
    Obtiene un rol específico y sus permisos.
    """
    return obtener_rol_controller(id_rol)


@rol_bp.route("", methods=["POST"])
@login_requerido
@solo_propietario
def crear_rol():
    """
    Crea un rol dentro del comercio autenticado.
    """
    return crear_rol_controller()



@rol_bp.route("/<int:id_rol>", methods=["PATCH"])
@login_requerido
@solo_propietario
def modificar_rol(id_rol):
    """
    Modifica el nombre y/o los permisos de un rol.
    """
    return modificar_rol_controller(id_rol)


@rol_bp.route("/<int:id_rol>/estado", methods=["PATCH"])
@login_requerido
@solo_propietario
def cambiar_estado_rol(id_rol):
    """
    Activa o desactiva un rol.
    """
    return cambiar_estado_rol_controller(id_rol)