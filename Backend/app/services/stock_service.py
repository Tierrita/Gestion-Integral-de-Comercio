"""
Servicio de stock.

Este módulo contiene la lógica de negocio relacionada
con el manejo del stock de los productos.
"""

from app.models.stock_model import (
    obtener_stock_producto,
    actualizar_stock_producto,
    registrar_movimiento_stock,
    obtener_stock_general
)

def ajustar_stock(id_producto, cantidad, tipo_ajuste, id_usuario):
    """
    Ajusta manualmente el stock de un producto
    y registra el movimiento realizado.
    """

    # Validar cantidad
    if not isinstance(cantidad, int):
        raise ValueError("La cantidad debe ser un número entero")

    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")

    # Buscar producto
    producto = obtener_stock_producto(id_producto)

    if not producto:
        raise ValueError("Producto no encontrado")

    stock_actual = producto[0]["stock"]

    # Calcular nuevo stock
    if tipo_ajuste == "AUMENTAR":
        nuevo_stock = stock_actual + cantidad
        tipo_movimiento = "AJUSTE_ENTRADA"

    elif tipo_ajuste == "DISMINUIR":
        nuevo_stock = stock_actual - cantidad
        tipo_movimiento = "AJUSTE_SALIDA"

    else:
        raise ValueError("Tipo de ajuste inválido")

    # Evitar stock negativo
    if nuevo_stock < 0:
        raise ValueError("El stock no puede quedar negativo")

    # Actualizar stock
    actualizar_stock_producto(
        id_producto,
        nuevo_stock
    )

    # Preparar movimiento
    movimiento = {
        "id_producto": id_producto,
        "id_usuario": id_usuario,
        "tipo_movimiento": tipo_movimiento,
        "cantidad": cantidad,
        "stock_anterior": stock_actual,
        "stock_nuevo": nuevo_stock,
        "observaciones": "Ajuste manual de stock"
    }

    # Registrar movimiento
    registrar_movimiento_stock(movimiento)

    return {
        "id_producto": id_producto,
        "stock_anterior": stock_actual,
        "stock_nuevo": nuevo_stock,
        "tipo_movimiento": tipo_movimiento
    }


def consultar_stock_general(buscar=None):
    """
    Devuelve el stock general o los productos cuyo nombre coincide.
    """
    if buscar:
        buscar = buscar.strip()

    return obtener_stock_general(buscar)


def consultar_alertas_stock():
    """
    Devuelve productos cuyo stock llegó al mínimo o está por debajo.
    """
    productos = obtener_stock_general()

    return [
        producto for producto in productos
        if producto["stock"] <= producto["stock_minimo"]
    ]