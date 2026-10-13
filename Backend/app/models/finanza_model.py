"""
Modelo de finanzas.

Este módulo se encarga del acceso a los datos necesarios
para realizar cálculos financieros del negocio.

Model → Supabase
"""

from core.supabase_client import get_client


def obtener_ventas_completadas(desde=None, hasta=None):
    """
    Obtiene las ventas completadas junto con sus detalles
    y la información básica de los productos vendidos.

    Opcionalmente permite filtrar las ventas por un rango
    de fechas utilizando fecha_venta.
    """

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


def obtener_movimientos_financieros(desde=None, hasta=None):
    """
    Obtiene los movimientos financieros registrados
    dentro de un período determinado.

    Si desde y hasta son None, devuelve todos los
    movimientos financieros.
    """

    supabase = get_client()

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
    )

    if desde is not None:
        query = query.gte(
            "fecha_movimiento",
            desde.isoformat()
        )

    if hasta is not None:
        query = query.lt(
            "fecha_movimiento",
            hasta.isoformat()
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



# ======================================================
# COMPRAS PARA ANÁLISIS FINANCIERO
# ======================================================

def obtener_compras_completadas(desde=None, hasta=None):
    """
    Obtiene las compras completadas junto con:
    - Información del proveedor.
    - Detalles de la compra.
    - Información básica de los productos comprados.

    Opcionalmente permite filtrar las compras
    por un rango de fechas.
    """

    supabase = get_client()

    query = (
        supabase
        .table("compras")
        .select(
            """
            id_compra,
            fecha_compra,
            id_proveedor,
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