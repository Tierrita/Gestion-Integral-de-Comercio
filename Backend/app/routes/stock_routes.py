"""
Rutas de stock.

Este módulo define las rutas HTTP relacionadas
con la gestión del stock.
"""

from flask import Blueprint
from app.controllers.stock_controller import (
    ajustar_stock_controller,
    consultar_stock_general_controller,
    consultar_alertas_stock_controller
)


stock_bp = Blueprint("stock", __name__)


@stock_bp.route("/stock/<int:id_producto>/ajustar", methods=["PATCH"])
def ajustar_stock_route(id_producto):
    """
    Ajusta manualmente el stock de un producto.
    """

    return ajustar_stock_controller(id_producto)


@stock_bp.route("/stock", methods=["GET"])
def consultar_stock_general_route():
    """
    Consulta el stock de todos los productos.
    """
    return consultar_stock_general_controller()


@stock_bp.route("/stock/alertas", methods=["GET"])
def consultar_alertas_stock_route():
    """
    Consulta los productos que llegaron al stock mínimo.
    """
    return consultar_alertas_stock_controller()