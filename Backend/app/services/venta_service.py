"""
Servicio de ventas.

Este módulo contiene la lógica de negocio relacionada
con las ventas.
"""

from app.models.venta_model import (
    insertar_venta,
    insertar_detalle_venta,
    obtener_producto_por_id,
    actualizar_stock_producto,
    registrar_movimiento_stock,
    obtener_ventas,
    obtener_venta_por_id,
    obtener_detalles_venta,
    actualizar_estado_venta
)


def crear_venta(datos):
    """
    Registra una venta junto con sus productos.

    Valida la existencia y disponibilidad de stock,
    calcula los subtotales y el total general,
    registra la venta, descuenta el stock y genera
    los movimientos correspondientes en el historial.
    """

    if not datos:
        raise ValueError("No se enviaron datos de la venta")

    # Validar datos generales
    if "id_usuario" not in datos:
        raise ValueError("El campo 'id_usuario' es obligatorio")

    if "metodo_pago" not in datos:
        raise ValueError("El campo 'metodo_pago' es obligatorio")

    if "productos" not in datos:
        raise ValueError("El campo 'productos' es obligatorio")

    productos = datos["productos"]

    if not isinstance(productos, list) or len(productos) == 0:
        raise ValueError("La venta debe contener al menos un producto")

    # Preparar productos y validar stock antes de crear la venta
    detalles = []
    total_venta = 0

    for producto_venta in productos:

        if "id_producto" not in producto_venta:
            raise ValueError("Cada producto debe tener 'id_producto'")

        if "cantidad" not in producto_venta:
            raise ValueError("Cada producto debe tener 'cantidad'")

        if "precio_unitario" not in producto_venta:
            raise ValueError("Cada producto debe tener 'precio_unitario'")

        cantidad = producto_venta["cantidad"]
        precio_unitario = producto_venta["precio_unitario"]

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        if precio_unitario <= 0:
            raise ValueError("El precio unitario debe ser mayor a 0")

        # Consultar producto
        producto = obtener_producto_por_id(
            producto_venta["id_producto"]
        )

        if not producto:
            raise ValueError(
                f"El producto con ID "
                f"{producto_venta['id_producto']} no existe"
            )

        stock_actual = producto["stock"]

        # Validar disponibilidad
        if stock_actual < cantidad:
            raise ValueError(
                f"Stock insuficiente para el producto "
                f"{producto['nombre_producto']}. "
                f"Stock disponible: {stock_actual}"
            )

        subtotal = cantidad * precio_unitario

        total_venta += subtotal

        detalles.append({
            "id_producto": producto_venta["id_producto"],
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal,
            "stock_anterior": stock_actual,
            "stock_nuevo": stock_actual - cantidad
        })

    # Crear venta principal
    datos_venta = {
        "id_usuario": datos["id_usuario"],
        "total": total_venta,
        "metodo_pago": datos["metodo_pago"],
        "estado": datos.get("estado", "COMPLETADA"),
        "observaciones": datos.get("observaciones")
    }

    venta_creada = insertar_venta(datos_venta)

    id_venta = venta_creada[0]["id_venta"]

    # Registrar productos de la venta
    detalles_creados = []

    for detalle in detalles:

        datos_detalle = {
            "id_venta": id_venta,
            "id_producto": detalle["id_producto"],
            "cantidad": detalle["cantidad"],
            "precio_unitario": detalle["precio_unitario"],
            "subtotal": detalle["subtotal"]
        }

        detalle_creado = insertar_detalle_venta(datos_detalle)

        detalles_creados.extend(detalle_creado)

        # Descontar stock
        actualizar_stock_producto(
            detalle["id_producto"],
            detalle["stock_nuevo"]
        )

        # Registrar movimiento
        datos_movimiento = {
            "id_producto": detalle["id_producto"],
            "id_usuario": datos["id_usuario"],
            "tipo_movimiento": "VENTA",
            "cantidad": detalle["cantidad"],
            "stock_anterior": detalle["stock_anterior"],
            "stock_nuevo": detalle["stock_nuevo"],
            "observaciones": f"Venta #{id_venta}"
        }

        registrar_movimiento_stock(datos_movimiento)

    return {
        "venta": venta_creada[0],
        "detalles": detalles_creados
    }


def listar_ventas():
    """
    Obtiene todas las ventas registradas.
    """

    ventas = obtener_ventas()

    return ventas



def buscar_venta_por_id(id_venta):
    """
    Obtiene una venta específica junto con
    todos sus detalles.
    """

    venta = obtener_venta_por_id(id_venta)

    if not venta:
        raise ValueError("Venta no encontrada")

    detalles = obtener_detalles_venta(id_venta)

    return {
        "venta": venta,
        "detalles": detalles
    }



def anular_venta(id_venta):
    """
    Anula una venta registrada.

    Devuelve al stock los productos incluidos en la venta,
    registra los movimientos correspondientes en el historial
    y cambia el estado de la venta a 'ANULADA'.
    """

    # Buscar la venta
    venta = obtener_venta_por_id(id_venta)

    if not venta:
        raise ValueError("Venta no encontrada")

    # Evitar doble anulación
    if venta["estado"].upper() == "ANULADA":
        raise ValueError("La venta ya se encuentra anulada")

    # Obtener productos vendidos
    detalles = obtener_detalles_venta(id_venta)

    if not detalles:
        raise ValueError("La venta no posee productos asociados")

    productos_a_revertir = []

    # Preparar la devolución de stock
    for detalle in detalles:

        producto = obtener_producto_por_id(
            detalle["id_producto"]
        )

        if not producto:
            raise ValueError(
                f"El producto con ID {detalle['id_producto']} no existe"
            )

        stock_actual = producto["stock"]
        cantidad = detalle["cantidad"]

        productos_a_revertir.append({
            "id_producto": detalle["id_producto"],
            "cantidad": cantidad,
            "stock_anterior": stock_actual,
            "stock_nuevo": stock_actual + cantidad
        })

    # Devolver productos al stock
    for producto in productos_a_revertir:

        actualizar_stock_producto(
            producto["id_producto"],
            producto["stock_nuevo"]
        )

        # Registrar anulación en historial
        datos_movimiento = {
            "id_producto": producto["id_producto"],
            "id_usuario": venta["id_usuario"],
            "tipo_movimiento": "ANULACION_VENTA",
            "cantidad": producto["cantidad"],
            "stock_anterior": producto["stock_anterior"],
            "stock_nuevo": producto["stock_nuevo"],
            "observaciones": f"Anulación Venta #{id_venta}"
        }

        registrar_movimiento_stock(datos_movimiento)

    # Cambiar estado de la venta
    venta_actualizada = actualizar_estado_venta(
        id_venta,
        "ANULADA"
    )

    return {
        "venta": venta_actualizada,
        "productos_revertidos": productos_a_revertir
    }