"""
Servicio de roles.

Contiene las reglas de negocio relacionadas con los roles
y la asignación de permisos dentro de cada comercio.
"""

from app.models.rol_model import (
    obtener_roles,
    obtener_rol_por_id,
    obtener_permisos,
    obtener_permisos_rol,
    insertar_rol,
    insertar_permisos_rol,
    actualizar_rol,
    eliminar_permisos_rol,
    contar_usuarios_rol,
    guardar_rol_con_permisos
)


def listar_roles(id_comercio):
    """
    Lista los roles pertenecientes al comercio autenticado.
    """

    return obtener_roles(id_comercio)


def listar_permisos():
    """
    Devuelve el catálogo global de permisos disponibles.
    """

    return obtener_permisos()


def obtener_detalle_rol(id_rol, id_comercio):
    """
    Obtiene un rol y sus permisos.
    """

    rol = obtener_rol_por_id(id_rol, id_comercio)

    if not rol:
        raise ValueError("Rol no encontrado")

    permisos = obtener_permisos_rol(id_rol)

    rol["permisos"] = permisos

    return rol


def crear_rol(datos, id_comercio):
    """
    Crea un rol para el comercio autenticado y le asigna permisos.
    """

    nombre_rol = str(datos.get("nombre_rol", "")).strip()
    ids_permisos = datos.get("permisos", [])

    # -------------------------
    # Validaciones básicas
    # -------------------------

    if not nombre_rol:
        raise ValueError("El nombre del rol es obligatorio")

    if len(nombre_rol) < 3:
        raise ValueError("El nombre del rol debe tener al menos 3 caracteres")

    if not isinstance(ids_permisos, list):
        raise ValueError("Los permisos deben enviarse como una lista")

    # Evitar IDs repetidos
    ids_permisos = list(dict.fromkeys(ids_permisos))

    # -------------------------
    # Validar permisos
    # -------------------------

    permisos_disponibles = obtener_permisos()

    ids_validos = {
        permiso["id_permiso"]
        for permiso in permisos_disponibles
    }

    for id_permiso in ids_permisos:
        if id_permiso not in ids_validos:
            raise ValueError(
                f"El permiso con ID {id_permiso} no existe"
            )

    id_rol = guardar_rol_con_permisos(
        id_comercio, None, nombre_rol, ids_permisos
    )
    return obtener_detalle_rol(id_rol, id_comercio)



def modificar_rol(id_rol, datos, id_comercio):
    """
    Modifica el nombre y/o los permisos de un rol.

    El rol debe pertenecer al comercio autenticado.
    """

    # -------------------------
    # Verificar rol
    # -------------------------

    rol = obtener_rol_por_id(id_rol, id_comercio)

    if not rol:
        raise ValueError("Rol no encontrado")

    nombre_rol = None
    if "nombre_rol" in datos:
        nombre_rol = str(datos.get("nombre_rol", "")).strip()
        if len(nombre_rol) < 3:
            raise ValueError("El nombre del rol debe tener al menos 3 caracteres")

    ids_permisos = None
    if "permisos" in datos:
        ids_permisos = datos["permisos"]
        if not isinstance(ids_permisos, list):
            raise ValueError("Los permisos deben enviarse como una lista")
        ids_permisos = list(dict.fromkeys(ids_permisos))
        ids_validos = {p["id_permiso"] for p in obtener_permisos()}
        if any(p not in ids_validos for p in ids_permisos):
            raise ValueError("Se indicó un permiso inexistente")

    if nombre_rol is None and ids_permisos is None:
        raise ValueError("No se enviaron cambios para el rol")

    guardar_rol_con_permisos(id_comercio, id_rol, nombre_rol, ids_permisos)
    return obtener_detalle_rol(id_rol, id_comercio)



def cambiar_estado_rol(id_rol, datos, id_comercio):
    """
    Activa o desactiva un rol.

    Un rol no puede ser desactivado mientras tenga
    usuarios asignados.
    """

    # -------------------------
    # Verificar rol
    # -------------------------

    rol = obtener_rol_por_id(id_rol, id_comercio)

    if not rol:
        raise ValueError("Rol no encontrado")

    # -------------------------
    # Validar estado
    # -------------------------

    if "estado" not in datos:
        raise ValueError("El estado es obligatorio")

    nuevo_estado = datos["estado"]

    if not isinstance(nuevo_estado, bool):
        raise ValueError(
            "El estado debe ser true o false"
        )

    # -------------------------
    # Evitar operación innecesaria
    # -------------------------

    if rol["estado"] == nuevo_estado:
        if nuevo_estado:
            raise ValueError("El rol ya se encuentra activo")

        raise ValueError("El rol ya se encuentra inactivo")

    # -------------------------
    # Validar desactivación
    # -------------------------

    if nuevo_estado is False:

        cantidad_usuarios = contar_usuarios_rol(
            id_rol,
            id_comercio
        )

        if cantidad_usuarios > 0:
            raise ValueError(
                "No se puede desactivar el rol porque tiene usuarios asignados"
            )

    # -------------------------
    # Actualizar estado
    # -------------------------

    resultado = actualizar_rol(
        id_rol,
        id_comercio,
        {
            "estado": nuevo_estado
        }
    )

    if not resultado:
        raise RuntimeError(
            "No se pudo actualizar el estado del rol"
        )

    return obtener_detalle_rol(
        id_rol,
        id_comercio
    )