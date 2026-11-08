"""
Controlador de proveedores.
"""

from flask import jsonify, request, g

from app.services.proveedor_service import (
    crear_proveedor,
    listar_proveedores,
    buscar_proveedor_por_id,
    editar_proveedor,
    cambiar_estado_proveedor
)


def crear_proveedor_controller():
    datos = request.get_json(silent=True) or {}

    try:
        proveedor = crear_proveedor(
            datos,
            g.id_comercio
        )

        return jsonify({
            "message": "Proveedor creado correctamente",
            "proveedor": proveedor
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def obtener_proveedores_controller():
    try:
        proveedores = listar_proveedores(
            g.id_comercio
        )

        return jsonify(proveedores), 200

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def obtener_proveedor_controller(id_proveedor):
    try:
        proveedor = buscar_proveedor_por_id(
            id_proveedor,
            g.id_comercio
        )

        return jsonify(proveedor), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def editar_proveedor_controller(id_proveedor):
    datos = request.get_json(silent=True) or {}

    try:
        proveedor = editar_proveedor(
            id_proveedor,
            datos,
            g.id_comercio
        )

        return jsonify({
            "message": "Proveedor actualizado correctamente",
            "proveedor": proveedor
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Proveedor no encontrado":
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


def cambiar_estado_proveedor_controller(id_proveedor):
    datos = request.get_json(silent=True) or {}

    try:
        proveedor = cambiar_estado_proveedor(
            id_proveedor,
            datos,
            g.id_comercio
        )

        return jsonify({
            "message": (
                "Estado de proveedor actualizado correctamente"
            ),
            "proveedor": proveedor
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Proveedor no encontrado":
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