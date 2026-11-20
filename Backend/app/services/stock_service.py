"""Servicio de stock del comercio autenticado."""

from app.models.stock_model import (
    obtener_stock_producto,
    ajustar_stock_atomico as ejecutar_ajuste_atomico,
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

    try:
        return ejecutar_ajuste_atomico(
            id_producto=id_producto,
            id_comercio=id_comercio,
            id_usuario=id_usuario,
            cantidad=cantidad_decimal,
            tipo_ajuste=tipo_ajuste,
        )
    except Exception as error:
        # Errores de negocio conocidos: mantener respuesta 400/404 del controller.
        mensaje = str(error)
        errores_negocio = (
            "Producto no encontrado",
            "No se puede ajustar el stock de un producto inactivo",
            "El stock no puede quedar negativo",
            "Usuario no autorizado para este comercio",
            "Cantidad inválida",
            "La cantidad en unidades debe ser entera",
        )
        for texto in errores_negocio:
            if texto in mensaje:
                raise ValueError(texto) from error
        raise


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
