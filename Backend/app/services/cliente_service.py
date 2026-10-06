"""
Servicio de clientes.

Este módulo contiene la lógica de negocio relacionada
con la gestión de clientes.
"""

from app.models.cliente_model import (
    insertar_cliente,
    obtener_clientes,
    obtener_cliente_por_id,
    actualizar_cliente,
    actualizar_estado_cliente,
    obtener_ventas_cliente,
    obtener_detalles_venta_cliente
)


def crear_cliente(datos):
    """
    Registra un nuevo cliente.
    """

    if not datos:
        raise ValueError("No se enviaron datos del cliente")

    # --------------------------------------------------
    # VALIDAR NOMBRE
    # --------------------------------------------------

    if "nombre_completo" not in datos:
        raise ValueError(
            "El campo 'nombre_completo' es obligatorio"
        )

    nombre_completo = datos["nombre_completo"]

    if not isinstance(nombre_completo, str):
        raise ValueError(
            "El nombre completo debe ser texto"
        )

    nombre_completo = nombre_completo.strip()

    if not nombre_completo:
        raise ValueError(
            "El nombre completo no puede estar vacío"
        )

    # --------------------------------------------------
    # VALIDAR TELÉFONO
    # --------------------------------------------------

    telefono = datos.get("telefono")

    if telefono is not None:
        if not isinstance(telefono, str):
            raise ValueError(
                "El teléfono debe ser texto"
            )

        telefono = telefono.strip()

        if not telefono:
            telefono = None

    # --------------------------------------------------
    # CREAR CLIENTE
    # --------------------------------------------------

    datos_cliente = {
        "nombre_completo": nombre_completo,
        "telefono": telefono,
        "estado": True
    }

    cliente_creado = insertar_cliente(datos_cliente)

    if not cliente_creado:
        raise ValueError(
            "No se pudo registrar el cliente"
        )

    return cliente_creado[0]


def listar_clientes():
    """
    Obtiene todos los clientes registrados.
    """

    return obtener_clientes()


def consultar_cliente_por_id(id_cliente):
    """
    Obtiene un cliente específico mediante su ID.
    """

    cliente = obtener_cliente_por_id(id_cliente)

    if not cliente:
        raise ValueError("Cliente no encontrado")

    return cliente


def editar_cliente(id_cliente, datos):
    """
    Modifica los datos editables de un cliente.
    """

    cliente = obtener_cliente_por_id(id_cliente)

    if not cliente:
        raise ValueError("Cliente no encontrado")

    if not datos:
        raise ValueError(
            "No se enviaron datos para actualizar"
        )

    datos_actualizacion = {}

    # --------------------------------------------------
    # NOMBRE
    # --------------------------------------------------

    if "nombre_completo" in datos:

        nombre_completo = datos["nombre_completo"]

        if not isinstance(nombre_completo, str):
            raise ValueError(
                "El nombre completo debe ser texto"
            )

        nombre_completo = nombre_completo.strip()

        if not nombre_completo:
            raise ValueError(
                "El nombre completo no puede estar vacío"
            )

        datos_actualizacion["nombre_completo"] = nombre_completo

    # --------------------------------------------------
    # TELÉFONO
    # --------------------------------------------------

    if "telefono" in datos:

        telefono = datos["telefono"]

        if telefono is not None:

            if not isinstance(telefono, str):
                raise ValueError(
                    "El teléfono debe ser texto"
                )

            telefono = telefono.strip()

            if not telefono:
                telefono = None

        datos_actualizacion["telefono"] = telefono

    # --------------------------------------------------
    # VALIDAR QUE HAYA CAMPOS EDITABLES
    # --------------------------------------------------

    if not datos_actualizacion:
        raise ValueError(
            "No se enviaron campos válidos para actualizar"
        )

    cliente_actualizado = actualizar_cliente(
        id_cliente,
        datos_actualizacion
    )

    if not cliente_actualizado:
        raise ValueError(
            "No se pudo actualizar el cliente"
        )

    return cliente_actualizado


def cambiar_estado_cliente(id_cliente, datos):
    """
    Activa o desactiva un cliente.
    """

    cliente = obtener_cliente_por_id(id_cliente)

    if not cliente:
        raise ValueError("Cliente no encontrado")

    if not datos:
        raise ValueError(
            "No se enviaron datos para actualizar el estado"
        )

    if "estado" not in datos:
        raise ValueError(
            "El campo 'estado' es obligatorio"
        )

    nuevo_estado = datos["estado"]

    if not isinstance(nuevo_estado, bool):
        raise ValueError(
            "El estado debe ser true o false"
        )

    # --------------------------------------------------
    # PROTEGER CLIENTE GENERAL
    # --------------------------------------------------

    if id_cliente == 1 and nuevo_estado is False:
        raise ValueError(
            "CLIENTE GENERAL no puede ser desactivado"
        )

    cliente_actualizado = actualizar_estado_cliente(
        id_cliente,
        nuevo_estado
    )

    if not cliente_actualizado:
        raise ValueError(
            "No se pudo actualizar el estado del cliente"
        )

    return cliente_actualizado


def consultar_historial_ventas_cliente(id_cliente):
    """
    Obtiene el historial de ventas de un cliente
    incluyendo los productos de cada venta.
    """

    cliente = obtener_cliente_por_id(id_cliente)

    if not cliente:
        raise ValueError("Cliente no encontrado")

    ventas = obtener_ventas_cliente(id_cliente)

    historial = []

    for venta in ventas:

        detalles = obtener_detalles_venta_cliente(
            venta["id_venta"]
        )

        historial.append({
            "venta": venta,
            "detalles": detalles
        })

    return {
        "cliente": {
            "id_cliente": cliente["id_cliente"],
            "nombre_completo": cliente["nombre_completo"],
            "telefono": cliente["telefono"],
            "estado": cliente["estado"]
        },
        "cantidad_ventas": len(ventas),
        "ventas": historial
    }