"""
Servicio de compras.

Contiene las reglas de negocio del módulo de compras
adaptadas a autenticación, permisos y multicomercio.
"""

from app.models.compra_model import (
    insertar_compra,
    insertar_detalle_compra,
    obtener_siguiente_numero_compra,
    obtener_proveedor_por_id,
    obtener_producto_por_id,
    actualizar_stock_producto,
    actualizar_precios_producto,
    registrar_movimiento_stock,
    obtener_compras,
    obtener_compra_por_id,
    obtener_detalles_compra,
    actualizar_estado_compra
)


def _es_entero_positivo(valor):
    return (
        isinstance(valor, int)
        and not isinstance(valor, bool)
        and valor > 0
    )


def crear_compra(datos, id_comercio, id_usuario):
    """
    Registra una compra dentro del comercio autenticado.

    id_comercio e id_usuario provienen del JWT y nunca
    del Body enviado por el frontend.
    """

    if not datos or not isinstance(datos, dict):
        raise ValueError("No se enviaron datos de la compra")

    id_proveedor = datos.get("id_proveedor")
    productos = datos.get("productos")

    if not _es_entero_positivo(id_proveedor):
        raise ValueError(
            "El id_proveedor debe ser un número entero mayor que cero"
        )

    if not isinstance(productos, list) or len(productos) == 0:
        raise ValueError(
            "La compra debe contener al menos un producto"
        )

    # --------------------------------------------------
    # VALIDAR PROVEEDOR
    # --------------------------------------------------

    proveedor = obtener_proveedor_por_id(
        id_proveedor,
        id_comercio
    )

    if not proveedor:
        raise ValueError(
            "Proveedor no encontrado en el comercio autenticado"
        )

    if not proveedor.get("estado"):
        raise ValueError(
            "No se puede registrar una compra con un proveedor inactivo"
        )

    # --------------------------------------------------
    # PREPARAR PRODUCTOS
    # --------------------------------------------------

    detalles = []
    total_compra = 0.0
    ids_productos = set()

    for producto_compra in productos:

        if not isinstance(producto_compra, dict):
            raise ValueError(
                "Cada producto de la compra debe ser un objeto válido"
            )

        id_producto = producto_compra.get("id_producto")
        cantidad = producto_compra.get("cantidad")
        precio_unitario = producto_compra.get("precio_unitario")

        if not _es_entero_positivo(id_producto):
            raise ValueError(
                "El id_producto debe ser un número entero mayor que cero"
            )

        if id_producto in ids_productos:
            raise ValueError(
                f"El producto con ID {id_producto} está repetido en la compra"
            )

        ids_productos.add(id_producto)

        if not _es_entero_positivo(cantidad):
            raise ValueError(
                "La cantidad debe ser un número entero mayor a 0"
            )

        if (
            not isinstance(precio_unitario, (int, float))
            or isinstance(precio_unitario, bool)
            or precio_unitario <= 0
        ):
            raise ValueError(
                "El precio unitario debe ser numérico y mayor a 0"
            )

        # --------------------------------------------------
        # PRODUCTO DEL MISMO COMERCIO
        # --------------------------------------------------

        producto_actual = obtener_producto_por_id(
            id_producto,
            id_comercio
        )

        if not producto_actual:
            raise ValueError(
                f"El producto con ID {id_producto} no existe "
                f"en el comercio autenticado"
            )

        if not producto_actual.get("estado"):
            raise ValueError(
                f"El producto {producto_actual['nombre_producto']} "
                f"se encuentra inactivo"
            )

        stock_actual = int(producto_actual["stock"])

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

        subtotal = round(
            cantidad * precio_compra,
            2
        )

        total_compra = round(
            total_compra + subtotal,
            2
        )

        # --------------------------------------------------
        # ACTUALIZACIÓN DE COSTO/PRECIO
        # --------------------------------------------------

        actualizar_precio = False
        nuevo_costo = costo_actual
        nuevo_precio_venta = precio_venta_actual
        markup = None

        if precio_compra > costo_actual:

            if costo_actual <= 0:
                raise ValueError(
                    f"No se puede calcular el porcentaje de recargo "
                    f"del producto {producto_actual['nombre_producto']} "
                    f"porque su costo actual es 0"
                )

            markup = (
                precio_venta_actual - costo_actual
            ) / costo_actual

            nuevo_costo = precio_compra

            nuevo_precio_venta = round(
                nuevo_costo * (1 + markup),
                2
            )

            actualizar_precio = True

        detalles.append({
            "id_producto": id_producto,
            "nombre_producto": producto_actual["nombre_producto"],
            "cantidad": cantidad,
            "precio_unitario": precio_compra,
            "subtotal": subtotal,

            "stock_anterior": stock_actual,
            "stock_nuevo": stock_actual + cantidad,

            "costo_anterior": costo_actual,
            "precio_venta_anterior": precio_venta_actual,

            "nuevo_costo": nuevo_costo,
            "nuevo_precio_venta": nuevo_precio_venta,

            "markup": markup,
            "actualizar_precio": actualizar_precio
        })

    # --------------------------------------------------
    # NUMERACIÓN LOCAL
    # --------------------------------------------------

    numero_compra = obtener_siguiente_numero_compra(
        id_comercio
    )

    if numero_compra is None:
        raise ValueError(
            "No se pudo generar el número de compra"
        )

    # --------------------------------------------------
    # CREAR COMPRA
    # --------------------------------------------------

    datos_compra = {
        "id_proveedor": id_proveedor,
        "id_usuario": id_usuario,
        "id_comercio": id_comercio,
        "numero_compra": numero_compra,
        "total_compra": total_compra,
        "estado": "COMPLETADA",
        "observaciones": datos.get("observaciones")
    }

    compra_creada = insertar_compra(
        datos_compra
    )

    if not compra_creada:
        raise ValueError(
            "No se pudo registrar la compra"
        )

    compra = compra_creada[0]
    id_compra = compra["id_compra"]

    detalles_creados = []
    productos_actualizados = []

    # --------------------------------------------------
    # DETALLES + STOCK + HISTORIAL
    # --------------------------------------------------

    for detalle in detalles:

        detalle_creado = insertar_detalle_compra({
            "id_compra": id_compra,
            "id_producto": detalle["id_producto"],
            "cantidad": detalle["cantidad"],
            "precio_unitario": detalle["precio_unitario"],
            "subtotal": detalle["subtotal"]
        })

        detalles_creados.extend(detalle_creado)

        if detalle["actualizar_precio"]:
            actualizar_precios_producto(
                detalle["id_producto"],
                id_comercio,
                detalle["nuevo_costo"],
                detalle["nuevo_precio_venta"]
            )

        actualizar_stock_producto(
            detalle["id_producto"],
            id_comercio,
            detalle["stock_nuevo"]
        )

        registrar_movimiento_stock({
            "id_producto": detalle["id_producto"],
            "id_usuario": id_usuario,
            "tipo_movimiento": "COMPRA",
            "cantidad": detalle["cantidad"],
            "stock_anterior": detalle["stock_anterior"],
            "stock_nuevo": detalle["stock_nuevo"],
            "observaciones": (
                f"Compra #{numero_compra} "
                f"(ID global {id_compra})"
            )
        })

        productos_actualizados.append({
            "id_producto": detalle["id_producto"],
            "nombre_producto": detalle["nombre_producto"],

            "costo_anterior": detalle["costo_anterior"],
            "costo_compra": detalle["precio_unitario"],
            "costo_actual": detalle["nuevo_costo"],

            "precio_venta_anterior":
                detalle["precio_venta_anterior"],

            "precio_venta_actual":
                detalle["nuevo_precio_venta"],

            "markup_porcentaje": (
                round(detalle["markup"] * 100, 2)
                if detalle["markup"] is not None
                else None
            ),

            "precio_actualizado":
                detalle["actualizar_precio"],

            "stock_anterior":
                detalle["stock_anterior"],

            "stock_actual":
                detalle["stock_nuevo"]
        })

    return {
        "compra": compra,
        "detalles": detalles_creados,
        "productos_actualizados": productos_actualizados
    }


def listar_compras(id_comercio):
    """
    Lista solamente compras del comercio autenticado.
    """

    return obtener_compras(id_comercio)


def buscar_compra_por_id(id_compra, id_comercio):
    """
    Busca una compra dentro del comercio autenticado.
    """

    compra = obtener_compra_por_id(
        id_compra,
        id_comercio
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


def anular_compra(
    id_compra,
    id_comercio,
    id_usuario_anulacion
):
    """
    Anula una compra del comercio autenticado.

    La autorización para esta operación es exclusiva
    del propietario y se controla desde la ruta.
    """

    compra = obtener_compra_por_id(
        id_compra,
        id_comercio
    )

    if not compra:
        raise ValueError(
            "Compra no encontrada"
        )

    if str(compra["estado"]).upper() == "ANULADA":
        raise ValueError(
            "La compra ya se encuentra anulada"
        )

    detalles = obtener_detalles_compra(
        id_compra
    )

    if not detalles:
        raise ValueError(
            "La compra no posee productos asociados"
        )

    productos_a_revertir = []

    # --------------------------------------------------
    # VALIDAR TODO ANTES DE MODIFICAR
    # --------------------------------------------------

    for detalle in detalles:

        producto = obtener_producto_por_id(
            detalle["id_producto"],
            id_comercio
        )

        if not producto:
            raise ValueError(
                f"El producto con ID "
                f"{detalle['id_producto']} no existe "
                f"en el comercio autenticado"
            )

        stock_actual = int(producto["stock"])
        cantidad = int(detalle["cantidad"])

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
            id_comercio,
            producto["stock_nuevo"]
        )

        registrar_movimiento_stock({
            "id_producto": producto["id_producto"],
            "id_usuario": id_usuario_anulacion,
            "tipo_movimiento": "ANULACION_COMPRA",
            "cantidad": producto["cantidad"],
            "stock_anterior": producto["stock_anterior"],
            "stock_nuevo": producto["stock_nuevo"],
            "observaciones": (
                f"Anulación Compra #{compra['numero_compra']} "
                f"(ID global {id_compra})"
            )
        })

    compra_actualizada = actualizar_estado_compra(
        id_compra,
        id_comercio,
        "ANULADA"
    )

    return {
        "compra": compra_actualizada,
        "productos_revertidos": productos_a_revertir
    }