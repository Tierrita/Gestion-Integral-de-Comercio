"""Servicio de compras: validación de entrada y operaciones atómicas mediante RPC."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from app.utils.cantidades import validar_cantidad
from app.models.compra_model import (
    obtener_proveedor_por_id,
    obtener_producto_por_id,
    obtener_compras,
    obtener_compra_por_id,
    obtener_detalles_compra,
    registrar_compra_rpc,
    anular_compra_rpc,
)

def _es_entero_positivo(valor):
    return (
        isinstance(valor, int)
        and not isinstance(valor, bool)
        and valor > 0
    )


def _decimal_precio(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float, str, Decimal)):
        raise ValueError(f"El {nombre} debe ser numérico")
    try:
        numero = Decimal(str(valor))
    except InvalidOperation:
        raise ValueError(f"El {nombre} debe ser numérico")
    if not numero.is_finite():
        raise ValueError(f"El {nombre} debe ser finito")
    return numero


def _dinero(valor):
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _json_numero(valor):
    """Convierte Decimal a número compatible con el cliente Supabase/JSON."""
    return float(valor)


def crear_compra(datos, id_comercio, id_usuario):
    """
    Registra una compra dentro del comercio autenticado.

    id_comercio e id_usuario provienen del JWT y nunca
    del Body enviado por el frontend.
    """

    if not datos or not isinstance(datos, dict):
        raise ValueError("No se enviaron datos de la compra")

    id_proveedor = datos.get("id_proveedor")
    productos = datos.get("productos")

    if not _es_entero_positivo(id_proveedor):
        raise ValueError(
            "El id_proveedor debe ser un número entero mayor que cero"
        )

    if not isinstance(productos, list) or len(productos) == 0:
        raise ValueError(
            "La compra debe contener al menos un producto"
        )

    # --------------------------------------------------
    # VALIDAR PROVEEDOR
    # --------------------------------------------------

    proveedor = obtener_proveedor_por_id(
        id_proveedor,
        id_comercio
    )

    if not proveedor:
        raise ValueError(
            "Proveedor no encontrado en el comercio autenticado"
        )

    if not proveedor.get("estado"):
        raise ValueError(
            "No se puede registrar una compra con un proveedor inactivo"
        )

    # --------------------------------------------------
    # PREPARAR PRODUCTOS
    # --------------------------------------------------

    detalles = []
    ids_productos = set()

    for producto_compra in productos:

        if not isinstance(producto_compra, dict):
            raise ValueError(
                "Cada producto de la compra debe ser un objeto válido"
            )

        id_producto = producto_compra.get("id_producto")
        cantidad = producto_compra.get("cantidad")
        precio_unitario = producto_compra.get("precio_unitario")

        if not _es_entero_positivo(id_producto):
            raise ValueError(
                "El id_producto debe ser un número entero mayor que cero"
            )

        if id_producto in ids_productos:
            raise ValueError(
                f"El producto con ID {id_producto} está repetido en la compra"
            )

        ids_productos.add(id_producto)

        precio_compra = _decimal_precio(precio_unitario, "precio unitario")
        if precio_compra <= 0:
            raise ValueError("El precio unitario debe ser mayor a 0")

        # --------------------------------------------------
        # PRODUCTO DEL MISMO COMERCIO
        # --------------------------------------------------

        producto_actual = obtener_producto_por_id(
            id_producto,
            id_comercio
        )

        if not producto_actual:
            raise ValueError(
                f"El producto con ID {id_producto} no existe "
                f"en el comercio autenticado"
            )

        if not producto_actual.get("estado"):
            raise ValueError(
                f"El producto {producto_actual['nombre_producto']} "
                f"se encuentra inactivo"
            )

        unidad = str(producto_actual.get("unidad_de_medida", "")).strip().upper()
        cantidad = validar_cantidad(cantidad, unidad)
        stock_actual = validar_cantidad(
            producto_actual["stock"], unidad, permitir_cero=True
        )

        if producto_actual.get("precio_costo") is None:
            raise ValueError(
                f"El producto {producto_actual['nombre_producto']} "
                f"no posee precio de costo"
            )

        if producto_actual.get("precio_venta") is None:
            raise ValueError(
                f"El producto {producto_actual['nombre_producto']} "
                f"no posee precio de venta"
            )

        costo_actual = _decimal_precio(producto_actual["precio_costo"], "costo actual")
        precio_venta_actual = _decimal_precio(
            producto_actual["precio_venta"], "precio de venta"
        )

        detalles.append({
            "id_producto": id_producto,
            "cantidad": _json_numero(cantidad),
            "precio_unitario": _json_numero(precio_compra),
        })

    resultado = registrar_compra_rpc(
        id_comercio=id_comercio,
        id_usuario=id_usuario,
        id_proveedor=id_proveedor,
        productos=detalles,
        observaciones=datos.get("observaciones"),
    )
    if not isinstance(resultado, dict) or not resultado.get("compra"):
        raise RuntimeError("La RPC de registro no devolvió una compra válida")
    return resultado


def listar_compras(id_comercio):
    """
    Lista solamente compras del comercio autenticado.
    """

    return obtener_compras(id_comercio)


def buscar_compra_por_id(id_compra, id_comercio):
    """
    Busca una compra dentro del comercio autenticado.
    """

    compra = obtener_compra_por_id(
        id_compra,
        id_comercio
    )

    if not compra:
        raise ValueError(
            "Compra no encontrada"
        )

    detalles = obtener_detalles_compra(
        id_compra
    )

    return {
        "compra": compra,
        "detalles": detalles
    }


def anular_compra(id_compra, id_comercio, id_usuario_anulacion):
    """Anula la compra de forma atómica. La ruta exige propietario."""
    if not _es_entero_positivo(id_compra):
        raise ValueError("El id_compra debe ser un entero positivo")
    resultado = anular_compra_rpc(id_compra, id_comercio, id_usuario_anulacion)
    if not isinstance(resultado, dict) or not resultado.get("compra"):
        raise RuntimeError("La RPC de anulación no devolvió una compra válida")
    return resultado
