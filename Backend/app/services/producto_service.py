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
    # STOCK
    # -----------------------------

    stock = datos.get("stock", 0)
    stock_minimo = datos.get("stock_minimo", 0)

    if isinstance(stock, bool) or not isinstance(stock, int):
        raise ValueError(
            "El stock debe ser un número entero"
        )

    if (
        isinstance(stock_minimo, bool)
        or not isinstance(stock_minimo, int)
    ):
        raise ValueError(
            "El stock mínimo debe ser un número entero"
        )

    if stock < 0:
        raise ValueError(
            "El stock no puede ser negativo"
        )

    if stock_minimo < 0:
        raise ValueError(
            "El stock mínimo no puede ser negativo"
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
        "unidad_de_medida": str(
            datos.get("unidad_de_medida", "")
        ).strip(),
        "stock": stock,
        "stock_minimo": stock_minimo,
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
    # STOCK MÍNIMO
    # -----------------------------

    if "stock_minimo" in datos_actualizados:

        stock_minimo = datos_actualizados["stock_minimo"]

        if (
            isinstance(stock_minimo, bool)
            or not isinstance(stock_minimo, int)
        ):
            raise ValueError(
                "El stock mínimo debe ser un número entero"
            )

        if stock_minimo < 0:
            raise ValueError(
                "El stock mínimo no puede ser negativo"
            )

    # -----------------------------
    # UNIDAD DE MEDIDA
    # -----------------------------

    if "unidad_de_medida" in datos_actualizados:

        unidad = str(
            datos_actualizados["unidad_de_medida"]
        ).strip()

        if len(unidad) < 1:
            raise ValueError(
                "La unidad de medida no puede estar vacía"
            )

        datos_actualizados["unidad_de_medida"] = unidad

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