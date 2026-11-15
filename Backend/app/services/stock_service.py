"""
Servicio de stock.

Este módulo contiene la lógica de negocio relacionada
con el manejo del stock.

Todas las operaciones se realizan dentro del comercio
del usuario autenticado.
"""

from app.models.stock_model import (
    obtener_stock_producto,
    registrar_ajuste_stock,
    obtener_stock_general
)


def ajustar_stock(
    id_producto,
    cantidad,
    tipo_ajuste,
    id_usuario,
    id_comercio,
    observaciones,
    stock_esperado=None,
):
    """
    Realiza un ajuste manual de stock.

    El usuario y el comercio son obtenidos desde
    la autenticación JWT y no desde el cliente.
    """

    # Validar cantidad.
    # bool hereda de int en Python, por eso se rechaza
    # explícitamente para no aceptar true/false como cantidad.
    if isinstance(cantidad, bool) or not isinstance(cantidad, int):
        raise ValueError(
            "La cantidad debe ser un número entero"
        )

    if cantidad <= 0:
        raise ValueError(
            "La cantidad debe ser mayor a 0"
        )

    # Validar tipo de ajuste
    if not isinstance(tipo_ajuste, str):
        raise ValueError(
            "El tipo de ajuste debe ser texto"
        )

    tipo_ajuste = tipo_ajuste.strip().upper()

    if tipo_ajuste not in ("AUMENTAR", "DISMINUIR"):
        raise ValueError(
            "Tipo de ajuste inválido. "
            "Debe ser AUMENTAR o DISMINUIR"
        )

    if not isinstance(observaciones, str) or len(observaciones.strip()) < 5:
        raise ValueError("El motivo debe tener al menos 5 caracteres")

    if stock_esperado is not None and type(stock_esperado) is not int:
        raise ValueError("El stock esperado debe ser un número entero")

    # Buscar el producto dentro del comercio autenticado
    producto = obtener_stock_producto(
        id_producto,
        id_comercio
    )

    if not producto:
        raise ValueError(
            "Producto no encontrado"
        )

    # No permitir ajustes manuales sobre productos inactivos
    if producto.get("estado") is False:
        raise ValueError(
            "No se puede ajustar el stock de un producto inactivo"
        )

    stock_actual = producto.get("stock")

    if stock_actual is None:
        raise ValueError(
            "El producto no posee un stock válido"
        )

    # Calcular nuevo stock
    if tipo_ajuste == "AUMENTAR":
        nuevo_stock = stock_actual + cantidad
        tipo_movimiento = "AJUSTE_ENTRADA"

    else:
        nuevo_stock = stock_actual - cantidad
        tipo_movimiento = "AJUSTE_SALIDA"

    # Evitar stock negativo
    if nuevo_stock < 0:
        raise ValueError(
            "El stock no puede quedar negativo"
        )

    referencia = stock_actual if stock_esperado is None else stock_esperado
    if referencia != stock_actual:
        return None

    return registrar_ajuste_stock({
        "p_id_producto": id_producto,
        "p_id_comercio": id_comercio,
        "p_id_usuario": id_usuario,
        "p_stock_anterior": referencia,
        "p_stock_nuevo": nuevo_stock,
        "p_cantidad": cantidad,
        "p_tipo": tipo_movimiento,
        "p_observaciones": observaciones.strip(),
    })


def consultar_stock_general(id_comercio, buscar=None):
    """
    Devuelve el stock correspondiente al comercio autenticado.

    Si se recibe ?buscar= permite filtrar por nombre.
    """

    if buscar is not None:
        if not isinstance(buscar, str):
            raise ValueError(
                "El parámetro de búsqueda debe ser texto"
            )

        buscar = buscar.strip()

        if not buscar:
            buscar = None

    return obtener_stock_general(
        id_comercio,
        buscar
    )


def consultar_alertas_stock(id_comercio):
    """
    Devuelve los productos activos cuyo stock
    se encuentra en el mínimo o por debajo.

    Solamente analiza productos pertenecientes
    al comercio autenticado.
    """

    productos = obtener_stock_general(
        id_comercio
    )

    alertas = []

    for producto in productos:

        # Los productos inactivos no deben generar
        # alertas operativas de stock.
        if producto.get("estado") is False:
            continue

        stock = producto.get("stock")
        stock_minimo = producto.get("stock_minimo")

        if stock is None or stock_minimo is None:
            continue

        if stock <= stock_minimo:
            alertas.append(producto)

    return alertas