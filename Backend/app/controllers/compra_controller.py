"""
Controlador de compras.
"""

from flask import jsonify, request, g
from postgrest.exceptions import APIError

from app.services.compra_service import (
    crear_compra,
    listar_compras,
    buscar_compra_por_id,
    anular_compra
)


def crear_compra_controller():
    try:
        datos = request.get_json(silent=True)

        compra = crear_compra(
            datos,
            g.id_comercio,
            g.id_usuario
        )

        return jsonify({
            "message": "Compra registrada correctamente",
            "compra": compra
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError:
        return jsonify({
            "error": "Error al registrar la compra"
        }), 500


def obtener_compras_controller():
    try:
        compras = listar_compras(
            g.id_comercio
        )

        return jsonify(compras), 200

    except APIError:
        return jsonify({
            "error": "Error al obtener las compras"
        }), 500


def obtener_compra_controller(id_compra):
    try:
        compra = buscar_compra_por_id(
            id_compra,
            g.id_comercio
        )

        return jsonify(compra), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except APIError:
        return jsonify({
            "error": "Error al obtener la compra"
        }), 500


def anular_compra_controller(id_compra):
    try:
        resultado = anular_compra(
            id_compra,
            g.id_comercio,
            g.id_usuario
        )

        return jsonify({
            "message": "Compra anulada correctamente",
            "resultado": resultado
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError:
        return jsonify({
            "error": "Error al anular la compra"
        }), 500