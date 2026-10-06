"""
Servicio de pagos a proveedores.

Este módulo contiene la lógica de negocio relacionada
con los pagos realizados a proveedores.
"""

from app.models.pago_proveedor_model import (
    insertar_pago_proveedor,
    obtener_pagos_proveedor,
    obtener_pago_proveedor_por_id,
    obtener_pagos_por_proveedor,
    actualizar_pago_proveedor
)

from app.models.proveedor_model import obtener_proveedor_por_id
from app.models.compra_model import obtener_compras_por_proveedor


def registrar_pago_proveedor(datos):
    """
    Registra un nuevo pago realizado a un proveedor.
    """

    if not datos:
        raise ValueError("No se enviaron datos del pago")

    # -----------------------------
    # VALIDAR CAMPOS OBLIGATORIOS
    # -----------------------------

    if "id_proveedor" not in datos:
        raise ValueError("El campo 'id_proveedor' es obligatorio")

    if "id_usuario" not in datos:
        raise ValueError("El campo 'id_usuario' es obligatorio")

    if "monto" not in datos:
        raise ValueError("El campo 'monto' es obligatorio")

    # -----------------------------
    # VALIDAR PROVEEDOR
    # -----------------------------

    id_proveedor = datos["id_proveedor"]

    if not isinstance(id_proveedor, int) or isinstance(id_proveedor, bool):
        raise ValueError("El id_proveedor debe ser un número entero")

    if id_proveedor <= 0:
        raise ValueError("El id_proveedor debe ser mayor que cero")

    proveedor = obtener_proveedor_por_id(id_proveedor)

    if not proveedor:
        raise ValueError("Proveedor no encontrado")

    # -----------------------------
    # VALIDAR USUARIO
    # -----------------------------

    id_usuario = datos["id_usuario"]

    if not isinstance(id_usuario, int) or isinstance(id_usuario, bool):
        raise ValueError("El id_usuario debe ser un número entero")

    if id_usuario <= 0:
        raise ValueError("El id_usuario debe ser mayor que cero")

    # -----------------------------
    # VALIDAR MONTO
    # -----------------------------

    monto = datos["monto"]

    if not isinstance(monto, (int, float)) or isinstance(monto, bool):
        raise ValueError("El monto debe ser numérico")

    if monto <= 0:
        raise ValueError("El monto debe ser mayor a cero")

    # -----------------------------
    # OBSERVACIONES
    # -----------------------------

    observaciones = datos.get("observaciones")

    if observaciones is not None:
        if not isinstance(observaciones, str):
            raise ValueError("Las observaciones deben ser texto")

        observaciones = observaciones.strip()

        if not observaciones:
            observaciones = None

    # -----------------------------
    # REGISTRAR PAGO
    # -----------------------------

    datos_pago = {
        "id_proveedor": id_proveedor,
        "id_usuario": id_usuario,
        "monto": monto,
        "estado": "COMPLETADO",
        "observaciones": observaciones
    }

    pago_creado = insertar_pago_proveedor(datos_pago)

    if not pago_creado:
        raise ValueError("No se pudo registrar el pago")

    return pago_creado[0]


def listar_pagos_proveedor():
    """
    Obtiene todos los pagos realizados a proveedores.
    """

    return obtener_pagos_proveedor()


def consultar_pago_proveedor_por_id(id_pago):
    """
    Obtiene un pago específico mediante su ID.
    """

    pago = obtener_pago_proveedor_por_id(id_pago)

    if not pago:
        raise ValueError("Pago no encontrado")

    return pago


def consultar_pagos_por_proveedor(id_proveedor):
    """
    Obtiene el historial de pagos de un proveedor.
    """

    proveedor = obtener_proveedor_por_id(id_proveedor)

    if not proveedor:
        raise ValueError("Proveedor no encontrado")

    return obtener_pagos_por_proveedor(id_proveedor)


def anular_pago_proveedor(id_pago, datos):
    """
    Anula un pago realizado a un proveedor.

    El pago no se elimina físicamente.
    Se cambia su estado a ANULADO y se registra
    quién realizó la anulación y el motivo.
    """

    if not datos:
        raise ValueError("No se enviaron datos para la anulación")

    # -----------------------------
    # BUSCAR PAGO
    # -----------------------------

    pago = obtener_pago_proveedor_por_id(id_pago)

    if not pago:
        raise ValueError("Pago no encontrado")

    if pago["estado"].upper() == "ANULADO":
        raise ValueError("El pago ya se encuentra anulado")

    # -----------------------------
    # VALIDAR USUARIO
    # -----------------------------

    if "id_usuario" not in datos:
        raise ValueError("El campo 'id_usuario' es obligatorio")

    id_usuario = datos["id_usuario"]

    if not isinstance(id_usuario, int) or isinstance(id_usuario, bool):
        raise ValueError("El id_usuario debe ser un número entero")

    if id_usuario <= 0:
        raise ValueError("El id_usuario debe ser mayor que cero")

    # -----------------------------
    # VALIDAR MOTIVO
    # -----------------------------

    if "motivo_anulacion" not in datos:
        raise ValueError("El campo 'motivo_anulacion' es obligatorio")

    motivo_anulacion = datos["motivo_anulacion"]

    if not isinstance(motivo_anulacion, str):
        raise ValueError("El motivo de anulación debe ser texto")

    motivo_anulacion = motivo_anulacion.strip()

    if len(motivo_anulacion) < 5:
        raise ValueError(
            "El motivo de anulación debe tener al menos 5 caracteres"
        )

    # -----------------------------
    # ANULAR PAGO
    # -----------------------------

    datos_actualizacion = {
        "estado": "ANULADO",
        "id_usuario_anulacion": id_usuario,
        "motivo_anulacion": motivo_anulacion
    }

    pago_actualizado = actualizar_pago_proveedor(
        id_pago,
        datos_actualizacion
    )

    if not pago_actualizado:
        raise ValueError("No se pudo anular el pago")

    return pago_actualizado


def consultar_saldo_proveedor(id_proveedor):
    """
    Calcula la cuenta corriente de un proveedor.

    Saldo = compras válidas - pagos completados.
    """

    # -----------------------------
    # VALIDAR PROVEEDOR
    # -----------------------------

    proveedor = obtener_proveedor_por_id(id_proveedor)

    if not proveedor:
        raise ValueError("Proveedor no encontrado")

    # -----------------------------
    # OBTENER OPERACIONES
    # -----------------------------

    compras = obtener_compras_por_proveedor(id_proveedor)
    pagos = obtener_pagos_por_proveedor(id_proveedor)

    # -----------------------------
    # CALCULAR COMPRAS VÁLIDAS
    # -----------------------------

    total_compras = sum(
        float(compra["total_compra"])
        for compra in compras
        if compra["estado"].upper() != "ANULADA"
    )

    # -----------------------------
    # CALCULAR PAGOS VÁLIDOS
    # -----------------------------

    total_pagos = sum(
        float(pago["monto"])
        for pago in pagos
        if pago["estado"].upper() == "COMPLETADO"
    )

    # -----------------------------
    # CALCULAR SALDO
    # -----------------------------

    saldo = total_compras - total_pagos

    # -----------------------------
    # DETERMINAR SITUACIÓN
    # -----------------------------

    if saldo > 0:
        situacion = "DEUDA"
    elif saldo < 0:
        situacion = "SALDO_A_FAVOR"
    else:
        situacion = "AL_DIA"

    # -----------------------------
    # RESPUESTA
    # -----------------------------

    return {
        "proveedor": {
            "id_proveedor": proveedor["id_proveedor"],
            "nombre_proveedor": proveedor["nombre_proveedor"]
        },
        "total_compras": total_compras,
        "total_pagos": total_pagos,
        "saldo": saldo,
        "situacion": situacion
    }