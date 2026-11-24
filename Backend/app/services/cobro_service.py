from decimal import Decimal, InvalidOperation
from collections import defaultdict

"""
Servicio de cobros.
Reglas de negocio, seguridad y aislamiento multicomercio.
"""

from app.models.cobro_model import (
    registrar_cobro_rpc,
    obtener_cobros,
    obtener_cobro_por_id,
    obtener_cobros_por_cliente,
    anular_cobro_rpc
)

from app.models.cliente_model import obtener_cliente_por_id
from app.models.venta_model import obtener_ventas_por_cliente
from app.models.cuenta_model import obtener_cuenta_por_id


def _entero_positivo(valor):
    return (
        isinstance(valor, int)
        and not isinstance(valor, bool)
        and valor > 0
    )


def registrar_cobro(datos, id_comercio, id_usuario):
    if not isinstance(datos, dict):
        raise ValueError("No se enviaron datos")

    id_cliente = datos.get("id_cliente")
    id_cuenta = datos.get("id_cuenta")
    monto = datos.get("monto")
    observaciones = datos.get("observaciones")

    if not _entero_positivo(id_cliente):
        raise ValueError(
            "El id_cliente debe ser un número entero mayor que cero"
        )

    if not _entero_positivo(id_cuenta):
        raise ValueError(
            "El id_cuenta debe ser un número entero mayor que cero"
        )

    # Validación exacta: evita NaN, infinitos, fracciones de centavo
    # y valores que excedan NUMERIC(12,2) en las cuentas.
    if isinstance(monto, bool) or not isinstance(monto, (int, float, str, Decimal)):
        raise ValueError("El monto debe ser numérico")
    try:
        importe = Decimal(str(monto))
    except InvalidOperation as exc:
        raise ValueError("El monto debe ser numérico") from exc
    if not importe.is_finite() or importe <= 0:
        raise ValueError("El monto debe ser finito y mayor que cero")
    if importe.as_tuple().exponent < -2:
        raise ValueError("El monto admite como máximo dos decimales")
    if importe > Decimal("9999999999.99"):
        raise ValueError("El monto excede el límite permitido")

    cliente = obtener_cliente_por_id(
        id_cliente,
        id_comercio
    )

    if not cliente:
        raise ValueError("Cliente no encontrado")

    if not cliente["estado"]:
        raise ValueError("El cliente se encuentra inactivo")

    cuenta = obtener_cuenta_por_id(
        id_cuenta,
        id_comercio
    )

    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    if not cuenta["estado"]:
        raise ValueError("La cuenta se encuentra inactiva")

    if observaciones is not None:
        if not isinstance(observaciones, str):
            raise ValueError(
                "Las observaciones deben ser texto"
            )

        observaciones = observaciones.strip() or None

    return registrar_cobro_rpc(
        id_cliente=id_cliente,
        id_cuenta=id_cuenta,
        id_usuario=id_usuario,
        id_comercio=id_comercio,
        monto=str(importe),
        observaciones=observaciones
    )


def listar_cobros(id_comercio):
    return obtener_cobros(id_comercio)


def consultar_cobro_por_id(id_cobro, id_comercio):
    cobros = obtener_cobro_por_id(
        id_cobro,
        id_comercio
    )

    if not cobros:
        raise ValueError("Cobro no encontrado")

    return cobros[0]


def consultar_cobros_por_cliente(
    id_cliente,
    id_comercio
):
    cliente = obtener_cliente_por_id(
        id_cliente,
        id_comercio
    )

    if not cliente:
        raise ValueError("Cliente no encontrado")

    cobros = obtener_cobros_por_cliente(
        id_cliente,
        id_comercio
    )

    return {
        "cliente": {
            "id_cliente": cliente["id_cliente"],
            "nombre_completo": cliente["nombre_completo"],
            "estado": cliente["estado"]
        },
        "cobros": cobros
    }


def anular_cobro(
    id_cobro,
    datos,
    id_comercio,
    id_usuario
):
    if not isinstance(datos, dict):
        raise ValueError("No se enviaron datos")

    motivo = datos.get("motivo_anulacion")

    if not isinstance(motivo, str):
        raise ValueError(
            "El motivo de anulación debe ser texto"
        )

    motivo = motivo.strip()

    if len(motivo) < 5:
        raise ValueError(
            "El motivo de anulación debe tener al menos 5 caracteres"
        )

    # Verificación previa multicomercio
    cobro = obtener_cobro_por_id(
        id_cobro,
        id_comercio
    )

    if not cobro:
        raise ValueError("Cobro no encontrado")

    return anular_cobro_rpc(
        id_cobro=id_cobro,
        id_usuario=id_usuario,
        id_comercio=id_comercio,
        motivo_anulacion=motivo
    )


def _calcular_saldo(ventas, cobros):
    total_ventas = sum((Decimal(str(v["total"])) for v in ventas
        if str(v.get("estado", "")).upper() != "ANULADA"
        and str(v.get("metodo_pago", "")).upper() == "CUENTA_CORRIENTE"), Decimal("0"))
    total_cobros = sum((Decimal(str(c["monto"])) for c in cobros
        if str(c.get("estado", "")).upper() == "COMPLETADO"), Decimal("0"))
    saldo = total_ventas - total_cobros
    return {"total_ventas": float(total_ventas), "total_cobros": float(total_cobros),
            "saldo": float(saldo), "situacion": "DEUDA" if saldo > 0 else "SALDO_A_FAVOR" if saldo < 0 else "AL_DIA"}


def listar_saldos_clientes(id_comercio):
    from app.models.cobro_model import obtener_cobros
    from app.models.venta_model import obtener_ventas
    from app.models.cliente_model import obtener_clientes
    ventas_por_cliente = defaultdict(list)
    cobros_por_cliente = defaultdict(list)
    for venta in obtener_ventas(id_comercio):
        ventas_por_cliente[venta["id_cliente"]].append(venta)
    for cobro in obtener_cobros(id_comercio):
        cobros_por_cliente[cobro["id_cliente"]].append(cobro)
    return [{"id_cliente": cliente["id_cliente"],
             **_calcular_saldo(ventas_por_cliente[cliente["id_cliente"]],
                              cobros_por_cliente[cliente["id_cliente"]])}
            for cliente in obtener_clientes(id_comercio)]


def consultar_saldo_cliente(
    id_cliente,
    id_comercio
):
    cliente = obtener_cliente_por_id(
        id_cliente,
        id_comercio
    )

    if not cliente:
        raise ValueError("Cliente no encontrado")

    ventas = obtener_ventas_por_cliente(
        id_cliente,
        id_comercio
    )

    cobros = obtener_cobros_por_cliente(
        id_cliente,
        id_comercio
    )

    return {"cliente": {"id_cliente": cliente["id_cliente"],
                        "nombre_completo": cliente["nombre_completo"],
                        "estado": cliente["estado"]},
            **_calcular_saldo(ventas, cobros)}
