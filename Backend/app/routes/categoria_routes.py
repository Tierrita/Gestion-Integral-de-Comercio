"""
Rutas de categorías.

Todas las rutas requieren autenticación.

Los permisos utilizados son:

categorias.ver
categorias.gestionar
"""

from flask import Blueprint

from app.controllers.categoria_controller import (
    crear_categoria_controller,
    obtener_categorias_controller,
    obtener_categoria_controller,
    editar_categoria_controller,
    cambiar_estado_categoria_controller
)

from core.auth import (
    login_requerido,
    permiso_requerido
)


categoria_bp = Blueprint(
    "categoria",
    __name__
)


@categoria_bp.route(
    "/categorias",
    methods=["POST"]
)
@login_requerido
@permiso_requerido("categorias.gestionar")
def crear_categoria_route():
    """
    Crea una categoría dentro del comercio autenticado.
    """

    return crear_categoria_controller()


@categoria_bp.route(
    "/categorias",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("categorias.ver")
def obtener_categorias_route():
    """
    Consulta las categorías del comercio autenticado.
    """

    return obtener_categorias_controller()


@categoria_bp.route(
    "/categorias/<int:id_categoria>",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("categorias.ver")
def obtener_categoria_route(id_categoria):
    """
    Consulta una categoría específica.
    """

    return obtener_categoria_controller(
        id_categoria
    )


@categoria_bp.route(
    "/categorias/<int:id_categoria>",
    methods=["PATCH"]
)
@login_requerido
@permiso_requerido("categorias.gestionar")
def editar_categoria_route(id_categoria):
    """
    Modifica una categoría del comercio autenticado.
    """

    return editar_categoria_controller(
        id_categoria
    )


@categoria_bp.route(
    "/categorias/<int:id_categoria>/estado",
    methods=["PATCH"]
)
@login_requerido
@permiso_requerido("categorias.gestionar")
def cambiar_estado_categoria_route(
    id_categoria
):
    """
    Activa o desactiva una categoría.
    """

    return cambiar_estado_categoria_controller(
        id_categoria
    )