"""
Controlador de pagos a proveedores.
"""

from flask import request, jsonify, g

from app.services.pago_proveedor_service import (
    registrar_pago_proveedor,
    listar_pagos_proveedor,
    consultar_pago_proveedor_por_id,
    consultar_pagos_por_proveedor,
    anular_pago_proveedor,
    consultar_saldo_proveedor
)


def registrar_pago_proveedor_controller():
    datos = request.get_json(silent=True) or {}

    try:
        pago = registrar_pago_proveedor(
            datos=datos,
            id_usuario=g.id_usuario,
            id_comercio=g.id_comercio
        )

        return jsonify({
            "message": (
                "Pago a proveedor registrado correctamente"
            ),
            "pago": pago
        }), 201

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


def listar_pagos_proveedor_controller():
    try:
        pagos = listar_pagos_proveedor(
            g.id_comercio
        )

        return jsonify(pagos), 200

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def consultar_pago_proveedor_por_id_controller(
    id_pago
):
    try:
        pago = consultar_pago_proveedor_por_id(
            id_pago,
            g.id_comercio
        )

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

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def consultar_pagos_por_proveedor_controller(
    id_proveedor
):
    try:
        pagos = consultar_pagos_por_proveedor(
            id_proveedor,
            g.id_comercio
        )

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

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def anular_pago_proveedor_controller(id_pago):
    datos = request.get_json(silent=True) or {}

    try:
        pago = anular_pago_proveedor(
            id_pago=id_pago,
            datos=datos,
            id_usuario=g.id_usuario,
            id_comercio=g.id_comercio
        )

        return jsonify({
            "message": (
                "Pago a proveedor anulado correctamente"
            ),
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

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def consultar_saldo_proveedor_controller(
    id_proveedor
):
    try:
        saldo = consultar_saldo_proveedor(
            id_proveedor,
            g.id_comercio
        )

        return jsonify(saldo), 200

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