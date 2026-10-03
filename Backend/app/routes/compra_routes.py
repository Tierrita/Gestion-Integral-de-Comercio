"""
Rutas de compras.

Este módulo define las rutas HTTP relacionadas
con las compras.
"""

from flask import Blueprint

from app.controllers.compra_controller import (
    crear_compra_controller,
    obtener_compras_controller,
    obtener_compra_controller,
    anular_compra_controller
)


compra_bp = Blueprint("compra", __name__)


@compra_bp.route("/compras", methods=["POST"])
def crear_compra_route():
    """
    Registra una nueva compra.
    """

    return crear_compra_controller()


@compra_bp.route("/compras", methods=["GET"])
def obtener_compras_route():
    """
    Consulta todas las compras registradas.
    """

    return obtener_compras_controller()


@compra_bp.route("/compras/<int:id_compra>", methods=["GET"])
def obtener_compra_route(id_compra):
    """
    Consulta una compra específica mediante su ID.
    """

    return obtener_compra_controller(id_compra)


@compra_bp.route("/compras/<int:id_compra>/anular", methods=["PATCH"])
def anular_compra_route(id_compra):
    """
    Anula una compra mediante su ID.
    """

    return anular_compra_controller(id_compra)