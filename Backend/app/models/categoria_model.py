"""
Modelo de categorías.

Este módulo se encarga del acceso a los datos relacionados
con las categorías almacenadas en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def insertar_categoria(datos):
    """
    Inserta una nueva categoría en la tabla 'categorias'
    utilizando los datos recibidos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_categorias():
    """
    Obtiene todas las categorías almacenadas
    en la tabla 'categorias'.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .select("*")
        .order("id_categoria")
        .execute()
    )

    return response.data



def obtener_categoria_por_id(id_categoria):
    """
    Obtiene una categoría específica mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .select("*")
        .eq("id_categoria", id_categoria)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_categoria(id_categoria, datos):
    """
    Actualiza los datos de una categoría mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .update(datos)
        .eq("id_categoria", id_categoria)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_estado_categoria(id_categoria, nuevo_estado):
    """
    Actualiza el estado de una categoría mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .update({"estado": nuevo_estado})
        .eq("id_categoria", id_categoria)
        .execute()
    )

    return response.data[0] if response.data else None