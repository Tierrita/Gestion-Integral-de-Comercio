"""
Servicio de cobros.

Este módulo contiene la lógica de negocio relacionada
con los cobros realizados por los clientes.
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


def registrar_cobro(datos):
    """
    Valida los datos recibidos y registra un cobro.

    El registro definitivo se realiza mediante una función RPC
    de Supabase que registra el cobro, actualiza el saldo
    de la cuenta financiera y genera el movimiento financiero.
    """

    # --------------------------------------------------
    # VALIDAR DATOS
    # --------------------------------------------------

    if not datos:
        raise ValueError("No se enviaron datos")

    campos_obligatorios = [
        "id_cliente",
        "id_cuenta",
        "id_usuario",
        "monto"
    ]

    for campo in campos_obligatorios:
        if campo not in datos:
            raise ValueError(
                f"El campo '{campo}' es obligatorio"
            )

    id_cliente = datos["id_cliente"]
    id_cuenta = datos["id_cuenta"]
    id_usuario = datos["id_usuario"]
    monto = datos["monto"]

    observaciones = datos.get("observaciones")

    # --------------------------------------------------
    # VALIDAR CLIENTE
    # --------------------------------------------------

    if (
        not isinstance(id_cliente, int)
        or isinstance(id_cliente, bool)
    ):
        raise ValueError(
            "El id_cliente debe ser un número entero"
        )

    if id_cliente <= 0:
        raise ValueError(
            "El id_cliente debe ser mayor que cero"
        )

    # --------------------------------------------------
    # VALIDAR CUENTA
    # --------------------------------------------------

    if (
        not isinstance(id_cuenta, int)
        or isinstance(id_cuenta, bool)
    ):
        raise ValueError(
            "El id_cuenta debe ser un número entero"
        )

    if id_cuenta <= 0:
        raise ValueError(
            "El id_cuenta debe ser mayor que cero"
        )

    # --------------------------------------------------
    # VALIDAR USUARIO
    # --------------------------------------------------

    if (
        not isinstance(id_usuario, int)
        or isinstance(id_usuario, bool)
    ):
        raise ValueError(
            "El id_usuario debe ser un número entero"
        )

    if id_usuario <= 0:
        raise ValueError(
            "El id_usuario debe ser mayor que cero"
        )

    # --------------------------------------------------
    # VALIDAR MONTO
    # --------------------------------------------------

    if (
        not isinstance(monto, (int, float))
        or isinstance(monto, bool)
    ):
        raise ValueError(
            "El monto debe ser numérico"
        )

    if monto <= 0:
        raise ValueError(
            "El monto debe ser mayor que cero"
        )

    # --------------------------------------------------
    # VALIDAR OBSERVACIONES
    # --------------------------------------------------

    if observaciones is not None:

        if not isinstance(observaciones, str):
            raise ValueError(
                "Las observaciones deben ser texto"
            )

        observaciones = observaciones.strip()

        if not observaciones:
            observaciones = None

    # --------------------------------------------------
    # REGISTRAR COBRO
    # --------------------------------------------------

    resultado = registrar_cobro_rpc(
        id_cliente=id_cliente,
        id_cuenta=id_cuenta,
        id_usuario=id_usuario,
        monto=monto,
        observaciones=observaciones
    )

    if not resultado:
        raise ValueError(
            "No se pudo registrar el cobro"
        )

    return resultado


def listar_cobros():
    """
    Obtiene todos los cobros registrados en el sistema.
    """

    return obtener_cobros()


def consultar_cobro_por_id(id_cobro):
    """
    Obtiene un cobro específico mediante su ID.
    """

    cobro = obtener_cobro_por_id(id_cobro)

    if not cobro:
        raise ValueError("Cobro no encontrado")

    return cobro[0]


def consultar_cobros_por_cliente(id_cliente):
    """
    Obtiene el historial de cobros de un cliente.
    """

    # --------------------------------------------------
    # VERIFICAR CLIENTE
    # --------------------------------------------------

    cliente = obtener_cliente_por_id(id_cliente)

    if not cliente:
        raise ValueError("Cliente no encontrado")

    # obtener_cliente_por_id() ya devuelve
    # directamente un diccionario.
    # NO debemos utilizar cliente[0].

    # --------------------------------------------------
    # OBTENER COBROS
    # --------------------------------------------------

    cobros = obtener_cobros_por_cliente(id_cliente)

    return {
        "cliente": {
            "id_cliente": cliente["id_cliente"],
            "nombre_completo": cliente["nombre_completo"],
            "estado": cliente["estado"]
        },
        "cobros": cobros
    }


def anular_cobro(id_cobro, datos):
    """
    Valida los datos recibidos y anula un cobro.

    La anulación se ejecuta mediante una función RPC
    de Supabase que modifica el estado del cobro,
    revierte el saldo de la cuenta financiera
    y registra el movimiento correspondiente.
    """

    # --------------------------------------------------
    # VALIDAR DATOS
    # --------------------------------------------------

    if not datos:
        raise ValueError("No se enviaron datos")

    campos_obligatorios = [
        "id_usuario",
        "motivo_anulacion"
    ]

    for campo in campos_obligatorios:
        if campo not in datos:
            raise ValueError(
                f"El campo '{campo}' es obligatorio"
            )

    id_usuario = datos["id_usuario"]
    motivo_anulacion = datos["motivo_anulacion"]

    # --------------------------------------------------
    # VALIDAR USUARIO
    # --------------------------------------------------

    if (
        not isinstance(id_usuario, int)
        or isinstance(id_usuario, bool)
    ):
        raise ValueError(
            "El id_usuario debe ser un número entero"
        )

    if id_usuario <= 0:
        raise ValueError(
            "El id_usuario debe ser mayor que cero"
        )

    # --------------------------------------------------
    # VALIDAR MOTIVO
    # --------------------------------------------------

    if not isinstance(motivo_anulacion, str):
        raise ValueError(
            "El motivo de anulación debe ser texto"
        )

    motivo_anulacion = motivo_anulacion.strip()

    if len(motivo_anulacion) < 5:
        raise ValueError(
            "El motivo de anulación debe tener al menos 5 caracteres"
        )

    # --------------------------------------------------
    # ANULAR COBRO
    # --------------------------------------------------

    resultado = anular_cobro_rpc(
        id_cobro=id_cobro,
        id_usuario=id_usuario,
        motivo_anulacion=motivo_anulacion
    )

    if not resultado:
        raise ValueError(
            "No se pudo anular el cobro"
        )

    return resultado


def consultar_saldo_cliente(id_cliente):
    """
    Calcula el saldo financiero actual de un cliente.

    Saldo =
    total de ventas válidas
    -
    total de cobros completados

    Saldo positivo → DEUDA
    Saldo cero     → AL_DIA
    Saldo negativo → SALDO_A_FAVOR
    """

    # --------------------------------------------------
    # VERIFICAR CLIENTE
    # --------------------------------------------------

    cliente = obtener_cliente_por_id(id_cliente)

    if not cliente:
        raise ValueError("Cliente no encontrado")

    # obtener_cliente_por_id() ya devuelve
    # directamente un diccionario.
    # NO debemos utilizar cliente[0].

    # --------------------------------------------------
    # OBTENER VENTAS Y COBROS
    # --------------------------------------------------

    ventas = obtener_ventas_por_cliente(id_cliente)
    cobros = obtener_cobros_por_cliente(id_cliente)

    # --------------------------------------------------
    # CALCULAR TOTAL DE VENTAS
    # --------------------------------------------------

    total_ventas = sum(
        float(venta["total"])
        for venta in ventas
        if venta["estado"].upper() != "ANULADA"
    )

    # --------------------------------------------------
    # CALCULAR TOTAL DE COBROS
    # --------------------------------------------------

    total_cobros = sum(
        float(cobro["monto"])
        for cobro in cobros
        if cobro["estado"].upper() == "COMPLETADO"
    )

    # --------------------------------------------------
    # CALCULAR SALDO
    # --------------------------------------------------

    saldo = total_ventas - total_cobros

    # --------------------------------------------------
    # DETERMINAR SITUACIÓN FINANCIERA
    # --------------------------------------------------

    if saldo > 0:
        situacion = "DEUDA"

    elif saldo < 0:
        situacion = "SALDO_A_FAVOR"

    else:
        situacion = "AL_DIA"

    # --------------------------------------------------
    # RESPUESTA
    # --------------------------------------------------

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