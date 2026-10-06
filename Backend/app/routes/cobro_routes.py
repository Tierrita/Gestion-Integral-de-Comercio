"""
Rutas de cobros.

Este módulo define los endpoints relacionados
con los cobros realizados por los clientes.
"""

from flask import Blueprint

from app.controllers.cobro_controller import (
    registrar_cobro_controller,
    listar_cobros_controller,
    consultar_cobro_por_id_controller,
    consultar_cobros_por_cliente_controller,
    anular_cobro_controller,
    consultar_saldo_cliente_controller
)


# Crear Blueprint
cobro_bp = Blueprint("cobros", __name__)


@cobro_bp.route("/cobros", methods=["POST"])
def registrar_cobro_route():
    """
    Endpoint para registrar un nuevo cobro de cliente.
    """
    return registrar_cobro_controller()


@cobro_bp.route("/cobros", methods=["GET"])
def listar_cobros_route():
    """
    Endpoint para consultar todos los cobros
    registrados en el sistema.
    """
    return listar_cobros_controller()

@cobro_bp.route("/cobros/<int:id_cobro>", methods=["GET"])
def consultar_cobro_por_id_route(id_cobro):
    """
    Endpoint para consultar un cobro específico
    mediante su ID.
    """
    return consultar_cobro_por_id_controller(id_cobro)


@cobro_bp.route("/clientes/<int:id_cliente>/cobros", methods=["GET"])
def consultar_cobros_por_cliente_route(id_cliente):
    """
    Endpoint para consultar el historial
    de cobros de un cliente.
    """
    return consultar_cobros_por_cliente_controller(id_cliente)



@cobro_bp.route("/cobros/<int:id_cobro>/anular", methods=["PATCH"])
def anular_cobro_route(id_cobro):
    """
    Endpoint para anular un cobro.
    """
    return anular_cobro_controller(id_cobro)


@cobro_bp.route("/clientes/<int:id_cliente>/saldo", methods=["GET"])
def consultar_saldo_cliente_route(id_cliente):
    """
    Endpoint para consultar el saldo financiero
    actual de un cliente.
    """
    return consultar_saldo_cliente_controller(id_cliente)