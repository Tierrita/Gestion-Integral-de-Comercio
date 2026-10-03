"""
Servicio de compras.

Este módulo contiene la lógica de negocio relacionada
con las compras.
"""

from app.models.compra_model import (
    insertar_compra,
    insertar_detalle_compra,
    obtener_producto_por_id,
    actualizar_stock_producto,
    registrar_movimiento_stock,
    obtener_compras,
    obtener_compra_por_id,
    obtener_detalles_compra,
    actualizar_estado_compra
)


def crear_compra(datos):
    """
    Registra una compra junto con sus productos.

    Calcula los subtotales de cada producto, el total
    general de la compra, actualiza el stock y registra
    los movimientos en el historial.
    """

    if not datos:
        raise ValueError("No se enviaron datos de la compra")

    # Validar datos generales
    if "id_proveedor" not in datos:
        raise ValueError("El campo 'id_proveedor' es obligatorio")

    if "id_usuario" not in datos:
        raise ValueError("El campo 'id_usuario' es obligatorio")

    if "productos" not in datos:
        raise ValueError("El campo 'productos' es obligatorio")

    productos = datos["productos"]

    if not isinstance(productos, list) or len(productos) == 0:
        raise ValueError("La compra debe contener al menos un producto")

    # Calcular subtotales y total de la compra
    detalles = []
    total_compra = 0

    for producto in productos:

        if "id_producto" not in producto:
            raise ValueError("Cada producto debe tener 'id_producto'")

        if "cantidad" not in producto:
            raise ValueError("Cada producto debe tener 'cantidad'")

        if "precio_unitario" not in producto:
            raise ValueError("Cada producto debe tener 'precio_unitario'")

        cantidad = producto["cantidad"]
        precio_unitario = producto["precio_unitario"]

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        if precio_unitario <= 0:
            raise ValueError("El precio unitario debe ser mayor a 0")

        subtotal = cantidad * precio_unitario

        total_compra += subtotal

        detalles.append({
            "id_producto": producto["id_producto"],
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "subtotal": subtotal
        })

    # Crear la compra principal
    datos_compra = {
        "id_proveedor": datos["id_proveedor"],
        "id_usuario": datos["id_usuario"],
        "total_compra": total_compra,
        "estado": datos.get("estado", "COMPLETADA"),
        "observaciones": datos.get("observaciones")
    }

    compra_creada = insertar_compra(datos_compra)

    id_compra = compra_creada[0]["id_compra"]

    # Registrar los productos de la compra
    detalles_creados = []

    for detalle in detalles:

        # Crear detalle de compra
        datos_detalle = {
            "id_compra": id_compra,
            "id_producto": detalle["id_producto"],
            "cantidad": detalle["cantidad"],
            "precio_unitario": detalle["precio_unitario"],
            "subtotal": detalle["subtotal"]
        }

        detalle_creado = insertar_detalle_compra(datos_detalle)

        detalles_creados.extend(detalle_creado)

        # Obtener stock actual del producto
        producto = obtener_producto_por_id(
            detalle["id_producto"]
        )

        if not producto:
            raise ValueError(
                f"El producto con ID {detalle['id_producto']} no existe"
            )

        stock_anterior = producto["stock"]

        # Calcular nuevo stock
        stock_nuevo = stock_anterior + detalle["cantidad"]

        # Actualizar stock del producto
        actualizar_stock_producto(
            detalle["id_producto"],
            stock_nuevo
        )

        # Preparar movimiento de stock
        datos_movimiento = {
            "id_producto": detalle["id_producto"],
            "id_usuario": datos["id_usuario"],
            "tipo_movimiento": "COMPRA",
            "cantidad": detalle["cantidad"],
            "stock_anterior": stock_anterior,
            "stock_nuevo": stock_nuevo,
            "observaciones": f"Compra #{id_compra}"
        }

        # Registrar movimiento en el historial
        registrar_movimiento_stock(datos_movimiento)

    # Devolver compra y detalles registrados
    return {
        "compra": compra_creada[0],
        "detalles": detalles_creados
    }



def listar_compras():
    """
    Obtiene todas las compras registradas.
    """

    compras = obtener_compras()

    return compras


def buscar_compra_por_id(id_compra):
    """
    Obtiene una compra específica junto con
    todos sus detalles.
    """

    compra = obtener_compra_por_id(id_compra)

    if not compra:
        raise ValueError("Compra no encontrada")

    detalles = obtener_detalles_compra(id_compra)

    return {
        "compra": compra,
        "detalles": detalles
    }



def anular_compra(id_compra):
    """
    Anula una compra registrada.

    Revierte el stock de los productos incluidos en la compra,
    registra los movimientos correspondientes en el historial
    y cambia el estado de la compra a 'ANULADA'.
    """

    # Buscar la compra
    compra = obtener_compra_por_id(id_compra)

    if not compra:
        raise ValueError("Compra no encontrada")

    # Verificar que no esté anulada previamente
    if compra["estado"].upper() == "ANULADA":
        raise ValueError("La compra ya se encuentra anulada")

    # Obtener productos de la compra
    detalles = obtener_detalles_compra(id_compra)

    if not detalles:
        raise ValueError("La compra no posee productos asociados")

    # Primero validar todos los productos antes de modificar stock
    productos_a_revertir = []

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

        # Evitar stock negativo
        if stock_actual < cantidad:
            raise ValueError(
                f"No se puede anular la compra. "
                f"Stock insuficiente para el producto "
                f"{detalle['id_producto']}"
            )

        productos_a_revertir.append({
            "id_producto": detalle["id_producto"],
            "cantidad": cantidad,
            "stock_anterior": stock_actual,
            "stock_nuevo": stock_actual - cantidad
        })

    # Revertir stock
    for producto in productos_a_revertir:

        actualizar_stock_producto(
            producto["id_producto"],
            producto["stock_nuevo"]
        )

        # Registrar la reversión en el historial
        datos_movimiento = {
            "id_producto": producto["id_producto"],
            "id_usuario": compra["id_usuario"],
            "tipo_movimiento": "ANULACION_COMPRA",
            "cantidad": producto["cantidad"],
            "stock_anterior": producto["stock_anterior"],
            "stock_nuevo": producto["stock_nuevo"],
            "observaciones": f"Anulación Compra #{id_compra}"
        }

        registrar_movimiento_stock(datos_movimiento)

    # Cambiar estado de la compra
    compra_actualizada = actualizar_estado_compra(
        id_compra,
        "ANULADA"
    )

    return {
        "compra": compra_actualizada,
        "productos_revertidos": productos_a_revertir
    }