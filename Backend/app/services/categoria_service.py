"""
Servicio de categorías.

Este módulo contiene la lógica de negocio relacionada
con las categorías.

Todas las operaciones se realizan dentro del comercio
del usuario autenticado.
"""

from app.models.categoria_model import (
    insertar_categoria,
    obtener_categorias,
    obtener_categoria_por_id,
    actualizar_categoria,
    actualizar_estado_categoria,
    obtener_productos_activos_por_categoria
)


def crear_categoria(datos, id_comercio):
    """
    Crea una nueva categoría dentro del comercio autenticado.

    El comercio y el estado inicial son controlados
    exclusivamente por el backend.
    """

    if not datos:
        raise ValueError(
            "No se enviaron datos de la categoría"
        )

    if "nombre_categoria" not in datos:
        raise ValueError(
            "El campo 'nombre_categoria' es obligatorio"
        )

    nombre_categoria = datos["nombre_categoria"]

    if not isinstance(nombre_categoria, str):
        raise ValueError(
            "El nombre de la categoría debe ser texto"
        )

    nombre_categoria = nombre_categoria.strip()

    if not nombre_categoria:
        raise ValueError(
            "El nombre de la categoría no puede estar vacío"
        )

    descripcion = datos.get("descripcion")

    if (
        descripcion is not None
        and not isinstance(descripcion, str)
    ):
        raise ValueError(
            "La descripción debe ser texto"
        )

    if isinstance(descripcion, str):
        descripcion = descripcion.strip()

    datos_categoria = {
        "nombre_categoria": nombre_categoria,
        "descripcion": descripcion,
        "estado": True,
        "id_comercio": id_comercio
    }

    categoria_creada = insertar_categoria(
        datos_categoria
    )

    if not categoria_creada:
        raise ValueError(
            "No se pudo crear la categoría"
        )

    return categoria_creada[0]


def listar_categorias(id_comercio):
    """
    Obtiene las categorías pertenecientes
    al comercio autenticado.
    """

    return obtener_categorias(id_comercio)


def buscar_categoria_por_id(
    id_categoria,
    id_comercio
):
    """
    Obtiene una categoría específica perteneciente
    al comercio autenticado.
    """

    categoria = obtener_categoria_por_id(
        id_categoria,
        id_comercio
    )

    if not categoria:
        raise ValueError(
            "Categoría no encontrada"
        )

    return categoria


def editar_categoria(
    id_categoria,
    datos,
    id_comercio
):
    """
    Modifica únicamente los campos permitidos
    de una categoría del comercio autenticado.

    No permite modificar desde este endpoint:
    - id_categoria
    - id_comercio
    - estado
    - fecha_alta
    """

    categoria = obtener_categoria_por_id(
        id_categoria,
        id_comercio
    )

    if not categoria:
        raise ValueError(
            "Categoría no encontrada"
        )

    if not datos:
        raise ValueError(
            "No se enviaron datos para actualizar"
        )

    datos_actualizados = {}

    if "nombre_categoria" in datos:

        nombre_categoria = datos[
            "nombre_categoria"
        ]

        if not isinstance(
            nombre_categoria,
            str
        ):
            raise ValueError(
                "El nombre de la categoría debe ser texto"
            )

        nombre_categoria = (
            nombre_categoria.strip()
        )

        if not nombre_categoria:
            raise ValueError(
                "El nombre de la categoría no puede estar vacío"
            )

        datos_actualizados[
            "nombre_categoria"
        ] = nombre_categoria

    if "descripcion" in datos:

        descripcion = datos["descripcion"]

        if (
            descripcion is not None
            and not isinstance(descripcion, str)
        ):
            raise ValueError(
                "La descripción debe ser texto"
            )

        if isinstance(descripcion, str):
            descripcion = descripcion.strip()

        datos_actualizados[
            "descripcion"
        ] = descripcion

    if not datos_actualizados:
        raise ValueError(
            "No se enviaron campos válidos para actualizar"
        )

    categoria_actualizada = actualizar_categoria(
        id_categoria,
        id_comercio,
        datos_actualizados
    )

    if not categoria_actualizada:
        raise ValueError(
            "No se pudo actualizar la categoría"
        )

    return categoria_actualizada


def cambiar_estado_categoria(
    id_categoria,
    datos,
    id_comercio
):
    """
    Activa o desactiva una categoría perteneciente
    al comercio autenticado.

    Una categoría no puede desactivarse mientras
    tenga productos activos asociados.
    """

    categoria = obtener_categoria_por_id(
        id_categoria,
        id_comercio
    )

    if not categoria:
        raise ValueError(
            "Categoría no encontrada"
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

    estado_actual = categoria.get(
        "estado",
        True
    )

    if estado_actual == nuevo_estado:

        if nuevo_estado:
            raise ValueError(
                "La categoría ya se encuentra activa"
            )

        raise ValueError(
            "La categoría ya se encuentra inactiva"
        )

    # Si se intenta desactivar, verificar primero
    # que no existan productos activos asociados.
    if nuevo_estado is False:

        productos_activos = (
            obtener_productos_activos_por_categoria(
                id_categoria,
                id_comercio
            )
        )

        if productos_activos:
            raise ValueError(
                "No se puede desactivar la categoría "
                "porque tiene productos activos asociados"
            )

    categoria_actualizada = (
        actualizar_estado_categoria(
            id_categoria,
            id_comercio,
            nuevo_estado
        )
    )

    if not categoria_actualizada:
        raise ValueError(
            "No se pudo actualizar el estado de la categoría"
        )

    return categoria_actualizada