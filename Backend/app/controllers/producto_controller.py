"""
Controlador de productos.

Este módulo recibe las solicitudes relacionadas con productos,
se comunica con la capa de servicios y prepara las respuestas
HTTP que serán enviadas al cliente.
"""

from flask import jsonify, request
from postgrest.exceptions import APIError

from app.services.producto_service import (
    listar_productos,
    buscar_producto_por_id,
    crear_producto
)


def obtener_productos_controller():
    """
    Obtiene todos los productos mediante la capa de servicios
    y devuelve una respuesta en formato JSON.
    """

    productos = listar_productos()

    return jsonify(productos), 200


def obtener_producto_controller(id_producto):
    """
    Obtiene un producto específico mediante su ID.
    """

    producto = buscar_producto_por_id(id_producto)

    if not producto:
        return jsonify({
            "mensaje": "Producto no encontrado"
        }), 404

    return jsonify(producto), 200


def crear_producto_controller():
    """
    Recibe los datos de un nuevo producto enviados en formato JSON.
    """

    datos = request.get_json()

    # Validar que se hayan enviado datos
    if not datos:
        return jsonify({
            "mensaje": "No se enviaron datos del producto"
        }), 400

    # Campos obligatorios para crear un producto
    campos_obligatorios = [
        "nombre_producto",
        "precio_costo",
        "precio_venta",
        "id_categoria",
        "id_proveedor",
        "unidad_de_medida"
    ]

    # Validar que estén presentes todos los campos obligatorios
    for campo in campos_obligatorios:
        if campo not in datos:
            return jsonify({
                "mensaje": f"Falta el campo obligatorio: {campo}"
            }), 400

    # Intentar crear el producto mediante la capa de servicios
    try:
        producto = crear_producto(datos)

        return jsonify(producto), 201

    except ValueError as error:
        return jsonify({
            "mensaje": str(error)
        }), 400

    except APIError as error:
        if error.code == "23503":
            return jsonify({
                "mensaje": "La categoría o el proveedor indicado no existe"
            }), 400

        return jsonify({
            "mensaje": "Error al crear el producto"
        }), 500
    