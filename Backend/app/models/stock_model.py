
"""
Modelo de stock.

Este módulo se encarga del acceso a los datos relacionados
con el stock de los productos almacenados en Supabase.

Todas las operaciones sobre productos se encuentran
aisladas por comercio.

Las cantidades se almacenan en PostgreSQL como NUMERIC(12,3):
- UNIDAD: cantidades enteras.
- KG: cantidades con hasta tres decimales.
"""

from decimal import Decimal

from core.supabase_client import get_client


def _numero_json(valor):
    """
    Convierte Decimal a un valor compatible con JSON.

    La validación de cantidades y unidades corresponde
    a la capa Service.
    """
    if isinstance(valor, Decimal):
        return float(valor)

    return valor


def obtener_stock_producto(id_producto, id_comercio):
    """
    Obtiene el stock de un producto perteneciente
    al comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select(
            "id_producto, nombre_producto, stock, "
            "stock_minimo, unidad_de_medida, estado, id_comercio"
        )
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None


def actualizar_stock_producto(
    id_producto,
    id_comercio,
    nuevo_stock
):
    """
    Actualiza el stock únicamente si el producto
    pertenece al comercio autenticado.

    Admite valores enteros o decimales previamente
    validados por el Service.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .update({
            "stock": _numero_json(nuevo_stock)
        })
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


def registrar_movimiento_stock(datos):
    """
    Registra un movimiento en historial_movimiento.

    Convierte los campos numéricos Decimal a valores
    compatibles con el cliente de Supabase.
    """

    supabase = get_client()

    datos_movimiento = datos.copy()

    for campo in (
        "cantidad",
        "stock_anterior",
        "stock_nuevo"
    ):
        if campo in datos_movimiento:
            datos_movimiento[campo] = _numero_json(
                datos_movimiento[campo]
            )

    response = (
        supabase
        .table("historial_movimiento")
        .insert(datos_movimiento)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_stock_general(id_comercio, buscar=None):
    """
    Obtiene únicamente el stock correspondiente
    al comercio autenticado.

    Opcionalmente permite buscar productos por nombre.
    """

    supabase = get_client()

    consulta = (
        supabase
        .table("productos")
        .select(
            "id_producto, numero_producto, nombre_producto, id_categoria, "
            "stock, stock_minimo, unidad_de_medida, estado, id_comercio"
        )
        .eq("id_comercio", id_comercio)
    )

    if buscar:
        consulta = consulta.ilike(
            "nombre_producto",
            f"%{buscar}%"
        )

    response = (
        consulta
        .order("nombre_producto")
        .execute()
    )

    return response.data


def obtener_historial_stock(id_comercio, id_producto=None):
    """
    Obtiene los movimientos de stock de los productos
    pertenecientes al comercio autenticado.

    No confía en identificadores de comercio enviados
    desde el frontend.

    Solo consulta los nombres de los usuarios autorizados.
    No expone correos, contraseñas ni datos sensibles.
    """

    supabase = get_client()

    # --------------------------------------------------
    # 1. OBTENER PRODUCTOS DEL COMERCIO
    # --------------------------------------------------

    productos_query = (
        supabase
        .table("productos")
        .select(
            "id_producto, numero_producto, "
            "nombre_producto, unidad_de_medida"
        )
        .eq("id_comercio", id_comercio)
    )

    if id_producto is not None:
        productos_query = productos_query.eq(
            "id_producto",
            id_producto
        )

    productos = productos_query.execute().data or []

    if not productos:
        return []

    productos_por_id = {
        producto["id_producto"]: producto
        for producto in productos
    }

    ids_productos = list(productos_por_id.keys())

    # --------------------------------------------------
    # 2. OBTENER MOVIMIENTOS AUTORIZADOS
    # --------------------------------------------------

    movimientos = (
        supabase
        .table("historial_movimiento")
        .select("*")
        .in_("id_producto", ids_productos)
        .execute()
    ).data or []

    if not movimientos:
        return []

    # --------------------------------------------------
    # 3. CONSULTAR RESPONSABLES DEL MISMO COMERCIO
    # --------------------------------------------------

    ids_usuarios = list({
        movimiento["id_usuario"]
        for movimiento in movimientos
        if movimiento.get("id_usuario") is not None
    })

    usuarios_por_id = {}

    if ids_usuarios:
        usuarios = (
            supabase
            .table("usuarios")
            .select("id_usuario, nombre_completo")
            .eq("id_comercio", id_comercio)
            .in_("id_usuario", ids_usuarios)
            .execute()
        ).data or []

        usuarios_por_id = {
            usuario["id_usuario"]: usuario.get(
                "nombre_completo"
            )
            for usuario in usuarios
        }

    # --------------------------------------------------
    # 4. ENRIQUECER HISTORIAL
    # --------------------------------------------------

    for movimiento in movimientos:

        producto = productos_por_id.get(
            movimiento["id_producto"]
        )

        if producto:
            movimiento["nombre_producto"] = producto[
                "nombre_producto"
            ]

            movimiento["numero_producto"] = producto[
                "numero_producto"
            ]

            movimiento["unidad_de_medida"] = producto.get(
                "unidad_de_medida"
            )

        movimiento["nombre_responsable"] = (
            usuarios_por_id.get(
                movimiento.get("id_usuario")
            )
        )

    return movimientos
