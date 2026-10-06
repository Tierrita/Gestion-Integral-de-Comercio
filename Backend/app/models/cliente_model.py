"""
Modelo de clientes.

Este módulo se encarga del acceso a los datos relacionados
con los clientes almacenados en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def insertar_cliente(datos):
    """
    Inserta un nuevo cliente en la tabla 'clientes'.
    """

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_clientes():
    """
    Obtiene todos los clientes registrados.
    """

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .select("*")
        .order("id_cliente")
        .execute()
    )

    return response.data


def obtener_cliente_por_id(id_cliente):
    """
    Obtiene un cliente específico mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .select("*")
        .eq("id_cliente", id_cliente)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_cliente(id_cliente, datos):
    """
    Actualiza los datos de un cliente mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .update(datos)
        .eq("id_cliente", id_cliente)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_estado_cliente(id_cliente, nuevo_estado):
    """
    Actualiza el estado activo/inactivo de un cliente.
    """

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .update({"estado": nuevo_estado})
        .eq("id_cliente", id_cliente)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_ventas_cliente(id_cliente):
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


def obtener_detalles_venta_cliente(id_venta):
    """
    Obtiene los productos asociados a una venta.
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