"""
Controlador de categorías.

Este módulo recibe las solicitudes relacionadas con categorías,
se comunica con la capa de servicios y prepara las respuestas
HTTP que serán enviadas al cliente.

El comercio utilizado en las operaciones se obtiene
exclusivamente desde el usuario autenticado.
"""

from flask import jsonify, request, g
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
    Crea una categoría dentro del comercio autenticado.
    """

    try:
        datos = request.get_json() or {}

        categoria = crear_categoria(
            datos=datos,
            id_comercio=g.id_comercio
        )

        return jsonify({
            "message": "Categoría creada correctamente",
            "categoria": categoria
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError:
        return jsonify({
            "error": "Error al crear la categoría"
        }), 500

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def obtener_categorias_controller():
    """
    Obtiene únicamente las categorías
    del comercio autenticado.
    """

    try:
        categorias = listar_categorias(
            g.id_comercio
        )

        return jsonify(categorias), 200

    except APIError:
        return jsonify({
            "error": "Error al obtener las categorías"
        }), 500

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def obtener_categoria_controller(id_categoria):
    """
    Obtiene una categoría específica únicamente
    si pertenece al comercio autenticado.
    """

    try:
        categoria = buscar_categoria_por_id(
            id_categoria=id_categoria,
            id_comercio=g.id_comercio
        )

        return jsonify(categoria), 200

    except ValueError as error:

        if str(error) == "Categoría no encontrada":
            return jsonify({
                "error": str(error)
            }), 404

        return jsonify({
            "error": str(error)
        }), 400

    except APIError:
        return jsonify({
            "error": "Error al obtener la categoría"
        }), 500

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def editar_categoria_controller(id_categoria):
    """
    Modifica una categoría perteneciente
    al comercio autenticado.
    """

    try:
        datos = request.get_json() or {}

        categoria = editar_categoria(
            id_categoria=id_categoria,
            datos=datos,
            id_comercio=g.id_comercio
        )

        return jsonify({
            "message": "Categoría actualizada correctamente",
            "categoria": categoria
        }), 200

    except ValueError as error:

        if str(error) == "Categoría no encontrada":
            return jsonify({
                "error": str(error)
            }), 404

        return jsonify({
            "error": str(error)
        }), 400

    except APIError:
        return jsonify({
            "error": "Error al actualizar la categoría"
        }), 500

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def cambiar_estado_categoria_controller(
    id_categoria
):
    """
    Activa o desactiva una categoría perteneciente
    al comercio autenticado.
    """

    try:
        datos = request.get_json() or {}

        categoria = cambiar_estado_categoria(
            id_categoria=id_categoria,
            datos=datos,
            id_comercio=g.id_comercio
        )

        return jsonify({
            "message": (
                "Estado de categoría actualizado correctamente"
            ),
            "categoria": categoria
        }), 200

    except ValueError as error:

        if str(error) == "Categoría no encontrada":
            return jsonify({
                "error": str(error)
            }), 404

        return jsonify({
            "error": str(error)
        }), 400

    except APIError:
        return jsonify({
            "error": (
                "Error al actualizar el estado de la categoría"
            )
        }), 500

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500