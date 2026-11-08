"""
Rutas del módulo de compras.

Seguridad:
- Todas las rutas requieren autenticación.
- Consultar compras requiere compras.ver.
- Registrar compras requiere compras.registrar.
- Anular compras es exclusivo del propietario.
"""

from flask import Blueprint

from app.controllers.compra_controller import (
    crear_compra_controller,
    obtener_compras_controller,
    obtener_compra_controller,
    anular_compra_controller
)

from core.auth import (
    login_requerido,
    permiso_requerido,
    solo_propietario
)


compra_bp = Blueprint(
    "compra",
    __name__
)


@compra_bp.route(
    "/compras",
    methods=["POST"]
)
@login_requerido
@permiso_requerido("compras.registrar")
def crear_compra_route():
    return crear_compra_controller()


@compra_bp.route(
    "/compras",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("compras.ver")
def obtener_compras_route():
    return obtener_compras_controller()


@compra_bp.route(
    "/compras/<int:id_compra>",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("compras.ver")
def obtener_compra_route(id_compra):
    return obtener_compra_controller(
        id_compra
    )


@compra_bp.route(
    "/compras/<int:id_compra>/anular",
    methods=["PATCH"]
)
@login_requerido
@solo_propietario
def anular_compra_route(id_compra):
    return anular_compra_controller(
        id_compra
    )