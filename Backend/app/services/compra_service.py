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
    actualizar_precios_producto,
    registrar_movimiento_stock,
    obtener_compras,
    obtener_compra_por_id,
    obtener_detalles_compra,
    actualizar_estado_compra
)


def crear_compra(datos):
    """
    Registra una compra junto con sus productos.

    Calcula los subtotales y el total de la compra,
    actualiza el stock y registra los movimientos.

    Si el nuevo costo de compra de un producto es mayor
    al costo actual, actualiza el precio de costo y
    recalcula el precio de venta manteniendo el mismo
    porcentaje de recargo (markup).

    Si el nuevo costo es menor o igual al actual,
    mantiene los precios actuales.
    """

    if not datos:
        raise ValueError("No se enviaron datos de la compra")

    # --------------------------------------------------
    # VALIDAR DATOS GENERALES
    # --------------------------------------------------

    if "id_proveedor" not in datos:
        raise ValueError(
            "El campo 'id_proveedor' es obligatorio"
        )

    if "id_usuario" not in datos:
        raise ValueError(
            "El campo 'id_usuario' es obligatorio"
        )

    if "productos" not in datos:
        raise ValueError(
            "El campo 'productos' es obligatorio"
        )

    id_proveedor = datos["id_proveedor"]
    id_usuario = datos["id_usuario"]
    productos = datos["productos"]

    if (
        not isinstance(id_proveedor, int)
        or isinstance(id_proveedor, bool)
        or id_proveedor <= 0
    ):
        raise ValueError(
            "El id_proveedor debe ser un número entero mayor que cero"
        )

    if (
        not isinstance(id_usuario, int)
        or isinstance(id_usuario, bool)
        or id_usuario <= 0
    ):
        raise ValueError(
            "El id_usuario debe ser un número entero mayor que cero"
        )

    if not isinstance(productos, list) or len(productos) == 0:
        raise ValueError(
            "La compra debe contener al menos un producto"
        )

    # --------------------------------------------------
    # PREPARAR PRODUCTOS
    # --------------------------------------------------

    detalles = []
    total_compra = 0

    for producto_compra in productos:

        if "id_producto" not in producto_compra:
            raise ValueError(
                "Cada producto debe tener 'id_producto'"
            )

        if "cantidad" not in producto_compra:
            raise ValueError(
                "Cada producto debe tener 'cantidad'"
            )

        if "precio_unitario" not in producto_compra:
            raise ValueError(
                "Cada producto debe tener 'precio_unitario'"
            )

        id_producto = producto_compra["id_producto"]
        cantidad = producto_compra["cantidad"]
        precio_unitario = producto_compra["precio_unitario"]

        # --------------------------------------------------
        # VALIDAR ID PRODUCTO
        # --------------------------------------------------

        if (
            not isinstance(id_producto, int)
            or isinstance(id_producto, bool)
            or id_producto <= 0
        ):
            raise ValueError(
                "El id_producto debe ser un número entero mayor que cero"
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
        # VALIDAR PRECIO DE COMPRA
        # --------------------------------------------------

        if (
            not isinstance(precio_unitario, (int, float))
            or isinstance(precio_unitario, bool)
        ):
            raise ValueError(
                "El precio unitario debe ser numérico"
            )

        if precio_unitario <= 0:
            raise ValueError(
                "El precio unitario debe ser mayor a 0"
            )

        # --------------------------------------------------
        # CONSULTAR PRODUCTO
        # --------------------------------------------------

        producto_actual = obtener_producto_por_id(
            id_producto
        )

        if not producto_actual:
            raise ValueError(
                f"El producto con ID {id_producto} no existe"
            )

        # --------------------------------------------------
        # OBTENER DATOS ACTUALES
        # --------------------------------------------------

        stock_actual = producto_actual["stock"]

        if producto_actual.get("precio_costo") is None:
            raise ValueError(
                f"El producto {producto_actual['nombre_producto']} "
                f"no posee precio de costo"
            )

        if producto_actual.get("precio_venta") is None:
            raise ValueError(
                f"El producto {producto_actual['nombre_producto']} "
                f"no posee precio de venta"
            )

        costo_actual = float(
            producto_actual["precio_costo"]
        )

        precio_venta_actual = float(
            producto_actual["precio_venta"]
        )

        precio_compra = float(precio_unitario)

        # --------------------------------------------------
        # CALCULAR SUBTOTAL
        # --------------------------------------------------

        subtotal = cantidad * precio_compra

        total_compra += subtotal

        # --------------------------------------------------
        # CALCULAR POSIBLE ACTUALIZACIÓN DE PRECIOS
        # --------------------------------------------------

        actualizar_precio = False

        nuevo_costo = costo_actual
        nuevo_precio_venta = precio_venta_actual
        markup = None

        if precio_compra > costo_actual:

            # Para mantener el porcentaje actual necesitamos
            # que exista un costo válido mayor a cero.
            if costo_actual <= 0:
                raise ValueError(
                    f"No se puede calcular el porcentaje de recargo "
                    f"del producto {producto_actual['nombre_producto']} "
                    f"porque su costo actual es 0"
                )

            # Ejemplo:
            # costo = 500
            # venta = 900
            #
            # markup = (900 - 500) / 500
            # markup = 0.80 = 80 %
            markup = (
                precio_venta_actual - costo_actual
            ) / costo_actual

            nuevo_costo = precio_compra

            nuevo_precio_venta = round(
                nuevo_costo * (1 + markup),
                2
            )

            actualizar_precio = True

        # --------------------------------------------------
        # CALCULAR NUEVO STOCK
        # --------------------------------------------------

        stock_nuevo = stock_actual + cantidad

        # --------------------------------------------------
        # GUARDAR INFORMACIÓN PREPARADA
        # --------------------------------------------------

        detalles.append({
            "id_producto": id_producto,
            "nombre_producto": producto_actual["nombre_producto"],
            "cantidad": cantidad,
            "precio_unitario": precio_compra,
            "subtotal": subtotal,

            "stock_anterior": stock_actual,
            "stock_nuevo": stock_nuevo,

            "costo_anterior": costo_actual,
            "precio_venta_anterior": precio_venta_actual,

            "nuevo_costo": nuevo_costo,
            "nuevo_precio_venta": nuevo_precio_venta,

            "markup": markup,
            "actualizar_precio": actualizar_precio
        })

    # --------------------------------------------------
    # CREAR COMPRA PRINCIPAL
    # --------------------------------------------------

    datos_compra = {
        "id_proveedor": id_proveedor,
        "id_usuario": id_usuario,
        "total_compra": total_compra,
        "estado": datos.get(
            "estado",
            "COMPLETADA"
        ),
        "observaciones": datos.get(
            "observaciones"
        )
    }

    compra_creada = insertar_compra(
        datos_compra
    )

    if not compra_creada:
        raise ValueError(
            "No se pudo registrar la compra"
        )

    id_compra = compra_creada[0]["id_compra"]

    # --------------------------------------------------
    # REGISTRAR PRODUCTOS DE LA COMPRA
    # --------------------------------------------------

    detalles_creados = []
    productos_actualizados = []

    for detalle in detalles:

        # --------------------------------------------------
        # CREAR DETALLE DE COMPRA
        # --------------------------------------------------

        datos_detalle = {
            "id_compra": id_compra,
            "id_producto": detalle["id_producto"],
            "cantidad": detalle["cantidad"],
            "precio_unitario": detalle["precio_unitario"],
            "subtotal": detalle["subtotal"]
        }

        detalle_creado = insertar_detalle_compra(
            datos_detalle
        )

        detalles_creados.extend(
            detalle_creado
        )

        # --------------------------------------------------
        # ACTUALIZAR PRECIOS SI EL COSTO AUMENTÓ
        # --------------------------------------------------

        if detalle["actualizar_precio"]:

            actualizar_precios_producto(
                detalle["id_producto"],
                detalle["nuevo_costo"],
                detalle["nuevo_precio_venta"]
            )

        # --------------------------------------------------
        # ACTUALIZAR STOCK
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
            "tipo_movimiento": "COMPRA",
            "cantidad": detalle["cantidad"],
            "stock_anterior": detalle["stock_anterior"],
            "stock_nuevo": detalle["stock_nuevo"],
            "observaciones": f"Compra #{id_compra}"
        }

        registrar_movimiento_stock(
            datos_movimiento
        )

        # --------------------------------------------------
        # INFORMACIÓN PARA LA RESPUESTA
        # --------------------------------------------------

        productos_actualizados.append({
            "id_producto": detalle["id_producto"],
            "nombre_producto": detalle["nombre_producto"],

            "costo_anterior": detalle["costo_anterior"],
            "costo_compra": detalle["precio_unitario"],
            "costo_actual": detalle["nuevo_costo"],

            "precio_venta_anterior": detalle[
                "precio_venta_anterior"
            ],

            "precio_venta_actual": detalle[
                "nuevo_precio_venta"
            ],

            "markup_porcentaje": (
                round(detalle["markup"] * 100, 2)
                if detalle["markup"] is not None
                else None
            ),

            "precio_actualizado": detalle[
                "actualizar_precio"
            ],

            "stock_anterior": detalle["stock_anterior"],
            "stock_actual": detalle["stock_nuevo"]
        })

    # --------------------------------------------------
    # RESPUESTA
    # --------------------------------------------------

    return {
        "compra": compra_creada[0],
        "detalles": detalles_creados,
        "productos_actualizados": productos_actualizados
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

    compra = obtener_compra_por_id(
        id_compra
    )

    if not compra:
        raise ValueError(
            "Compra no encontrada"
        )

    detalles = obtener_detalles_compra(
        id_compra
    )

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

    La anulación NO reduce automáticamente el precio de costo
    ni el precio de venta actual del producto.
    """

    # --------------------------------------------------
    # BUSCAR COMPRA
    # --------------------------------------------------

    compra = obtener_compra_por_id(
        id_compra
    )

    if not compra:
        raise ValueError(
            "Compra no encontrada"
        )

    # --------------------------------------------------
    # EVITAR DOBLE ANULACIÓN
    # --------------------------------------------------

    if compra["estado"].upper() == "ANULADA":
        raise ValueError(
            "La compra ya se encuentra anulada"
        )

    # --------------------------------------------------
    # OBTENER PRODUCTOS DE LA COMPRA
    # --------------------------------------------------

    detalles = obtener_detalles_compra(
        id_compra
    )

    if not detalles:
        raise ValueError(
            "La compra no posee productos asociados"
        )

    productos_a_revertir = []

    # --------------------------------------------------
    # VALIDAR TODOS LOS PRODUCTOS
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

    # --------------------------------------------------
    # REVERTIR STOCK
    # --------------------------------------------------

    for producto in productos_a_revertir:

        actualizar_stock_producto(
            producto["id_producto"],
            producto["stock_nuevo"]
        )

        datos_movimiento = {
            "id_producto": producto["id_producto"],
            "id_usuario": compra["id_usuario"],
            "tipo_movimiento": "ANULACION_COMPRA",
            "cantidad": producto["cantidad"],
            "stock_anterior": producto["stock_anterior"],
            "stock_nuevo": producto["stock_nuevo"],
            "observaciones": f"Anulación Compra #{id_compra}"
        }

        registrar_movimiento_stock(
            datos_movimiento
        )

    # --------------------------------------------------
    # CAMBIAR ESTADO DE LA COMPRA
    # --------------------------------------------------

    compra_actualizada = actualizar_estado_compra(
        id_compra,
        "ANULADA"
    )

    return {
        "compra": compra_actualizada,
        "productos_revertidos": productos_a_revertir
    }