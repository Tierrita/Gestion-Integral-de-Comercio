
"""
Modelo de ventas.

Acceso a datos del módulo de ventas.

Todas las operaciones principales se encuentran aisladas
por comercio.

Compatible con productos por UNIDAD y KG.

Route → Controller → Service → Model → Supabase
"""

from decimal import Decimal

from core.supabase_client import get_client


# ==================================================
# UTILIDADES
# ==================================================

def _numero_json(valor):
    """
    Convierte valores Decimal a números compatibles
    con el cliente JSON de Supabase.

    Las validaciones se realizan en el Service.
    """

    if isinstance(valor, Decimal):
        return float(valor)

    return valor


def _preparar_datos(datos):
    """
    Convierte los valores Decimal de un diccionario
    sin modificar el objeto original.
    """

    return {
        clave: _numero_json(valor)
        for clave, valor in datos.items()
    }


# ==================================================
# REGISTRAR VENTA
# ==================================================

def insertar_venta(datos):
    """Inserta una nueva venta."""

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .insert(_preparar_datos(datos))
        .execute()
    )

    return response.data


def insertar_detalle_venta(datos):
    """
    Inserta un detalle de venta.

    La cantidad admite decimales cuando el producto
    se comercializa por KG.
    """

    supabase = get_client()

    response = (
        supabase
        .table("detalle_venta")
        .insert(_preparar_datos(datos))
        .execute()
    )

    return response.data


# ==================================================
# NUMERACIÓN LOCAL
# ==================================================

def obtener_siguiente_numero_venta(id_comercio):
    """
    Obtiene el siguiente número local de venta
    para el comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .rpc(
            "obtener_siguiente_numero",
            {
                "p_id_comercio": id_comercio,
                "p_entidad": "VENTA"
            }
        )
        .execute()
    )

    return response.data


# ==================================================
# CLIENTES
# ==================================================

def obtener_cliente_por_id(id_cliente, id_comercio):
    """
    Obtiene un cliente únicamente si pertenece
    al comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("clientes")
        .select(
            "id_cliente, numero_cliente, nombre_completo, "
            "estado, id_comercio"
        )
        .eq("id_cliente", id_cliente)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None


# ==================================================
# PRODUCTOS
# ==================================================

def obtener_producto_por_id(id_producto, id_comercio):
    """
    Obtiene un producto únicamente dentro
    del comercio indicado.

    Incluye unidad_de_medida para validar cantidades
    enteras o decimales desde el Service.
    """

    supabase = get_client()

    response = (
        supabase
        .table("productos")
        .select(
            "id_producto, numero_producto, nombre_producto, "
            "stock, stock_minimo, unidad_de_medida, "
            "precio_costo, precio_venta, estado, id_comercio"
        )
        .eq("id_producto", id_producto)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None


# ==================================================
# CUENTAS FINANCIERAS
# ==================================================

def obtener_cuenta_por_id(id_cuenta, id_comercio):
    """
    Obtiene una cuenta financiera únicamente
    dentro del comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("cuentas")
        .select(
            "id_cuenta, nombre_cuenta, saldo, estado, id_comercio"
        )
        .eq("id_cuenta", id_cuenta)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None


# ==================================================
# ACTUALIZAR STOCK
# ==================================================

def actualizar_stock_producto(
    id_producto,
    id_comercio,
    nuevo_stock
):
    """
    Actualiza el stock solamente si el producto
    pertenece al comercio indicado.

    Admite cantidades enteras o decimales
    previamente validadas por el Service.
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


# ==================================================
# HISTORIAL DE STOCK
# ==================================================

def registrar_movimiento_stock(datos):
    """
    Registra un movimiento en historial_movimiento.

    Admite cantidades decimales sin truncarlas
    a números enteros.
    """

    supabase = get_client()

    response = (
        supabase
        .table("historial_movimiento")
        .insert(_preparar_datos(datos))
        .execute()
    )

    return response.data


# ==================================================
# CONSULTAR VENTAS
# ==================================================

def obtener_ventas(id_comercio):
    """
    Obtiene únicamente las ventas pertenecientes
    al comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .select("*")
        .eq("id_comercio", id_comercio)
        .order("numero_venta", desc=True)
        .execute()
    )

    return response.data


def obtener_venta_por_id(id_venta, id_comercio):
    """
    Obtiene una venta únicamente si pertenece
    al comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .select("*")
        .eq("id_venta", id_venta)
        .eq("id_comercio", id_comercio)
        .limit(1)
        .execute()
    )

    return response.data[0] if response.data else None


def obtener_detalles_venta(id_venta):
    """
    Obtiene los detalles asociados a una venta.

    El Service debe verificar previamente que
    la venta pertenece al comercio autenticado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("detalle_venta")
        .select("*")
        .eq("id_venta", id_venta)
        .order("id_detalle_venta")
        .execute()
    )

    return response.data


# ==================================================
# ANULAR VENTA
# ==================================================

def actualizar_estado_venta(
    id_venta,
    id_comercio,
    nuevo_estado
):
    """
    Actualiza el estado de una venta únicamente
    dentro del comercio indicado.
    """

    supabase = get_client()

    response = (
        supabase
        .table("ventas")
        .update({
            "estado": nuevo_estado
        })
        .eq("id_venta", id_venta)
        .eq("id_comercio", id_comercio)
        .execute()
    )

    return response.data[0] if response.data else None


# ==================================================
# COMPATIBILIDAD CON MÓDULO FINANCIERO
# ==================================================

def obtener_ventas_por_cliente(id_cliente, id_comercio=None):
    """
    Obtiene las ventas asociadas a un cliente.

    Se mantiene compatible con los módulos financieros
    existentes.

    Si se proporciona id_comercio, también aplica
    aislamiento multicomercio.

    IMPORTANTE:
    Los nuevos consumidores deben proporcionar
    id_comercio para garantizar el aislamiento.
    """

    supabase = get_client()

    consulta = (
        supabase
        .table("ventas")
        .select("*")
        .eq("id_cliente", id_cliente)
    )

    if id_comercio is not None:
        consulta = consulta.eq(
            "id_comercio",
            id_comercio
        )

    response = (
        consulta
        .order("fecha_venta", desc=True)
        .execute()
    )

    return response.data


# ==================================================
# REGISTRAR INGRESO FINANCIERO
# ==================================================

def registrar_ingreso_venta_rpc(
    id_venta,
    id_cuenta,
    id_usuario,
    monto
):
    """
    Registra mediante RPC el ingreso financiero
    correspondiente a una venta cobrada.

    Conserva el contrato de la función PostgreSQL
    registrar_ingreso_venta.
    """

    supabase = get_client()

    parametros = {
        "p_id_venta": id_venta,
        "p_id_cuenta": id_cuenta,
        "p_id_usuario": id_usuario,
        "p_monto": _numero_json(monto)
    }

    try:
        response = (
            supabase
            .rpc(
                "registrar_ingreso_venta",
                parametros
            )
            .execute()
        )

        return response.data

    except Exception as error:
        mensaje = str(error)

        errores_conocidos = [
            "Cuenta no encontrada",
            "La cuenta se encuentra inactiva",
            "El monto debe ser mayor que cero"
        ]

        for error_conocido in errores_conocidos:
            if error_conocido in mensaje:
                raise ValueError(
                    error_conocido
                )

        raise


# ==================================================
# ANULAR INGRESO FINANCIERO
# ==================================================

def anular_ingreso_venta_rpc(
    id_venta,
    id_usuario
):
    """
    Revierte mediante RPC el ingreso financiero
    generado por una venta.

    El id_usuario corresponde al usuario que realiza
    la anulación, no al usuario que creó la venta.

    Conserva el contrato de la función PostgreSQL
    anular_ingreso_venta.
    """

    supabase = get_client()

    parametros = {
        "p_id_venta": id_venta,
        "p_id_usuario": id_usuario
    }

    try:
        response = (
            supabase
            .rpc(
                "anular_ingreso_venta",
                parametros
            )
            .execute()
        )

        return response.data

    except Exception as error:
        mensaje = str(error)

        errores_conocidos = [
            "El ingreso de esta venta ya fue anulado",
            "Cuenta no encontrada",
            "Saldo insuficiente en la cuenta para anular la venta"
        ]

        for error_conocido in errores_conocidos:
            if error_conocido in mensaje:
                raise ValueError(
                    error_conocido
                )

        raise
