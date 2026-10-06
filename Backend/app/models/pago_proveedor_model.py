"""
Modelo de pagos a proveedores.

Este módulo se encarga del acceso a los datos relacionados
con los pagos realizados a proveedores almacenados en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def insertar_pago_proveedor(datos):
    """
    Registra un nuevo pago realizado a un proveedor.
    """

    supabase = get_client()

    response = (
        supabase
        .table("pagos_proveedor")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_pagos_proveedor():
    """
    Obtiene todos los pagos a proveedores registrados.
    """

    supabase = get_client()

    response = (
        supabase
        .table("pagos_proveedor")
        .select("*")
        .order("fecha_pago", desc=True)
        .execute()
    )

    return response.data


def obtener_pago_proveedor_por_id(id_pago):
    """
    Obtiene un pago específico mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("pagos_proveedor")
        .select("*")
        .eq("id_pago", id_pago)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_pagos_por_proveedor(id_proveedor):
    """
    Obtiene todos los pagos asociados a un proveedor.
    """

    supabase = get_client()

    response = (
        supabase
        .table("pagos_proveedor")
        .select("*")
        .eq("id_proveedor", id_proveedor)
        .order("fecha_pago", desc=True)
        .execute()
    )

    return response.data


def actualizar_pago_proveedor(id_pago, datos):
    """
    Actualiza los datos de un pago a proveedor.
    """

    supabase = get_client()

    response = (
        supabase
        .table("pagos_proveedor")
        .update(datos)
        .eq("id_pago", id_pago)
        .execute()
    )

    return response.data[0] if response.data else None