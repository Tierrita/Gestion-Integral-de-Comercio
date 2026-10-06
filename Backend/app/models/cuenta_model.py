"""
Modelo de cuentas financieras.

Este módulo se encarga del acceso a los datos relacionados
con la tabla 'cuentas' almacenada en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def obtener_cuenta_por_nombre(nombre_cuenta):
    """
    Busca una cuenta financiera mediante su nombre.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .select("*")
        .ilike("nombre_cuenta", nombre_cuenta)
        .execute()
    )

    return response.data


def insertar_cuenta(datos):
    """
    Inserta una nueva cuenta financiera en la tabla 'cuentas'.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_cuentas():
    """
    Obtiene todas las cuentas financieras registradas.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .select("*")
        .order("id_cuenta")
        .execute()
    )

    return response.data


def obtener_cuenta_por_id(id_cuenta):
    """
    Obtiene una cuenta financiera mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .select("*")
        .eq("id_cuenta", id_cuenta)
        .execute()
    )

    return response.data


def actualizar_cuenta(id_cuenta, datos):
    """
    Actualiza los datos permitidos de una cuenta financiera
    mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .update(datos)
        .eq("id_cuenta", id_cuenta)
        .execute()
    )

    return response.data


def actualizar_estado_cuenta(id_cuenta, nuevo_estado):
    """
    Actualiza el estado de una cuenta financiera.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .update({"estado": nuevo_estado})
        .eq("id_cuenta", id_cuenta)
        .execute()
    )

    return response.data


def ajustar_saldo_cuenta_rpc(
    id_cuenta,
    cantidad,
    tipo_ajuste,
    id_usuario,
    observaciones
):
    """
    Ejecuta un ajuste manual sobre el saldo de una cuenta financiera
    mediante la función RPC 'ajustar_saldo_cuenta' de Supabase.

    La función PostgreSQL actualiza el saldo de la cuenta y registra
    el movimiento financiero correspondiente dentro de una misma
    operación transaccional.
    """

    supabase = get_client()

    parametros = {
        "p_id_cuenta": id_cuenta,
        "p_cantidad": cantidad,
        "p_tipo_ajuste": tipo_ajuste,
        "p_id_usuario": id_usuario,
        "p_observaciones": observaciones
    }

    try:
        response = (
            supabase
            .rpc("ajustar_saldo_cuenta", parametros)
            .execute()
        )

        return response.data

    except Exception as error:
        mensaje = str(error)

        if "Fondos insuficientes para realizar el ajuste" in mensaje:
            raise ValueError(
                "Fondos insuficientes para realizar el ajuste"
            )

        if "Cuenta no encontrada" in mensaje:
            raise ValueError(
                "Cuenta no encontrada"
            )

        if "La cuenta se encuentra inactiva" in mensaje:
            raise ValueError(
                "La cuenta se encuentra inactiva"
            )

        raise