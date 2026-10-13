"""
Rutas de finanzas.

Define los endpoints relacionados con el módulo financiero.

Route → Controller
"""

from flask import Blueprint

from app.controllers.finanza_controller import (
    obtener_rentabilidad,
    obtener_caja,
    obtener_estadisticas_ventas,
    obtener_evolucion_ventas,
    obtener_estadisticas_productos,
    obtener_estadisticas_proveedores,
    obtener_estadisticas_clientes,
    obtener_estadisticas_stock_controller,
    obtener_dashboard_financiero_controller
)


finanza_bp = Blueprint(
    "finanza",
    __name__,
    url_prefix="/finanzas"
)


# ======================================================
# RENTABILIDAD
# ======================================================

@finanza_bp.route("/rentabilidad", methods=["GET"])
def rentabilidad():
    """
    Obtiene los indicadores generales de rentabilidad.
    """
    return obtener_rentabilidad()


# ======================================================
# CAJA
# ======================================================

@finanza_bp.route("/caja", methods=["GET"])
def caja():
    """
    Obtiene los movimientos e indicadores de caja.
    """
    return obtener_caja()


# ======================================================
# ESTADÍSTICAS DE VENTAS
# ======================================================

@finanza_bp.route("/ventas", methods=["GET"])
def ventas():
    """
    Obtiene las estadísticas generales de ventas.
    """
    return obtener_estadisticas_ventas()

# ======================================================
# EVOLUCIÓN DE VENTAS
# ======================================================

@finanza_bp.route("/ventas/evolucion", methods=["GET"])
def evolucion_ventas():
    """
    Obtiene la evolución de las ventas.
    """
    return obtener_evolucion_ventas()


# ======================================================
# ESTADÍSTICAS DE PRODUCTOS
# ======================================================

@finanza_bp.route("/productos", methods=["GET"])
def productos():
    """
    Obtiene las estadísticas y rankings de productos.
    """
    return obtener_estadisticas_productos()


# ======================================================
# ESTADÍSTICAS DE PROVEEDORES
# ======================================================

@finanza_bp.route("/proveedores", methods=["GET"])
def proveedores():
    """
    Obtiene las estadísticas y ranking de proveedores.
    """
    return obtener_estadisticas_proveedores()



# ======================================================
# CLIENTES
# ======================================================

@finanza_bp.route("/clientes", methods=["GET"])
def clientes():
    return obtener_estadisticas_clientes()



# ======================================================
# STOCK FINANCIERO
# ======================================================

@finanza_bp.route("/stock", methods=["GET"])
def obtener_estadisticas_stock():
    """
    Obtiene la valorización financiera del stock actual.
    """

    return obtener_estadisticas_stock_controller()


# ======================================================
# DASHBOARD FINANCIERO
# ======================================================

@finanza_bp.route("/dashboard", methods=["GET"])
def obtener_dashboard_financiero():
    """
    Obtiene el resumen principal del módulo financiero.
    """
    return obtener_dashboard_financiero_controller()