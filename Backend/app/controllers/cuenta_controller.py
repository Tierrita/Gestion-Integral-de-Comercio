"""
Controlador de cuentas financieras.

Este módulo se encarga de recibir las solicitudes HTTP
relacionadas con las cuentas financieras y generar
las respuestas JSON correspondientes.
"""

from flask import request, jsonify

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
    """
    Controlador para crear una nueva cuenta financiera.
    """

    try:
        datos = request.get_json(silent=True)

        cuenta = crear_cuenta(datos)

        return jsonify({
            "message": "Cuenta creada correctamente",
            "cuenta": cuenta
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


def listar_cuentas_controller():
    """
    Controlador para consultar todas las cuentas financieras.
    """

    try:
        cuentas = listar_cuentas()

        return jsonify({
            "cuentas": cuentas
        }), 200

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500


def consultar_cuenta_por_id_controller(id_cuenta):
    """
    Controlador para consultar una cuenta financiera mediante su ID.
    """

    try:
        cuenta = consultar_cuenta_por_id(id_cuenta)

        return jsonify({
            "cuenta": cuenta
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500

def editar_cuenta_controller(id_cuenta):
    """
    Controlador para modificar una cuenta financiera.
    """

    try:
        datos = request.get_json(silent=True)

        cuenta = editar_cuenta(id_cuenta, datos)

        return jsonify({
            "message": "Cuenta actualizada correctamente",
            "cuenta": cuenta
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cuenta no encontrada":
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

def cambiar_estado_cuenta_controller(id_cuenta):
    """
    Controlador para activar o desactivar
    una cuenta financiera.
    """

    try:
        datos = request.get_json(silent=True)

        cuenta = cambiar_estado_cuenta(
            id_cuenta,
            datos
        )

        return jsonify({
            "message": "Estado de la cuenta actualizado correctamente",
            "cuenta": cuenta
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cuenta no encontrada":
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


def ajustar_saldo_cuenta_controller(id_cuenta):
    """
    Controlador para realizar un ajuste manual
    sobre el saldo de una cuenta financiera.
    """

    try:
        datos = request.get_json(silent=True)

        resultado = ajustar_saldo_cuenta(
            id_cuenta,
            datos
        )

        return jsonify({
            "message": "Saldo de la cuenta ajustado correctamente",
            "ajuste": resultado
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cuenta no encontrada":
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


def consultar_movimientos_cuenta_controller(id_cuenta):
    """
    Controlador para consultar el historial de movimientos
    financieros de una cuenta.
    """

    try:
        resultado = consultar_movimientos_cuenta(id_cuenta)

        return jsonify(resultado), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cuenta no encontrada":
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