from flask import Blueprint

from app.controllers.cobro_controller import (
    registrar_cobro_controller,
    listar_cobros_controller,
    consultar_cobro_por_id_controller,
    consultar_cobros_por_cliente_controller,
    anular_cobro_controller,
    consultar_saldo_cliente_controller
)

from core.auth import (
    login_requerido,
    permiso_requerido,
    solo_propietario
)


cobro_bp = Blueprint("cobros", __name__)


@cobro_bp.route("/cobros", methods=["POST"])
@login_requerido
@permiso_requerido("cobros.registrar")
def registrar_cobro_route():
    return registrar_cobro_controller()


@cobro_bp.route("/cobros", methods=["GET"])
@login_requerido
@permiso_requerido("cobros.ver")
def listar_cobros_route():
    return listar_cobros_controller()


@cobro_bp.route("/cobros/<int:id_cobro>", methods=["GET"])
@login_requerido
@permiso_requerido("cobros.ver")
def consultar_cobro_por_id_route(id_cobro):
    return consultar_cobro_por_id_controller(id_cobro)


@cobro_bp.route(
    "/clientes/<int:id_cliente>/cobros",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("cobros.ver")
def consultar_cobros_por_cliente_route(id_cliente):
    return consultar_cobros_por_cliente_controller(
        id_cliente
    )


@cobro_bp.route(
    "/cobros/<int:id_cobro>/anular",
    methods=["PATCH"]
)
@login_requerido
@solo_propietario
def anular_cobro_route(id_cobro):
    return anular_cobro_controller(id_cobro)


@cobro_bp.route(
    "/clientes/<int:id_cliente>/saldo",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("clientes.ver_deuda")
def consultar_saldo_cliente_route(id_cliente):
    return consultar_saldo_cliente_controller(
        id_cliente
    )