"""Pruebas unitarias del adaptador RPC. Ejecutar desde Backend:
python -m unittest discover -s tests -p 'test_dashboard_rpc_model.py'
"""
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.models.dashboard_rpc_model import obtener_dashboard_rpc


class DashboardRpcModelTests(unittest.TestCase):
    def setUp(self):
        self.desde = datetime(2026, 11, 1, tzinfo=timezone.utc)
        self.hasta = datetime(2026, 12, 1, tzinfo=timezone.utc)

    @patch("app.models.dashboard_rpc_model.get_client")
    def test_envia_comercio_y_fechas_a_rpc(self, get_client):
        cliente = MagicMock()
        cliente.rpc.return_value.execute.return_value = SimpleNamespace(
            data={"ventas": {"facturacion": 123}}
        )
        get_client.return_value = cliente

        resultado = obtener_dashboard_rpc(3, self.desde, self.hasta)

        self.assertEqual(resultado["ventas"]["facturacion"], 123)
        cliente.rpc.assert_called_once_with(
            "obtener_dashboard_estadisticas",
            {
                "p_id_comercio": 3,
                "p_desde": self.desde.isoformat(),
                "p_hasta": self.hasta.isoformat(),
            },
        )

    @patch("app.models.dashboard_rpc_model.get_client")
    def test_rechaza_comercio_invalido_sin_consultar(self, get_client):
        for comercio in (None, 0, -1, True, "3"):
            with self.subTest(comercio=comercio):
                with self.assertRaises(ValueError):
                    obtener_dashboard_rpc(comercio, self.desde, self.hasta)
        get_client.assert_not_called()

    @patch("app.models.dashboard_rpc_model.get_client")
    def test_rechaza_fechas_invertidas(self, get_client):
        with self.assertRaises(ValueError):
            obtener_dashboard_rpc(1, self.hasta, self.desde)
        get_client.assert_not_called()

    @patch("app.models.dashboard_rpc_model.get_client")
    def test_rechaza_respuesta_inesperada(self, get_client):
        get_client.return_value.rpc.return_value.execute.return_value = (
            SimpleNamespace(data=[])
        )
        with self.assertRaises(RuntimeError):
            obtener_dashboard_rpc(1, self.desde, self.hasta)


if __name__ == "__main__":
    unittest.main()
