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

    if (
        not isinstance(monto, (int, float))
        or isinstance(monto, bool)
        or monto <= 0
    ):
        raise ValueError("El monto debe ser mayor que cero")

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
        monto=monto,
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

    total_ventas = sum(
        float(venta["total"])
        for venta in ventas
        if venta["estado"].upper() != "ANULADA"
    )

    total_cobros = sum(
        float(cobro["monto"])
        for cobro in cobros
        if cobro["estado"].upper() == "COMPLETADO"
    )

    saldo = total_ventas - total_cobros

    if saldo > 0:
        situacion = "DEUDA"
    elif saldo < 0:
        situacion = "SALDO_A_FAVOR"
    else:
        situacion = "AL_DIA"

    return {
        "cliente": {
            "id_cliente": cliente["id_cliente"],
            "nombre_completo": cliente["nombre_completo"],
            "estado": cliente["estado"]
        },
        "total_ventas": total_ventas,
        "total_cobros": total_cobros,
        "saldo": saldo,
        "situacion": situacion
    }