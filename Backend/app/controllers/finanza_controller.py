"""
Controlador de finanzas multicomercio.

Recibe las solicitudes HTTP relacionadas con el módulo
financiero y devuelve las respuestas JSON.

El comercio se obtiene exclusivamente del usuario
autenticado mediante JWT.

Controller → Service
"""

from flask import jsonify, request, g

from app.services.finanza_service import (
    calcular_rentabilidad,
    calcular_caja,
    calcular_estadisticas_ventas,
    calcular_evolucion_ventas,
    calcular_estadisticas_productos,
    calcular_estadisticas_proveedores,
    calcular_estadisticas_clientes,
    calcular_estadisticas_stock,
    calcular_dashboard_financiero
)


# ======================================================
# RENTABILIDAD
# ======================================================

def obtener_rentabilidad():
    """
    Obtiene los indicadores de rentabilidad
    del comercio autenticado.
    """

    try:
        periodo = request.args.get("periodo")
        desde = request.args.get("desde")
        hasta = request.args.get("hasta")

        rentabilidad = calcular_rentabilidad(
            g.id_comercio,
            periodo=periodo,
            desde=desde,
            hasta=hasta
        )

        return jsonify({
            "message": "Rentabilidad obtenida correctamente",
            "rentabilidad": rentabilidad
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


# ======================================================
# CAJA
# ======================================================

def obtener_caja():
    """
    Obtiene los indicadores de caja
    del comercio autenticado.
    """

    try:
        periodo = request.args.get("periodo")
        desde = request.args.get("desde")
        hasta = request.args.get("hasta")

        caja = calcular_caja(
            g.id_comercio,
            periodo=periodo,
            desde=desde,
            hasta=hasta
        )

        return jsonify({
            "message": "Caja obtenida correctamente",
            "caja": caja
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


# ======================================================
# ESTADÍSTICAS DE VENTAS
# ======================================================

def obtener_estadisticas_ventas():
    """
    Obtiene las estadísticas generales de ventas
    del comercio autenticado.
    """

    try:
        periodo = request.args.get("periodo")
        desde = request.args.get("desde")
        hasta = request.args.get("hasta")

        ventas = calcular_estadisticas_ventas(
            g.id_comercio,
            periodo=periodo,
            desde=desde,
            hasta=hasta
        )

        return jsonify({
            "message": "Estadísticas de ventas obtenidas correctamente",
            "ventas": ventas
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


# ======================================================
# EVOLUCIÓN DE VENTAS
# ======================================================

def obtener_evolucion_ventas():
    """
    Obtiene la evolución de ventas
    del comercio autenticado.
    """

    try:
        periodo = request.args.get("periodo")
        desde = request.args.get("desde")
        hasta = request.args.get("hasta")

        evolucion = calcular_evolucion_ventas(
            g.id_comercio,
            periodo=periodo,
            desde=desde,
            hasta=hasta
        )

        return jsonify({
            "message": "Evolución de ventas obtenida correctamente",
            "ventas": evolucion
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


# ======================================================
# ESTADÍSTICAS DE PRODUCTOS
# ======================================================

def obtener_estadisticas_productos():
    """
    Obtiene las estadísticas y rankings de productos
    del comercio autenticado.
    """

    try:
        periodo = request.args.get("periodo")
        desde = request.args.get("desde")
        hasta = request.args.get("hasta")

        productos = calcular_estadisticas_productos(
            g.id_comercio,
            periodo=periodo,
            desde=desde,
            hasta=hasta
        )

        return jsonify({
            "message": "Estadísticas de productos obtenidas correctamente",
            "productos": productos
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


# ======================================================
# ESTADÍSTICAS DE PROVEEDORES
# ======================================================

def obtener_estadisticas_proveedores():
    """
    Obtiene las estadísticas y ranking de proveedores
    del comercio autenticado.
    """

    try:
        periodo = request.args.get("periodo")
        desde = request.args.get("desde")
        hasta = request.args.get("hasta")

        proveedores = calcular_estadisticas_proveedores(
            g.id_comercio,
            periodo=periodo,
            desde=desde,
            hasta=hasta
        )

        return jsonify({
            "message": "Estadísticas de proveedores obtenidas correctamente",
            "proveedores": proveedores
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


# ======================================================
# ESTADÍSTICAS DE CLIENTES
# ======================================================

def obtener_estadisticas_clientes():
    """
    Obtiene las estadísticas comerciales de los clientes
    del comercio autenticado.
    """

    try:
        periodo = request.args.get("periodo")
        desde = request.args.get("desde")
        hasta = request.args.get("hasta")

        clientes = calcular_estadisticas_clientes(
            g.id_comercio,
            periodo=periodo,
            desde=desde,
            hasta=hasta
        )

        return jsonify({
            "message": "Estadísticas de clientes obtenidas correctamente",
            "clientes": clientes
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


# ======================================================
# STOCK FINANCIERO
# ======================================================

def obtener_estadisticas_stock_controller():
    """
    Obtiene la valorización financiera del stock
    del comercio autenticado.
    """

    try:
        periodo = request.args.get("periodo")
        desde = request.args.get("desde")
        hasta = request.args.get("hasta")

        resultado = calcular_estadisticas_stock(
            g.id_comercio,
            periodo=periodo,
            desde=desde,
            hasta=hasta
        )

        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


# ======================================================
# DASHBOARD FINANCIERO
# ======================================================

def obtener_dashboard_financiero_controller():
    """
    Obtiene el dashboard financiero
    del comercio autenticado.
    """

    try:
        periodo = request.args.get("periodo")
        desde = request.args.get("desde")
        hasta = request.args.get("hasta")

        resultado = calcular_dashboard_financiero(
            g.id_comercio,
            periodo=periodo,
            desde=desde,
            hasta=hasta
        )

        return jsonify(resultado), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500