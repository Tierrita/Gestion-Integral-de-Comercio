"""
Servicio de ventas.

Contiene la lógica de negocio del módulo de ventas,
incluyendo seguridad multicomercio, stock y movimientos
financieros.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from app.utils.cantidades import validar_cantidad

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
    anular_ingreso_venta_rpc,
    registrar_venta_transaccional_rpc,
    anular_venta_completa_rpc,
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


def _precio_decimal(valor, nombre):
    """Valida importes sin utilizar float en los cálculos."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float, str, Decimal)):
        raise ValueError(f"El {nombre} debe ser numérico")
    try:
        numero = Decimal(str(valor))
    except InvalidOperation:
        raise ValueError(f"El {nombre} debe ser numérico")
    if not numero.is_finite():
        raise ValueError(f"El {nombre} debe ser finito")
    return numero


def _redondear_importe(valor):
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _json_numero(valor):
    """Adapta Decimal a los datos numéricos JSON que usa el modelo."""
    return float(valor)


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
    total_venta = Decimal("0.00")

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

        unidad = str(producto.get("unidad_de_medida", "")).strip().upper()
        cantidad = validar_cantidad(cantidad, unidad)
        stock_actual = validar_cantidad(
            stock_actual, unidad, permitir_cero=True
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

        precio_unitario = _precio_decimal(
            producto["precio_venta"], "precio de venta"
        )
        costo_unitario = _precio_decimal(
            producto["precio_costo"], "precio de costo"
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

        subtotal = _redondear_importe(cantidad * precio_unitario)

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

    total_venta = _redondear_importe(total_venta)

 
    # ==================================================
    # REGISTRO TRANSACCIONAL
    # ==================================================

    productos_rpc = [
        {
            "id_producto": detalle["id_producto"],
            "cantidad": _json_numero(detalle["cantidad"])
        }
        for detalle in detalles
    ]

    resultado = registrar_venta_transaccional_rpc(
        id_comercio=id_comercio,
        id_usuario=id_usuario,
        id_cliente=id_cliente,
        metodo_pago=metodo_pago,
        id_cuenta=id_cuenta,
        productos=productos_rpc,
        observaciones=datos.get("observaciones")
    )

    if not resultado:
        raise ValueError(
            "No se pudo registrar la venta"
        )

    return resultado


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
    Anula una venta utilizando una única
    transacción PostgreSQL en Supabase.
    """

    # Validar ID de venta
    if not isinstance(id_venta, int) or id_venta <= 0:
        raise ValueError("ID de venta inválido")

    # Validar ID de comercio
    if not isinstance(id_comercio, int) or id_comercio <= 0:
        raise ValueError("ID de comercio inválido")

    # Validar usuario que realiza la anulación
    if (
        not isinstance(id_usuario_anulacion, int)
        or id_usuario_anulacion <= 0
    ):
        raise ValueError("ID de usuario inválido")

    # Ejecutar la anulación completa en Supabase
    resultado = anular_venta_completa_rpc(
        id_venta=id_venta,
        id_comercio=id_comercio,
        id_usuario=id_usuario_anulacion
    )

    if not resultado:
        raise ValueError("No se pudo anular la venta")

    return resultado
