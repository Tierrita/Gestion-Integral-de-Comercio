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
    Inserta una nueva categoría.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_categorias(id_comercio):
    """
    Obtiene únicamente las categorías pertenecientes
    al comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("id_categoria")
        .execute()
    )

    return response.data


def obtener_categoria_por_id(id_categoria, id_comercio):
    """
    Obtiene una categoría específica perteneciente
    al comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .select("*")
        .eq("id_categoria", id_categoria)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_categoria(
    id_categoria,
    id_comercio,
    datos
):
    """
    Actualiza una categoría perteneciente
    al comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .update(datos)
        .eq("id_categoria", id_categoria)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_estado_categoria(
    id_categoria,
    id_comercio,
    nuevo_estado
):
    """
    Activa o desactiva una categoría perteneciente
    al comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .update({
            "estado": nuevo_estado
        })
        .eq("id_categoria", id_categoria)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_productos_activos_por_categoria(
    id_categoria,
    id_comercio
):
    """
    Obtiene los productos activos asociados a una categoría
    dentro del mismo comercio.

    Se utiliza para impedir que una categoría sea desactivada
    mientras todavía tenga productos activos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select("id_producto")
        .eq("id_categoria", id_categoria)
        .eq("id_comercio", id_comercio)
        .eq("estado", True)
        .execute()
    )

    return response.data