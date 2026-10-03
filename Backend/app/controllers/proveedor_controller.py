"""
Controlador de proveedores.

Este módulo recibe las solicitudes relacionadas con proveedores,
se comunica con la capa de servicios y prepara las respuestas
HTTP que serán enviadas al cliente.
"""

from flask import jsonify, request
from postgrest.exceptions import APIError

from app.services.proveedor_service import (
    crear_proveedor,
    listar_proveedores,
    buscar_proveedor_por_id,
    editar_proveedor,
    cambiar_estado_proveedor

)


def crear_proveedor_controller():
    """
    Recibe los datos de un proveedor, los envía a la capa
    de servicios y devuelve la respuesta correspondiente.
    """

    try:
        # Obtener datos enviados en formato JSON
        datos = request.get_json()

        # Enviar datos a la capa de servicios
        proveedor = crear_proveedor(datos)

        # Respuesta exitosa
        return jsonify({
            "message": "Proveedor creado correctamente",
            "proveedor": proveedor
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al crear el proveedor",
            "detalle": str(error)
        }), 500



def obtener_proveedores_controller():
    """
    Obtiene todos los proveedores mediante la capa de servicios
    y devuelve una respuesta en formato JSON.
    """

    try:
        proveedores = listar_proveedores()

        return jsonify(proveedores), 200

    except APIError as error:
        return jsonify({
            "error": "Error al obtener los proveedores",
            "detalle": str(error)
        }), 500




def obtener_proveedor_controller(id_proveedor):
    """
    Obtiene un proveedor específico mediante su ID.
    """

    try:
        proveedor = buscar_proveedor_por_id(id_proveedor)

        return jsonify(proveedor), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except APIError as error:
        return jsonify({
            "error": "Error al obtener el proveedor",
            "detalle": str(error)
        }), 500



def editar_proveedor_controller(id_proveedor):
    """
    Edita un proveedor existente mediante su ID.
    """

    try:
        datos = request.get_json()

        proveedor = editar_proveedor(
            id_proveedor,
            datos
        )

        return jsonify({
            "message": "Proveedor actualizado correctamente",
            "proveedor": proveedor
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al actualizar el proveedor",
            "detalle": str(error)
        }), 500


def cambiar_estado_proveedor_controller(id_proveedor):
    """
    Cambia el estado de un proveedor mediante su ID.
    """

    try:
        datos = request.get_json()

        proveedor = cambiar_estado_proveedor(
            id_proveedor,
            datos
        )

        return jsonify({
            "message": "Estado de proveedor actualizado correctamente",
            "proveedor": proveedor
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return jsonify({
            "error": "Error al actualizar el estado del proveedor",
            "detalle": str(error)
        }), 500