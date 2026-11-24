"""Pruebas unitarias de Clientes V2 (sin conectarse a Supabase).

Desde Backend: python -m unittest discover -s tests -p 'test_cliente_v2.py'
"""
import unittest
from unittest.mock import patch

from app.services import cliente_service as servicio


class ValidacionClientesV2Tests(unittest.TestCase):
    def test_compatibilidad_v1(self):
        self.assertEqual(
            servicio.validar_datos_cliente(
                {"nombre_completo": " Ana López ", "telefono": " "}, creacion=True
            ),
            {"nombre_completo": "Ana López", "telefono": None},
        )

    def test_campos_v2(self):
        datos = servicio.validar_datos_cliente(
            {"nombre_completo": " Mi Comercio ", "tipo_cliente": "comercio",
             "tipo_documento": "cuit", "numero_documento": "30-12345678-9",
             "email": " ADMIN@EJEMPLO.COM ", "direccion": "Calle 123"},
            creacion=True,
        )
        self.assertEqual(datos["tipo_cliente"], "COMERCIO")
        self.assertEqual(datos["tipo_documento"], "CUIT")
        self.assertEqual(datos["email"], "admin@ejemplo.com")

    def test_rechaza_campo_de_sistema(self):
        for campo in ("id_cliente", "id_comercio", "numero_cliente", "estado"):
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                servicio.validar_datos_cliente(
                    {"nombre_completo": "Cliente", campo: 999}, creacion=True
                )

    def test_rechaza_nombre_invalido(self):
        for nombre in (None, "", " ", "A", 123):
            with self.subTest(nombre=nombre), self.assertRaises(ValueError):
                servicio.validar_datos_cliente(
                    {"nombre_completo": nombre}, creacion=True
                )

    def test_rechaza_tipos_invalidos(self):
        for datos in (
            {"tipo_cliente": "INVENTADO"},
            {"tipo_cliente": None},
            {"tipo_documento": "ABC"},
            {"email": "no-es-email"},
        ):
            with self.subTest(datos=datos), self.assertRaises(ValueError):
                servicio.validar_datos_cliente(datos)

    def test_cliente_general_no_cambia_nombre(self):
        with self.assertRaisesRegex(ValueError, "CLIENTE GENERAL"):
            servicio.validar_datos_cliente(
                {"nombre_completo": "Otro"}, cliente_general=True
            )
        self.assertEqual(
            servicio.validar_datos_cliente(
                {"telefono": "2474"}, cliente_general=True
            ), {"telefono": "2474"}
        )

    @patch.object(servicio, "insertar_cliente")
    @patch.object(servicio, "obtener_siguiente_numero_cliente", return_value=8)
    def test_crear_usa_comercio_del_contexto(self, _numero, insertar):
        insertar.side_effect = lambda datos: datos
        cliente = servicio.crear_cliente(
            {"nombre_completo": "Cliente prueba", "tipo_cliente": "EMPRESA"}, 17
        )
        self.assertEqual(cliente["id_comercio"], 17)
        self.assertEqual(cliente["numero_cliente"], 8)
        self.assertIs(cliente["estado"], True)

    @patch.object(servicio, "actualizar_cliente")
    @patch.object(servicio, "obtener_cliente_por_id")
    def test_editar_preserva_filtro_comercio(self, obtener, actualizar):
        obtener.return_value = {"id_cliente": 4, "numero_cliente": 2}
        actualizar.side_effect = lambda _id, _comercio, datos: datos
        servicio.editar_cliente(4, {"email": "a@b.com"}, 17)
        obtener.assert_called_once_with(4, 17)
        actualizar.assert_called_once_with(4, 17, {"email": "a@b.com"})

    @patch.object(servicio, "obtener_cliente_por_id", return_value=None)
    def test_editar_cliente_ajeno_no_actualiza(self, _obtener):
        with patch.object(servicio, "actualizar_cliente") as actualizar:
            with self.assertRaisesRegex(ValueError, "no encontrado"):
                servicio.editar_cliente(99, {"telefono": "123"}, 17)
            actualizar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
