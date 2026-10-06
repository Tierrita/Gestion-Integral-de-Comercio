"""
Rutas de pagos a proveedores.

Este módulo define los endpoints relacionados
con los pagos realizados a proveedores.
"""

from flask import Blueprint

from app.controllers.pago_proveedor_controller import (
    registrar_pago_proveedor_controller,
    listar_pagos_proveedor_controller,
    consultar_pago_proveedor_por_id_controller,
    consultar_pagos_por_proveedor_controller,
    anular_pago_proveedor_controller,
    consultar_saldo_proveedor_controller
)


pago_proveedor_bp = Blueprint(
    "pagos_proveedor",
    __name__
)


@pago_proveedor_bp.route("/pagos-proveedor", methods=["POST"])
def registrar_pago_proveedor_route():
    return registrar_pago_proveedor_controller()


@pago_proveedor_bp.route("/pagos-proveedor", methods=["GET"])
def listar_pagos_proveedor_route():
    return listar_pagos_proveedor_controller()


@pago_proveedor_bp.route(
    "/pagos-proveedor/<int:id_pago>",
    methods=["GET"]
)
def consultar_pago_proveedor_por_id_route(id_pago):
    return consultar_pago_proveedor_por_id_controller(id_pago)


@pago_proveedor_bp.route(
    "/proveedores/<int:id_proveedor>/pagos",
    methods=["GET"]
)
def consultar_pagos_por_proveedor_route(id_proveedor):
    return consultar_pagos_por_proveedor_controller(id_proveedor)

@pago_proveedor_bp.route(
    "/pagos-proveedor/<int:id_pago>/anular",
    methods=["PATCH"]
)
def anular_pago_proveedor_route(id_pago):
    return anular_pago_proveedor_controller(id_pago)


@pago_proveedor_bp.route(
    "/proveedores/<int:id_proveedor>/saldo",
    methods=["GET"]
)
def consultar_saldo_proveedor_route(id_proveedor):
    """
    Obtiene la cuenta corriente de un proveedor.
    """

    return consultar_saldo_proveedor_controller(id_proveedor)