"""
Servicio de categorías.

Este módulo contiene la lógica de negocio relacionada
con las categorías.
"""

from app.models.categoria_model import (
    insertar_categoria,
    obtener_categorias,
    obtener_categoria_por_id,
    actualizar_categoria,
    actualizar_estado_categoria
)


def crear_categoria(datos):
    """
    Crea una nueva categoría luego de validar
    los datos recibidos.
    """

    if not datos:
        raise ValueError("No se enviaron datos de la categoría")

    if "nombre_categoria" not in datos:
        raise ValueError("El campo 'nombre_categoria' es obligatorio")

    nombre_categoria = datos["nombre_categoria"]

    if not isinstance(nombre_categoria, str):
        raise ValueError("El nombre de la categoría debe ser texto")

    if not nombre_categoria.strip():
        raise ValueError("El nombre de la categoría no puede estar vacío")

    datos_categoria = {
        "nombre_categoria": nombre_categoria.strip(),
        "descripcion": datos.get("descripcion"),
        "estado": datos.get("estado", True)
    }

    categoria_creada = insertar_categoria(datos_categoria)

    return categoria_creada[0]

def listar_categorias():
    """
    Obtiene todas las categorías registradas.
    """

    categorias = obtener_categorias()

    return categorias


def buscar_categoria_por_id(id_categoria):
    """
    Obtiene una categoría específica mediante su ID.
    """

    categoria = obtener_categoria_por_id(id_categoria)

    if not categoria:
        raise ValueError("Categoría no encontrada")

    return categoria


def editar_categoria(id_categoria, datos):
    """
    Edita los datos de una categoría existente.

    Permite modificar únicamente el nombre y la descripción
    de la categoría.
    """

    # Verificar que la categoría exista
    categoria = obtener_categoria_por_id(id_categoria)

    if not categoria:
        raise ValueError("Categoría no encontrada")

    # Verificar que se hayan enviado datos
    if not datos:
        raise ValueError("No se enviaron datos para actualizar")

    datos_actualizados = {}

    # Actualizar nombre si fue enviado
    if "nombre_categoria" in datos:

        nombre_categoria = datos["nombre_categoria"]

        if not isinstance(nombre_categoria, str):
            raise ValueError(
                "El nombre de la categoría debe ser texto"
            )

        if not nombre_categoria.strip():
            raise ValueError(
                "El nombre de la categoría no puede estar vacío"
            )

        datos_actualizados["nombre_categoria"] = (
            nombre_categoria.strip()
        )

    # Actualizar descripción si fue enviada
    if "descripcion" in datos:
        datos_actualizados["descripcion"] = datos["descripcion"]

    # Verificar que exista algún campo permitido para actualizar
    if not datos_actualizados:
        raise ValueError(
            "No se enviaron campos válidos para actualizar"
        )

    categoria_actualizada = actualizar_categoria(
        id_categoria,
        datos_actualizados
    )

    return categoria_actualizada


def cambiar_estado_categoria(id_categoria, datos):
    """
    Cambia el estado de una categoría.

    Permite activar o desactivar una categoría
    utilizando un valor booleano.
    """

    # Verificar que la categoría exista
    categoria = obtener_categoria_por_id(id_categoria)

    if not categoria:
        raise ValueError("Categoría no encontrada")

    # Verificar que se hayan enviado datos
    if not datos:
        raise ValueError("No se enviaron datos")

    # Verificar que exista el campo estado
    if "estado" not in datos:
        raise ValueError("El campo 'estado' es obligatorio")

    nuevo_estado = datos["estado"]

    # El estado debe ser booleano
    if not isinstance(nuevo_estado, bool):
        raise ValueError(
            "El campo 'estado' debe ser true o false"
        )

    categoria_actualizada = actualizar_estado_categoria(
        id_categoria,
        nuevo_estado
    )

    return categoria_actualizada