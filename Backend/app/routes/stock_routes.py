"""
Rutas de stock.

Este módulo define las rutas HTTP relacionadas
con la gestión del stock.

Todas las rutas requieren autenticación y permisos.
"""

from flask import Blueprint

from app.controllers.stock_controller import (
    ajustar_stock_controller,
    consultar_stock_general_controller,
    consultar_alertas_stock_controller
)

from core.auth import (
    login_requerido,
    permiso_requerido
)


stock_bp = Blueprint(
    "stock",
    __name__
)


@stock_bp.route(
    "/stock/<int:id_producto>/ajustar",
    methods=["PATCH"]
)
@login_requerido
@permiso_requerido("stock.ajustar")
def ajustar_stock_route(id_producto):
    """
    Ajusta manualmente el stock de un producto.

    Requiere:
    stock.ajustar
    """

    return ajustar_stock_controller(
        id_producto
    )


@stock_bp.route(
    "/stock",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("stock.ver")
def consultar_stock_general_route():
    """
    Consulta el stock correspondiente
    al comercio autenticado.

    Requiere:
    stock.ver
    """

    return consultar_stock_general_controller()


@stock_bp.route(
    "/stock/alertas",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("stock.ver")
def consultar_alertas_stock_route():
    """
    Consulta las alertas de stock
    correspondientes al comercio autenticado.

    Requiere:
    stock.ver
    """

    return consultar_alertas_stock_controller()