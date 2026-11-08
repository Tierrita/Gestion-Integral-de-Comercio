"""
Modelo de compras.

Acceso a datos del módulo de compras.
Todas las consultas principales se encuentran aisladas
por comercio.
"""

from core.supabase_client import get_client


def insertar_compra(datos):
    supabase = get_client()

    response = (
        supabase
        .table("compras")
        .insert(datos)
        .execute()
    )

    return response.data


def insertar_detalle_compra(datos):
    supabase = get_client()

    response = (
        supabase
        .table("detalle_compra")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_siguiente_numero_compra(id_comercio):
    """
    Obtiene el siguiente número local de compra
    para el comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .rpc(
            "obtener_siguiente_numero",
            {
                "p_id_comercio": id_comercio,
                "p_entidad": "COMPRA"
            }
        )
        .execute()
    )

    return response.data


def obtener_proveedor_por_id(id_proveedor, id_comercio):
    """
    Obtiene un proveedor únicamente si pertenece
    al comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .select(
            "id_proveedor, nombre_proveedor, estado, "
            "id_comercio, numero_proveedor"
        )
        .eq("id_proveedor", id_proveedor)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_producto_por_id(id_producto, id_comercio):
    """
    Obtiene un producto únicamente dentro del comercio.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select(
            "id_producto, numero_producto, nombre_producto, "
            "stock, precio_costo, precio_venta, estado, id_comercio"
        )
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_stock_producto(id_producto, id_comercio, nuevo_stock):
    """
    Actualiza stock solamente si el producto pertenece
    al comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .update({"stock": nuevo_stock})
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_precios_producto(
    id_producto,
    id_comercio,
    nuevo_precio_costo,
    nuevo_precio_venta
):
    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .update({
            "precio_costo": nuevo_precio_costo,
            "precio_venta": nuevo_precio_venta
        })
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def registrar_movimiento_stock(datos):
    supabase = get_client()

    response = (
        supabase
        .table("historial_movimiento")
        .insert(datos)
        .execute()
    )

    return response.data


def obtener_compras(id_comercio):
    """
    Lista únicamente las compras del comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("compras")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("numero_compra", desc=True)
        .execute()
    )

    return response.data


def obtener_compra_por_id(id_compra, id_comercio):
    """
    Busca una compra dentro de un comercio específico.
    """

    supabase = get_client()

    response = (
        supabase
        .table("compras")
        .select("*")
        .eq("id_compra", id_compra)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_detalles_compra(id_compra):
    supabase = get_client()

    response = (
        supabase
        .table("detalle_compra")
        .select("*")
        .eq("id_compra", id_compra)
        .order("id_detalle_compra")
        .execute()
    )

    return response.data


def actualizar_estado_compra(
    id_compra,
    id_comercio,
    nuevo_estado
):
    """
    Actualiza el estado solamente dentro del comercio.
    """

    supabase = get_client()

    response = (
        supabase
        .table("compras")
        .update({"estado": nuevo_estado})
        .eq("id_compra", id_compra)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None