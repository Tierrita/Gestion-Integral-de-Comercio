"""
Servicio de ventas.

Contiene la lógica de negocio del módulo de ventas,
incluyendo seguridad multicomercio, stock y movimientos
financieros.
"""

from app.models.venta_model import (
    insertar_venta,
    insertar_detalle_venta,
    obtener_siguiente_numero_venta,
    obtener_cliente_por_id,
    obtener_producto_por_id,
    obtener_cuenta_por_id,
    actualizar_stock_producto,
    registrar_movimiento_stock,
    obtener_ventas,
    obtener_venta_por_id,
    obtener_detalles_venta,
    actualizar_estado_venta,
    registrar_ingreso_venta_rpc,
    anular_ingreso_venta_rpc
)


def _es_entero_positivo(valor):
    """
    Indica si un valor es un entero positivo.
    bool se excluye porque en Python hereda de int.
    """

    return (
        isinstance(valor, int)
        and not isinstance(valor, bool)
        and valor > 0
    )


def crear_venta(
    datos,
    id_comercio,
    id_usuario
):
    """
    Registra una venta dentro del comercio autenticado.

    Los campos sensibles son controlados por el backend:
    id_usuario, id_comercio, numero_venta, total y estado.

    Los precios y costos se obtienen directamente
    desde los productos almacenados en la base de datos.
    """

    if not datos or not isinstance(datos, dict):
        raise ValueError(
            "No se enviaron datos válidos de la venta"
        )

    # ==================================================
    # CLIENTE
    # ==================================================

    id_cliente = datos.get(
        "id_cliente"
    )

    if not _es_entero_positivo(id_cliente):
        raise ValueError(
            "El id_cliente debe ser un número entero mayor que cero"
        )

    cliente = obtener_cliente_por_id(
        id_cliente,
        id_comercio
    )

    if not cliente:
        raise ValueError(
            "Cliente no encontrado en el comercio actual"
        )

    if cliente.get("estado") is not True:
        raise ValueError(
            "El cliente se encuentra inactivo"
        )

    # ==================================================
    # MÉTODO DE PAGO
    # ==================================================

    metodo_pago = datos.get(
        "metodo_pago"
    )

    if not isinstance(metodo_pago, str):
        raise ValueError(
            "El metodo_pago debe ser texto"
        )

    metodo_pago = metodo_pago.strip().upper()

    if not metodo_pago:
        raise ValueError(
            "El metodo_pago no puede estar vacío"
        )

    # ==================================================
    # CUENTA FINANCIERA
    # ==================================================

    id_cuenta = datos.get(
        "id_cuenta"
    )

    if metodo_pago != "CUENTA_CORRIENTE":

        if not _es_entero_positivo(id_cuenta):
            raise ValueError(
                "El id_cuenta es obligatorio para ventas "
                "cobradas en el momento"
            )

        cuenta = obtener_cuenta_por_id(
            id_cuenta,
            id_comercio
        )

        if not cuenta:
            raise ValueError(
                "Cuenta financiera no encontrada en el comercio actual"
            )

        if cuenta.get("estado") is not True:
            raise ValueError(
                "La cuenta financiera se encuentra inactiva"
            )

    # ==================================================
    # PRODUCTOS
    # ==================================================

    productos = datos.get(
        "productos"
    )

    if (
        not isinstance(productos, list)
        or len(productos) == 0
    ):
        raise ValueError(
            "La venta debe contener al menos un producto"
        )

    detalles = []
    productos_utilizados = set()
    total_venta = 0.0

    for producto_venta in productos:

        if not isinstance(producto_venta, dict):
            raise ValueError(
                "Cada producto de la venta debe ser un objeto válido"
            )

        id_producto = producto_venta.get(
            "id_producto"
        )

        cantidad = producto_venta.get(
            "cantidad"
        )

        if not _es_entero_positivo(id_producto):
            raise ValueError(
                "El id_producto debe ser un número entero mayor que cero"
            )

        if not _es_entero_positivo(cantidad):
            raise ValueError(
                "La cantidad debe ser un número entero mayor que cero"
            )

        # ----------------------------------------------
        # EVITAR PRODUCTOS DUPLICADOS
        # ----------------------------------------------

        if id_producto in productos_utilizados:
            raise ValueError(
                f"El producto con ID {id_producto} "
                "está repetido en la venta"
            )

        productos_utilizados.add(
            id_producto
        )

        # ----------------------------------------------
        # PRODUCTO DEL COMERCIO
        # ----------------------------------------------

        producto = obtener_producto_por_id(
            id_producto,
            id_comercio
        )

        if not producto:
            raise ValueError(
                f"El producto con ID {id_producto} "
                "no existe en el comercio actual"
            )

        if producto.get("estado") is not True:
            raise ValueError(
                f"El producto {producto['nombre_producto']} "
                "se encuentra inactivo"
            )

        # ----------------------------------------------
        # STOCK
        # ----------------------------------------------

        stock_actual = producto.get(
            "stock"
        )

        if stock_actual is None:
            raise ValueError(
                f"El producto {producto['nombre_producto']} "
                "no posee stock válido"
            )

        stock_actual = int(
            stock_actual
        )

        if stock_actual < cantidad:
            raise ValueError(
                f"Stock insuficiente para el producto "
                f"{producto['nombre_producto']}. "
                f"Stock disponible: {stock_actual}"
            )

        # ----------------------------------------------
        # PRECIOS REALES DESDE LA BD
        # ----------------------------------------------

        if producto.get("precio_venta") is None:
            raise ValueError(
                f"El producto {producto['nombre_producto']} "
                "no posee precio de venta"
            )

        if producto.get("precio_costo") is None:
            raise ValueError(
                f"El producto {producto['nombre_producto']} "
                "no posee precio de costo"
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
                "posee un precio de venta inválido"
            )

        if costo_unitario < 0:
            raise ValueError(
                f"El producto {producto['nombre_producto']} "
                "posee un precio de costo inválido"
            )

        # ----------------------------------------------
        # SUBTOTAL
        # ----------------------------------------------

        subtotal = round(
            cantidad * precio_unitario,
            2
        )

        total_venta += subtotal

        detalles.append({
            "id_producto": id_producto,
            "nombre_producto": producto["nombre_producto"],
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "costo_unitario": costo_unitario,
            "subtotal": subtotal,
            "stock_anterior": stock_actual,
            "stock_nuevo": stock_actual - cantidad
        })

    total_venta = round(
        total_venta,
        2
    )

    # ==================================================
    # NÚMERO LOCAL
    # ==================================================

    numero_venta = obtener_siguiente_numero_venta(
        id_comercio
    )

    if numero_venta is None:
        raise ValueError(
            "No se pudo generar el número de venta"
        )

    # ==================================================
    # CREAR VENTA
    # ==================================================

    datos_venta = {
        "id_usuario": id_usuario,
        "id_cliente": id_cliente,
        "id_comercio": id_comercio,
        "numero_venta": numero_venta,
        "total": total_venta,
        "metodo_pago": metodo_pago,
        "estado": "COMPLETADA",
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

    venta = venta_creada[0]

    id_venta = venta[
        "id_venta"
    ]

    # ==================================================
    # DETALLES + STOCK + HISTORIAL
    # ==================================================

    detalles_creados = []
    productos_actualizados = []

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

        # ----------------------------------------------
        # DESCONTAR STOCK
        # ----------------------------------------------

        producto_actualizado = actualizar_stock_producto(
            detalle["id_producto"],
            id_comercio,
            detalle["stock_nuevo"]
        )

        if not producto_actualizado:
            raise ValueError(
                f"No se pudo actualizar el stock del producto "
                f"{detalle['nombre_producto']}"
            )

        # ----------------------------------------------
        # HISTORIAL
        # ----------------------------------------------

        registrar_movimiento_stock({
            "id_producto": detalle["id_producto"],
            "id_usuario": id_usuario,
            "tipo_movimiento": "VENTA",
            "cantidad": detalle["cantidad"],
            "stock_anterior": detalle["stock_anterior"],
            "stock_nuevo": detalle["stock_nuevo"],
            "observaciones": (
                f"Venta #{numero_venta} "
                f"(ID global {id_venta})"
            )
        })

        productos_actualizados.append({
            "id_producto": detalle["id_producto"],
            "nombre_producto": detalle["nombre_producto"],
            "cantidad": detalle["cantidad"],
            "stock_anterior": detalle["stock_anterior"],
            "stock_actual": detalle["stock_nuevo"],
            "precio_unitario": detalle["precio_unitario"],
            "costo_unitario": detalle["costo_unitario"]
        })

    # ==================================================
    # MOVIMIENTO FINANCIERO
    # ==================================================

    movimiento_financiero = None

    if metodo_pago != "CUENTA_CORRIENTE":

        movimiento_financiero = registrar_ingreso_venta_rpc(
            id_venta=id_venta,
            id_cuenta=id_cuenta,
            id_usuario=id_usuario,
            monto=total_venta
        )

    # ==================================================
    # RESPUESTA
    # ==================================================

    return {
        "venta": venta,
        "detalles": detalles_creados,
        "productos_actualizados": productos_actualizados,
        "movimiento_financiero": movimiento_financiero
    }


def listar_ventas(id_comercio):
    """
    Obtiene únicamente las ventas
    del comercio autenticado.
    """

    return obtener_ventas(
        id_comercio
    )


def buscar_venta_por_id(
    id_venta,
    id_comercio
):
    """
    Obtiene una venta específica del comercio
    junto con sus detalles.
    """

    venta = obtener_venta_por_id(
        id_venta,
        id_comercio
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


def anular_venta(
    id_venta,
    id_comercio,
    id_usuario_anulacion
):
    """
    Anula una venta perteneciente al comercio autenticado.

    Devuelve los productos al stock y revierte el ingreso
    financiero cuando la venta había sido cobrada.

    El usuario que queda registrado en la anulación
    es quien ejecuta actualmente la operación.
    """

    # ==================================================
    # BUSCAR VENTA
    # ==================================================

    venta = obtener_venta_por_id(
        id_venta,
        id_comercio
    )

    if not venta:
        raise ValueError(
            "Venta no encontrada"
        )

    # ==================================================
    # EVITAR DOBLE ANULACIÓN
    # ==================================================

    if (
        str(
            venta.get("estado", "")
        ).upper()
        == "ANULADA"
    ):
        raise ValueError(
            "La venta ya se encuentra anulada"
        )

    # ==================================================
    # DETALLES
    # ==================================================

    detalles = obtener_detalles_venta(
        id_venta
    )

    if not detalles:
        raise ValueError(
            "La venta no posee productos asociados"
        )

    productos_a_revertir = []

    for detalle in detalles:

        producto = obtener_producto_por_id(
            detalle["id_producto"],
            id_comercio
        )

        if not producto:
            raise ValueError(
                f"El producto con ID "
                f"{detalle['id_producto']} no existe "
                "en el comercio actual"
            )

        stock_actual = int(
            producto["stock"]
        )

        cantidad = int(
            detalle["cantidad"]
        )

        productos_a_revertir.append({
            "id_producto": detalle["id_producto"],
            "nombre_producto": producto["nombre_producto"],
            "cantidad": cantidad,
            "stock_anterior": stock_actual,
            "stock_nuevo": stock_actual + cantidad
        })

    # ==================================================
    # REVERTIR MOVIMIENTO FINANCIERO
    # ==================================================
    #
    # Primero se revierte el dinero.
    #
    # Si la cuenta no posee fondos suficientes para
    # realizar la anulación, la operación se detiene
    # antes de modificar el stock.
    #
    # Para CUENTA_CORRIENTE la RPC devuelve None porque
    # la venta no generó un ingreso financiero inmediato.
    # ==================================================

    movimiento_financiero = anular_ingreso_venta_rpc(
        id_venta=id_venta,
        id_usuario=id_usuario_anulacion
    )

    # ==================================================
    # DEVOLVER STOCK
    # ==================================================

    productos_revertidos = []

    for producto in productos_a_revertir:

        producto_actualizado = actualizar_stock_producto(
            producto["id_producto"],
            id_comercio,
            producto["stock_nuevo"]
        )

        if not producto_actualizado:
            raise ValueError(
                f"No se pudo devolver el stock del producto "
                f"{producto['nombre_producto']}"
            )

        registrar_movimiento_stock({
            "id_producto": producto["id_producto"],
            "id_usuario": id_usuario_anulacion,
            "tipo_movimiento": "ANULACION_VENTA",
            "cantidad": producto["cantidad"],
            "stock_anterior": producto["stock_anterior"],
            "stock_nuevo": producto["stock_nuevo"],
            "observaciones": (
                f"Anulación Venta #{venta['numero_venta']} "
                f"(ID global {id_venta})"
            )
        })

        productos_revertidos.append({
            "id_producto": producto["id_producto"],
            "cantidad": producto["cantidad"],
            "stock_anterior": producto["stock_anterior"],
            "stock_nuevo": producto["stock_nuevo"]
        })

    # ==================================================
    # CAMBIAR ESTADO
    # ==================================================

    venta_actualizada = actualizar_estado_venta(
        id_venta,
        id_comercio,
        "ANULADA"
    )

    if not venta_actualizada:
        raise ValueError(
            "No se pudo actualizar el estado de la venta"
        )

    # ==================================================
    # RESPUESTA
    # ==================================================

    return {
        "venta": venta_actualizada,
        "productos_revertidos": productos_revertidos,
        "movimiento_financiero": movimiento_financiero
    }