"""
Rutas de productos.

Este módulo define los endpoints relacionados con productos.

Todas las rutas requieren autenticación mediante JWT
y aplican los permisos correspondientes al usuario.

Route → Controller → Service → Model → Supabase
"""

from flask import Blueprint

from app.controllers.producto_controller import (
    obtener_productos_controller,
    obtener_producto_controller,
    crear_producto_controller,
    modificar_producto_controller,
)

from core.auth import (
    login_requerido,
    permiso_requerido,
)


producto_bp = Blueprint(
    "producto",
    __name__
)


@producto_bp.route("/productos", methods=["GET"])
@login_requerido
@permiso_requerido("productos.ver")
def obtener_productos():
    """
    Lista los productos del comercio autenticado.
    """

    return obtener_productos_controller()


@producto_bp.route(
    "/productos/<int:id_producto>",
    methods=["GET"]
)
@login_requerido
@permiso_requerido("productos.ver")
def obtener_producto(id_producto):
    """
    Obtiene un producto específico perteneciente
    al comercio autenticado.
    """

    return obtener_producto_controller(
        id_producto
    )


@producto_bp.route("/productos", methods=["POST"])
@login_requerido
@permiso_requerido("productos.crear")
def crear_producto():
    """
    Crea un producto dentro del comercio autenticado.
    """

    return crear_producto_controller()


@producto_bp.route(
    "/productos/<int:id_producto>",
    methods=["PATCH"]
)
@login_requerido
@permiso_requerido("productos.modificar")
def modificar_producto(id_producto):
    """
    Modifica los datos comerciales de un producto
    perteneciente al comercio autenticado.

    El stock y el estado no se modifican
    mediante este endpoint.
    """

    return modificar_producto_controller(
        id_producto
    )