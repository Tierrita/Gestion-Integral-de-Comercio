
"""
Controlador de compras.

Responsabilidades:
- Recibir solicitudes HTTP.
- Obtener el comercio y usuario autenticados.
- Invocar la capa Service.
- Devolver respuestas JSON consistentes.
- Traducir errores de validación conocidos.

La lógica de negocio permanece en Service
y las operaciones transaccionales en PostgreSQL.
"""

from flask import jsonify, request, g
from postgrest.exceptions import APIError

from app.services.compra_service import (
    crear_compra,
    listar_compras,
    buscar_compra_por_id,
    anular_compra,
)


def _respuesta_error_rpc(error, mensaje_generico):
    """
    Traduce errores conocidos de validación PostgreSQL.

    Los errores inesperados no exponen información
    interna de la base de datos al cliente.
    """

    codigo = str(getattr(error, "code", "") or "")
    mensaje = str(getattr(error, "message", "") or "")

    # P0001: excepción de negocio generada por PL/pgSQL.
    # Solo se utiliza para las RPC de compras conocidas.
    if codigo == "P0001":
        return jsonify({
            "error": mensaje or "Operación rechazada"
        }), 400

    return jsonify({
        "error": mensaje_generico
    }), 500


# ==================================================
# REGISTRAR COMPRA
# ==================================================

def crear_compra_controller():
    try:
        datos = request.get_json(silent=True)

        resultado = crear_compra(
            datos,
            g.id_comercio,
            g.id_usuario,
        )

        return jsonify({
            "message": "Compra registrada correctamente",
            "compra": resultado["compra"],
            "detalles": resultado["detalles"],
            "productos_actualizados":
                resultado["productos_actualizados"],
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return _respuesta_error_rpc(
            error,
            "Error al registrar la compra",
        )


# ==================================================
# LISTAR COMPRAS
# ==================================================

def obtener_compras_controller():
    try:
        compras = listar_compras(g.id_comercio)

        return jsonify(compras), 200

    except APIError:
        return jsonify({
            "error": "Error al obtener las compras"
        }), 500


# ==================================================
# OBTENER COMPRA POR ID
# ==================================================

def obtener_compra_controller(id_compra):
    try:
        resultado = buscar_compra_por_id(
            id_compra,
            g.id_comercio,
        )

        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except APIError:
        return jsonify({
            "error": "Error al obtener la compra"
        }), 500


# ==================================================
# ANULAR COMPRA
# ==================================================

def anular_compra_controller(id_compra):
    try:
        resultado = anular_compra(
            id_compra,
            g.id_comercio,
            g.id_usuario,
        )

        return jsonify({
            "message": "Compra anulada correctamente",
            "resultado": resultado,
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:
        return _respuesta_error_rpc(
            error,
            "Error al anular la compra",
        )
