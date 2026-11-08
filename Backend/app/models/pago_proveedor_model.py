"""
Modelo de pagos a proveedores.

Los pagos se aíslan por comercio mediante la relación
con el proveedor al que pertenecen.
"""

from core.supabase_client import get_client


def insertar_pago_proveedor(datos):
    supabase = get_client()

    response = (
        supabase
        .table("pagos_proveedor")
        .insert(datos)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_pagos_proveedor(id_comercio):
    supabase = get_client()

    proveedores = (
        supabase
        .table("proveedores")
        .select("id_proveedor")
        .eq("id_comercio", id_comercio)
        .execute()
    )

    ids = [
        proveedor["id_proveedor"]
        for proveedor in proveedores.data
    ]

    if not ids:
        return []

    response = (
        supabase
        .table("pagos_proveedor")
        .select("*")
        .in_("id_proveedor", ids)
        .order("fecha_pago", desc=True)
        .execute()
    )

    return response.data


def obtener_pago_proveedor_por_id(
    id_pago,
    id_comercio
):
    supabase = get_client()

    pagos = obtener_pagos_proveedor(id_comercio)

    for pago in pagos:
        if pago["id_pago"] == id_pago:
            return pago

    return None


def obtener_pagos_por_proveedor(
    id_proveedor,
    id_comercio
):
    supabase = get_client()

    proveedor = (
        supabase
        .table("proveedores")
        .select("id_proveedor")
        .eq("id_proveedor", id_proveedor)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    if not proveedor.data:
        return None

    response = (
        supabase
        .table("pagos_proveedor")
        .select("*")
        .eq("id_proveedor", id_proveedor)
        .order("fecha_pago", desc=True)
        .execute()
    )

    return response.data


def actualizar_pago_proveedor(
    id_pago,
    id_comercio,
    datos
):
    supabase = get_client()

    pago = obtener_pago_proveedor_por_id(
        id_pago,
        id_comercio
    )

    if not pago:
        return None

    response = (
        supabase
        .table("pagos_proveedor")
        .update(datos)
        .eq("id_pago", id_pago)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_compras_proveedor(
    id_proveedor,
    id_comercio
):
    supabase = get_client()

    response = (
        supabase
        .table("compras")
        .select(
            "id_compra, id_proveedor, id_comercio, "
            "total_compra, estado"
        )
        .eq("id_proveedor", id_proveedor)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data