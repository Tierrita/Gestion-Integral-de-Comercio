"""Pruebas HTTP de rutas financieras con JWT real y servicios simulados.

Desde Backend:
python -m unittest discover -s tests -p 'test_finanzas_jwt_http.py' -v

No utiliza Supabase ni escribe datos.
"""
import unittest
from unittest.mock import patch

from flask import Flask

from app.routes.finanza_routes import finanza_bp
from core.auth import generar_token


class FinanzasJwtHttpTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(TESTING=True, JWT_SECRET_KEY="clave-de-pruebas-segura-de-mas-de-32-bytes-solo-test")
        self.app.register_blueprint(finanza_bp)
        self.client = self.app.test_client()

    def _usuario(self, comercio=1, propietario=True, activo=True):
        return {
            "id_usuario": 27,
            "id_comercio": comercio,
            "id_rol": None,
            "es_propietario": propietario,
            "estado": activo,
            "password": "hash-de-prueba",
        }

    def _headers(self, usuario):
        with self.app.app_context():
            token = generar_token(usuario)
        return {"Authorization": f"Bearer {token}"}

    def _mock_identidad(self, usuario, comercio_activo=True):
        return (
            patch("core.auth.obtener_usuario_por_id", return_value=usuario),
            patch("core.auth.obtener_comercio_usuario",
                  return_value={"id_comercio": usuario["id_comercio"],
                                "estado": comercio_activo}),
        )

    def test_sin_token_rechazado_en_ambas_rutas(self):
        for ruta in ("/finanzas/dashboard", "/finanzas/cuentas-por-cobrar/actual"):
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(ruta).status_code, 401)

    def test_token_invalido_rechazado(self):
        respuesta = self.client.get(
            "/finanzas/dashboard", headers={"Authorization": "Bearer no-es-jwt"}
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_empleado_no_puede_consultar_finanzas(self):
        usuario = self._usuario(propietario=False)
        identidad, comercio = self._mock_identidad(usuario)
        with identidad, comercio:
            for ruta in ("/finanzas/dashboard", "/finanzas/cuentas-por-cobrar/actual"):
                with self.subTest(ruta=ruta):
                    self.assertEqual(
                        self.client.get(ruta, headers=self._headers(usuario)).status_code,
                        403,
                    )

    def test_usuario_inactivo_no_puede_consultar(self):
        usuario = self._usuario(activo=False)
        identidad, comercio = self._mock_identidad(usuario)
        with identidad, comercio:
            respuesta = self.client.get(
                "/finanzas/dashboard", headers=self._headers(usuario)
            )
        self.assertEqual(respuesta.status_code, 403)

    def test_comercio_inactivo_no_puede_consultar(self):
        usuario = self._usuario()
        identidad, comercio = self._mock_identidad(usuario, comercio_activo=False)
        with identidad, comercio:
            respuesta = self.client.get(
                "/finanzas/dashboard", headers=self._headers(usuario)
            )
        self.assertEqual(respuesta.status_code, 403)

    def test_dashboard_usa_comercio_autenticado_no_querystring(self):
        usuario = self._usuario(comercio=3)
        identidad, comercio = self._mock_identidad(usuario)
        with identidad, comercio, patch(
            "app.controllers.finanza_controller.calcular_dashboard_financiero",
            return_value={"clientes": {"total_por_cobrar": 123}},
        ) as calcular:
            respuesta = self.client.get(
                "/finanzas/dashboard?periodo=mes&id_comercio=1",
                headers=self._headers(usuario),
            )
        self.assertEqual(respuesta.status_code, 200)
        calcular.assert_called_once_with(
            3, periodo="mes", desde=None, hasta=None
        )

    def test_deuda_actual_usa_comercio_autenticado_no_querystring(self):
        usuario = self._usuario(comercio=3)
        identidad, comercio = self._mock_identidad(usuario)
        with identidad, comercio, patch(
            "app.services.finanza_service.calcular_cuentas_por_cobrar_actuales",
            return_value={"total_por_cobrar": 166666.67,
                          "cantidad_clientes_con_deuda": 1},
        ) as calcular:
            respuesta = self.client.get(
                "/finanzas/cuentas-por-cobrar/actual?id_comercio=1",
                headers=self._headers(usuario),
            )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json()["total_por_cobrar"], 166666.67)
        calcular.assert_called_once_with(3)

    def test_token_anterior_a_cambio_de_password_es_rechazado(self):
        anterior = self._usuario()
        actual = dict(anterior, password="hash-nuevo")
        identidad, comercio = self._mock_identidad(actual)
        with identidad, comercio:
            respuesta = self.client.get(
                "/finanzas/dashboard", headers=self._headers(anterior)
            )
        self.assertEqual(respuesta.status_code, 401)


if __name__ == "__main__":
    unittest.main()
