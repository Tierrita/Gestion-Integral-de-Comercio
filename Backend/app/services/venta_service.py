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
    obtiene el precio de venta y costo directamente
    desde el producto, calcula los subtotales y el total,
    registra la venta, descuenta el stock y genera
    los movimientos correspondientes en el historial.

    El costo_unitario queda guardado en detalle_venta
    como costo histórico al momento de realizar la venta.
    """

    if not datos:
        raise ValueError("No se enviaron datos de la venta")

    # --------------------------------------------------
    # VALIDAR DATOS GENERALES
    # --------------------------------------------------

    if "id_usuario" not in datos:
        raise ValueError(
            "El campo 'id_usuario' es obligatorio"
        )

    if "id_cliente" not in datos:
        raise ValueError(
            "El campo 'id_cliente' es obligatorio"
        )

    if "metodo_pago" not in datos:
        raise ValueError(
            "El campo 'metodo_pago' es obligatorio"
        )

    if "productos" not in datos:
        raise ValueError(
            "El campo 'productos' es obligatorio"
        )

    # --------------------------------------------------
    # VALIDAR ID USUARIO
    # --------------------------------------------------

    id_usuario = datos["id_usuario"]

    if (
        not isinstance(id_usuario, int)
        or isinstance(id_usuario, bool)
    ):
        raise ValueError(
            "El id_usuario debe ser un número entero"
        )

    if id_usuario <= 0:
        raise ValueError(
            "El id_usuario debe ser mayor que cero"
        )

    # --------------------------------------------------
    # VALIDAR ID CLIENTE
    # --------------------------------------------------

    id_cliente = datos["id_cliente"]

    if (
        not isinstance(id_cliente, int)
        or isinstance(id_cliente, bool)
    ):
        raise ValueError(
            "El id_cliente debe ser un número entero"
        )

    if id_cliente <= 0:
        raise ValueError(
            "El id_cliente debe ser mayor que cero"
        )

    # --------------------------------------------------
    # VALIDAR MÉTODO DE PAGO
    # --------------------------------------------------

    metodo_pago = datos["metodo_pago"]

    if not isinstance(metodo_pago, str):
        raise ValueError(
            "El metodo_pago debe ser texto"
        )

    metodo_pago = metodo_pago.strip()

    if not metodo_pago:
        raise ValueError(
            "El metodo_pago no puede estar vacío"
        )

    # --------------------------------------------------
    # VALIDAR PRODUCTOS
    # --------------------------------------------------

    productos = datos["productos"]

    if not isinstance(productos, list) or len(productos) == 0:
        raise ValueError(
            "La venta debe contener al menos un producto"
        )

    # --------------------------------------------------
    # PREPARAR PRODUCTOS Y VALIDAR STOCK
    # --------------------------------------------------

    detalles = []
    total_venta = 0

    for producto_venta in productos:

        if "id_producto" not in producto_venta:
            raise ValueError(
                "Cada producto debe tener 'id_producto'"
            )

        if "cantidad" not in producto_venta:
            raise ValueError(
                "Cada producto debe tener 'cantidad'"
            )

        id_producto = producto_venta["id_producto"]
        cantidad = producto_venta["cantidad"]

        # --------------------------------------------------
        # VALIDAR ID PRODUCTO
        # --------------------------------------------------

        if (
            not isinstance(id_producto, int)
            or isinstance(id_producto, bool)
        ):
            raise ValueError(
                "El id_producto debe ser un número entero"
            )

        if id_producto <= 0:
            raise ValueError(
                "El id_producto debe ser mayor que cero"
            )

        # --------------------------------------------------
        # VALIDAR CANTIDAD
        # --------------------------------------------------

        if (
            not isinstance(cantidad, int)
            or isinstance(cantidad, bool)
        ):
            raise ValueError(
                "La cantidad debe ser un número entero"
            )

        if cantidad <= 0:
            raise ValueError(
                "La cantidad debe ser mayor a 0"
            )

        # --------------------------------------------------
        # CONSULTAR PRODUCTO
        # --------------------------------------------------

        producto = obtener_producto_por_id(
            id_producto
        )

        if not producto:
            raise ValueError(
                f"El producto con ID {id_producto} no existe"
            )

        # --------------------------------------------------
        # OBTENER DATOS ACTUALES DEL PRODUCTO
        # --------------------------------------------------

        stock_actual = producto["stock"]

        if producto.get("precio_venta") is None:
            raise ValueError(
                f"El producto {producto['nombre_producto']} "
                f"no posee precio de venta"
            )

        if producto.get("precio_costo") is None:
            raise ValueError(
                f"El producto {producto['nombre_producto']} "
                f"no posee precio de costo"
            )

        precio_unitario = float(
            producto["precio_venta"]
        )

        costo_unitario = float(
            producto["precio_costo"]
        )

        if precio_unitario <= 0:
            raise ValueError(
                f"El producto {producto['nombre_producto']} "
                f"posee un precio de venta inválido"
            )

        if costo_unitario < 0:
            raise ValueError(
                f"El producto {producto['nombre_producto']} "
                f"posee un precio de costo inválido"
            )

        # --------------------------------------------------
        # VALIDAR STOCK
        # --------------------------------------------------

        if stock_actual < cantidad:
            raise ValueError(
                f"Stock insuficiente para el producto "
                f"{producto['nombre_producto']}. "
                f"Stock disponible: {stock_actual}"
            )

        # --------------------------------------------------
        # CALCULAR SUBTOTAL
        # --------------------------------------------------

        subtotal = cantidad * precio_unitario

        total_venta += subtotal

        # --------------------------------------------------
        # PREPARAR DETALLE
        # --------------------------------------------------

        detalles.append({
            "id_producto": id_producto,
            "cantidad": cantidad,

            # Precio histórico de venta
            "precio_unitario": precio_unitario,

            # Costo histórico del producto
            "costo_unitario": costo_unitario,

            "subtotal": subtotal,

            "stock_anterior": stock_actual,
            "stock_nuevo": stock_actual - cantidad
        })

    # --------------------------------------------------
    # CREAR VENTA PRINCIPAL
    # --------------------------------------------------

    datos_venta = {
        "id_usuario": id_usuario,
        "id_cliente": id_cliente,
        "total": total_venta,
        "metodo_pago": metodo_pago,
        "estado": datos.get(
            "estado",
            "COMPLETADA"
        ),
        "observaciones": datos.get(
            "observaciones"
        )
    }

    venta_creada = insertar_venta(
        datos_venta
    )

    if not venta_creada:
        raise ValueError(
            "No se pudo registrar la venta"
        )

    id_venta = venta_creada[0]["id_venta"]

    # --------------------------------------------------
    # REGISTRAR DETALLES
    # --------------------------------------------------

    detalles_creados = []

    for detalle in detalles:

        datos_detalle = {
            "id_venta": id_venta,
            "id_producto": detalle["id_producto"],
            "cantidad": detalle["cantidad"],
            "precio_unitario": detalle["precio_unitario"],
            "costo_unitario": detalle["costo_unitario"],
            "subtotal": detalle["subtotal"]
        }

        detalle_creado = insertar_detalle_venta(
            datos_detalle
        )

        detalles_creados.extend(
            detalle_creado
        )

        # --------------------------------------------------
        # DESCONTAR STOCK
        # --------------------------------------------------

        actualizar_stock_producto(
            detalle["id_producto"],
            detalle["stock_nuevo"]
        )

        # --------------------------------------------------
        # REGISTRAR MOVIMIENTO DE STOCK
        # --------------------------------------------------

        datos_movimiento = {
            "id_producto": detalle["id_producto"],
            "id_usuario": id_usuario,
            "tipo_movimiento": "VENTA",
            "cantidad": detalle["cantidad"],
            "stock_anterior": detalle["stock_anterior"],
            "stock_nuevo": detalle["stock_nuevo"],
            "observaciones": f"Venta #{id_venta}"
        }

        registrar_movimiento_stock(
            datos_movimiento
        )

    # --------------------------------------------------
    # RESPUESTA
    # --------------------------------------------------

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

    venta = obtener_venta_por_id(
        id_venta
    )

    if not venta:
        raise ValueError(
            "Venta no encontrada"
        )

    detalles = obtener_detalles_venta(
        id_venta
    )

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

    # --------------------------------------------------
    # BUSCAR VENTA
    # --------------------------------------------------

    venta = obtener_venta_por_id(
        id_venta
    )

    if not venta:
        raise ValueError(
            "Venta no encontrada"
        )

    # --------------------------------------------------
    # EVITAR DOBLE ANULACIÓN
    # --------------------------------------------------

    if venta["estado"].upper() == "ANULADA":
        raise ValueError(
            "La venta ya se encuentra anulada"
        )

    # --------------------------------------------------
    # OBTENER PRODUCTOS VENDIDOS
    # --------------------------------------------------

    detalles = obtener_detalles_venta(
        id_venta
    )

    if not detalles:
        raise ValueError(
            "La venta no posee productos asociados"
        )

    productos_a_revertir = []

    # --------------------------------------------------
    # PREPARAR DEVOLUCIÓN DE STOCK
    # --------------------------------------------------

    for detalle in detalles:

        producto = obtener_producto_por_id(
            detalle["id_producto"]
        )

        if not producto:
            raise ValueError(
                f"El producto con ID "
                f"{detalle['id_producto']} no existe"
            )

        stock_actual = producto["stock"]
        cantidad = detalle["cantidad"]

        productos_a_revertir.append({
            "id_producto": detalle["id_producto"],
            "cantidad": cantidad,
            "stock_anterior": stock_actual,
            "stock_nuevo": stock_actual + cantidad
        })

    # --------------------------------------------------
    # DEVOLVER PRODUCTOS AL STOCK
    # --------------------------------------------------

    for producto in productos_a_revertir:

        actualizar_stock_producto(
            producto["id_producto"],
            producto["stock_nuevo"]
        )

        # --------------------------------------------------
        # REGISTRAR MOVIMIENTO DE ANULACIÓN
        # --------------------------------------------------

        datos_movimiento = {
            "id_producto": producto["id_producto"],
            "id_usuario": venta["id_usuario"],
            "tipo_movimiento": "ANULACION_VENTA",
            "cantidad": producto["cantidad"],
            "stock_anterior": producto["stock_anterior"],
            "stock_nuevo": producto["stock_nuevo"],
            "observaciones": (
                f"Anulación Venta #{id_venta}"
            )
        }

        registrar_movimiento_stock(
            datos_movimiento
        )

    # --------------------------------------------------
    # CAMBIAR ESTADO DE LA VENTA
    # --------------------------------------------------

    venta_actualizada = actualizar_estado_venta(
        id_venta,
        "ANULADA"
    )

    return {
        "venta": venta_actualizada,
        "productos_revertidos": productos_a_revertir
    }