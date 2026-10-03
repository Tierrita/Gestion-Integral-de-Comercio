"""
Controlador de stock.

Este módulo recibe las solicitudes relacionadas con stock,
se comunica con la capa de servicios y prepara las respuestas
HTTP que serán enviadas al cliente.
"""

from flask import jsonify, request
from app.services.stock_service import (
    ajustar_stock, 
    consultar_stock_general,
    consultar_alertas_stock
)


def ajustar_stock_controller(id_producto):
    """
    Recibe los datos necesarios para realizar
    un ajuste manual de stock.
    """

    datos = request.get_json()

    if not datos:
        return jsonify({
            "error": "No se enviaron datos"
        }), 400

    cantidad = datos.get("cantidad")
    tipo_ajuste = datos.get("tipo_ajuste")
    id_usuario = datos.get("id_usuario")

    if cantidad is None or tipo_ajuste is None or id_usuario is None:
        return jsonify({
            "error": "Faltan datos obligatorios"
        }), 400

    try:
        resultado = ajustar_stock(
            id_producto,
            cantidad,
            tipo_ajuste,
            id_usuario
        )

        return jsonify({
            "message": "Stock ajustado correctamente",
            "data": resultado
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400



def consultar_stock_general_controller():
    """
    Devuelve el stock general o filtra por nombre si llega ?buscar=.
    """
    buscar = request.args.get("buscar")
    productos = consultar_stock_general(buscar)

    return jsonify(productos), 200



def consultar_alertas_stock_controller():
    """
    Devuelve los productos con alerta de stock en formato JSON.
    """
    alertas = consultar_alertas_stock()
    return jsonify(alertas), 200