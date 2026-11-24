"""Pruebas unitarias de reglas financieras V2 sin conexión a Supabase."""
import unittest
from unittest.mock import patch

from app.services.cobro_service import _calcular_saldo, registrar_cobro
from app.services.pago_proveedor_service import (
    registrar_pago_proveedor, consultar_saldo_proveedor, anular_pago_proveedor,
)

MODULO = "app.services.pago_proveedor_service"


class TestCobrosPagosV2(unittest.TestCase):
    def test_cobros_solo_ventas_a_credito(self):
        saldo = _calcular_saldo(
            [{"total": 100, "estado": "COMPLETADA", "metodo_pago": "CUENTA_CORRIENTE"},
             {"total": 50, "estado": "COMPLETADA", "metodo_pago": "EFECTIVO"},
             {"total": 40, "estado": "ANULADA", "metodo_pago": "CUENTA_CORRIENTE"}],
            [{"monto": 30, "estado": "COMPLETADO"},
             {"monto": 20, "estado": "ANULADO"}],
        )
        self.assertEqual(saldo["saldo"], 70)
        self.assertEqual(saldo["situacion"], "DEUDA")

    def test_anticipo_cliente_es_saldo_a_favor(self):
        saldo = _calcular_saldo([], [{"monto": 25, "estado": "COMPLETADO"}])
        self.assertEqual(saldo["saldo"], -25)
        self.assertEqual(saldo["situacion"], "SALDO_A_FAVOR")

    @patch("app.services.cobro_service.registrar_cobro_rpc")
    @patch("app.services.cobro_service.obtener_cuenta_por_id")
    @patch("app.services.cobro_service.obtener_cliente_por_id")
    def test_cobro_valida_precision_y_limite(self, cliente, cuenta, rpc):
        cliente.return_value = {"estado": True}
        cuenta.return_value = {"estado": True}
        for monto in [0, -1, True, "NaN", "Infinity", "12.345", "10000000000.00", "abc"]:
            with self.subTest(monto=monto), self.assertRaises(ValueError):
                registrar_cobro({"id_cliente": 1, "id_cuenta": 2, "monto": monto}, 1, 3)
        rpc.assert_not_called()

    @patch("app.services.cobro_service.registrar_cobro_rpc")
    @patch("app.services.cobro_service.obtener_cuenta_por_id")
    @patch("app.services.cobro_service.obtener_cliente_por_id")
    def test_cobro_envia_importe_decimal_exacto(self, cliente, cuenta, rpc):
        cliente.return_value = {"estado": True}
        cuenta.return_value = {"estado": True}
        rpc.return_value = {"estado": "COMPLETADO"}
        registrar_cobro({"id_cliente": 1, "id_cuenta": 2, "monto": "15.25"}, 1, 3)
        self.assertEqual(rpc.call_args.kwargs["monto"], "15.25")

    @patch(f"{MODULO}.insertar_pago_proveedor")
    @patch(f"{MODULO}.obtener_proveedor_por_id")
    def test_pago_no_incluye_cuenta_financiera(self, proveedor, insertar):
        proveedor.return_value = {"id_proveedor": 7, "estado": True}
        insertar.side_effect = lambda datos: datos
        pago = registrar_pago_proveedor(
            {"id_proveedor": 7, "monto": "50.25", "observaciones": "Pago parcial"},
            id_usuario=2, id_comercio=1,
        )
        self.assertEqual(pago["monto"], "50.25")
        self.assertNotIn("id_cuenta", pago)
        self.assertNotIn("id_comercio", pago)

    @patch(f"{MODULO}.insertar_pago_proveedor")
    @patch(f"{MODULO}.obtener_proveedor_por_id")
    def test_pago_rechaza_importes_invalidos(self, proveedor, insertar):
        proveedor.return_value = {"id_proveedor": 7, "estado": True}
        for monto in [-1, 0, "NaN", "Infinity", "12.345", "10000000000.00", True]:
            with self.subTest(monto=monto), self.assertRaises(ValueError):
                registrar_pago_proveedor({"id_proveedor": 7, "monto": monto}, 2, 1)
        insertar.assert_not_called()

    @patch(f"{MODULO}.obtener_pagos_por_proveedor")
    @patch(f"{MODULO}.obtener_compras_proveedor")
    @patch(f"{MODULO}.obtener_proveedor_por_id")
    def test_saldo_proveedor_ignora_pagos_anulados(self, proveedor, compras, pagos):
        proveedor.return_value = {"id_proveedor": 7, "numero_proveedor": 3, "nombre_proveedor": "Prueba"}
        compras.return_value = [{"total_compra": 150, "estado": "COMPLETADA"}]
        pagos.return_value = [{"monto": 50, "estado": "COMPLETADO"},
                              {"monto": 20, "estado": "ANULADO"}]
        saldo = consultar_saldo_proveedor(7, 1)
        self.assertEqual(saldo["saldo"], 100)
        self.assertEqual(saldo["situacion"], "DEUDA")

    @patch(f"{MODULO}.actualizar_pago_proveedor")
    @patch(f"{MODULO}.obtener_pago_proveedor_por_id")
    def test_anulacion_pago_no_toca_cuentas(self, obtener, actualizar):
        obtener.return_value = {"id_pago": 8, "estado": "COMPLETADO"}
        actualizar.side_effect = lambda _id, _comercio, datos: datos
        resultado = anular_pago_proveedor(8, {"motivo_anulacion": "Duplicado"}, 2, 1)
        self.assertEqual(resultado["estado"], "ANULADO")
        self.assertEqual(resultado["motivo_anulacion"], "Duplicado")
        self.assertNotIn("id_cuenta", resultado)


if __name__ == "__main__":
    unittest.main()
