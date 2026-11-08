"""
Rutas de clientes.

Todas las rutas requieren autenticación JWT.
Los permisos se controlan según la operación realizada.
"""

from flask import Blueprint

from core.auth import (
    login_requerido,
    permiso_requerido,
)

from app.controllers.cliente_controller import (
    crear_cliente_controller,
    obtener_clientes_controller,
    obtener_cliente_controller,
    editar_cliente_controller,
    cambiar_estado_cliente_controller,
    obtener_historial_ventas_cliente_controller,
)


cliente_bp = Blueprint("cliente", __name__)


@cliente_bp.route("/clientes", methods=["POST"])
@login_requerido
@permiso_requerido("clientes.crear")
def crear_cliente_route():
    return crear_cliente_controller()


@cliente_bp.route("/clientes", methods=["GET"])
@login_requerido
@permiso_requerido("clientes.ver")
def obtener_clientes_route():
    return obtener_clientes_controller()


@cliente_bp.route(
    "/clientes/<int:id_cliente>",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("clientes.ver")
def obtener_cliente_route(id_cliente):
    return obtener_cliente_controller(id_cliente)


@cliente_bp.route(
    "/clientes/<int:id_cliente>",
    methods=["PATCH"]
)
@login_requerido
@permiso_requerido("clientes.modificar")
def editar_cliente_route(id_cliente):
    return editar_cliente_controller(id_cliente)


@cliente_bp.route(
    "/clientes/<int:id_cliente>/estado",
    methods=["PATCH"]
)
@login_requerido
@permiso_requerido("clientes.modificar")
def cambiar_estado_cliente_route(id_cliente):
    return cambiar_estado_cliente_controller(id_cliente)


@cliente_bp.route(
    "/clientes/<int:id_cliente>/ventas",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("clientes.ver")
def obtener_historial_ventas_cliente_route(id_cliente):
    return obtener_historial_ventas_cliente_controller(
        id_cliente
    )