"""
Modelo de productos.

Este módulo se encarga del acceso a los datos relacionados
con la tabla 'productos' almacenada en Supabase.

Todas las consultas y modificaciones de productos
se encuentran aisladas por comercio.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.

Las cantidades se validan en el Service y se envían al modelo
como números compatibles con JSON. PostgreSQL almacena los
valores decimales mediante columnas NUMERIC(12,3).
"""

from core.supabase_client import get_client


def obtener_productos(id_comercio):
    """Obtiene todos los productos pertenecientes a un comercio."""
    supabase = get_client()
    response = (
        supabase.table("productos")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("numero_producto")
        .execute()
    )
    return response.data


def obtener_producto_por_id(id_producto, id_comercio):
    """Obtiene un producto por ID, limitado al comercio autenticado."""
    supabase = get_client()
    response = (
        supabase.table("productos")
        .select("*")
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def obtener_siguiente_numero_producto(id_comercio):
    """Obtiene el siguiente número visible de producto por comercio."""
    supabase = get_client()
    response = (
        supabase.rpc(
            "obtener_siguiente_numero",
            {"p_id_comercio": id_comercio, "p_entidad": "PRODUCTO"},
        ).execute()
    )
    return response.data


def insertar_producto(datos):
    """Inserta un producto con comercio y numeración definidos por el Service."""
    supabase = get_client()
    response = supabase.table("productos").insert(datos).execute()
    return response.data[0] if response.data else None


def actualizar_producto(id_producto, id_comercio, datos):
    """Actualiza únicamente un producto perteneciente al comercio indicado."""
    supabase = get_client()
    response = (
        supabase.table("productos")
        .update(datos)
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .execute()
    )
    return response.data[0] if response.data else None


def obtener_categoria_por_id(id_categoria, id_comercio):
    """Obtiene una categoría del comercio indicado."""
    supabase = get_client()
    response = (
        supabase.table("categorias")
        .select("*")
        .eq("id_categoria", id_categoria)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def obtener_proveedor_por_id(id_proveedor, id_comercio):
    """Obtiene un proveedor del comercio indicado."""
    supabase = get_client()
    response = (
        supabase.table("proveedores")
        .select("*")
        .eq("id_proveedor", id_proveedor)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None
