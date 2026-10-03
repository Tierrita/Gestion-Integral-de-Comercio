"""
Rutas de ventas.

Este módulo define las rutas HTTP relacionadas
con las ventas.
"""

from flask import Blueprint

from app.controllers.venta_controller import (
    crear_venta_controller,
    obtener_ventas_controller,
    obtener_venta_controller,
    anular_venta_controller
)


venta_bp = Blueprint("venta", __name__)


@venta_bp.route("/ventas", methods=["POST"])
def crear_venta_route():
    """
    Registra una nueva venta.
    """

    return crear_venta_controller()


@venta_bp.route("/ventas", methods=["GET"])
def obtener_ventas_route():
    """
    Consulta todas las ventas registradas.
    """

    return obtener_ventas_controller()


@venta_bp.route("/ventas/<int:id_venta>", methods=["GET"])
def obtener_venta_route(id_venta):
    """
    Consulta una venta específica mediante su ID.
    """

    return obtener_venta_controller(id_venta)


@venta_bp.route("/ventas/<int:id_venta>/anular", methods=["PATCH"])
def anular_venta_route(id_venta):
    """
    Anula una venta mediante su ID.
    """

    return anular_venta_controller(id_venta)