"""
Rutas de categorías.

Este módulo define las rutas HTTP relacionadas
con las categorías.
"""

from flask import Blueprint

from app.controllers.categoria_controller import (
    crear_categoria_controller,
    obtener_categorias_controller,
    obtener_categoria_controller,
    editar_categoria_controller,
    cambiar_estado_categoria_controller
)


categoria_bp = Blueprint("categoria", __name__)


@categoria_bp.route("/categorias", methods=["POST"])
def crear_categoria_route():
    """
    Crea una nueva categoría.
    """

    return crear_categoria_controller()


@categoria_bp.route("/categorias", methods=["GET"])
def obtener_categorias_route():
    """
    Consulta todas las categorías registradas.
    """

    return obtener_categorias_controller()


@categoria_bp.route("/categorias/<int:id_categoria>", methods=["GET"])
def obtener_categoria_route(id_categoria):
    """
    Consulta una categoría específica mediante su ID.
    """

    return obtener_categoria_controller(id_categoria)


@categoria_bp.route("/categorias/<int:id_categoria>", methods=["PATCH"])
def editar_categoria_route(id_categoria):
    """
    Edita una categoría existente mediante su ID.
    """

    return editar_categoria_controller(id_categoria)


@categoria_bp.route(
    "/categorias/<int:id_categoria>/estado",
    methods=["PATCH"]
)
def cambiar_estado_categoria_route(id_categoria):
    """
    Cambia el estado de una categoría mediante su ID.
    """

    return cambiar_estado_categoria_controller(id_categoria)