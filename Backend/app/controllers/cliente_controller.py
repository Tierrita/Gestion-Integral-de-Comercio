"""
Controlador de clientes.

Este módulo recibe las solicitudes relacionadas con clientes,
se comunica con la capa de servicios y prepara las respuestas
HTTP que serán enviadas al cliente.
"""

from flask import jsonify, request
from postgrest.exceptions import APIError

from app.services.cliente_service import (
    crear_cliente,
    listar_clientes,
    consultar_cliente_por_id,
    editar_cliente,
    cambiar_estado_cliente,
    consultar_historial_ventas_cliente
)


def crear_cliente_controller():
    """
    Recibe los datos de un cliente y registra
    un nuevo cliente mediante la capa de servicios.
    """

    try:
        datos = request.get_json()

        cliente = crear_cliente(datos)

        return jsonify({
            "message": "Cliente registrado correctamente",
            "cliente": cliente
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al registrar el cliente",
            "detalle": str(error)
        }), 500


def obtener_clientes_controller():
    """
    Obtiene todos los clientes registrados.
    """

    try:
        clientes = listar_clientes()

        return jsonify(clientes), 200

    except APIError as error:
        return jsonify({
            "error": "Error al obtener los clientes",
            "detalle": str(error)
        }), 500


def obtener_cliente_controller(id_cliente):
    """
    Obtiene un cliente específico mediante su ID.
    """

    try:
        cliente = consultar_cliente_por_id(id_cliente)

        return jsonify(cliente), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except APIError as error:
        return jsonify({
            "error": "Error al obtener el cliente",
            "detalle": str(error)
        }), 500


def editar_cliente_controller(id_cliente):
    """
    Actualiza los datos editables de un cliente.
    """

    try:
        datos = request.get_json()

        cliente = editar_cliente(
            id_cliente,
            datos
        )

        return jsonify({
            "message": "Cliente actualizado correctamente",
            "cliente": cliente
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cliente no encontrado":
            return jsonify({
                "error": mensaje
            }), 404

        return jsonify({
            "error": mensaje
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al actualizar el cliente",
            "detalle": str(error)
        }), 500


def cambiar_estado_cliente_controller(id_cliente):
    """
    Activa o desactiva un cliente.
    """

    try:
        datos = request.get_json()

        cliente = cambiar_estado_cliente(
            id_cliente,
            datos
        )

        return jsonify({
            "message": "Estado del cliente actualizado correctamente",
            "cliente": cliente
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cliente no encontrado":
            return jsonify({
                "error": mensaje
            }), 404

        return jsonify({
            "error": mensaje
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al actualizar el estado del cliente",
            "detalle": str(error)
        }), 500


def obtener_historial_ventas_cliente_controller(id_cliente):
    """
    Obtiene el historial de ventas de un cliente,
    incluyendo los detalles de cada venta.
    """

    try:
        historial = consultar_historial_ventas_cliente(
            id_cliente
        )

        return jsonify(historial), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cliente no encontrado":
            return jsonify({
                "error": mensaje
            }), 404

        return jsonify({
            "error": mensaje
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al obtener el historial de ventas",
            "detalle": str(error)
        }), 500