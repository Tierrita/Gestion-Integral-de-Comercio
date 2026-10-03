"""
Modelo de compras.

Este módulo se encarga del acceso a los datos relacionados
con las compras y sus detalles almacenados en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def insertar_compra(datos):
    """
    Inserta una nueva compra en la tabla 'compras'
    utilizando los datos recibidos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("compras")
        .insert(datos)
        .execute()
    )

    return response.data


def insertar_detalle_compra(datos):
    """
    Inserta un nuevo detalle en la tabla 'detalle_compra'
    utilizando los datos recibidos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("detalle_compra")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_producto_por_id(id_producto):
    """
    Obtiene un producto mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select("id_producto, nombre_producto, stock")
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


def obtener_compras():
    """
    Obtiene todas las compras almacenadas
    en la tabla 'compras'.
    """

    supabase = get_client()

    response = (
        supabase
        .table("compras")
        .select("*")
        .order("id_compra", desc=True)
        .execute()
    )

    return response.data


def obtener_compra_por_id(id_compra):
    """
    Obtiene una compra específica mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("compras")
        .select("*")
        .eq("id_compra", id_compra)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_detalles_compra(id_compra):
    """
    Obtiene todos los detalles asociados a una compra.
    """

    supabase = get_client()

    response = (
        supabase
        .table("detalle_compra")
        .select("*")
        .eq("id_compra", id_compra)
        .execute()
    )

    return response.data


def actualizar_estado_compra(id_compra, nuevo_estado):
    """
    Actualiza el estado de una compra mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("compras")
        .update({"estado": nuevo_estado})
        .eq("id_compra", id_compra)
        .execute()
    )

    return response.data[0] if response.data else None