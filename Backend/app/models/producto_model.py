"""
Modelo de productos.

Este módulo se encarga del acceso a los datos relacionados
con la tabla 'producto' almacenada en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


"""
Modelo de productos.

Este módulo se encarga del acceso a los datos relacionados
con la tabla 'productos' almacenada en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def obtener_productos(id_comercio):
    """
    Obtiene todos los productos pertenecientes a un comercio.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("numero_producto")
        .execute()
    )

    return response.data


def obtener_producto_por_id(id_producto, id_comercio):
    """
    Obtiene un producto específico verificando que pertenezca
    al comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select("*")
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data


def obtener_siguiente_numero_producto(id_comercio):
    """
    Solicita a PostgreSQL el siguiente número visible de producto
    correspondiente al comercio.
    """

    supabase = get_client()

    response = (
        supabase
        .rpc(
            "obtener_siguiente_numero",
            {
                "p_id_comercio": id_comercio,
                "p_entidad": "PRODUCTO"
            }
        )
        .execute()
    )

    return response.data


def insertar_producto(datos):
    """
    Inserta un nuevo producto en la tabla 'productos'.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .insert(datos)
        .execute()
    )

    return response.data




def obtener_producto_por_id(id_producto):
    """
    Obtiene un producto específico de la tabla 'productos'
    mediante su ID.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select("*")
        .eq("id_producto", id_producto)
        .execute()
    )

    return response.data

def insertar_producto(datos):
    """
    Inserta un nuevo producto en la tabla 'productos'
    utilizando los datos recibidos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .insert(datos)
        .execute()
    )

    return response.data