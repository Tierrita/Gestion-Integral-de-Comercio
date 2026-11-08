"""
Rutas del módulo de ventas.

Todas las rutas requieren autenticación.

Las operaciones normales utilizan permisos por rol.
La anulación de una venta es exclusiva del propietario.
"""

from flask import Blueprint

from app.controllers.venta_controller import (
    crear_venta_controller,
    obtener_ventas_controller,
    obtener_venta_controller,
    anular_venta_controller
)

from core.auth import (
    login_requerido,
    permiso_requerido,
    solo_propietario
)


venta_bp = Blueprint(
    "venta",
    __name__
)


@venta_bp.route(
    "/ventas",
    methods=["POST"]
)
@login_requerido
@permiso_requerido("ventas.crear")
def crear_venta_route():
    """Registra una nueva venta."""

    return crear_venta_controller()


@venta_bp.route(
    "/ventas",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("ventas.ver")
def obtener_ventas_route():
    """Consulta las ventas del comercio autenticado."""

    return obtener_ventas_controller()


@venta_bp.route(
    "/ventas/<int:id_venta>",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("ventas.ver")
def obtener_venta_route(id_venta):
    """Consulta una venta específica."""

    return obtener_venta_controller(
        id_venta
    )


@venta_bp.route(
    "/ventas/<int:id_venta>/anular",
    methods=["PATCH"]
)
@login_requerido
@solo_propietario
def anular_venta_route(id_venta):
    """Anula una venta. Exclusivo del propietario."""

    return anular_venta_controller(
        id_venta
    )