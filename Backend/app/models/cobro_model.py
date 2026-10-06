"""
Modelo de cobros.

Este módulo se encarga del acceso a los datos relacionados
con los cobros de clientes almacenados en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def registrar_cobro_rpc(
    id_cliente,
    id_cuenta,
    id_usuario,
    monto,
    observaciones=None
):
    """
    Registra un cobro mediante la función RPC 'registrar_cobro'
    de Supabase.

    La función PostgreSQL registra el cobro, actualiza el saldo
    de la cuenta financiera y genera el movimiento financiero
    correspondiente dentro de una misma transacción.
    """

    supabase = get_client()

    parametros = {
        "p_id_cliente": id_cliente,
        "p_id_cuenta": id_cuenta,
        "p_id_usuario": id_usuario,
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

        # Errores de negocio generados por PostgreSQL
        errores_conocidos = [
            "Cliente no encontrado",
            "El cliente se encuentra inactivo",
            "Cuenta no encontrada",
            "La cuenta se encuentra inactiva",
            "El monto debe ser mayor que cero",
            "El usuario es obligatorio"
        ]

        for error_conocido in errores_conocidos:
            if error_conocido in mensaje:
                raise ValueError(error_conocido)

        raise



def obtener_cobros():
    """
    Obtiene todos los cobros registrados.

    Los cobros se ordenan desde el más reciente
    hasta el más antiguo.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cobros")
        .select("*")
        .order("fecha_cobro", desc=True)
        .execute()
    )

    return response.data



def obtener_cobro_por_id(id_cobro):
    """
    Obtiene un cobro específico mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cobros")
        .select("*")
        .eq("id_cobro", id_cobro)
        .execute()
    )

    return response.data



def obtener_cobros_por_cliente(id_cliente):
    """
    Obtiene todos los cobros registrados para un cliente.

    Los cobros se ordenan desde el más reciente
    hasta el más antiguo.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cobros")
        .select("*")
        .eq("id_cliente", id_cliente)
        .order("fecha_cobro", desc=True)
        .execute()
    )

    return response.data


def anular_cobro_rpc(
    id_cobro,
    id_usuario,
    motivo_anulacion
):
    """
    Anula un cobro mediante la función RPC 'anular_cobro'
    de Supabase.

    La función PostgreSQL anula el cobro, revierte el dinero
    de la cuenta financiera y registra el movimiento de
    anulación dentro de una misma transacción.
    """

    supabase = get_client()

    parametros = {
        "p_id_cobro": id_cobro,
        "p_id_usuario": id_usuario,
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

        errores_conocidos = [
            "Cobro no encontrado",
            "El cobro ya se encuentra anulado",
            "Cuenta no encontrada",
            "Fondos insuficientes para revertir el cobro",
            "El usuario es obligatorio",
            "El motivo de anulación debe tener al menos 5 caracteres"
        ]

        for error_conocido in errores_conocidos:
            if error_conocido in mensaje:
                raise ValueError(error_conocido)

        raise


def obtener_ventas_por_cliente(id_cliente):
    """
    Obtiene todas las ventas asociadas a un cliente.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .select("*")
        .eq("id_cliente", id_cliente)
        .order("fecha_venta", desc=True)
        .execute()
    )

    return response.data