from flask import request, jsonify, g

from app.services.cuenta_service import (
    crear_cuenta,
    listar_cuentas,
    consultar_cuenta_por_id,
    editar_cuenta,
    cambiar_estado_cuenta,
    ajustar_saldo_cuenta,
    consultar_movimientos_cuenta
)


def crear_cuenta_controller():
    try:
        cuenta = crear_cuenta(
            request.get_json(silent=True),
            g.id_comercio
        )

        return jsonify({
            "message": "Cuenta creada correctamente",
            "cuenta": cuenta
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def listar_cuentas_controller():
    try:
        return jsonify({
            "cuentas": listar_cuentas(
                g.id_comercio
            )
        }), 200

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def consultar_cuenta_por_id_controller(id_cuenta):
    try:
        cuenta = consultar_cuenta_por_id(
            id_cuenta,
            g.id_comercio
        )

        return jsonify({"cuenta": cuenta}), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def editar_cuenta_controller(id_cuenta):
    try:
        cuenta = editar_cuenta(
            id_cuenta,
            request.get_json(silent=True),
            g.id_comercio
        )

        return jsonify({
            "message": "Cuenta actualizada correctamente",
            "cuenta": cuenta
        }), 200

    except ValueError as error:
        mensaje = str(error)
        codigo = (
            404
            if mensaje == "Cuenta no encontrada"
            else 400
        )

        return jsonify({"error": mensaje}), codigo

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def cambiar_estado_cuenta_controller(id_cuenta):
    try:
        cuenta = cambiar_estado_cuenta(
            id_cuenta,
            request.get_json(silent=True),
            g.id_comercio
        )

        return jsonify({
            "message":
                "Estado de la cuenta actualizado correctamente",
            "cuenta": cuenta
        }), 200

    except ValueError as error:
        mensaje = str(error)
        codigo = (
            404
            if mensaje == "Cuenta no encontrada"
            else 400
        )

        return jsonify({"error": mensaje}), codigo

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def ajustar_saldo_cuenta_controller(id_cuenta):
    try:
        resultado = ajustar_saldo_cuenta(
            id_cuenta,
            request.get_json(silent=True),
            g.id_comercio,
            g.id_usuario
        )

        return jsonify({
            "message":
                "Saldo de la cuenta ajustado correctamente",
            "ajuste": resultado
        }), 200

    except ValueError as error:
        mensaje = str(error)
        codigo = (
            404
            if mensaje == "Cuenta no encontrada"
            else 400
        )

        return jsonify({"error": mensaje}), codigo

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def consultar_movimientos_cuenta_controller(id_cuenta):
    try:
        resultado = consultar_movimientos_cuenta(
            id_cuenta,
            g.id_comercio
        )

        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500