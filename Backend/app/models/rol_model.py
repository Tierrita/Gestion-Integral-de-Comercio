"""
Modelo de roles.

Este módulo se encarga del acceso a los datos relacionados
con los roles y permisos almacenados en Supabase.

Cada rol pertenece a un comercio.
Los permisos son globales y se asignan mediante rol_permiso.
"""

from core.supabase_client import get_client


def obtener_roles(id_comercio):
    """
    Obtiene todos los roles pertenecientes a un comercio.
    """

    supabase = get_client()

    response = (
        supabase
        .table("roles")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("id_rol")
        .execute()
    )

    return response.data


def obtener_rol_por_id(id_rol, id_comercio):
    """
    Obtiene un rol verificando que pertenezca al comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("roles")
        .select("*")
        .eq("id_rol", id_rol)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def obtener_permisos():
    """
    Obtiene el catálogo global de permisos.
    """

    supabase = get_client()

    response = (
        supabase
        .table("permisos")
        .select("*")
        .order("modulo")
        .order("codigo")
        .execute()
    )

    return response.data


def obtener_permisos_rol(id_rol):
    """
    Obtiene los permisos asignados a un rol.
    """

    supabase = get_client()

    response = (
        supabase
        .table("rol_permiso")
        .select(
            "id_permiso, permisos(id_permiso, codigo, modulo, descripcion)"
        )
        .eq("id_rol", id_rol)
        .execute()
    )

    return response.data


def insertar_rol(datos):
    """
    Crea un nuevo rol.
    """

    supabase = get_client()

    response = (
        supabase
        .table("roles")
        .insert(datos)
        .execute()
    )

    return response.data


def insertar_permisos_rol(permisos):
    """
    Asigna permisos a un rol.
    """

    if not permisos:
        return []

    supabase = get_client()

    response = (
        supabase
        .table("rol_permiso")
        .insert(permisos)
        .execute()
    )

    return response.data



def actualizar_rol(id_rol, id_comercio, datos):
    """
    Actualiza un rol verificando que pertenezca
    al comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("roles")
        .update(datos)
        .eq("id_rol", id_rol)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data



def contar_usuarios_rol(id_rol, id_comercio):
    """
    Cuenta cuántos usuarios del comercio tienen asignado el rol.
    """

    supabase = get_client()

    response = (
        supabase
        .table("usuarios")
        .select("id_usuario")
        .eq("id_rol", id_rol)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return len(response.data)


def eliminar_permisos_rol(id_rol):
    """
    Elimina las asignaciones actuales de permisos de un rol.

    No elimina los permisos del catálogo global.
    """

    supabase = get_client()

    response = (
        supabase
        .table("rol_permiso")
        .delete()
        .eq("id_rol", id_rol)
        .execute()
    )

    return response.data