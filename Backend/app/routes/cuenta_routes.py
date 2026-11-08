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

from core.auth import (
    login_requerido,
    solo_propietario
)


cuenta_bp = Blueprint("cuentas", __name__)


@cuenta_bp.route("/cuentas", methods=["POST"])
@login_requerido
@solo_propietario
def crear_cuenta_route():
    return crear_cuenta_controller()


@cuenta_bp.route("/cuentas", methods=["GET"])
@login_requerido
def listar_cuentas_route():
    return listar_cuentas_controller()


@cuenta_bp.route(
    "/cuentas/<int:id_cuenta>",
    methods=["GET"]
)
@login_requerido
def consultar_cuenta_por_id_route(id_cuenta):
    return consultar_cuenta_por_id_controller(
        id_cuenta
    )


@cuenta_bp.route(
    "/cuentas/<int:id_cuenta>",
    methods=["PATCH"]
)
@login_requerido
@solo_propietario
def editar_cuenta_route(id_cuenta):
    return editar_cuenta_controller(id_cuenta)


@cuenta_bp.route(
    "/cuentas/<int:id_cuenta>/estado",
    methods=["PATCH"]
)
@login_requerido
@solo_propietario
def cambiar_estado_cuenta_route(id_cuenta):
    return cambiar_estado_cuenta_controller(
        id_cuenta
    )


@cuenta_bp.route(
    "/cuentas/<int:id_cuenta>/ajustar",
    methods=["PATCH"]
)
@login_requerido
@solo_propietario
def ajustar_saldo_cuenta_route(id_cuenta):
    return ajustar_saldo_cuenta_controller(
        id_cuenta
    )


@cuenta_bp.route(
    "/cuentas/<int:id_cuenta>/movimientos",
    methods=["GET"]
)
@login_requerido
@solo_propietario
def consultar_movimientos_cuenta_route(id_cuenta):
    return consultar_movimientos_cuenta_controller(
        id_cuenta
    )