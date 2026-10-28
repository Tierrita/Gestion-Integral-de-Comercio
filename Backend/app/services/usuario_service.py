"""
Servicio de usuarios.

Este módulo contiene la lógica de negocio relacionada
con los usuarios y empleados de cada comercio.

Route → Controller → Service → Model → Supabase
"""

from app.models.usuario_model import (
    obtener_usuarios_comercio,
    obtener_usuario_comercio_por_id,
    obtener_usuario_por_email,
    insertar_usuario,
    actualizar_usuario,
    actualizar_estado_usuario,
    actualizar_rol_usuario,
    
)

from app.models.rol_model import obtener_rol_por_id

from werkzeug.security import generate_password_hash

def listar_usuarios(id_comercio):
    """
    Lista los usuarios pertenecientes al comercio autenticado.
    """

    usuarios = obtener_usuarios_comercio(id_comercio)

    return usuarios


def obtener_usuario(id_usuario, id_comercio):
    """
    Obtiene un usuario específico perteneciente
    al comercio autenticado.
    """

    usuario = obtener_usuario_comercio_por_id(
        id_usuario,
        id_comercio
    )

    if not usuario:
        raise ValueError("Usuario no encontrado")

    return usuario



def crear_usuario(datos, id_comercio):
    """
    Crea un nuevo empleado dentro del comercio autenticado.
    """

    nombre_completo = str(datos.get("nombre_completo", "")).strip()
    email = str(datos.get("email", "")).strip().lower()
    password = str(datos.get("password", ""))
    telefono = datos.get("telefono")
    direccion = datos.get("direccion")
    id_rol = datos.get("id_rol")

    # Validar nombre
    if len(nombre_completo) < 3:
        raise ValueError(
            "El nombre completo debe tener al menos 3 caracteres"
        )

    # Validar email
    if not email or "@" not in email:
        raise ValueError("El email no es válido")

    # Verificar que el email no esté registrado
    usuario_existente = obtener_usuario_por_email(email)

    if usuario_existente:
        raise ValueError("El email ya se encuentra registrado")

    # Validar contraseña
    if len(password) < 8:
        raise ValueError(
            "La contraseña debe tener al menos 8 caracteres"
        )

    # Validar rol
    if id_rol is None:
        raise ValueError("El rol es obligatorio")

    rol = obtener_rol_por_id(id_rol, id_comercio)

    if not rol:
        raise ValueError(
            "El rol no existe o no pertenece al comercio"
        )

    if not rol.get("estado"):
        raise ValueError(
            "No se puede asignar un rol inactivo"
        )

    # Generar hash de la contraseña
    password_hash = generate_password_hash(
        password,
        method="pbkdf2:sha256"
    )

    nuevo_usuario = {
        "id_comercio": id_comercio,
        "id_rol": id_rol,
        "nombre_completo": nombre_completo,
        "email": email,
        "password": password_hash,
        "telefono": telefono,
        "direccion": direccion,
        "dni": None,
        "es_propietario": False,
        "estado": True,
    }

    usuario = insertar_usuario(nuevo_usuario)

    if not usuario:
        raise ValueError("No se pudo crear el usuario")

    # Nunca devolver el hash de la contraseña
    usuario.pop("password", None)

    return usuario


def modificar_usuario(id_usuario, datos, id_comercio, id_usuario_actual):
    """
    Modifica los datos básicos de un empleado.

    No permite:
    - Modificar al propietario.
    - Modificarse a sí mismo.
    - Cambiar rol.
    - Cambiar estado.
    - Cambiar contraseña.
    - Cambiar comercio.
    """

    usuario = obtener_usuario_comercio_por_id(
        id_usuario,
        id_comercio
    )

    if not usuario:
        raise ValueError("Usuario no encontrado")

    if usuario.get("es_propietario"):
        raise PermissionError(
            "El propietario no puede ser modificado desde la gestión de empleados"
        )

    if id_usuario == id_usuario_actual:
        raise PermissionError(
            "No puede modificar su propio usuario desde la gestión de empleados"
        )

    datos_permitidos = {}

    # Nombre completo
    if "nombre_completo" in datos:
        nombre_completo = str(
            datos.get("nombre_completo", "")
        ).strip()

        if len(nombre_completo) < 3:
            raise ValueError(
                "El nombre completo debe tener al menos 3 caracteres"
            )

        datos_permitidos["nombre_completo"] = nombre_completo

    # Teléfono
    if "telefono" in datos:
        telefono = datos.get("telefono")

        if telefono is not None:
            telefono = str(telefono).strip()

        datos_permitidos["telefono"] = telefono

    # Dirección
    if "direccion" in datos:
        direccion = datos.get("direccion")

        if direccion is not None:
            direccion = str(direccion).strip()

        datos_permitidos["direccion"] = direccion

    if not datos_permitidos:
        raise ValueError(
            "No se enviaron datos válidos para modificar"
        )

    usuario_actualizado = actualizar_usuario(
        id_usuario,
        id_comercio,
        datos_permitidos
    )

    if not usuario_actualizado:
        raise ValueError(
            "No se pudo actualizar el usuario"
        )

    # Nunca devolver el hash de contraseña.
    usuario_actualizado.pop("password", None)

    return usuario_actualizado



def cambiar_estado_usuario(
    id_usuario,
    estado,
    id_comercio,
    id_usuario_actual
):
    """
    Activa o desactiva un empleado del comercio.
    """

    if not isinstance(estado, bool):
        raise ValueError(
            "El estado debe ser true o false"
        )

    usuario = obtener_usuario_comercio_por_id(
        id_usuario,
        id_comercio
    )

    if not usuario:
        raise ValueError("Usuario no encontrado")

    if usuario.get("es_propietario"):
        raise PermissionError(
            "El propietario no puede ser desactivado"
        )

    if id_usuario == id_usuario_actual:
        raise PermissionError(
            "No puede cambiar el estado de su propio usuario"
        )

    usuario_actualizado = actualizar_estado_usuario(
        id_usuario,
        id_comercio,
        estado
    )

    if not usuario_actualizado:
        raise ValueError(
            "No se pudo actualizar el estado del usuario"
        )

    usuario_actualizado.pop("password", None)

    return usuario_actualizado




def cambiar_rol_usuario(id_usuario, id_rol, id_comercio):
    """
    Cambia el rol de un empleado.

    El propietario no puede recibir un rol normal.
    El rol debe existir, pertenecer al mismo comercio
    y encontrarse activo.
    """

    usuario = obtener_usuario_comercio_por_id(
        id_usuario,
        id_comercio
    )

    if not usuario:
        raise ValueError("Usuario no encontrado")

    if usuario.get("es_propietario"):
        raise PermissionError(
            "No se puede cambiar el rol del propietario"
        )

    if id_rol is None:
        raise ValueError("El rol es obligatorio")

    rol = obtener_rol_por_id(
        id_rol,
        id_comercio
    )

    if not rol:
        raise ValueError(
            "El rol no existe o no pertenece al comercio"
        )

    if not rol.get("estado"):
        raise ValueError(
            "No se puede asignar un rol inactivo"
        )

    usuario_actualizado = actualizar_rol_usuario(
        id_usuario,
        id_comercio,
        id_rol
    )

    if not usuario_actualizado:
        raise ValueError(
            "No se pudo actualizar el rol del usuario"
        )

    usuario_actualizado.pop("password", None)

    return usuario_actualizado



def restablecer_password_usuario(
    id_usuario,
    nueva_password,
    id_comercio,
    id_usuario_actual
):
    """
    Restablece la contraseña de un empleado.

    No permite modificar la contraseña del propietario
    ni la del propio usuario desde la gestión de empleados.
    """

    usuario = obtener_usuario_comercio_por_id(
        id_usuario,
        id_comercio
    )

    if not usuario:
        raise ValueError("Usuario no encontrado")

    if usuario.get("es_propietario"):
        raise PermissionError(
            "La contraseña del propietario no puede restablecerse desde la gestión de empleados"
        )

    if id_usuario == id_usuario_actual:
        raise PermissionError(
            "No puede restablecer su propia contraseña desde la gestión de empleados"
        )

    if not isinstance(nueva_password, str):
        raise ValueError(
            "La nueva contraseña debe ser válida"
        )

    nueva_password = nueva_password.strip()

    if len(nueva_password) < 8:
        raise ValueError(
            "La nueva contraseña debe tener al menos 8 caracteres"
        )

    password_hash = generate_password_hash(
        nueva_password,
        method="pbkdf2:sha256"
    )

    usuario_actualizado = actualizar_usuario(
        id_usuario,
        id_comercio,
        {
            "password": password_hash
        }
    )

    if not usuario_actualizado:
        raise ValueError(
            "No se pudo restablecer la contraseña del usuario"
        )

    usuario_actualizado.pop("password", None)

    return usuario_actualizado