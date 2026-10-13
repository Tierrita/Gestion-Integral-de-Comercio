"""
Modelo de ventas.

Este módulo se encarga del acceso a los datos relacionados
con las ventas y sus detalles almacenados en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def insertar_venta(datos):
    """
    Inserta una nueva venta en la tabla 'ventas'
    utilizando los datos recibidos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .insert(datos)
        .execute()
    )

    return response.data


def insertar_detalle_venta(datos):
    """
    Inserta un nuevo detalle en la tabla 'detalle_venta'
    utilizando los datos recibidos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("detalle_venta")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_producto_por_id(id_producto):
    """
    Obtiene un producto mediante su ID.

    Incluye stock, precio de costo y precio de venta
    necesarios para registrar correctamente una venta
    y conservar el costo histórico.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select(
            "id_producto, "
            "nombre_producto, "
            "stock, "
            "precio_costo, "
            "precio_venta"
        )
        .eq("id_producto", id_producto)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_stock_producto(id_producto, nuevo_stock):
    """
    Actualiza el stock de un producto mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .update({"stock": nuevo_stock})
        .eq("id_producto", id_producto)
        .execute()
    )

    return response.data[0] if response.data else None


def registrar_movimiento_stock(datos):
    """
    Registra un movimiento de stock en la tabla
    'historial_movimiento'.
    """

    supabase = get_client()

    response = (
        supabase
        .table("historial_movimiento")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_ventas():
    """
    Obtiene todas las ventas almacenadas
    en la tabla 'ventas'.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .select("*")
        .order("id_venta", desc=True)
        .execute()
    )

    return response.data


def obtener_venta_por_id(id_venta):
    """
    Obtiene una venta específica mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .select("*")
        .eq("id_venta", id_venta)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_detalles_venta(id_venta):
    """
    Obtiene todos los detalles asociados a una venta.
    """

    supabase = get_client()

    response = (
        supabase
        .table("detalle_venta")
        .select("*")
        .eq("id_venta", id_venta)
        .execute()
    )

    return response.data


def actualizar_estado_venta(id_venta, nuevo_estado):
    """
    Actualiza el estado de una venta mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .update({"estado": nuevo_estado})
        .eq("id_venta", id_venta)
        .execute()
    )

    return response.data[0] if response.data else None



def obtener_ventas_por_cliente(id_cliente):
    """
    Obtiene todas las ventas asociadas a un cliente.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .select("*")
        .eq("id_cliente", id_cliente)
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
    Registra el ingreso de dinero generado por una venta
    mediante la función RPC 'registrar_ingreso_venta'.

    La función PostgreSQL actualiza el saldo de la cuenta
    y registra el movimiento financiero dentro de una
    misma transacción.
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
            .rpc("registrar_ingreso_venta", parametros)
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
                raise ValueError(error_conocido)

        raise



def anular_ingreso_venta_rpc(
    id_venta,
    id_usuario
):
    """
    Revierte el ingreso financiero generado por una venta.

    La función RPC descuenta el monto de la cuenta original
    y registra un movimiento financiero ANULACION_VENTA.

    Si la venta no había generado un ingreso financiero
    (por ejemplo, CUENTA_CORRIENTE), devuelve None.
    """

    supabase = get_client()

    parametros = {
        "p_id_venta": id_venta,
        "p_id_usuario": id_usuario
    }

    try:
        response = (
            supabase
            .rpc("anular_ingreso_venta", parametros)
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
                raise ValueError(error_conocido)

        raise