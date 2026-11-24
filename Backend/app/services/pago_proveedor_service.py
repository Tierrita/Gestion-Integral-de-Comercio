"""
Servicio de pagos a proveedores.

Contiene la lógica de negocio y garantiza
el aislamiento multicomercio.
"""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from app.models.pago_proveedor_model import (
    insertar_pago_proveedor,
    obtener_pagos_proveedor,
    obtener_pago_proveedor_por_id,
    obtener_pagos_por_proveedor,
    actualizar_pago_proveedor,
    obtener_compras_proveedor
)

from app.models.proveedor_model import (
    obtener_proveedor_por_id
)


def registrar_pago_proveedor(
    datos,
    id_usuario,
    id_comercio
):
    if not isinstance(datos, dict) or not datos:
        raise ValueError(
            "No se enviaron datos del pago"
        )

    if "id_proveedor" not in datos:
        raise ValueError(
            "El campo 'id_proveedor' es obligatorio"
        )

    if "monto" not in datos:
        raise ValueError(
            "El campo 'monto' es obligatorio"
        )

    id_proveedor = datos["id_proveedor"]

    if (
        isinstance(id_proveedor, bool)
        or not isinstance(id_proveedor, int)
    ):
        raise ValueError(
            "El id_proveedor debe ser un número entero"
        )

    if id_proveedor <= 0:
        raise ValueError(
            "El id_proveedor debe ser mayor que cero"
        )

    proveedor = obtener_proveedor_por_id(
        id_proveedor,
        id_comercio
    )

    if not proveedor:
        raise ValueError(
            "Proveedor no encontrado"
        )

    if proveedor.get("estado") is False:
        raise ValueError(
            "No se puede registrar un pago a un proveedor inactivo"
        )

    monto = datos["monto"]

    if isinstance(monto, bool) or not isinstance(monto, (int, float, str, Decimal)):
        raise ValueError("El monto debe ser numérico")
    try:
        monto = Decimal(str(monto))
    except InvalidOperation as exc:
        raise ValueError("El monto debe ser numérico") from exc
    if not monto.is_finite() or monto <= 0:
        raise ValueError("El monto debe ser finito y mayor a cero")
    if monto.as_tuple().exponent < -2:
        raise ValueError("El monto admite como máximo dos decimales")
    if monto > Decimal("9999999999.99"):
        raise ValueError("El monto excede el límite permitido")

    observaciones = datos.get("observaciones")

    if observaciones is not None:
        if not isinstance(observaciones, str):
            raise ValueError(
                "Las observaciones deben ser texto"
            )

        observaciones = observaciones.strip() or None

    datos_pago = {
        "id_proveedor": id_proveedor,
        "id_usuario": id_usuario,
        "monto": str(monto),
        "estado": "COMPLETADO",
        "observaciones": observaciones
    }

    pago = insertar_pago_proveedor(
        datos_pago
    )

    if not pago:
        raise ValueError(
            "No se pudo registrar el pago"
        )

    return pago


def listar_pagos_proveedor(id_comercio):
    return obtener_pagos_proveedor(
        id_comercio
    )


def consultar_pago_proveedor_por_id(
    id_pago,
    id_comercio
):
    pago = obtener_pago_proveedor_por_id(
        id_pago,
        id_comercio
    )

    if not pago:
        raise ValueError(
            "Pago no encontrado"
        )

    return pago


def consultar_pagos_por_proveedor(
    id_proveedor,
    id_comercio
):
    proveedor = obtener_proveedor_por_id(
        id_proveedor,
        id_comercio
    )

    if not proveedor:
        raise ValueError(
            "Proveedor no encontrado"
        )

    pagos = obtener_pagos_por_proveedor(
        id_proveedor,
        id_comercio
    )

    return pagos or []


def anular_pago_proveedor(
    id_pago,
    datos,
    id_usuario,
    id_comercio
):
    if not datos:
        raise ValueError(
            "No se enviaron datos para la anulación"
        )

    pago = obtener_pago_proveedor_por_id(
        id_pago,
        id_comercio
    )

    if not pago:
        raise ValueError(
            "Pago no encontrado"
        )

    if pago["estado"].upper() == "ANULADO":
        raise ValueError(
            "El pago ya se encuentra anulado"
        )

    motivo = datos.get("motivo_anulacion")

    if motivo is None:
        raise ValueError(
            "El campo 'motivo_anulacion' es obligatorio"
        )

    if not isinstance(motivo, str):
        raise ValueError(
            "El motivo de anulación debe ser texto"
        )

    motivo = motivo.strip()

    if len(motivo) < 5:
        raise ValueError(
            "El motivo de anulación debe tener al menos 5 caracteres"
        )

    datos_actualizacion = {
        "estado": "ANULADO",
        "id_usuario_anulacion": id_usuario,
        "fecha_anulacion": datetime.now(
            timezone.utc
        ).isoformat(),
        "motivo_anulacion": motivo
    }

    pago_actualizado = actualizar_pago_proveedor(
        id_pago,
        id_comercio,
        datos_actualizacion
    )

    if not pago_actualizado:
        raise ValueError(
            "No se pudo anular el pago"
        )

    return pago_actualizado


def consultar_saldo_proveedor(
    id_proveedor,
    id_comercio
):
    proveedor = obtener_proveedor_por_id(
        id_proveedor,
        id_comercio
    )

    if not proveedor:
        raise ValueError(
            "Proveedor no encontrado"
        )

    compras = obtener_compras_proveedor(
        id_proveedor,
        id_comercio
    )

    pagos = obtener_pagos_por_proveedor(
        id_proveedor,
        id_comercio
    ) or []

    total_compras = sum(
        (Decimal(str(compra["total_compra"])) for compra in compras
         if str(compra["estado"]).upper() == "COMPLETADA"), Decimal("0")
    )

    total_pagos = sum(
        (Decimal(str(pago["monto"])) for pago in pagos
         if str(pago["estado"]).upper() == "COMPLETADO"), Decimal("0")
    )

    saldo = total_compras - total_pagos

    if saldo > 0:
        situacion = "DEUDA"
    elif saldo < 0:
        situacion = "SALDO_A_FAVOR"
    else:
        situacion = "AL_DIA"

    return {
        "proveedor": {
            "id_proveedor": proveedor["id_proveedor"],
            "numero_proveedor": proveedor["numero_proveedor"],
            "nombre_proveedor": proveedor["nombre_proveedor"]
        },
        "total_compras": float(total_compras),
        "total_pagos": float(total_pagos),
        "saldo": float(saldo),
        "situacion": situacion
    }

def listar_saldos_proveedores(id_comercio):
    """Devuelve un saldo por proveedor sin afectar las cuentas financieras."""
    from collections import defaultdict
    from app.models.proveedor_model import obtener_proveedores
    from app.models.pago_proveedor_model import obtener_compras_comercio

    compras_por_proveedor = defaultdict(lambda: Decimal("0"))
    pagos_por_proveedor = defaultdict(lambda: Decimal("0"))
    for compra in obtener_compras_comercio(id_comercio):
        if str(compra.get("estado", "")).upper() == "COMPLETADA":
            compras_por_proveedor[compra["id_proveedor"]] += Decimal(str(compra["total_compra"]))
    for pago in obtener_pagos_proveedor(id_comercio):
        if str(pago.get("estado", "")).upper() == "COMPLETADO":
            pagos_por_proveedor[pago["id_proveedor"]] += Decimal(str(pago["monto"]))

    saldos = []
    for proveedor in obtener_proveedores(id_comercio):
        identificador = proveedor["id_proveedor"]
        compras = compras_por_proveedor[identificador]
        pagos = pagos_por_proveedor[identificador]
        saldo = compras - pagos
        saldos.append({
            "id_proveedor": identificador,
            "numero_proveedor": proveedor["numero_proveedor"],
            "total_compras": float(compras),
            "total_pagos": float(pagos),
            "saldo": float(saldo),
            "situacion": "DEUDA" if saldo > 0 else "SALDO_A_FAVOR" if saldo < 0 else "AL_DIA",
        })
    return saldos
