from flask import request, jsonify, g

from app.services.cobro_service import (
    registrar_cobro,
    listar_cobros,
    consultar_cobro_por_id,
    consultar_cobros_por_cliente,
    anular_cobro,
    consultar_saldo_cliente
)


def registrar_cobro_controller():
    try:
        datos = request.get_json(silent=True)

        resultado = registrar_cobro(
            datos,
            g.id_comercio,
            g.id_usuario
        )

        return jsonify({
            "message": "Cobro registrado correctamente",
            "cobro": resultado
        }), 201

    except ValueError as error:
        mensaje = str(error)

        if mensaje in [
            "Cliente no encontrado",
            "Cuenta no encontrada",
            "Cobro no encontrado"
        ]:
            return jsonify({"error": mensaje}), 404

        return jsonify({"error": mensaje}), 400

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def listar_cobros_controller():
    try:
        return jsonify({
            "cobros": listar_cobros(g.id_comercio)
        }), 200

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def consultar_cobro_por_id_controller(id_cobro):
    try:
        cobro = consultar_cobro_por_id(
            id_cobro,
            g.id_comercio
        )

        return jsonify({"cobro": cobro}), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def consultar_cobros_por_cliente_controller(id_cliente):
    try:
        resultado = consultar_cobros_por_cliente(
            id_cliente,
            g.id_comercio
        )

        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def anular_cobro_controller(id_cobro):
    try:
        datos = request.get_json(silent=True)

        resultado = anular_cobro(
            id_cobro,
            datos,
            g.id_comercio,
            g.id_usuario
        )

        return jsonify({
            "message": "Cobro anulado correctamente",
            "cobro": resultado
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje in [
            "Cobro no encontrado",
            "Cuenta no encontrada"
        ]:
            return jsonify({"error": mensaje}), 404

        return jsonify({"error": mensaje}), 400

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500


def consultar_saldo_cliente_controller(id_cliente):
    try:
        resultado = consultar_saldo_cliente(
            id_cliente,
            g.id_comercio
        )

        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        return jsonify({
            "error": "Error interno del servidor"
        }), 500