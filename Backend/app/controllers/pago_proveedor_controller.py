"""
Controller de pagos a proveedores.

Este módulo se encarga de recibir las solicitudes HTTP
relacionadas con los pagos a proveedores y devolver
las respuestas correspondientes en formato JSON.
"""

from flask import request, jsonify

from app.services.pago_proveedor_service import (
    registrar_pago_proveedor,
    listar_pagos_proveedor,
    consultar_pago_proveedor_por_id,
    consultar_pagos_por_proveedor,
    anular_pago_proveedor,
    consultar_saldo_proveedor
)


def registrar_pago_proveedor_controller():
    """
    Registra un nuevo pago a proveedor.
    """

    try:
        datos = request.get_json()

        pago = registrar_pago_proveedor(datos)

        return jsonify({
            "message": "Pago a proveedor registrado correctamente",
            "pago": pago
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500


def listar_pagos_proveedor_controller():
    """
    Obtiene todos los pagos realizados a proveedores.
    """

    try:
        pagos = listar_pagos_proveedor()

        return jsonify(pagos), 200

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500


def consultar_pago_proveedor_por_id_controller(id_pago):
    """
    Obtiene un pago específico mediante su ID.
    """

    try:
        pago = consultar_pago_proveedor_por_id(id_pago)

        return jsonify(pago), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Pago no encontrado":
            return jsonify({
                "error": mensaje
            }), 404

        return jsonify({
            "error": mensaje
        }), 400

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500


def consultar_pagos_por_proveedor_controller(id_proveedor):
    """
    Obtiene todos los pagos asociados a un proveedor.
    """

    try:
        pagos = consultar_pagos_por_proveedor(id_proveedor)

        return jsonify(pagos), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Proveedor no encontrado":
            return jsonify({
                "error": mensaje
            }), 404

        return jsonify({
            "error": mensaje
        }), 400

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500


def anular_pago_proveedor_controller(id_pago):
    """
    Anula un pago realizado a un proveedor.
    """

    try:
        datos = request.get_json()

        pago = anular_pago_proveedor(id_pago, datos)

        return jsonify({
            "message": "Pago a proveedor anulado correctamente",
            "pago": pago
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Pago no encontrado":
            return jsonify({
                "error": mensaje
            }), 404

        return jsonify({
            "error": mensaje
        }), 400

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500


def consultar_saldo_proveedor_controller(id_proveedor):
    """
    Obtiene la cuenta corriente de un proveedor.
    """

    try:
        saldo = consultar_saldo_proveedor(id_proveedor)

        return jsonify(saldo), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Proveedor no encontrado":
            return jsonify({"error": mensaje}), 404

        return jsonify({"error": mensaje}), 400

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500