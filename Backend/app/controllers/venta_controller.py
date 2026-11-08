"""
Controlador de ventas.

Recibe solicitudes HTTP, utiliza la información segura
del usuario autenticado almacenada en Flask g y delega
la lógica de negocio al servicio.
"""

from flask import jsonify, request, g
from postgrest.exceptions import APIError

from app.services.venta_service import (
    crear_venta,
    listar_ventas,
    buscar_venta_por_id,
    anular_venta
)


def crear_venta_controller():
    """Registra una nueva venta."""

    try:
        datos = request.get_json(
            silent=True
        )

        venta = crear_venta(
            datos,
            g.id_comercio,
            g.id_usuario
        )

        return jsonify({
            "message": "Venta registrada correctamente",
            "venta": venta
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError:
        return jsonify({
            "error": "Error al registrar la venta"
        }), 500


def obtener_ventas_controller():
    """Lista las ventas del comercio autenticado."""

    try:
        ventas = listar_ventas(
            g.id_comercio
        )

        return jsonify(
            ventas
        ), 200

    except APIError:
        return jsonify({
            "error": "Error al obtener las ventas"
        }), 500


def obtener_venta_controller(id_venta):
    """
    Obtiene una venta específica del comercio
    autenticado junto con sus detalles.
    """

    try:
        venta = buscar_venta_por_id(
            id_venta,
            g.id_comercio
        )

        return jsonify(
            venta
        ), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except APIError:
        return jsonify({
            "error": "Error al obtener la venta"
        }), 500


def anular_venta_controller(id_venta):
    """
    Anula una venta.

    El usuario que ejecuta la anulación se obtiene
    desde el token JWT.
    """

    try:
        resultado = anular_venta(
            id_venta,
            g.id_comercio,
            g.id_usuario
        )

        return jsonify({
            "message": "Venta anulada correctamente",
            "resultado": resultado
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError:
        return jsonify({
            "error": "Error al anular la venta"
        }), 500