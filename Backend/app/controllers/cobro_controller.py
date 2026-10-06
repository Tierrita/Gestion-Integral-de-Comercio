"""
Controlador de cobros.

Este módulo se encarga de recibir las solicitudes HTTP
relacionadas con los cobros realizados por los clientes
y devolver las respuestas correspondientes en formato JSON.
"""

from flask import request, jsonify

from app.services.cobro_service import (
    registrar_cobro,
    listar_cobros,
    consultar_cobro_por_id,
    consultar_cobros_por_cliente,
    anular_cobro,
    consultar_saldo_cliente
)


def registrar_cobro_controller():
    """
    Controlador para registrar un nuevo cobro de cliente.
    """

    try:
        # Obtener datos enviados en el body
        datos = request.get_json(silent=True)

        # Ejecutar lógica de negocio
        resultado = registrar_cobro(datos)

        return jsonify({
            "message": "Cobro registrado correctamente",
            "cobro": resultado
        }), 201

    except ValueError as error:
        mensaje = str(error)

        # Recursos inexistentes
        if mensaje in [
            "Cliente no encontrado",
            "Cuenta no encontrada"
        ]:
            return jsonify({
                "error": mensaje
            }), 404

        # Errores de validación o reglas de negocio
        return jsonify({
            "error": mensaje
        }), 400

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500



def listar_cobros_controller():
    """
    Controlador para consultar todos los cobros
    registrados en el sistema.
    """

    try:
        cobros = listar_cobros()

        return jsonify({
            "cobros": cobros
        }), 200

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500


def consultar_cobro_por_id_controller(id_cobro):
    """
    Controlador para consultar un cobro específico
    mediante su ID.
    """

    try:
        cobro = consultar_cobro_por_id(id_cobro)

        return jsonify({
            "cobro": cobro
        }), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cobro no encontrado":
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


def consultar_cobros_por_cliente_controller(id_cliente):
    """
    Controlador para consultar el historial
    de cobros de un cliente.
    """

    try:
        resultado = consultar_cobros_por_cliente(id_cliente)

        return jsonify(resultado), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cliente no encontrado":
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


def anular_cobro_controller(id_cobro):
    """
    Controlador para anular un cobro.

    La anulación revierte el dinero de la cuenta financiera
    y registra el movimiento financiero correspondiente.
    """

    try:
        # Obtener datos enviados en el body
        datos = request.get_json(silent=True)

        # Ejecutar lógica de negocio
        resultado = anular_cobro(
            id_cobro,
            datos
        )

        return jsonify({
            "message": "Cobro anulado correctamente",
            "cobro": resultado
        }), 200

    except ValueError as error:
        mensaje = str(error)

        # Recursos inexistentes
        if mensaje in [
            "Cobro no encontrado",
            "Cuenta no encontrada"
        ]:
            return jsonify({
                "error": mensaje
            }), 404

        # Errores de validación o reglas de negocio
        return jsonify({
            "error": mensaje
        }), 400

    except Exception as error:
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(error)
        }), 500


def consultar_saldo_cliente_controller(id_cliente):
    """
    Controlador para consultar el saldo financiero
    actual de un cliente.
    """

    try:
        resultado = consultar_saldo_cliente(id_cliente)

        return jsonify(resultado), 200

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Cliente no encontrado":
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