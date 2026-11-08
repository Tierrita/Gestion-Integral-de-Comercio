"""
Modelo de clientes.

Acceso a datos del módulo de clientes.
Todas las operaciones se encuentran aisladas por comercio.

Route → Controller → Service → Model → Supabase
"""

from core.supabase_client import get_client


def obtener_clientes(id_comercio):
    """Obtiene los clientes pertenecientes al comercio autenticado."""

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("numero_cliente")
        .execute()
    )

    return response.data


def obtener_cliente_por_id(id_cliente, id_comercio):
    """Obtiene un cliente verificando que pertenezca al comercio."""

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .select("*")
        .eq("id_cliente", id_cliente)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_siguiente_numero_cliente(id_comercio):
    """Obtiene el siguiente número local de cliente del comercio."""

    supabase = get_client()

    response = (
        supabase
        .rpc(
            "obtener_siguiente_numero",
            {
                "p_id_comercio": id_comercio,
                "p_entidad": "CLIENTE"
            }
        )
        .execute()
    )

    return response.data


def insertar_cliente(datos):
    """Inserta un cliente."""

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .insert(datos)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_cliente(id_cliente, id_comercio, datos):
    """Actualiza un cliente perteneciente al comercio."""

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .update(datos)
        .eq("id_cliente", id_cliente)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_ventas_cliente(id_cliente, id_comercio):
    """
    Obtiene las ventas del cliente verificando también
    el comercio al que pertenecen.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .select("*")
        .eq("id_cliente", id_cliente)
        .eq("id_comercio", id_comercio)
        .order("fecha_venta", desc=True)
        .execute()
    )

    return response.data


def obtener_detalles_venta_cliente(id_venta):
    """Obtiene los detalles asociados a una venta."""

    supabase = get_client()

    response = (
        supabase
        .table("detalle_venta")
        .select("*")
        .eq("id_venta", id_venta)
        .execute()
    )

    return response.data