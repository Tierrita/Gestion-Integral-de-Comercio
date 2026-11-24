"""Prueba real de doble anulacion concurrente por HTTP. Solo base de PRUEBAS.

Ejecutar desde Backend con Flask activo:
 python3 tests/test_concurrencia_financiera_v2_http.py --cliente 1 --cuenta 1 --proveedor 1
Se solicita JWT del propietario sin mostrarlo ni guardarlo.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from getpass import getpass
import json
from threading import Barrier
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4


def dinero(valor):
    return Decimal(str(valor))


def main():
    parser = argparse.ArgumentParser(description="Prueba concurrente de cobros y pagos V2")
    parser.add_argument("--url", default="http://127.0.0.1:5001/api")
    parser.add_argument("--cliente", type=int, required=True)
    parser.add_argument("--cuenta", type=int, required=True)
    parser.add_argument("--proveedor", type=int, required=True)
    args = parser.parse_args()
    token = getpass("JWT del propietario (no se muestra): ").strip()
    if not token:
        parser.error("Se necesita JWT del propietario")
    base = args.url.rstrip("/")
    marca = "TEST-CONCURRENCIA-" + uuid4().hex[:10]

    def llamar(metodo, ruta, datos=None):
        body = json.dumps(datos).encode() if datos is not None else None
        req = Request(base + ruta, data=body, method=metodo, headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        })
        try:
            with urlopen(req, timeout=25) as respuesta:
                return respuesta.status, json.loads(respuesta.read())
        except HTTPError as error:
            try:
                payload = json.loads(error.read())
            except ValueError:
                payload = {"error": "Respuesta no JSON"}
            return error.code, payload

    def obtener(ruta):
        status, payload = llamar("GET", ruta)
        if status != 200:
            raise RuntimeError(f"GET {ruta}: HTTP {status}: {payload}")
        return payload

    def competir(ruta):
        barrera = Barrier(2)
        def intento(numero):
            barrera.wait(timeout=10)
            return llamar("PATCH", ruta, {"motivo_anulacion": f"Prueba simultanea {numero} - {marca}"})
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(intento, i) for i in (1, 2)]
            resultados = [f.result() for f in futures]
        print("  Respuestas:", [(codigo, p.get("error", p.get("message"))) for codigo, p in resultados])
        if sum(codigo == 200 for codigo, _ in resultados) != 1:
            raise AssertionError("Debe haber exactamente una anulacion exitosa")
        if sum(codigo in (400, 404, 409) for codigo, _ in resultados) != 1:
            raise AssertionError("La segunda anulacion debe rechazarse como operacion invalida")

    cuenta = obtener(f"/cuentas/{args.cuenta}")["cuenta"]
    saldo_inicial = dinero(cuenta["saldo"])
    print("Prueba:", marca)
    print("Saldo inicial:", saldo_inicial)
    status, respuesta = llamar("POST", "/cobros", {
        "id_cliente": args.cliente, "id_cuenta": args.cuenta,
        "monto": "15.25", "observaciones": marca,
    })
    if status != 201:
        raise RuntimeError(f"No se pudo crear cobro: {status} {respuesta}")
    id_cobro = int(respuesta["cobro"]["id_cobro"])
    print("Cobro creado:", id_cobro)
    try:
        assert dinero(obtener(f"/cuentas/{args.cuenta}")["cuenta"]["saldo"]) == saldo_inicial + Decimal("15.25"), "Cobro no sumo exactamente 15.25"
        competir(f"/cobros/{id_cobro}/anular")
        assert dinero(obtener(f"/cuentas/{args.cuenta}")["cuenta"]["saldo"]) == saldo_inicial, "Saldo incorrecto tras concurrencia"
        movimientos = obtener(f"/cuentas/{args.cuenta}/movimientos")["movimientos"]
        relacionados = [m for m in movimientos if str(m.get("tipo_origen")) == "COBRO" and str(m.get("id_origen")) == str(id_cobro)]
        assert sum(m.get("tipo_movimiento") == "COBRO" for m in relacionados) == 1, "Cobro duplicado en movimientos"
        assert sum(m.get("tipo_movimiento") == "ANULACION_COBRO" for m in relacionados) == 1, "Reversion duplicada o ausente"
        print("APROBADO: cobro, concurrencia, movimientos y saldo")
    except Exception:
        print(f"ATENCION: revisar cobro #{id_cobro}; puede quedar sin anular")
        raise

    saldo_proveedor_antes = dinero(obtener(f"/proveedores/{args.proveedor}/saldo")["saldo"])
    status, respuesta = llamar("POST", "/pagos-proveedor", {
        "id_proveedor": args.proveedor, "monto": "15.25", "observaciones": marca,
    })
    if status != 201:
        raise RuntimeError(f"No se pudo crear pago: {status} {respuesta}")
    id_pago = int(respuesta["pago"]["id_pago"])
    print("Pago creado:", id_pago)
    try:
        assert dinero(obtener(f"/proveedores/{args.proveedor}/saldo")["saldo"]) == saldo_proveedor_antes - Decimal("15.25"), "Pago no redujo deuda"
        competir(f"/pagos-proveedor/{id_pago}/anular")
        assert dinero(obtener(f"/proveedores/{args.proveedor}/saldo")["saldo"]) == saldo_proveedor_antes, "Deuda incorrecta tras concurrencia"
        assert dinero(obtener(f"/cuentas/{args.cuenta}")["cuenta"]["saldo"]) == saldo_inicial, "Pago altero la caja"
        movimientos_despues = obtener(f"/cuentas/{args.cuenta}/movimientos")["movimientos"]
        assert sum(m.get("tipo_movimiento") == "ANULACION_COBRO" and str(m.get("id_origen")) == str(id_cobro) for m in movimientos_despues) == 1
        print("APROBADO: pago, concurrencia, deuda y caja intacta")
    except Exception:
        print(f"ATENCION: revisar pago #{id_pago}; puede quedar sin anular")
        raise
    print("RESULTADO FINAL: CONCURRENCIA V2 APROBADA")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, RuntimeError, HTTPError, URLError, TimeoutError) as error:
        raise SystemExit("PRUEBA FALLIDA: " + str(error))
