"""Servicio de stock del comercio autenticado.

PREPARACIÓN PARA MIGRACIÓN DECIMAL: no habilitar ajustes KG hasta que
las columnas, las funciones SQL y el resto del backend estén migrados.
La actualización del stock y su historial aún no son atómicos; migrar
ambas escrituras a una RPC transaccional antes del despliegue.
"""

from decimal import Decimal

from app.models.stock_model import (
    obtener_stock_producto,
    actualizar_stock_producto,
    registrar_movimiento_stock,
    obtener_stock_general,
    obtener_historial_stock,
)
from app.utils.cantidades import validar_cantidad


def _unidad_producto(producto):
    unidad = str(producto.get("unidad_de_medida", "")).strip().upper()
    if unidad not in ("UNIDAD", "KG"):
        raise ValueError("La unidad de medida debe ser UNIDAD o KG")
    return unidad


def _numero_json(valor):
    """Convierte Decimal a número JSON; precisión exacta se conserva en cálculos.

    La conversión a float se realiza únicamente en el borde de la API.
    """
    return float(valor)


def ajustar_stock(id_producto, cantidad, tipo_ajuste, id_usuario, id_comercio):
    """Ajusta el stock de un producto del comercio autenticado."""
    if not isinstance(tipo_ajuste, str):
        raise ValueError("El tipo de ajuste debe ser texto")

    tipo_ajuste = tipo_ajuste.strip().upper()
    if tipo_ajuste not in ("AUMENTAR", "DISMINUIR"):
        raise ValueError(
            "Tipo de ajuste inválido. Debe ser AUMENTAR o DISMINUIR"
        )

    producto = obtener_stock_producto(id_producto, id_comercio)
    if not producto:
        raise ValueError("Producto no encontrado")

    if producto.get("estado") is False:
        raise ValueError("No se puede ajustar el stock de un producto inactivo")

    unidad = _unidad_producto(producto)
    cantidad_decimal = validar_cantidad(cantidad, unidad)

    stock_bruto = producto.get("stock")
    if stock_bruto is None:
        raise ValueError("El producto no posee un stock válido")
    stock_actual = validar_cantidad(stock_bruto, unidad, permitir_cero=True)

    if tipo_ajuste == "AUMENTAR":
        nuevo_stock = stock_actual + cantidad_decimal
        tipo_movimiento = "AJUSTE_ENTRADA"
    else:
        nuevo_stock = stock_actual - cantidad_decimal
        tipo_movimiento = "AJUSTE_SALIDA"

    if nuevo_stock < Decimal("0"):
        raise ValueError("El stock no puede quedar negativo")

    # NOTA: son dos escrituras independientes. Antes de producción,
    # reemplazarlas por una única función SQL transaccional con bloqueo.
    producto_actualizado = actualizar_stock_producto(
        id_producto, id_comercio, _numero_json(nuevo_stock)
    )
    if not producto_actualizado:
        raise ValueError("No se pudo actualizar el stock del producto")

    movimiento = {
        "id_producto": id_producto,
        "id_usuario": id_usuario,
        "tipo_movimiento": tipo_movimiento,
        "cantidad": _numero_json(cantidad_decimal),
        "stock_anterior": _numero_json(stock_actual),
        "stock_nuevo": _numero_json(nuevo_stock),
        "observaciones": "Ajuste manual de stock",
    }
    movimiento_registrado = registrar_movimiento_stock(movimiento)
    if not movimiento_registrado:
        raise ValueError("No se pudo registrar el movimiento de stock")

    return {
        "id_producto": id_producto,
        "nombre_producto": producto["nombre_producto"],
        "stock_anterior": _numero_json(stock_actual),
        "stock_nuevo": _numero_json(nuevo_stock),
        "cantidad": _numero_json(cantidad_decimal),
        "tipo_movimiento": tipo_movimiento,
    }


def consultar_stock_general(id_comercio, buscar=None):
    """Lista stock del comercio y opcionalmente filtra por nombre."""
    if buscar is not None:
        if not isinstance(buscar, str):
            raise ValueError("El parámetro de búsqueda debe ser texto")
        buscar = buscar.strip() or None
    return obtener_stock_general(id_comercio, buscar)


def consultar_alertas_stock(id_comercio):
    """Devuelve productos activos con stock menor o igual al mínimo."""
    productos = obtener_stock_general(id_comercio)
    alertas = []
    for producto in productos:
        if producto.get("estado") is False:
            continue
        stock = producto.get("stock")
        stock_minimo = producto.get("stock_minimo")
        if stock is None or stock_minimo is None:
            continue
        unidad = _unidad_producto(producto)
        stock_decimal = validar_cantidad(stock, unidad, permitir_cero=True)
        minimo_decimal = validar_cantidad(stock_minimo, unidad, permitir_cero=True)
        if stock_decimal <= minimo_decimal:
            alertas.append(producto)
    return alertas


def consultar_historial_stock(id_comercio, id_producto=None):
    """Consulta de solo lectura de movimientos de stock."""
    return obtener_historial_stock(id_comercio, id_producto)
