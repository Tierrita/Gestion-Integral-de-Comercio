"""
Rutas de cuentas financieras.

Este módulo define los endpoints relacionados
con las cuentas financieras del sistema.
"""

from flask import Blueprint

from app.controllers.cuenta_controller import (
    crear_cuenta_controller,
    listar_cuentas_controller,
    consultar_cuenta_por_id_controller,
    editar_cuenta_controller,
    cambiar_estado_cuenta_controller,
    ajustar_saldo_cuenta_controller,
    consultar_movimientos_cuenta_controller
)


cuenta_bp = Blueprint("cuentas", __name__)


@cuenta_bp.route("/cuentas", methods=["POST"])
def crear_cuenta_route():
    """
    Endpoint para crear una nueva cuenta financiera.
    """
    return crear_cuenta_controller()


@cuenta_bp.route("/cuentas", methods=["GET"])
def listar_cuentas_route():
    """
    Endpoint para consultar todas las cuentas financieras.
    """
    return listar_cuentas_controller()


@cuenta_bp.route("/cuentas/<int:id_cuenta>", methods=["GET"])
def consultar_cuenta_por_id_route(id_cuenta):
    """
    Endpoint para consultar una cuenta financiera mediante su ID.
    """
    return consultar_cuenta_por_id_controller(id_cuenta)


@cuenta_bp.route("/cuentas/<int:id_cuenta>", methods=["PATCH"])
def editar_cuenta_route(id_cuenta):
    """
    Endpoint para modificar una cuenta financiera.
    """
    return editar_cuenta_controller(id_cuenta)

@cuenta_bp.route("/cuentas/<int:id_cuenta>/estado", methods=["PATCH"])
def cambiar_estado_cuenta_route(id_cuenta):
    """
    Endpoint para activar o desactivar
    una cuenta financiera.
    """
    return cambiar_estado_cuenta_controller(id_cuenta)


@cuenta_bp.route("/cuentas/<int:id_cuenta>/ajustar", methods=["PATCH"])
def ajustar_saldo_cuenta_route(id_cuenta):
    """
    Endpoint para realizar un ajuste manual
    sobre el saldo de una cuenta financiera.
    """
    return ajustar_saldo_cuenta_controller(id_cuenta)



@cuenta_bp.route("/cuentas/<int:id_cuenta>/movimientos", methods=["GET"])
def consultar_movimientos_cuenta_route(id_cuenta):
    """
    Endpoint para consultar el historial de movimientos
    financieros de una cuenta.
    """
    return consultar_movimientos_cuenta_controller(id_cuenta)