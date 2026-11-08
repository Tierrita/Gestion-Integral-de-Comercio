"""
Modelo de proveedores.

Acceso a datos de proveedores con aislamiento por comercio.
"""

from core.supabase_client import get_client


def insertar_proveedor(datos):
    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .insert(datos)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_proveedores(id_comercio):
    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("numero_proveedor")
        .execute()
    )

    return response.data


def obtener_proveedor_por_id(id_proveedor, id_comercio):
    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .select("*")
        .eq("id_proveedor", id_proveedor)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_proveedor(id_proveedor, id_comercio, datos):
    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .update(datos)
        .eq("id_proveedor", id_proveedor)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_estado_proveedor(
    id_proveedor,
    id_comercio,
    nuevo_estado
):
    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .update({"estado": nuevo_estado})
        .eq("id_proveedor", id_proveedor)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_siguiente_numero_proveedor(id_comercio):
    """
    Obtiene el próximo número visible de proveedor
    para el comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .select("numero_proveedor")
        .eq("id_comercio", id_comercio)
        .order("numero_proveedor", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        return 1

    return int(response.data[0]["numero_proveedor"]) + 1