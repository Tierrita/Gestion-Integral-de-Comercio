"""Modelo de compras. Las escrituras críticas se ejecutan mediante RPC atómicas."""
from core.supabase_client import get_client


def registrar_compra_rpc(id_comercio, id_usuario, id_proveedor, productos, observaciones=None):
    response = get_client().rpc("registrar_compra_transaccional", {
        "p_id_comercio": id_comercio,
        "p_id_usuario": id_usuario,
        "p_id_proveedor": id_proveedor,
        "p_productos": productos,
        "p_observaciones": observaciones,
    }).execute()
    return response.data


def anular_compra_rpc(id_compra, id_comercio, id_usuario_anulacion):
    response = get_client().rpc("anular_compra_transaccional", {
        "p_id_compra": id_compra,
        "p_id_comercio": id_comercio,
        "p_id_usuario_anulacion": id_usuario_anulacion,
    }).execute()
    return response.data


def obtener_proveedor_por_id(id_proveedor, id_comercio):
    response = (get_client().table("proveedores")
        .select("id_proveedor,nombre_proveedor,estado,id_comercio,numero_proveedor")
        .eq("id_proveedor", id_proveedor).eq("id_comercio", id_comercio)
        .limit(1).execute())
    return response.data[0] if response.data else None


def obtener_producto_por_id(id_producto, id_comercio):
    response = (get_client().table("productos")
        .select("id_producto,numero_producto,nombre_producto,stock,stock_minimo,unidad_de_medida,precio_costo,precio_venta,estado,id_comercio")
        .eq("id_producto", id_producto).eq("id_comercio", id_comercio)
        .limit(1).execute())
    return response.data[0] if response.data else None


def obtener_compras(id_comercio):
    response = (get_client().table("compras").select("*")
        .eq("id_comercio", id_comercio)
        .order("numero_compra", desc=True).execute())
    return response.data


def obtener_compra_por_id(id_compra, id_comercio):
    response = (get_client().table("compras").select("*")
        .eq("id_compra", id_compra).eq("id_comercio", id_comercio)
        .limit(1).execute())
    return response.data[0] if response.data else None


def obtener_detalles_compra(id_compra):
    response = (get_client().table("detalle_compra").select("*")
        .eq("id_compra", id_compra)
        .order("id_detalle_compra").execute())
    return response.data
