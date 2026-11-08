"""
Modelo de ventas.

Acceso a datos del módulo de ventas.
Todas las operaciones principales se encuentran aisladas
por comercio.

Route → Controller → Service → Model → Supabase
"""

from core.supabase_client import get_client


def insertar_venta(datos):
    """Inserta una nueva venta."""

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .insert(datos)
        .execute()
    )

    return response.data


def insertar_detalle_venta(datos):
    """Inserta un detalle de venta."""

    supabase = get_client()

    response = (
        supabase
        .table("detalle_venta")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_siguiente_numero_venta(id_comercio):
    """
    Obtiene el siguiente número local de venta
    para el comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .rpc(
            "obtener_siguiente_numero",
            {
                "p_id_comercio": id_comercio,
                "p_entidad": "VENTA"
            }
        )
        .execute()
    )

    return response.data


def obtener_cliente_por_id(id_cliente, id_comercio):
    """
    Obtiene un cliente únicamente si pertenece
    al comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .select(
            "id_cliente, numero_cliente, nombre_completo, "
            "estado, id_comercio"
        )
        .eq("id_cliente", id_cliente)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_producto_por_id(id_producto, id_comercio):
    """
    Obtiene un producto únicamente dentro
    del comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select(
            "id_producto, numero_producto, nombre_producto, "
            "stock, precio_costo, precio_venta, estado, id_comercio"
        )
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_cuenta_por_id(id_cuenta, id_comercio):
    """
    Obtiene una cuenta financiera únicamente
    dentro del comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .select(
            "id_cuenta, nombre_cuenta, saldo, estado, id_comercio"
        )
        .eq("id_cuenta", id_cuenta)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_stock_producto(
    id_producto,
    id_comercio,
    nuevo_stock
):
    """
    Actualiza el stock solamente si el producto
    pertenece al comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .update({
            "stock": nuevo_stock
        })
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def registrar_movimiento_stock(datos):
    """Registra un movimiento en historial_movimiento."""

    supabase = get_client()

    response = (
        supabase
        .table("historial_movimiento")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_ventas(id_comercio):
    """
    Obtiene únicamente las ventas pertenecientes
    al comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("numero_venta", desc=True)
        .execute()
    )

    return response.data


def obtener_venta_por_id(id_venta, id_comercio):
    """
    Obtiene una venta únicamente si pertenece
    al comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .select("*")
        .eq("id_venta", id_venta)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_detalles_venta(id_venta):
    """Obtiene los detalles asociados a una venta."""

    supabase = get_client()

    response = (
        supabase
        .table("detalle_venta")
        .select("*")
        .eq("id_venta", id_venta)
        .order("id_detalle_venta")
        .execute()
    )

    return response.data


def actualizar_estado_venta(
    id_venta,
    id_comercio,
    nuevo_estado
):
    """
    Actualiza el estado de una venta únicamente
    dentro del comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .update({
            "estado": nuevo_estado
        })
        .eq("id_venta", id_venta)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_ventas_por_cliente(id_cliente, id_comercio=None):
    """
    Obtiene las ventas asociadas a un cliente.

    Se mantiene compatible con los módulos financieros
    existentes.

    Si se proporciona id_comercio, también aplica
    aislamiento multicomercio.
    """

    supabase = get_client()

    consulta = (
        supabase
        .table("ventas")
        .select("*")
        .eq("id_cliente", id_cliente)
    )

    if id_comercio is not None:
        consulta = consulta.eq(
            "id_comercio",
            id_comercio
        )

    response = (
        consulta
        .order("fecha_venta", desc=True)
        .execute()
    )

    return response.data


def registrar_ingreso_venta_rpc(
    id_venta,
    id_cuenta,
    id_usuario,
    monto
):
    """
    Registra mediante RPC el ingreso financiero
    correspondiente a una venta cobrada.
    """

    supabase = get_client()

    parametros = {
        "p_id_venta": id_venta,
        "p_id_cuenta": id_cuenta,
        "p_id_usuario": id_usuario,
        "p_monto": monto
    }

    try:
        response = (
            supabase
            .rpc(
                "registrar_ingreso_venta",
                parametros
            )
            .execute()
        )

        return response.data

    except Exception as error:
        mensaje = str(error)

        errores_conocidos = [
            "Cuenta no encontrada",
            "La cuenta se encuentra inactiva",
            "El monto debe ser mayor que cero"
        ]

        for error_conocido in errores_conocidos:
            if error_conocido in mensaje:
                raise ValueError(
                    error_conocido
                )

        raise


def anular_ingreso_venta_rpc(
    id_venta,
    id_usuario
):
    """
    Revierte mediante RPC el ingreso financiero
    generado por una venta.

    El id_usuario corresponde al usuario que realiza
    la anulación, no al usuario que creó la venta.
    """

    supabase = get_client()

    parametros = {
        "p_id_venta": id_venta,
        "p_id_usuario": id_usuario
    }

    try:
        response = (
            supabase
            .rpc(
                "anular_ingreso_venta",
                parametros
            )
            .execute()
        )

        return response.data

    except Exception as error:
        mensaje = str(error)

        errores_conocidos = [
            "El ingreso de esta venta ya fue anulado",
            "Cuenta no encontrada",
            "Saldo insuficiente en la cuenta para anular la venta"
        ]

        for error_conocido in errores_conocidos:
            if error_conocido in mensaje:
                raise ValueError(
                    error_conocido
                )

        raise