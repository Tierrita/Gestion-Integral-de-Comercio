"""
Rutas de productos.

Este módulo define los endpoints relacionados con los productos
y conecta las solicitudes HTTP con el controlador correspondiente.
"""

from flask import Blueprint
from app.controllers.producto_controller import (
    obtener_productos_controller,
    obtener_producto_controller, 
    crear_producto_controller
)


producto_bp = Blueprint("producto", __name__)


@producto_bp.route("/productos", methods=["GET"])
def obtener_productos():
    """
    Endpoint para obtener todos los productos.
    """
    return obtener_productos_controller()


@producto_bp.route("/productos/<int:id_producto>", methods=["GET"])
def obtener_producto(id_producto):
    """
    Endpoint para obtener un producto específico mediante su ID.
    """
    return obtener_producto_controller(id_producto)



@producto_bp.route("/productos", methods=["POST"])
def crear_producto():
    """
    Endpoint para crear un nuevo producto.
    """
    return crear_producto_controller()