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


def obtener_usuarios_comercio(id_comercio):
    """
    Obtiene todos los usuarios pertenecientes a un comercio.

    No devuelve la contraseña de los usuarios.
    """

    supabase = get_client()

    response = (
        supabase
        .table("usuarios")
        .select(
            "id_usuario, "
            "email, "
            "telefono, "
            "fecha_registro, "
            "estado, "
            "id_comercio, "
            "id_rol, "
            "nombre_completo, "
            "dni, "
            "direccion, "
            "es_propietario"
        )
        .eq("id_comercio", id_comercio)
        .order("id_usuario")
        .execute()
    )

    return response.data

def obtener_usuario_comercio_por_id(id_usuario, id_comercio):
    """
    Obtiene un usuario específico verificando que
    pertenezca al comercio autenticado.

    No devuelve la contraseña.
    """

    supabase = get_client()

    response = (
        supabase
        .table("usuarios")
        .select(
            "id_usuario, "
            "email, "
            "telefono, "
            "fecha_registro, "
            "estado, "
            "id_comercio, "
            "id_rol, "
            "nombre_completo, "
            "dni, "
            "direccion, "
            "es_propietario"
        )
        .eq("id_usuario", id_usuario)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]



def insertar_usuario(datos):
    """
    Inserta un nuevo usuario en la base de datos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("usuarios")
        .insert(datos)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def actualizar_usuario(id_usuario, id_comercio, datos):
    """
    Actualiza los datos de un usuario perteneciente
    a un comercio específico.
    """

    supabase = get_client()

    response = (
        supabase
        .table("usuarios")
        .update(datos)
        .eq("id_usuario", id_usuario)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]



def actualizar_estado_usuario(id_usuario, id_comercio, estado):
    """
    Actualiza el estado activo/inactivo de un usuario
    perteneciente a un comercio específico.
    """

    supabase = get_client()

    response = (
        supabase
        .table("usuarios")
        .update({
            "estado": estado
        })
        .eq("id_usuario", id_usuario)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]



def actualizar_rol_usuario(id_usuario, id_comercio, id_rol):
    """
    Actualiza el rol de un usuario perteneciente
    a un comercio específico.
    """

    supabase = get_client()

    response = (
        supabase
        .table("usuarios")
        .update({
            "id_rol": id_rol
        })
        .eq("id_usuario", id_usuario)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]