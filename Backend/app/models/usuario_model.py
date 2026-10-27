"""
Modelo de usuarios.

Este módulo se encarga del acceso a los datos relacionados
con los usuarios almacenados en Supabase.

Controller → maneja la respuesta HTTP/JSON.
Service → maneja la lógica de negocio.
Model → maneja el acceso a los datos.
"""

from core.supabase_client import get_client


def obtener_usuario_por_email(email):
    """
    Obtiene un usuario por su email.

    Se utiliza principalmente durante el proceso de autenticación.
    """

    supabase = get_client()

    response = (
        supabase
        .table("usuarios")
        .select("*")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def obtener_usuario_por_id(id_usuario):
    """
    Obtiene un usuario por su ID interno.
    """

    supabase = get_client()

    response = (
        supabase
        .table("usuarios")
        .select("*")
        .eq("id_usuario", id_usuario)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def obtener_comercio_usuario(id_comercio):
    """
    Obtiene el comercio al que pertenece el usuario.

    Permite validar, entre otras cosas, que el comercio
    continúe activo.
    """

    supabase = get_client()

    response = (
        supabase
        .table("comercios")
        .select("*")
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]