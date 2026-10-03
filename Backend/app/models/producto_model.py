"""
Modelo de productos.

Este módulo se encarga del acceso a los datos relacionados
con la tabla 'producto' almacenada en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def obtener_productos():
    """
    Obtiene todos los productos almacenados en la tabla 'producto'.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select("*")
        .execute()
    )

    return response.data




def obtener_producto_por_id(id_producto):
    """
    Obtiene un producto específico de la tabla 'productos'
    mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select("*")
        .eq("id_producto", id_producto)
        .execute()
    )

    return response.data

def insertar_producto(datos):
    """
    Inserta un nuevo producto en la tabla 'productos'
    utilizando los datos recibidos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .insert(datos)
        .execute()
    )

    return response.data