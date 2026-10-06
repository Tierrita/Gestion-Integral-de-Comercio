"""
Rutas de clientes.

Este módulo define las rutas HTTP relacionadas
con la gestión de clientes.
"""

from flask import Blueprint

from app.controllers.cliente_controller import (
    crear_cliente_controller,
    obtener_clientes_controller,
    obtener_cliente_controller,
    editar_cliente_controller,
    cambiar_estado_cliente_controller,
    obtener_historial_ventas_cliente_controller
)


cliente_bp = Blueprint("cliente", __name__)


@cliente_bp.route("/clientes", methods=["POST"])
def crear_cliente_route():
    """
    Registra un nuevo cliente.
    """

    return crear_cliente_controller()


@cliente_bp.route("/clientes", methods=["GET"])
def obtener_clientes_route():
    """
    Consulta todos los clientes registrados.
    """

    return obtener_clientes_controller()


@cliente_bp.route("/clientes/<int:id_cliente>", methods=["GET"])
def obtener_cliente_route(id_cliente):
    """
    Consulta un cliente específico mediante su ID.
    """

    return obtener_cliente_controller(id_cliente)


@cliente_bp.route("/clientes/<int:id_cliente>", methods=["PATCH"])
def editar_cliente_route(id_cliente):
    """
    Actualiza los datos de un cliente.
    """

    return editar_cliente_controller(id_cliente)


@cliente_bp.route("/clientes/<int:id_cliente>/estado", methods=["PATCH"])
def cambiar_estado_cliente_route(id_cliente):
    """
    Activa o desactiva un cliente.
    """

    return cambiar_estado_cliente_controller(id_cliente)


@cliente_bp.route("/clientes/<int:id_cliente>/ventas", methods=["GET"])
def obtener_historial_ventas_cliente_route(id_cliente):
    """
    Consulta el historial de ventas de un cliente.
    """

    return obtener_historial_ventas_cliente_controller(id_cliente)