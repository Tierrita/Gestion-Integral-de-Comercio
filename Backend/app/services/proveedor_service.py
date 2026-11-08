"""
Servicio de proveedores.

Contiene las reglas de negocio relacionadas con proveedores
y garantiza el aislamiento por comercio.
"""

from app.models.proveedor_model import (
    insertar_proveedor,
    obtener_proveedores,
    obtener_proveedor_por_id,
    actualizar_proveedor,
    actualizar_estado_proveedor,
    obtener_siguiente_numero_proveedor
)


def crear_proveedor(datos, id_comercio):
    if not datos:
        raise ValueError(
            "No se enviaron datos del proveedor"
        )

    nombre = datos.get("nombre_proveedor")

    if nombre is None:
        raise ValueError(
            "El campo 'nombre_proveedor' es obligatorio"
        )

    if not isinstance(nombre, str):
        raise ValueError(
            "El nombre del proveedor debe ser texto"
        )

    nombre = nombre.strip()

    if not nombre:
        raise ValueError(
            "El nombre del proveedor no puede estar vacío"
        )

    numero_proveedor = obtener_siguiente_numero_proveedor(
        id_comercio
    )

    datos_proveedor = {
        "nombre_proveedor": nombre,
        "telefono": datos.get("telefono"),
        "email": datos.get("email"),
        "direccion": datos.get("direccion"),
        "descripcion": datos.get("descripcion"),
        "estado": True,
        "id_comercio": id_comercio,
        "numero_proveedor": numero_proveedor
    }

    proveedor = insertar_proveedor(datos_proveedor)

    if not proveedor:
        raise ValueError(
            "No se pudo crear el proveedor"
        )

    return proveedor


def listar_proveedores(id_comercio):
    return obtener_proveedores(id_comercio)


def buscar_proveedor_por_id(
    id_proveedor,
    id_comercio
):
    proveedor = obtener_proveedor_por_id(
        id_proveedor,
        id_comercio
    )

    if not proveedor:
        raise ValueError(
            "Proveedor no encontrado"
        )

    return proveedor


def editar_proveedor(
    id_proveedor,
    datos,
    id_comercio
):
    proveedor = obtener_proveedor_por_id(
        id_proveedor,
        id_comercio
    )

    if not proveedor:
        raise ValueError(
            "Proveedor no encontrado"
        )

    if not datos:
        raise ValueError(
            "No se enviaron datos para actualizar"
        )

    datos_actualizados = {}

    if "nombre_proveedor" in datos:
        nombre = datos["nombre_proveedor"]

        if not isinstance(nombre, str):
            raise ValueError(
                "El nombre del proveedor debe ser texto"
            )

        nombre = nombre.strip()

        if not nombre:
            raise ValueError(
                "El nombre del proveedor no puede estar vacío"
            )

        datos_actualizados["nombre_proveedor"] = nombre

    campos_permitidos = (
        "telefono",
        "email",
        "direccion",
        "descripcion"
    )

    for campo in campos_permitidos:
        if campo in datos:
            datos_actualizados[campo] = datos[campo]

    if not datos_actualizados:
        raise ValueError(
            "No se enviaron campos válidos para actualizar"
        )

    proveedor_actualizado = actualizar_proveedor(
        id_proveedor,
        id_comercio,
        datos_actualizados
    )

    if not proveedor_actualizado:
        raise ValueError(
            "No se pudo actualizar el proveedor"
        )

    return proveedor_actualizado


def cambiar_estado_proveedor(
    id_proveedor,
    datos,
    id_comercio
):
    proveedor = obtener_proveedor_por_id(
        id_proveedor,
        id_comercio
    )

    if not proveedor:
        raise ValueError(
            "Proveedor no encontrado"
        )

    if not datos:
        raise ValueError(
            "No se enviaron datos"
        )

    if "estado" not in datos:
        raise ValueError(
            "El campo 'estado' es obligatorio"
        )

    nuevo_estado = datos["estado"]

    if not isinstance(nuevo_estado, bool):
        raise ValueError(
            "El campo 'estado' debe ser true o false"
        )

    if proveedor["estado"] == nuevo_estado:
        if nuevo_estado:
            raise ValueError(
                "El proveedor ya se encuentra activo"
            )

        raise ValueError(
            "El proveedor ya se encuentra inactivo"
        )

    proveedor_actualizado = actualizar_estado_proveedor(
        id_proveedor,
        id_comercio,
        nuevo_estado
    )

    if not proveedor_actualizado:
        raise ValueError(
            "No se pudo actualizar el estado del proveedor"
        )

    return proveedor_actualizado