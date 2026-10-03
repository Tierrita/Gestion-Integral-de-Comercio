"""
Controlador de categorías.

Este módulo recibe las solicitudes relacionadas con categorías,
se comunica con la capa de servicios y prepara las respuestas
HTTP que serán enviadas al cliente.
"""

from flask import jsonify, request
from postgrest.exceptions import APIError

from app.services.categoria_service import (
    crear_categoria,
    listar_categorias,
    buscar_categoria_por_id,
    editar_categoria,
    cambiar_estado_categoria
)


def crear_categoria_controller():
    """
    Recibe los datos de una categoría, los envía a la capa
    de servicios y devuelve la respuesta correspondiente.
    """

    try:
        datos = request.get_json()

        categoria = crear_categoria(datos)

        return jsonify({
            "message": "Categoría creada correctamente",
            "categoria": categoria
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al crear la categoría",
            "detalle": str(error)
        }), 500


def obtener_categorias_controller():
    """
    Obtiene todas las categorías mediante la capa de servicios
    y devuelve una respuesta en formato JSON.
    """

    try:
        categorias = listar_categorias()

        return jsonify(categorias), 200

    except APIError as error:
        return jsonify({
            "error": "Error al obtener las categorías",
            "detalle": str(error)
        }), 500




def obtener_categoria_controller(id_categoria):
    """
    Obtiene una categoría específica mediante su ID.
    """

    try:
        categoria = buscar_categoria_por_id(id_categoria)

        return jsonify(categoria), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except APIError as error:
        return jsonify({
            "error": "Error al obtener la categoría",
            "detalle": str(error)
        }), 500



def editar_categoria_controller(id_categoria):
    """
    Edita una categoría existente mediante su ID.
    """

    try:
        datos = request.get_json()

        categoria = editar_categoria(
            id_categoria,
            datos
        )

        return jsonify({
            "message": "Categoría actualizada correctamente",
            "categoria": categoria
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al actualizar la categoría",
            "detalle": str(error)
        }), 500


def cambiar_estado_categoria_controller(id_categoria):
    """
    Cambia el estado de una categoría mediante su ID.
    """

    try:
        datos = request.get_json()

        categoria = cambiar_estado_categoria(
            id_categoria,
            datos
        )

        return jsonify({
            "message": "Estado de categoría actualizado correctamente",
            "categoria": categoria
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al actualizar el estado de la categoría",
            "detalle": str(error)
        }), 500