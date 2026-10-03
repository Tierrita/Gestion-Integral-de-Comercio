"""
Controlador de ventas.

Este módulo recibe las solicitudes relacionadas con ventas,
se comunica con la capa de servicios y prepara las respuestas
HTTP que serán enviadas al cliente.
"""

from flask import jsonify, request
from postgrest.exceptions import APIError

from app.services.venta_service import (
    crear_venta,
    listar_ventas,
    buscar_venta_por_id,
    anular_venta
)


def crear_venta_controller():
    """
    Recibe los datos de una venta, los envía a la capa
    de servicios y devuelve la respuesta correspondiente.
    """

    try:
        datos = request.get_json()

        venta = crear_venta(datos)

        return jsonify({
            "message": "Venta registrada correctamente",
            "venta": venta
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al registrar la venta",
            "detalle": str(error)
        }), 500



def obtener_ventas_controller():
    """
    Obtiene todas las ventas mediante la capa de servicios
    y devuelve una respuesta en formato JSON.
    """

    try:
        ventas = listar_ventas()

        return jsonify(ventas), 200

    except APIError as error:
        return jsonify({
            "error": "Error al obtener las ventas",
            "detalle": str(error)
        }), 500

def obtener_venta_controller(id_venta):
    """
    Obtiene una venta específica mediante su ID,
    junto con todos sus detalles.
    """

    try:
        venta = buscar_venta_por_id(id_venta)

        return jsonify(venta), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except APIError as error:
        return jsonify({
            "error": "Error al obtener la venta",
            "detalle": str(error)
        }), 500


def anular_venta_controller(id_venta):
    """
    Anula una venta mediante su ID.

    La lógica de devolución de stock y registro
    de movimientos se realiza en la capa de servicios.
    """

    try:
        resultado = anular_venta(id_venta)

        return jsonify({
            "message": "Venta anulada correctamente",
            "resultado": resultado
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al anular la venta",
            "detalle": str(error)
        }), 500