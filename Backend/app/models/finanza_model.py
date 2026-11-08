"""
Modelo de finanzas multicomercio.

Toda consulta financiera queda limitada al comercio
del usuario autenticado.

Model → Supabase
"""

from core.supabase_client import get_client


def obtener_ventas_completadas(
    id_comercio,
    desde=None,
    hasta=None
):
    supabase = get_client()

    query = (
        supabase
        .table("ventas")
        .select(
            """
            id_venta,
            fecha_venta,
            total,
            estado,
            id_cliente,
            id_comercio,
            clientes (
                nombre_completo
            ),
            detalle_venta (
                id_detalle_venta,
                id_producto,
                cantidad,
                precio_unitario,
                subtotal,
                costo_unitario,
                productos (
                    nombre_producto
                )
            )
            """
        )
        .eq("id_comercio", id_comercio)
        .eq("estado", "COMPLETADA")
    )

    if desde:
        query = query.gte(
            "fecha_venta",
            desde
        )

    if hasta:
        query = query.lt(
            "fecha_venta",
            hasta
        )

    response = query.execute()

    return response.data


def obtener_movimientos_financieros(
    id_comercio,
    desde=None,
    hasta=None
):
    """
    Obtiene únicamente movimientos correspondientes
    a cuentas del comercio autenticado.
    """

    supabase = get_client()

    cuentas_response = (
        supabase
        .table("cuentas")
        .select("id_cuenta")
        .eq("id_comercio", id_comercio)
        .execute()
    )

    ids_cuentas = [
        cuenta["id_cuenta"]
        for cuenta in cuentas_response.data
    ]

    if not ids_cuentas:
        return []

    query = (
        supabase
        .table("movimientos_financieros")
        .select(
            "id_movimiento,"
            "id_cuenta,"
            "id_usuario,"
            "tipo_movimiento,"
            "monto,"
            "saldo_anterior,"
            "saldo_nuevo,"
            "tipo_origen,"
            "id_origen,"
            "fecha_movimiento,"
            "observaciones"
        )
        .in_("id_cuenta", ids_cuentas)
    )

    if desde is not None:
        fecha_desde = (
            desde.isoformat()
            if hasattr(desde, "isoformat")
            else desde
        )

        query = query.gte(
            "fecha_movimiento",
            fecha_desde
        )

    if hasta is not None:
        fecha_hasta = (
            hasta.isoformat()
            if hasattr(hasta, "isoformat")
            else hasta
        )

        query = query.lt(
            "fecha_movimiento",
            fecha_hasta
        )

    response = (
        query
        .order(
            "fecha_movimiento",
            desc=False
        )
        .execute()
    )

    return response.data


def obtener_compras_completadas(
    id_comercio,
    desde=None,
    hasta=None
):
    supabase = get_client()

    query = (
        supabase
        .table("compras")
        .select(
            """
            id_compra,
            fecha_compra,
            id_proveedor,
            id_comercio,
            total_compra,
            estado,
            proveedores (
                nombre_proveedor
            ),
            detalle_compra (
                id_detalle_compra,
                id_producto,
                cantidad,
                precio_unitario,
                subtotal,
                productos (
                    nombre_producto
                )
            )
            """
        )
        .eq("id_comercio", id_comercio)
        .eq("estado", "COMPLETADA")
    )

    if desde:
        query = query.gte(
            "fecha_compra",
            desde
        )

    if hasta:
        query = query.lt(
            "fecha_compra",
            hasta
        )

    response = (
        query
        .order(
            "fecha_compra",
            desc=False
        )
        .execute()
    )

    return response.data