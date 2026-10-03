"""
Servicio de proveedores.

Este módulo contiene la lógica de negocio relacionada
con los proveedores.
"""

from app.models.proveedor_model import (
    insertar_proveedor,
    obtener_proveedores,
    obtener_proveedor_por_id,
    actualizar_proveedor,
    actualizar_estado_proveedor
)


def crear_proveedor(datos):
    """
    Crea un nuevo proveedor luego de validar
    los datos recibidos.
    """

    # Verificar que se hayan enviado datos
    if not datos:
        raise ValueError("No se enviaron datos del proveedor")

    # Verificar campo obligatorio
    if "nombre_proveedor" not in datos:
        raise ValueError(
            "El campo 'nombre_proveedor' es obligatorio"
        )

    nombre_proveedor = datos["nombre_proveedor"]

    # Validar que el nombre sea texto
    if not isinstance(nombre_proveedor, str):
        raise ValueError(
            "El nombre del proveedor debe ser texto"
        )

    # Validar que el nombre no esté vacío
    if not nombre_proveedor.strip():
        raise ValueError(
            "El nombre del proveedor no puede estar vacío"
        )

    # Preparar los datos que serán enviados al modelo
    datos_proveedor = {
        "nombre_proveedor": nombre_proveedor.strip(),
        "telefono": datos.get("telefono"),
        "email": datos.get("email"),
        "direccion": datos.get("direccion"),
        "estado": datos.get("estado", True),
        "descripcion": datos.get("descripcion")
    }

    # Validar estado si fue enviado
    if not isinstance(datos_proveedor["estado"], bool):
        raise ValueError(
            "El campo 'estado' debe ser true o false"
        )

    # Registrar proveedor
    proveedor_creado = insertar_proveedor(datos_proveedor)

    return proveedor_creado[0]


def listar_proveedores():
    """
    Obtiene todos los proveedores registrados.
    """

    proveedores = obtener_proveedores()

    return proveedores


def buscar_proveedor_por_id(id_proveedor):
    """
    Obtiene un proveedor específico mediante su ID.
    """

    proveedor = obtener_proveedor_por_id(id_proveedor)

    if not proveedor:
        raise ValueError("Proveedor no encontrado")

    return proveedor

def editar_proveedor(id_proveedor, datos):
    """
    Edita los datos de un proveedor existente.

    Permite modificar el nombre, teléfono, email,
    dirección y descripción del proveedor.
    """

    # Verificar que el proveedor exista
    proveedor = obtener_proveedor_por_id(id_proveedor)

    if not proveedor:
        raise ValueError("Proveedor no encontrado")

    # Verificar que se hayan enviado datos
    if not datos:
        raise ValueError("No se enviaron datos para actualizar")

    datos_actualizados = {}

    # Validar nombre del proveedor
    if "nombre_proveedor" in datos:
        nombre_proveedor = datos["nombre_proveedor"]

        if not isinstance(nombre_proveedor, str):
            raise ValueError(
                "El nombre del proveedor debe ser texto"
            )

        if not nombre_proveedor.strip():
            raise ValueError(
                "El nombre del proveedor no puede estar vacío"
            )

        datos_actualizados["nombre_proveedor"] = (
            nombre_proveedor.strip()
        )

    # Campos opcionales que pueden modificarse
    if "telefono" in datos:
        datos_actualizados["telefono"] = datos["telefono"]

    if "email" in datos:
        datos_actualizados["email"] = datos["email"]

    if "direccion" in datos:
        datos_actualizados["direccion"] = datos["direccion"]

    if "descripcion" in datos:
        datos_actualizados["descripcion"] = datos["descripcion"]

    # Verificar que exista al menos un campo válido
    if not datos_actualizados:
        raise ValueError(
            "No se enviaron campos válidos para actualizar"
        )

    # Actualizar proveedor
    proveedor_actualizado = actualizar_proveedor(
        id_proveedor,
        datos_actualizados
    )

    return proveedor_actualizado


def cambiar_estado_proveedor(id_proveedor, datos):
    """
    Cambia el estado de un proveedor.

    Permite activar o desactivar un proveedor
    utilizando un valor booleano.
    """

    # Verificar que el proveedor exista
    proveedor = obtener_proveedor_por_id(id_proveedor)

    if not proveedor:
        raise ValueError("Proveedor no encontrado")

    # Verificar que se hayan enviado datos
    if not datos:
        raise ValueError("No se enviaron datos")

    # Verificar que exista el campo estado
    if "estado" not in datos:
        raise ValueError("El campo 'estado' es obligatorio")

    nuevo_estado = datos["estado"]

    # El estado debe ser booleano
    if not isinstance(nuevo_estado, bool):
        raise ValueError(
            "El campo 'estado' debe ser true o false"
        )

    # Actualizar estado
    proveedor_actualizado = actualizar_estado_proveedor(
        id_proveedor,
        nuevo_estado
    )

    return proveedor_actualizado