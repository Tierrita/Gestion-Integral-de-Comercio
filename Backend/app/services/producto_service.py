"""
Este módulo contiene la lógica de negocio relacionada con los productos.
Se comunica con la capa de modelos para obtener o modificar datos.
"""

from app.models.producto_model import (
    obtener_productos,
    obtener_producto_por_id,
    insertar_producto

)



def listar_productos():
    """
    Solicita al modelo todos los productos disponibles.
    """

    productos = obtener_productos()

    return productos



def buscar_producto_por_id(id_producto):
    """
    Solicita al modelo un producto específico mediante su ID.
    """

    producto = obtener_producto_por_id(id_producto)

    return producto


def crear_producto(datos):
    """
    Solicita al modelo la creación de un nuevo producto.
    """
    if not isinstance(datos["precio_costo"], (int, float)):
        raise ValueError("El precio de costo debe ser un número")

    if not isinstance(datos["precio_venta"], (int, float)):
        raise ValueError("El precio de venta debe ser un número")

    if "stock" in datos and not isinstance(datos["stock"], int):
        raise ValueError("El stock debe ser un número entero")

    if "stock_minimo" in datos and not isinstance(datos["stock_minimo"], int):
        raise ValueError("El stock mínimo debe ser un número entero")

    if datos["precio_costo"] < 0:
        raise ValueError("El precio de costo no puede ser negativo")

    if datos["precio_venta"] < 0:
        raise ValueError("El precio de venta no puede ser negativo")

    if datos.get("stock", 0) < 0:
        raise ValueError("El stock no puede ser negativo")

    if datos.get("stock_minimo", 0) < 0:
        raise ValueError("El stock mínimo no puede ser negativo")
    producto = insertar_producto(datos)

    return producto