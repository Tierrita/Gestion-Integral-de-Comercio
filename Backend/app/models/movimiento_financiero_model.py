"""
Modelo de movimientos financieros.

Este módulo se encarga del acceso a los datos relacionados
con la tabla 'movimientos_financieros' almacenada en Supabase.

Los movimientos financieros permiten registrar cada cambio
realizado sobre el saldo de una cuenta financiera.
"""

from core.supabase_client import get_client


def insertar_movimiento_financiero(datos):
    """
    Inserta un nuevo movimiento financiero
    en la tabla 'movimientos_financieros'.
    """

    supabase = get_client()

    response = (
        supabase
        .table("movimientos_financieros")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_movimientos_por_cuenta(id_cuenta):
    """
    Obtiene todos los movimientos financieros
    correspondientes a una cuenta.

    Los movimientos se ordenan desde el más reciente
    hasta el más antiguo.
    """

    supabase = get_client()

    response = (
        supabase
        .table("movimientos_financieros")
        .select("*")
        .eq("id_cuenta", id_cuenta)
        .order("fecha_movimiento", desc=True)
        .execute()
    )

    return response.data