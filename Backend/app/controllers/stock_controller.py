"""
Controlador de stock.

Este módulo recibe las solicitudes relacionadas con stock,
se comunica con la capa de servicios y prepara las respuestas
HTTP que serán enviadas al cliente.
"""

from flask import jsonify, request, g

from app.services.stock_service import (
    ajustar_stock,
    consultar_stock_general,
    consultar_alertas_stock
)


def ajustar_stock_controller(id_producto):
    """
    Realiza un ajuste manual de stock.

    id_usuario e id_comercio se obtienen exclusivamente
    del usuario autenticado.
    """

    datos = request.get_json(silent=True) or {}

    if not datos:
        return jsonify({
            "error": "No se enviaron datos"
        }), 400

    cantidad = datos.get("cantidad")
    tipo_ajuste = datos.get("tipo_ajuste")

    if cantidad is None or tipo_ajuste is None:
        return jsonify({
            "error": (
                "Los campos 'cantidad' y "
                "'tipo_ajuste' son obligatorios"
            )
        }), 400

    try:
        resultado = ajustar_stock(
            id_producto=id_producto,
            cantidad=cantidad,
            tipo_ajuste=tipo_ajuste,
            id_usuario=g.id_usuario,
            id_comercio=g.id_comercio
        )

        return jsonify({
            "message": "Stock ajustado correctamente",
            "data": resultado
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Producto no encontrado":
            return jsonify({
                "error": mensaje
            }), 404

        return jsonify({
            "error": mensaje
        }), 400

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def consultar_stock_general_controller():
    """
    Devuelve el stock del comercio autenticado.

    Permite filtrar mediante:
    GET /stock?buscar=texto
    """

    buscar = request.args.get("buscar")

    try:
        productos = consultar_stock_general(
            id_comercio=g.id_comercio,
            buscar=buscar
        )

        return jsonify(productos), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def consultar_alertas_stock_controller():
    """
    Devuelve los productos activos del comercio
    autenticado que alcanzaron o superaron hacia abajo
    su stock mínimo.
    """

    try:
        alertas = consultar_alertas_stock(
            id_comercio=g.id_comercio
        )

        return jsonify(alertas), 200

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500