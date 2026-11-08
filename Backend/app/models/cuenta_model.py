"""
Modelo de cuentas financieras multicomercio.
"""

from core.supabase_client import get_client


def obtener_cuenta_por_nombre(
    nombre_cuenta,
    id_comercio
):
    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .select("*")
        .eq("id_comercio", id_comercio)
        .ilike("nombre_cuenta", nombre_cuenta)
        .execute()
    )

    return response.data


def insertar_cuenta(datos):
    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_cuentas(id_comercio):
    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("id_cuenta")
        .execute()
    )

    return response.data


def obtener_cuenta_por_id(
    id_cuenta,
    id_comercio
):
    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .select("*")
        .eq("id_cuenta", id_cuenta)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def actualizar_cuenta(
    id_cuenta,
    id_comercio,
    datos
):
    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .update(datos)
        .eq("id_cuenta", id_cuenta)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data


def actualizar_estado_cuenta(
    id_cuenta,
    id_comercio,
    nuevo_estado
):
    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .update({"estado": nuevo_estado})
        .eq("id_cuenta", id_cuenta)
        .eq("id_comercio", id_comercio)
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

        errores = [
            "Fondos insuficientes para realizar el ajuste",
            "Cuenta no encontrada",
            "La cuenta se encuentra inactiva",
            "La cantidad debe ser mayor que cero",
            "El tipo de ajuste debe ser AUMENTAR o DISMINUIR",
            "El usuario es obligatorio",
            "Las observaciones deben tener al menos 3 caracteres"
        ]

        for error_conocido in errores:
            if error_conocido in mensaje:
                raise ValueError(error_conocido)

        raise