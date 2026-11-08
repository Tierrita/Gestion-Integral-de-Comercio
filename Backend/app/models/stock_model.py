"""
Modelo de stock.

Este módulo se encarga del acceso a los datos relacionados
con el stock de los productos almacenados en Supabase.

Todas las operaciones sobre productos se encuentran
aisladas por comercio.
"""

from core.supabase_client import get_client


def obtener_stock_producto(id_producto, id_comercio):
    """
    Obtiene el stock de un producto perteneciente
    al comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select(
            "id_producto, nombre_producto, stock, "
            "stock_minimo, unidad_de_medida, estado, id_comercio"
        )
        .eq("id_producto", id_producto)
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
    Actualiza el stock únicamente si el producto
    pertenece al comercio autenticado.
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
    """
    Registra un movimiento de stock en
    historial_movimiento.
    """

    supabase = get_client()

    response = (
        supabase
        .table("historial_movimiento")
        .insert(datos)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_stock_general(id_comercio, buscar=None):
    """
    Obtiene únicamente el stock correspondiente
    al comercio autenticado.

    Opcionalmente permite buscar productos por nombre.
    """

    supabase = get_client()

    consulta = (
        supabase
        .table("productos")
        .select(
            "id_producto, numero_producto, nombre_producto, "
            "stock, stock_minimo, unidad_de_medida, estado, id_comercio"
        )
        .eq("id_comercio", id_comercio)
    )

    if buscar:
        consulta = consulta.ilike(
            "nombre_producto",
            f"%{buscar}%"
        )

    response = (
        consulta
        .order("nombre_producto")
        .execute()
    )

    return response.data