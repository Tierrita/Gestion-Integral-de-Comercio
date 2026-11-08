"""
Servicio de cuentas financieras multicomercio.
"""

from app.models.cuenta_model import (
    obtener_cuenta_por_nombre,
    insertar_cuenta,
    obtener_cuentas,
    obtener_cuenta_por_id,
    actualizar_cuenta,
    actualizar_estado_cuenta,
    ajustar_saldo_cuenta_rpc
)

from app.models.movimiento_financiero_model import (
    obtener_movimientos_por_cuenta
)


def crear_cuenta(datos, id_comercio):
    if not isinstance(datos, dict):
        raise ValueError("No se enviaron datos")

    nombre = datos.get("nombre_cuenta")

    if not isinstance(nombre, str):
        raise ValueError(
            "El campo 'nombre_cuenta' debe ser texto"
        )

    nombre = nombre.strip()

    if not nombre:
        raise ValueError(
            "El campo 'nombre_cuenta' no puede estar vacío"
        )

    if obtener_cuenta_por_nombre(
        nombre,
        id_comercio
    ):
        raise ValueError(
            "Ya existe una cuenta con ese nombre"
        )

    resultado = insertar_cuenta({
        "nombre_cuenta": nombre,
        "saldo": 0,
        "estado": True,
        "id_comercio": id_comercio
    })

    if not resultado:
        raise ValueError("No se pudo crear la cuenta")

    return resultado[0]


def listar_cuentas(id_comercio):
    return obtener_cuentas(id_comercio)


def consultar_cuenta_por_id(
    id_cuenta,
    id_comercio
):
    cuenta = obtener_cuenta_por_id(
        id_cuenta,
        id_comercio
    )

    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    return cuenta


def editar_cuenta(
    id_cuenta,
    datos,
    id_comercio
):
    cuenta = obtener_cuenta_por_id(
        id_cuenta,
        id_comercio
    )

    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    if not isinstance(datos, dict):
        raise ValueError("No se enviaron datos")

    nombre = datos.get("nombre_cuenta")

    if not isinstance(nombre, str):
        raise ValueError(
            "El campo 'nombre_cuenta' debe ser texto"
        )

    nombre = nombre.strip()

    if not nombre:
        raise ValueError(
            "El campo 'nombre_cuenta' no puede estar vacío"
        )

    existentes = obtener_cuenta_por_nombre(
        nombre,
        id_comercio
    )

    for existente in existentes:
        if existente["id_cuenta"] != id_cuenta:
            raise ValueError(
                "Ya existe una cuenta con ese nombre"
            )

    resultado = actualizar_cuenta(
        id_cuenta,
        id_comercio,
        {"nombre_cuenta": nombre}
    )

    if not resultado:
        raise ValueError(
            "No se pudo actualizar la cuenta"
        )

    return resultado[0]


def cambiar_estado_cuenta(
    id_cuenta,
    datos,
    id_comercio
):
    cuenta = obtener_cuenta_por_id(
        id_cuenta,
        id_comercio
    )

    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    if not isinstance(datos, dict):
        raise ValueError("No se enviaron datos")

    nuevo_estado = datos.get("estado")

    if not isinstance(nuevo_estado, bool):
        raise ValueError(
            "El campo 'estado' debe ser booleano"
        )

    if nuevo_estado is False:
        if float(cuenta["saldo"]) != 0:
            raise ValueError(
                "No se puede desactivar una cuenta con saldo disponible"
            )

    resultado = actualizar_estado_cuenta(
        id_cuenta,
        id_comercio,
        nuevo_estado
    )

    if not resultado:
        raise ValueError(
            "No se pudo actualizar el estado de la cuenta"
        )

    return resultado[0]


def ajustar_saldo_cuenta(
    id_cuenta,
    datos,
    id_comercio,
    id_usuario
):
    cuenta = obtener_cuenta_por_id(
        id_cuenta,
        id_comercio
    )

    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    if not cuenta["estado"]:
        raise ValueError(
            "La cuenta se encuentra inactiva"
        )

    if not isinstance(datos, dict):
        raise ValueError("No se enviaron datos")

    cantidad = datos.get("cantidad")
    tipo = datos.get("tipo_ajuste")
    observaciones = datos.get("observaciones")

    if (
        not isinstance(cantidad, (int, float))
        or isinstance(cantidad, bool)
        or cantidad <= 0
    ):
        raise ValueError(
            "La cantidad debe ser mayor que cero"
        )

    if not isinstance(tipo, str):
        raise ValueError(
            "El tipo de ajuste debe ser texto"
        )

    tipo = tipo.strip().upper()

    if tipo not in ["AUMENTAR", "DISMINUIR"]:
        raise ValueError(
            "El tipo de ajuste debe ser AUMENTAR o DISMINUIR"
        )

    if not isinstance(observaciones, str):
        raise ValueError(
            "Las observaciones deben ser texto"
        )

    observaciones = observaciones.strip()

    if len(observaciones) < 3:
        raise ValueError(
            "Las observaciones deben tener al menos 3 caracteres"
        )

    return ajustar_saldo_cuenta_rpc(
        id_cuenta=id_cuenta,
        cantidad=cantidad,
        tipo_ajuste=tipo,
        id_usuario=id_usuario,
        observaciones=observaciones
    )


def consultar_movimientos_cuenta(
    id_cuenta,
    id_comercio
):
    cuenta = obtener_cuenta_por_id(
        id_cuenta,
        id_comercio
    )

    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    movimientos = obtener_movimientos_por_cuenta(
        id_cuenta
    )

    return {
        "cuenta": cuenta,
        "movimientos": movimientos
    }