"""
Servicio de clientes.

Contiene las reglas de negocio del módulo de clientes
y garantiza el aislamiento multicomercio.

Route → Controller → Service → Model → Supabase
"""

from app.models.cliente_model import (
    obtener_clientes,
    obtener_cliente_por_id,
    obtener_siguiente_numero_cliente,
    insertar_cliente,
    actualizar_cliente,
    obtener_ventas_cliente,
    obtener_detalles_venta_cliente,
)


def listar_clientes(id_comercio):
    """Lista los clientes del comercio autenticado."""

    return obtener_clientes(id_comercio)


def consultar_cliente_por_id(id_cliente, id_comercio):
    """Consulta un cliente dentro del comercio autenticado."""

    cliente = obtener_cliente_por_id(
        id_cliente,
        id_comercio
    )

    if not cliente:
        raise ValueError("Cliente no encontrado")

    return cliente


def crear_cliente(datos, id_comercio):
    """
    Registra un cliente.

    id_comercio, numero_cliente y estado
    son controlados exclusivamente por el backend.
    """

    if not datos:
        raise ValueError("No se enviaron datos del cliente")

    nombre_completo = datos.get("nombre_completo")

    if not isinstance(nombre_completo, str):
        raise ValueError(
            "El nombre completo es obligatorio y debe ser texto"
        )

    nombre_completo = nombre_completo.strip()

    if len(nombre_completo) < 2:
        raise ValueError(
            "El nombre completo debe tener al menos 2 caracteres"
        )

    telefono = datos.get("telefono")

    if telefono is not None:
        if not isinstance(telefono, str):
            raise ValueError("El teléfono debe ser texto")

        telefono = telefono.strip()

        if not telefono:
            telefono = None

    numero_cliente = obtener_siguiente_numero_cliente(
        id_comercio
    )

    if numero_cliente is None:
        raise ValueError(
            "No se pudo generar el número del cliente"
        )

    nuevo_cliente = {
        "id_comercio": id_comercio,
        "numero_cliente": numero_cliente,
        "nombre_completo": nombre_completo,
        "telefono": telefono,
        "estado": True,
    }

    cliente = insertar_cliente(nuevo_cliente)

    if not cliente:
        raise ValueError("No se pudo registrar el cliente")

    return cliente


def editar_cliente(id_cliente, datos, id_comercio):
    """Modifica únicamente los campos editables del cliente."""

    cliente = obtener_cliente_por_id(
        id_cliente,
        id_comercio
    )

    if not cliente:
        raise ValueError("Cliente no encontrado")

    if not datos:
        raise ValueError(
            "No se enviaron datos para actualizar"
        )

    campos_permitidos = {
        "nombre_completo",
        "telefono",
    }

    datos_actualizacion = {
        campo: valor
        for campo, valor in datos.items()
        if campo in campos_permitidos
    }

    if not datos_actualizacion:
        raise ValueError(
            "No se enviaron campos válidos para actualizar"
        )

    if "nombre_completo" in datos_actualizacion:

        # El CLIENTE GENERAL es un registro especial del sistema.
        if cliente.get("numero_cliente") == 1:
            raise ValueError(
                "No se puede modificar el nombre de CLIENTE GENERAL"
            )

        nombre = datos_actualizacion["nombre_completo"]

        if not isinstance(nombre, str):
            raise ValueError(
                "El nombre completo debe ser texto"
            )

        nombre = nombre.strip()

        if len(nombre) < 2:
            raise ValueError(
                "El nombre completo debe tener al menos 2 caracteres"
            )

        datos_actualizacion["nombre_completo"] = nombre

    if "telefono" in datos_actualizacion:

        telefono = datos_actualizacion["telefono"]

        if telefono is not None:

            if not isinstance(telefono, str):
                raise ValueError(
                    "El teléfono debe ser texto"
                )

            telefono = telefono.strip()

            if not telefono:
                telefono = None

        datos_actualizacion["telefono"] = telefono

    cliente_actualizado = actualizar_cliente(
        id_cliente,
        id_comercio,
        datos_actualizacion
    )

    if not cliente_actualizado:
        raise ValueError(
            "No se pudo actualizar el cliente"
        )

    return cliente_actualizado


def cambiar_estado_cliente(
    id_cliente,
    datos,
    id_comercio
):
    """Activa o desactiva un cliente del comercio."""

    cliente = obtener_cliente_por_id(
        id_cliente,
        id_comercio
    )

    if not cliente:
        raise ValueError("Cliente no encontrado")

    if not datos or "estado" not in datos:
        raise ValueError(
            "El campo 'estado' es obligatorio"
        )

    nuevo_estado = datos["estado"]

    if not isinstance(nuevo_estado, bool):
        raise ValueError(
            "El estado debe ser true o false"
        )

    # CLIENTE GENERAL es el cliente local número 1
    # de cada comercio.
    if cliente.get("numero_cliente") == 1:
        if nuevo_estado is False:
            raise ValueError(
                "CLIENTE GENERAL no puede ser desactivado"
            )

    estado_actual = cliente.get("estado", True)

    if estado_actual == nuevo_estado:

        if nuevo_estado:
            raise ValueError(
                "El cliente ya se encuentra activo"
            )

        raise ValueError(
            "El cliente ya se encuentra inactivo"
        )

    cliente_actualizado = actualizar_cliente(
        id_cliente,
        id_comercio,
        {"estado": nuevo_estado}
    )

    if not cliente_actualizado:
        raise ValueError(
            "No se pudo actualizar el estado del cliente"
        )

    return cliente_actualizado


def consultar_historial_ventas_cliente(
    id_cliente,
    id_comercio
):
    """
    Obtiene el historial de ventas de un cliente
    perteneciente al comercio autenticado.
    """

    cliente = obtener_cliente_por_id(
        id_cliente,
        id_comercio
    )

    if not cliente:
        raise ValueError("Cliente no encontrado")

    ventas = obtener_ventas_cliente(
        id_cliente,
        id_comercio
    )

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
            "numero_cliente": cliente["numero_cliente"],
            "nombre_completo": cliente["nombre_completo"],
            "telefono": cliente["telefono"],
            "estado": cliente["estado"],
        },
        "cantidad_ventas": len(ventas),
        "ventas": historial,
    }