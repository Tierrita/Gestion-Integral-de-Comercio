"""
Controlador de clientes.

Recibe las solicitudes HTTP y utiliza el comercio
obtenido desde el contexto de autenticación.
"""

from flask import jsonify, request, g
from postgrest.exceptions import APIError

from app.services.cliente_service import (
    crear_cliente,
    listar_clientes,
    consultar_cliente_por_id,
    editar_cliente,
    cambiar_estado_cliente,
    consultar_historial_ventas_cliente,
)


def crear_cliente_controller():
    try:
        datos = request.get_json(silent=True)

        cliente = crear_cliente(
            datos,
            g.id_comercio
        )

        return jsonify({
            "message": "Cliente registrado correctamente",
            "cliente": cliente
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError:
        return jsonify({
            "error": "Error al registrar el cliente"
        }), 500


def obtener_clientes_controller():
    try:
        clientes = listar_clientes(
            g.id_comercio
        )

        return jsonify(clientes), 200

    except APIError:
        return jsonify({
            "error": "Error al obtener los clientes"
        }), 500


def obtener_cliente_controller(id_cliente):
    try:
        cliente = consultar_cliente_por_id(
            id_cliente,
            g.id_comercio
        )

        return jsonify(cliente), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except APIError:
        return jsonify({
            "error": "Error al obtener el cliente"
        }), 500


def editar_cliente_controller(id_cliente):
    try:
        datos = request.get_json(silent=True)

        cliente = editar_cliente(
            id_cliente,
            datos,
            g.id_comercio
        )

        return jsonify({
            "message": "Cliente actualizado correctamente",
            "cliente": cliente
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cliente no encontrado":
            return jsonify({"error": mensaje}), 404

        return jsonify({"error": mensaje}), 400

    except APIError:
        return jsonify({
            "error": "Error al actualizar el cliente"
        }), 500


def cambiar_estado_cliente_controller(id_cliente):
    try:
        datos = request.get_json(silent=True)

        cliente = cambiar_estado_cliente(
            id_cliente,
            datos,
            g.id_comercio
        )

        return jsonify({
            "message": "Estado del cliente actualizado correctamente",
            "cliente": cliente
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cliente no encontrado":
            return jsonify({"error": mensaje}), 404

        return jsonify({"error": mensaje}), 400

    except APIError:
        return jsonify({
            "error": "Error al actualizar el estado del cliente"
        }), 500


def obtener_historial_ventas_cliente_controller(id_cliente):
    try:
        historial = consultar_historial_ventas_cliente(
            id_cliente,
            g.id_comercio
        )

        return jsonify(historial), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cliente no encontrado":
            return jsonify({"error": mensaje}), 404

        return jsonify({"error": mensaje}), 400

    except APIError:
        return jsonify({
            "error": "Error al obtener el historial de ventas"
        }), 500