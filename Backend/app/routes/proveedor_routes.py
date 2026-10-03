"""
Rutas de proveedores.

Este módulo define las rutas HTTP relacionadas
con los proveedores.
"""

from flask import Blueprint

from app.controllers.proveedor_controller import (
    crear_proveedor_controller,
    obtener_proveedores_controller,
    obtener_proveedor_controller,
    editar_proveedor_controller,
    cambiar_estado_proveedor_controller

)


proveedor_bp = Blueprint("proveedor", __name__)


@proveedor_bp.route("/proveedores", methods=["POST"])
def crear_proveedor_route():
    """
    Crea un nuevo proveedor.
    """

    return crear_proveedor_controller()



@proveedor_bp.route("/proveedores", methods=["GET"])
def obtener_proveedores_route():
    """
    Consulta todos los proveedores registrados.
    """

    return obtener_proveedores_controller()


@proveedor_bp.route(
    "/proveedores/<int:id_proveedor>",
    methods=["GET"]
)
def obtener_proveedor_route(id_proveedor):
    """
    Consulta un proveedor específico mediante su ID.
    """

    return obtener_proveedor_controller(id_proveedor)



@proveedor_bp.route(
    "/proveedores/<int:id_proveedor>",
    methods=["PATCH"]
)
def editar_proveedor_route(id_proveedor):
    """
    Edita un proveedor existente mediante su ID.
    """

    return editar_proveedor_controller(id_proveedor)



@proveedor_bp.route(
    "/proveedores/<int:id_proveedor>/estado",
    methods=["PATCH"]
)
def cambiar_estado_proveedor_route(id_proveedor):
    """
    Cambia el estado de un proveedor mediante su ID.
    """

    return cambiar_estado_proveedor_controller(id_proveedor)