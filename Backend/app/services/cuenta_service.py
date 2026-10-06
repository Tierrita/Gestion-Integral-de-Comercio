"""
Servicio de cuentas financieras.

Este módulo contiene la lógica de negocio relacionada
con las cuentas financieras del sistema.
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


def crear_cuenta(datos):
    """
    Valida los datos recibidos y crea una nueva cuenta financiera.
    """

    # Verificar que se hayan enviado datos
    if not datos:
        raise ValueError("No se enviaron datos")

    # Verificar que exista nombre_cuenta
    if "nombre_cuenta" not in datos:
        raise ValueError("El campo 'nombre_cuenta' es obligatorio")

    nombre_cuenta = datos["nombre_cuenta"]

    # Verificar que el nombre sea texto
    if not isinstance(nombre_cuenta, str):
        raise ValueError("El campo 'nombre_cuenta' debe ser texto")

    # Eliminar espacios innecesarios
    nombre_cuenta = nombre_cuenta.strip()

    # Verificar que el nombre no quede vacío
    if not nombre_cuenta:
        raise ValueError("El campo 'nombre_cuenta' no puede estar vacío")

    # Verificar si ya existe una cuenta con ese nombre
    cuenta_existente = obtener_cuenta_por_nombre(nombre_cuenta)

    if cuenta_existente:
        raise ValueError("Ya existe una cuenta con ese nombre")

    # Preparar únicamente los datos permitidos
    nueva_cuenta = {
        "nombre_cuenta": nombre_cuenta
    }

    # Registrar cuenta
    resultado = insertar_cuenta(nueva_cuenta)

    if not resultado:
        raise ValueError("No se pudo crear la cuenta")

    return resultado[0]

def listar_cuentas():
    """
    Obtiene todas las cuentas financieras registradas.
    """

    cuentas = obtener_cuentas()

    return cuentas



def consultar_cuenta_por_id(id_cuenta):
    """
    Obtiene una cuenta financiera mediante su ID.
    """

    cuenta = obtener_cuenta_por_id(id_cuenta)

    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    return cuenta[0]

def editar_cuenta(id_cuenta, datos):
    """
    Valida y modifica el nombre de una cuenta financiera.
    """

    # Verificar que la cuenta exista
    cuenta_actual = obtener_cuenta_por_id(id_cuenta)

    if not cuenta_actual:
        raise ValueError("Cuenta no encontrada")

    # Verificar que se hayan enviado datos
    if not datos:
        raise ValueError("No se enviaron datos")

    # Solamente nombre_cuenta puede modificarse
    if "nombre_cuenta" not in datos:
        raise ValueError(
            "No se enviaron campos válidos para actualizar"
        )

    nombre_cuenta = datos["nombre_cuenta"]

    # Verificar que el nombre sea texto
    if not isinstance(nombre_cuenta, str):
        raise ValueError(
            "El campo 'nombre_cuenta' debe ser texto"
        )

    # Eliminar espacios innecesarios
    nombre_cuenta = nombre_cuenta.strip()

    # Evitar nombres vacíos
    if not nombre_cuenta:
        raise ValueError(
            "El campo 'nombre_cuenta' no puede estar vacío"
        )

    # Buscar si existe otra cuenta con ese nombre
    cuentas_mismo_nombre = obtener_cuenta_por_nombre(nombre_cuenta)

    for cuenta in cuentas_mismo_nombre:
        if cuenta["id_cuenta"] != id_cuenta:
            raise ValueError(
                "Ya existe una cuenta con ese nombre"
            )

    # Preparar únicamente el campo permitido
    datos_actualizados = {
        "nombre_cuenta": nombre_cuenta
    }

    resultado = actualizar_cuenta(
        id_cuenta,
        datos_actualizados
    )

    if not resultado:
        raise ValueError("No se pudo actualizar la cuenta")

    return resultado[0]


def cambiar_estado_cuenta(id_cuenta, datos):
    """
    Activa o desactiva una cuenta financiera.

    Una cuenta solamente puede desactivarse
    cuando su saldo es igual a cero.
    """

    # Verificar que la cuenta exista
    cuenta = obtener_cuenta_por_id(id_cuenta)

    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    cuenta = cuenta[0]

    # Verificar datos recibidos
    if not datos:
        raise ValueError("No se enviaron datos")

    if "estado" not in datos:
        raise ValueError("El campo 'estado' es obligatorio")

    nuevo_estado = datos["estado"]

    # El estado debe ser booleano
    if not isinstance(nuevo_estado, bool):
        raise ValueError("El campo 'estado' debe ser booleano")

    # Si se intenta desactivar la cuenta
    if nuevo_estado is False:

        saldo_actual = float(cuenta["saldo"])

        if saldo_actual != 0:
            raise ValueError(
                "No se puede desactivar una cuenta con saldo disponible"
            )

    resultado = actualizar_estado_cuenta(
        id_cuenta,
        nuevo_estado
    )

    if not resultado:
        raise ValueError(
            "No se pudo actualizar el estado de la cuenta"
        )

    return resultado[0]



def ajustar_saldo_cuenta(id_cuenta, datos):
    """
    Valida y realiza un ajuste manual sobre el saldo
    de una cuenta financiera.

    El ajuste se ejecuta mediante una función RPC de Supabase
    que actualiza el saldo y registra el movimiento financiero
    dentro de una misma operación transaccional.
    """

    # Verificar que la cuenta exista
    cuenta = obtener_cuenta_por_id(id_cuenta)

    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    cuenta = cuenta[0]

    # Verificar que la cuenta esté activa
    if not cuenta["estado"]:
        raise ValueError("La cuenta se encuentra inactiva")

    # Verificar datos recibidos
    if not datos:
        raise ValueError("No se enviaron datos")

    # Verificar campos obligatorios
    campos_obligatorios = [
        "cantidad",
        "tipo_ajuste",
        "id_usuario",
        "observaciones"
    ]

    for campo in campos_obligatorios:
        if campo not in datos:
            raise ValueError(
                f"El campo '{campo}' es obligatorio"
            )

    cantidad = datos["cantidad"]
    tipo_ajuste = datos["tipo_ajuste"]
    id_usuario = datos["id_usuario"]
    observaciones = datos["observaciones"]

    # Validar cantidad
    if (
        not isinstance(cantidad, (int, float))
        or isinstance(cantidad, bool)
    ):
        raise ValueError("La cantidad debe ser numérica")

    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero")

    # Validar tipo de ajuste
    if not isinstance(tipo_ajuste, str):
        raise ValueError("El tipo de ajuste debe ser texto")

    tipo_ajuste = tipo_ajuste.strip().upper()

    if tipo_ajuste not in ["AUMENTAR", "DISMINUIR"]:
        raise ValueError(
            "El tipo de ajuste debe ser AUMENTAR o DISMINUIR"
        )

    # Validar usuario
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

    # Validar observaciones
    if not isinstance(observaciones, str):
        raise ValueError(
            "Las observaciones deben ser texto"
        )

    observaciones = observaciones.strip()

    if len(observaciones) < 3:
        raise ValueError(
            "Las observaciones deben tener al menos 3 caracteres"
        )

    # Ejecutar ajuste transaccional mediante Supabase RPC
    resultado = ajustar_saldo_cuenta_rpc(
        id_cuenta=id_cuenta,
        cantidad=cantidad,
        tipo_ajuste=tipo_ajuste,
        id_usuario=id_usuario,
        observaciones=observaciones
    )

    if not resultado:
        raise ValueError(
            "No se pudo realizar el ajuste de saldo"
        )

    return resultado

def consultar_movimientos_cuenta(id_cuenta):
    """
    Consulta el historial de movimientos financieros
    de una cuenta determinada.
    """

    # Verificar que la cuenta exista
    cuenta = obtener_cuenta_por_id(id_cuenta)

    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    cuenta = cuenta[0]

    # Obtener movimientos financieros de la cuenta
    movimientos = obtener_movimientos_por_cuenta(id_cuenta)

    # Construir respuesta
    return {
        "cuenta": {
            "id_cuenta": cuenta["id_cuenta"],
            "nombre_cuenta": cuenta["nombre_cuenta"],
            "saldo": cuenta["saldo"],
            "estado": cuenta["estado"]
        },
        "movimientos": movimientos
    }