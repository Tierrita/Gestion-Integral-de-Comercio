"""
Rutas de usuarios.

Define los endpoints relacionados con los usuarios
y empleados del comercio.
"""

from flask import Blueprint

from app.controllers.usuario_controller import (
    obtener_usuarios_controller,
    obtener_usuario_controller,
    crear_usuario_controller,
    modificar_usuario_controller,
    cambiar_estado_usuario_controller,
    cambiar_rol_usuario_controller,
    restablecer_password_usuario_controller
)

from core.auth import (
    login_requerido,
    permiso_requerido,
    solo_propietario
)


usuario_bp = Blueprint(
    "usuarios",
    __name__,
    url_prefix="/usuarios"
)


@usuario_bp.route("", methods=["GET"])
@login_requerido
@permiso_requerido("usuarios.gestionar")
def obtener_usuarios():
    """
    Lista los usuarios pertenecientes
    al comercio autenticado.

    Requiere permiso para gestionar usuarios.
    """

    return obtener_usuarios_controller()


@usuario_bp.route("/<int:id_usuario>", methods=["GET"])
@login_requerido
@permiso_requerido("usuarios.gestionar")
def obtener_usuario(id_usuario):
    """
    Obtiene un usuario específico perteneciente
    al comercio autenticado.

    Requiere permiso para gestionar usuarios.
    """

    return obtener_usuario_controller(id_usuario)


@usuario_bp.route("", methods=["POST"])
@login_requerido
@permiso_requerido("usuarios.gestionar")
def crear_usuario():
    """
    Crea un nuevo empleado dentro del comercio autenticado.

    Requiere permiso para gestionar usuarios.
    """

    return crear_usuario_controller()


@usuario_bp.route("/<int:id_usuario>", methods=["PATCH"])
@login_requerido
@permiso_requerido("usuarios.gestionar")
def modificar_usuario(id_usuario):
    """
    Modifica los datos básicos de un empleado
    perteneciente al comercio autenticado.
    """

    return modificar_usuario_controller(id_usuario)



@usuario_bp.route(
    "/<int:id_usuario>/estado",
    methods=["PATCH"]
)
@login_requerido
@permiso_requerido("usuarios.gestionar")
def cambiar_estado_usuario(id_usuario):
    """
    Activa o desactiva un empleado
    perteneciente al comercio autenticado.
    """

    return cambiar_estado_usuario_controller(id_usuario)




@usuario_bp.route(
    "/<int:id_usuario>/rol",
    methods=["PATCH"]
)
@login_requerido
@solo_propietario
def cambiar_rol_usuario(id_usuario):
    """
    Cambia el rol de un empleado.

    Operación exclusiva del propietario.
    """

    return cambiar_rol_usuario_controller(id_usuario)


@usuario_bp.route(
    "/<int:id_usuario>/password",
    methods=["PATCH"]
)
@login_requerido
@permiso_requerido("usuarios.gestionar")
def restablecer_password_usuario(id_usuario):
    """
    Restablece la contraseña de un empleado.
    """

    return restablecer_password_usuario_controller(
        id_usuario
    )