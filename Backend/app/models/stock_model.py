"""
Modelo de stock.

Este módulo se encarga del acceso a los datos relacionados
con el stock de los productos almacenados en Supabase.
"""

from core.supabase_client import get_client


def obtener_stock_producto(id_producto):
    """
    Obtiene el stock actual de un producto mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select("id_producto, nombre_producto, stock")
        .eq("id_producto", id_producto)
        .execute()
    )

    return response.data


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

    return response.data



def registrar_movimiento_stock(datos):
    """
    Registra un movimiento de stock en el historial.
    """

    supabase = get_client()

    response = (
        supabase
        .table("historial_movimiento")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_stock_general(buscar=None):
    """
    Obtiene el stock de todos los productos o filtra por nombre.
    """
    supabase = get_client()

    consulta = (
        supabase
        .table("productos")
        .select(
            "id_producto, nombre_producto, stock, stock_minimo, unidad_de_medida"
        )
    )

    if buscar:
        consulta = consulta.ilike("nombre_producto", f"%{buscar}%")

    response = consulta.order("nombre_producto").execute()
    return response.data