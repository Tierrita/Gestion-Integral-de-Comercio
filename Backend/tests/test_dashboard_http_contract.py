"""Regresión HTTP de controladores financieros sin credenciales ni escrituras.

Desde Backend:
python -m unittest discover -s tests -p 'test_dashboard_http_contract.py' -v

Prueba la capa Controller con request_context; NO reemplaza las pruebas
del Blueprint completo con JWT ni una prueba real contra Supabase.
"""
import unittest
from unittest.mock import patch
from flask import Flask, g

from app.controllers.finanza_controller import (
    obtener_dashboard_financiero_controller,
    obtener_cuentas_por_cobrar_actuales_controller,
)


class DashboardHttpContractTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True

    @patch("app.services.finanza_service.calcular_cuentas_por_cobrar_actuales")
    def test_deuda_actual_comercio_del_contexto(self, calcular):
        calcular.return_value = {
            "total_por_cobrar": 166666.67,
            "cantidad_clientes_con_deuda": 1,
        }
        with self.app.test_request_context("/finanzas/cuentas-por-cobrar/actual"):
            g.id_comercio = 3
            respuesta, estado = obtener_cuentas_por_cobrar_actuales_controller()
        self.assertEqual(estado, 200)
        self.assertEqual(respuesta.get_json()["total_por_cobrar"], 166666.67)
        calcular.assert_called_once_with(3)

    @patch("app.controllers.finanza_controller.calcular_dashboard_financiero")
    def test_dashboard_pasa_filtros_y_comercio_del_contexto(self, calcular):
        calcular.return_value = {
            "ventas": {"facturacion": 0},
            "clientes": {"total_por_cobrar": 12684199},
        }
        with self.app.test_request_context(
            "/finanzas/dashboard?desde=2026-10-01&hasta=2026-10-31"
        ):
            g.id_comercio = 1
            respuesta, estado = obtener_dashboard_financiero_controller()
        self.assertEqual(estado, 200)
        self.assertEqual(respuesta.get_json()["clientes"]["total_por_cobrar"], 12684199)
        calcular.assert_called_once_with(
            1, periodo=None, desde="2026-10-01", hasta="2026-10-31"
        )

    @patch("app.controllers.finanza_controller.calcular_dashboard_financiero")
    def test_dashboard_rango_invalido_retorna_400(self, calcular):
        calcular.side_effect = ValueError("Rango inválido")
        with self.app.test_request_context("/finanzas/dashboard?periodo=invalido"):
            g.id_comercio = 1
            respuesta, estado = obtener_dashboard_financiero_controller()
        self.assertEqual(estado, 400)
        self.assertIn("error", respuesta.get_json())

    @patch("app.services.finanza_service.calcular_cuentas_por_cobrar_actuales")
    def test_deuda_error_no_filtra_detalles_internos(self, calcular):
        calcular.side_effect = RuntimeError("clave interna de prueba")
        with self.app.test_request_context("/finanzas/cuentas-por-cobrar/actual"):
            g.id_comercio = 1
            respuesta, estado = obtener_cuentas_por_cobrar_actuales_controller()
        self.assertEqual(estado, 500)
        self.assertNotIn("clave interna", str(respuesta.get_json()))


if __name__ == "__main__":
    unittest.main()
