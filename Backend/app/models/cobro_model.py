"""
Modelo de cobros.
Acceso a datos de cobros con aislamiento multicomercio.
"""

from core.supabase_client import get_client


def registrar_cobro_rpc(
    id_cliente,
    id_cuenta,
    id_usuario,
    id_comercio,
    monto,
    observaciones=None
):
    supabase = get_client()

    parametros = {
        "p_id_cliente": id_cliente,
        "p_id_cuenta": id_cuenta,
        "p_id_usuario": id_usuario,
        "p_id_comercio": id_comercio,
        "p_monto": monto,
        "p_observaciones": observaciones
    }

    try:
        response = (
            supabase
            .rpc("registrar_cobro", parametros)
            .execute()
        )
        return response.data

    except Exception as error:
        mensaje = str(error)

        errores = [
            "Cliente no encontrado",
            "El cliente se encuentra inactivo",
            "Cuenta no encontrada",
            "La cuenta se encuentra inactiva",
            "El monto debe ser mayor que cero",
            "El usuario es obligatorio",
            "El comercio es obligatorio",
            "Usuario no encontrado en el comercio",
            "El usuario se encuentra inactivo"
        ]

        for error_conocido in errores:
            if error_conocido in mensaje:
                raise ValueError(error_conocido)

        raise


def obtener_cobros(id_comercio):
    supabase = get_client()

    response = (
        supabase
        .table("cobros")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("fecha_cobro", desc=True)
        .execute()
    )

    return response.data


def obtener_cobro_por_id(id_cobro, id_comercio):
    supabase = get_client()

    response = (
        supabase
        .table("cobros")
        .select("*")
        .eq("id_cobro", id_cobro)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data


def obtener_cobros_por_cliente(id_cliente, id_comercio):
    supabase = get_client()

    response = (
        supabase
        .table("cobros")
        .select("*")
        .eq("id_cliente", id_cliente)
        .eq("id_comercio", id_comercio)
        .order("fecha_cobro", desc=True)
        .execute()
    )

    return response.data


def anular_cobro_rpc(
    id_cobro,
    id_usuario,
    id_comercio,
    motivo_anulacion
):
    supabase = get_client()

    parametros = {
        "p_id_cobro": id_cobro,
        "p_id_usuario": id_usuario,
        "p_id_comercio": id_comercio,
        "p_motivo_anulacion": motivo_anulacion
    }

    try:
        response = (
            supabase
            .rpc("anular_cobro", parametros)
            .execute()
        )

        return response.data

    except Exception as error:
        mensaje = str(error)

        errores = [
            "Cobro no encontrado",
            "El cobro ya se encuentra anulado",
            "Cuenta no encontrada",
            "Fondos insuficientes para revertir el cobro",
            "El usuario es obligatorio",
            "El comercio es obligatorio",
            "Usuario no encontrado en el comercio",
            "El motivo de anulación debe tener al menos 5 caracteres"
        ]

        for error_conocido in errores:
            if error_conocido in mensaje:
                raise ValueError(error_conocido)

        raise