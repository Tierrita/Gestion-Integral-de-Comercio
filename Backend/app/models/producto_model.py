"""
Modelo de productos.

Este módulo se encarga del acceso a los datos relacionados
con la tabla 'productos' almacenada en Supabase.

Todas las consultas y modificaciones de productos
se encuentran aisladas por comercio.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def obtener_productos(id_comercio):
    """
    Obtiene todos los productos pertenecientes
    a un comercio específico.
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
    Obtiene un producto por su ID interno verificando
    que pertenezca al comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select("*")
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def obtener_siguiente_numero_producto(id_comercio):
    """
    Obtiene el siguiente número visible de producto
    correspondiente al comercio.

    La numeración es independiente para cada comercio.
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

    Los datos deben incluir el id_comercio y
    numero_producto definidos previamente por el Service.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .insert(datos)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def actualizar_producto(id_producto, id_comercio, datos):
    """
    Actualiza un producto verificando que pertenezca
    al comercio indicado.

    El filtro por id_comercio evita modificar productos
    pertenecientes a otro comercio.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .update(datos)
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def obtener_categoria_por_id(id_categoria, id_comercio):
    """
    Obtiene una categoría verificando que pertenezca
    al mismo comercio.
    """

    supabase = get_client()

    response = (
        supabase
        .table("categorias")
        .select("*")
        .eq("id_categoria", id_categoria)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def obtener_proveedor_por_id(id_proveedor, id_comercio):
    """
    Obtiene un proveedor verificando que pertenezca
    al mismo comercio.
    """

    supabase = get_client()

    response = (
        supabase
        .table("proveedores")
        .select("*")
        .eq("id_proveedor", id_proveedor)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]