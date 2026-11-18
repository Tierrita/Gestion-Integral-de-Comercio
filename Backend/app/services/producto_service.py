"""
Servicio de productos.

Este módulo contiene la lógica de negocio relacionada
con los productos de cada comercio.

Route → Controller → Service → Model → Supabase
"""

from app.models.producto_model import (
    obtener_productos,
    obtener_producto_por_id,
    obtener_siguiente_numero_producto,
    insertar_producto,
    actualizar_producto,
    obtener_categoria_por_id,
    obtener_proveedor_por_id,
)

from app.utils.cantidades import validar_cantidad


def listar_productos(id_comercio):
    """
    Lista únicamente los productos pertenecientes
    al comercio autenticado.
    """

    return obtener_productos(id_comercio)


def buscar_producto_por_id(id_producto, id_comercio):
    """
    Busca un producto verificando que pertenezca
    al comercio autenticado.
    """

    producto = obtener_producto_por_id(
        id_producto,
        id_comercio
    )

    if not producto:
        raise ValueError("Producto no encontrado")

    return producto


def crear_producto(datos, id_comercio):
    """
    Crea un producto dentro del comercio autenticado.

    El id_comercio y numero_producto son determinados
    exclusivamente por el backend.
    """

    campos_obligatorios = [
        "nombre_producto",
        "precio_costo",
        "precio_venta",
        "id_categoria",
        "id_proveedor",
        "unidad_de_medida",
    ]

    for campo in campos_obligatorios:
        if campo not in datos:
            raise ValueError(
                f"Falta el campo obligatorio: {campo}"
            )

    # -----------------------------
    # NOMBRE
    # -----------------------------

    nombre_producto = str(
        datos.get("nombre_producto", "")
    ).strip()

    if len(nombre_producto) < 2:
        raise ValueError(
            "El nombre del producto debe tener al menos 2 caracteres"
        )

    # -----------------------------
    # PRECIOS
    # -----------------------------

    precio_costo = datos.get("precio_costo")
    precio_venta = datos.get("precio_venta")

    if (
        isinstance(precio_costo, bool)
        or not isinstance(precio_costo, (int, float))
    ):
        raise ValueError(
            "El precio de costo debe ser un número"
        )

    if (
        isinstance(precio_venta, bool)
        or not isinstance(precio_venta, (int, float))
    ):
        raise ValueError(
            "El precio de venta debe ser un número"
        )

    if precio_costo < 0:
        raise ValueError(
            "El precio de costo no puede ser negativo"
        )

    if precio_venta < 0:
        raise ValueError(
            "El precio de venta no puede ser negativo"
        )

    # -----------------------------
    # UNIDAD DE MEDIDA Y STOCK
    # -----------------------------

    unidad = str(datos.get("unidad_de_medida", "")).strip().upper()
    if unidad not in ("UNIDAD", "KG"):
        raise ValueError("La unidad de medida debe ser UNIDAD o KG")

    stock = validar_cantidad(datos.get("stock", 0), unidad, permitir_cero=True)
    stock_minimo = validar_cantidad(
        datos.get("stock_minimo", 0), unidad, permitir_cero=True
    )

    # -----------------------------
    # CATEGORÍA
    # -----------------------------

    id_categoria = datos.get("id_categoria")

    categoria = obtener_categoria_por_id(
        id_categoria,
        id_comercio
    )

    if not categoria:
        raise ValueError(
            "La categoría no existe o no pertenece al comercio"
        )

    if not categoria.get("estado", True):
        raise ValueError(
            "No se puede asignar una categoría inactiva"
        )

    # -----------------------------
    # PROVEEDOR
    # -----------------------------

    id_proveedor = datos.get("id_proveedor")

    proveedor = obtener_proveedor_por_id(
        id_proveedor,
        id_comercio
    )

    if not proveedor:
        raise ValueError(
            "El proveedor no existe o no pertenece al comercio"
        )

    if not proveedor.get("estado", True):
        raise ValueError(
            "No se puede asignar un proveedor inactivo"
        )

    # -----------------------------
    # NÚMERO LOCAL
    # -----------------------------

    numero_producto = obtener_siguiente_numero_producto(
        id_comercio
    )

    if numero_producto is None:
        raise ValueError(
            "No se pudo generar el número del producto"
        )

    # -----------------------------
    # DATOS CONTROLADOS POR BACKEND
    # -----------------------------

    nuevo_producto = {
        "id_comercio": id_comercio,
        "numero_producto": numero_producto,
        "nombre_producto": nombre_producto,
        "precio_costo": precio_costo,
        "precio_venta": precio_venta,
        "id_categoria": id_categoria,
        "id_proveedor": id_proveedor,
        "unidad_de_medida": unidad,
        "stock": float(stock),
        "stock_minimo": float(stock_minimo),
        "estado": True,
    }

    producto = insertar_producto(
        nuevo_producto
    )

    if not producto:
        raise ValueError(
            "No se pudo crear el producto"
        )

    return producto


def modificar_producto(
    id_producto,
    datos,
    id_comercio,
    puede_modificar_costo=False
):
    """
    Modifica los datos comerciales de un producto.

    No permite modificar mediante este endpoint:
    - id_producto
    - id_comercio
    - numero_producto
    - stock
    - estado
    - fecha_alta

    El stock y el estado poseen flujos independientes.
    """

    producto_actual = obtener_producto_por_id(
        id_producto,
        id_comercio
    )

    if not producto_actual:
        raise ValueError("Producto no encontrado")

    if not datos:
        raise ValueError(
            "No se enviaron datos para modificar"
        )

    # -----------------------------
    # CAMPOS PERMITIDOS
    # -----------------------------

    campos_permitidos = {
        "nombre_producto",
        "precio_costo",
        "precio_venta",
        "id_categoria",
        "id_proveedor",
        "unidad_de_medida",
        "stock_minimo",
    }

    datos_actualizados = {
        campo: valor
        for campo, valor in datos.items()
        if campo in campos_permitidos
    }

    if not datos_actualizados:
        raise ValueError(
            "No se enviaron campos válidos para modificar"
        )

    # -----------------------------
    # PRECIO DE COSTO
    # -----------------------------

    if "precio_costo" in datos_actualizados:

        if not puede_modificar_costo:
            raise PermissionError(
                "No tiene permisos para modificar el precio de costo"
            )

        precio_costo = datos_actualizados["precio_costo"]

        if (
            isinstance(precio_costo, bool)
            or not isinstance(precio_costo, (int, float))
        ):
            raise ValueError(
                "El precio de costo debe ser un número"
            )

        if precio_costo < 0:
            raise ValueError(
                "El precio de costo no puede ser negativo"
            )

    # -----------------------------
    # NOMBRE
    # -----------------------------

    if "nombre_producto" in datos_actualizados:

        nombre_producto = str(
            datos_actualizados["nombre_producto"]
        ).strip()

        if len(nombre_producto) < 2:
            raise ValueError(
                "El nombre del producto debe tener al menos 2 caracteres"
            )

        datos_actualizados["nombre_producto"] = nombre_producto

    # -----------------------------
    # PRECIO DE VENTA
    # -----------------------------

    if "precio_venta" in datos_actualizados:

        precio_venta = datos_actualizados["precio_venta"]

        if (
            isinstance(precio_venta, bool)
            or not isinstance(precio_venta, (int, float))
        ):
            raise ValueError(
                "El precio de venta debe ser un número"
            )

        if precio_venta < 0:
            raise ValueError(
                "El precio de venta no puede ser negativo"
            )

    # -----------------------------
    # UNIDAD DE MEDIDA Y STOCK MÍNIMO
    # -----------------------------

    unidad_anterior = str(producto_actual["unidad_de_medida"]).strip().upper()
    unidad = str(
        datos_actualizados.get("unidad_de_medida", unidad_anterior)
    ).strip().upper()

    if unidad not in ("UNIDAD", "KG"):
        raise ValueError("La unidad de medida debe ser UNIDAD o KG")

    if "unidad_de_medida" in datos_actualizados:
        # Cambiar la unidad altera el significado del stock y de su historial.
        # Por seguridad, esta operación requiere un flujo específico de migración.
        if unidad != unidad_anterior:
            raise ValueError(
                "No se puede cambiar la unidad de medida de un producto existente. "
                "Requiere una migración controlada de stock e historial"
            )
        datos_actualizados["unidad_de_medida"] = unidad

    if "stock_minimo" in datos_actualizados:
        stock_minimo = validar_cantidad(
            datos_actualizados["stock_minimo"], unidad, permitir_cero=True
        )
        # Convertir solo en el límite de serialización JSON del cliente Supabase.
        datos_actualizados["stock_minimo"] = float(stock_minimo)

    # -----------------------------
    # CATEGORÍA
    # -----------------------------

    if "id_categoria" in datos_actualizados:

        id_categoria = datos_actualizados["id_categoria"]

        categoria = obtener_categoria_por_id(
            id_categoria,
            id_comercio
        )

        if not categoria:
            raise ValueError(
                "La categoría no existe o no pertenece al comercio"
            )

        if not categoria.get("estado", True):
            raise ValueError(
                "No se puede asignar una categoría inactiva"
            )

    # -----------------------------
    # PROVEEDOR
    # -----------------------------

    if "id_proveedor" in datos_actualizados:

        id_proveedor = datos_actualizados["id_proveedor"]

        proveedor = obtener_proveedor_por_id(
            id_proveedor,
            id_comercio
        )

        if not proveedor:
            raise ValueError(
                "El proveedor no existe o no pertenece al comercio"
            )

        if not proveedor.get("estado", True):
            raise ValueError(
                "No se puede asignar un proveedor inactivo"
            )

    # -----------------------------
    # ACTUALIZACIÓN
    # -----------------------------

    producto = actualizar_producto(
        id_producto,
        id_comercio,
        datos_actualizados
    )

    if not producto:
        raise ValueError(
            "No se pudo modificar el producto"
        )

    return producto




def cambiar_estado_producto(
    id_producto,
    datos,
    id_comercio
):
    """
    Activa o desactiva un producto perteneciente
    al comercio autenticado.

    El producto no se elimina físicamente.
    Solamente se modifica su estado.
    """

    # -----------------------------
    # VERIFICAR PRODUCTO
    # -----------------------------

    producto_actual = obtener_producto_por_id(
        id_producto,
        id_comercio
    )

    if not producto_actual:
        raise ValueError("Producto no encontrado")

    # -----------------------------
    # VALIDAR BODY
    # -----------------------------

    if not datos or "estado" not in datos:
        raise ValueError(
            "El estado es obligatorio"
        )

    nuevo_estado = datos["estado"]

    # bool se valida explícitamente para evitar
    # valores como 1, 0, "true" o "false".
    if not isinstance(nuevo_estado, bool):
        raise ValueError(
            "El estado debe ser true o false"
        )

    # -----------------------------
    # EVITAR OPERACIÓN INNECESARIA
    # -----------------------------

    estado_actual = producto_actual.get(
        "estado",
        True
    )

    if estado_actual == nuevo_estado:

        if nuevo_estado:
            raise ValueError(
                "El producto ya se encuentra activo"
            )

        raise ValueError(
            "El producto ya se encuentra inactivo"
        )

    # -----------------------------
    # ACTUALIZAR ESTADO
    # -----------------------------

    producto = actualizar_producto(
        id_producto,
        id_comercio,
        {
            "estado": nuevo_estado
        }
    )

    if not producto:
        raise ValueError(
            "No se pudo actualizar el estado del producto"
        )

    return producto