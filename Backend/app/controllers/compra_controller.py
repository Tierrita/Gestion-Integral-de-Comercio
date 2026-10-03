"""
Controlador de compras.

Este módulo recibe las solicitudes relacionadas con compras,
se comunica con la capa de servicios y prepara las respuestas
HTTP que serán enviadas al cliente.
"""

from flask import jsonify, request
from postgrest.exceptions import APIError

from app.services.compra_service import (
    crear_compra,
    listar_compras,
    buscar_compra_por_id,
    anular_compra
)



def crear_compra_controller():
    """
    Recibe los datos de una compra, los envía a la capa
    de servicios y devuelve la respuesta correspondiente.
    """

    try:
        datos = request.get_json()

        compra = crear_compra(datos)

        return jsonify({
            "message": "Compra registrada correctamente",
            "compra": compra
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al registrar la compra",
            "detalle": str(error)
        }), 500



def obtener_compras_controller():
    """
    Obtiene todas las compras mediante la capa de servicios
    y devuelve una respuesta en formato JSON.
    """

    try:
        compras = listar_compras()

        return jsonify(compras), 200

    except APIError as error:
        return jsonify({
            "error": "Error al obtener las compras",
            "detalle": str(error)
        }), 500


def obtener_compra_controller(id_compra):
    """
    Obtiene una compra específica mediante su ID,
    junto con todos sus detalles.
    """

    try:
        compra = buscar_compra_por_id(id_compra)

        return jsonify(compra), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except APIError as error:
        return jsonify({
            "error": "Error al obtener la compra",
            "detalle": str(error)
        }), 500



def anular_compra_controller(id_compra):
    """
    Anula una compra mediante su ID.

    La lógica de reversión de stock y registro
    de movimientos se realiza en la capa de servicios.
    """

    try:
        resultado = anular_compra(id_compra)

        return jsonify({
            "message": "Compra anulada correctamente",
            "resultado": resultado
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al anular la compra",
            "detalle": str(error)
        }), 500