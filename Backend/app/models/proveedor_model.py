"""
Modelo de proveedores.

Este módulo se encarga del acceso a los datos relacionados
con los proveedores almacenados en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def insertar_proveedor(datos):
    """
    Inserta un nuevo proveedor en la tabla 'proveedores'
    utilizando los datos recibidos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_proveedores():
    """
    Obtiene todos los proveedores almacenados
    en la tabla 'proveedores'.
    """

    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .select("*")
        .order("id_proveedor")
        .execute()
    )

    return response.data



def obtener_proveedor_por_id(id_proveedor):
    """
    Obtiene un proveedor específico mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .select("*")
        .eq("id_proveedor", id_proveedor)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_proveedor_por_id(id_proveedor):
    """
    Obtiene un proveedor específico mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .select("*")
        .eq("id_proveedor", id_proveedor)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_proveedor(id_proveedor, datos):
    """
    Actualiza los datos de un proveedor mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .update(datos)
        .eq("id_proveedor", id_proveedor)
        .execute()
    )

    return response.data[0] if response.data else None



def actualizar_estado_proveedor(id_proveedor, nuevo_estado):
    """
    Actualiza el estado de un proveedor mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .update({"estado": nuevo_estado})
        .eq("id_proveedor", id_proveedor)
        .execute()
    )

    return response.data[0] if response.data else None