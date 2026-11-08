"""
Rutas de proveedores.

Todas las operaciones requieren autenticación
y permisos específicos.
"""

from flask import Blueprint

from app.controllers.proveedor_controller import (
    crear_proveedor_controller,
    obtener_proveedores_controller,
    obtener_proveedor_controller,
    editar_proveedor_controller,
    cambiar_estado_proveedor_controller
)

from core.auth import (
    login_requerido,
    permiso_requerido
)


proveedor_bp = Blueprint(
    "proveedor",
    __name__
)


@proveedor_bp.route(
    "/proveedores",
    methods=["POST"]
)
@login_requerido
@permiso_requerido("proveedores.crear")
def crear_proveedor_route():
    return crear_proveedor_controller()


@proveedor_bp.route(
    "/proveedores",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("proveedores.ver")
def obtener_proveedores_route():
    return obtener_proveedores_controller()


@proveedor_bp.route(
    "/proveedores/<int:id_proveedor>",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("proveedores.ver")
def obtener_proveedor_route(id_proveedor):
    return obtener_proveedor_controller(
        id_proveedor
    )


@proveedor_bp.route(
    "/proveedores/<int:id_proveedor>",
    methods=["PATCH"]
)
@login_requerido
@permiso_requerido("proveedores.modificar")
def editar_proveedor_route(id_proveedor):
    return editar_proveedor_controller(
        id_proveedor
    )


@proveedor_bp.route(
    "/proveedores/<int:id_proveedor>/estado",
    methods=["PATCH"]
)
@login_requerido
@permiso_requerido("proveedores.modificar")
def cambiar_estado_proveedor_route(id_proveedor):
    return cambiar_estado_proveedor_controller(
        id_proveedor
    )