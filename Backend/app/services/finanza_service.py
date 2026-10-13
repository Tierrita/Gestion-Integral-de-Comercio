"""
Servicio de finanzas.

Este módulo contiene la lógica de negocio relacionada
con los indicadores financieros del sistema.

Service → Model
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


from app.models.finanza_model import (
    obtener_ventas_completadas,
    obtener_movimientos_financieros,
    obtener_compras_completadas
)

from app.models.proveedor_model import (
    obtener_proveedores
)

from app.services.pago_proveedor_service import (
    consultar_saldo_proveedor
)

from app.services.cobro_service import (
    consultar_saldo_cliente
)

from app.models.producto_model import (
    obtener_productos
)


# ======================================================
# CONFIGURACIÓN
# ======================================================

ZONA_HORARIA = ZoneInfo("America/Argentina/Buenos_Aires")


# ======================================================
# FUNCIONES AUXILIARES
# ======================================================

def _convertir_fecha_supabase(fecha_texto):
    """
    Convierte una fecha recibida desde Supabase a datetime.

    Soporta:
    - Fechas terminadas en Z.
    - Fechas con zona horaria +00:00.
    - Fechas con microsegundos.
    - Fechas sin microsegundos.

    Finalmente convierte la fecha al horario de Argentina.
    """

    if not fecha_texto:
        raise ValueError("La fecha recibida desde Supabase está vacía")

    fecha_texto = fecha_texto.strip()

    # Supabase puede representar UTC utilizando Z.
    if fecha_texto.endswith("Z"):
        fecha_texto = fecha_texto[:-1] + "+00:00"

    formatos = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
    ]

    fecha = None

    for formato in formatos:
        try:
            fecha = datetime.strptime(fecha_texto, formato)
            break
        except ValueError:
            continue

    if fecha is None:
        raise ValueError(
            f"Formato de fecha no reconocido: '{fecha_texto}'"
        )

    return fecha.astimezone(ZONA_HORARIA)


def _obtener_rango_periodo(
    periodo=None,
    desde=None,
    hasta=None
):
    """
    Obtiene el rango de fechas correspondiente
    al período solicitado.

    Períodos disponibles:
    - hoy
    - semana
    - mes
    - anio
    - personalizado

    Si no se especifica período, utiliza el mes actual.
    """

    ahora = datetime.now(ZONA_HORARIA)

    # --------------------------------------------------
    # PERÍODO PERSONALIZADO
    # --------------------------------------------------

    if desde or hasta:

        if not desde or not hasta:
            raise ValueError(
                "Para un período personalizado debe indicar "
                "'desde' y 'hasta'"
            )

        try:
            fecha_desde = datetime.strptime(
                desde,
                "%Y-%m-%d"
            ).replace(
                tzinfo=ZONA_HORARIA
            )

            fecha_hasta = datetime.strptime(
                hasta,
                "%Y-%m-%d"
            ).replace(
                tzinfo=ZONA_HORARIA
            )

        except ValueError:
            raise ValueError(
                "Las fechas deben tener formato YYYY-MM-DD"
            )

        if fecha_desde > fecha_hasta:
            raise ValueError(
                "La fecha 'desde' no puede ser mayor que 'hasta'"
            )

        # El límite superior es exclusivo.
        fecha_hasta += timedelta(days=1)

        return (
            "personalizado",
            fecha_desde,
            fecha_hasta
        )

    # --------------------------------------------------
    # PERÍODO POR DEFECTO
    # --------------------------------------------------

    if periodo is None:
        periodo = "mes"

    periodo = periodo.lower()

    # --------------------------------------------------
    # HOY
    # --------------------------------------------------

    if periodo == "hoy":

        fecha_desde = ahora.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        fecha_hasta = fecha_desde + timedelta(days=1)

    # --------------------------------------------------
    # SEMANA
    # --------------------------------------------------

    elif periodo == "semana":

        fecha_desde = (
            ahora - timedelta(days=ahora.weekday())
        ).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        fecha_hasta = fecha_desde + timedelta(days=7)

    # --------------------------------------------------
    # MES
    # --------------------------------------------------

    elif periodo == "mes":

        fecha_desde = ahora.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        if fecha_desde.month == 12:

            fecha_hasta = fecha_desde.replace(
                year=fecha_desde.year + 1,
                month=1
            )

        else:

            fecha_hasta = fecha_desde.replace(
                month=fecha_desde.month + 1
            )

    # --------------------------------------------------
    # AÑO
    # --------------------------------------------------

    elif periodo == "anio":

        fecha_desde = ahora.replace(
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        fecha_hasta = fecha_desde.replace(
            year=fecha_desde.year + 1
        )

    else:

        raise ValueError(
            "Período inválido. "
            "Valores permitidos: hoy, semana, mes, anio"
        )

    return (
        periodo,
        fecha_desde,
        fecha_hasta
    )


def _crear_periodo_respuesta(
    tipo_periodo,
    fecha_desde,
    fecha_hasta
):
    """
    Genera el objeto período utilizado
    en las respuestas del módulo financiero.
    """

    return {
        "tipo": tipo_periodo,
        "desde": fecha_desde.date().isoformat(),
        "hasta": (
            fecha_hasta - timedelta(microseconds=1)
        ).date().isoformat()
    }


# ======================================================
# RENTABILIDAD
# ======================================================

def calcular_rentabilidad(
    periodo=None,
    desde=None,
    hasta=None
):
    """
    Calcula la rentabilidad del negocio para
    el período solicitado.

    Indicadores:
    - Facturación.
    - Costo de lo vendido.
    - Ganancia bruta.
    - Margen bruto.
    - Cantidad de ventas.

    Si existen ventas antiguas sin costo histórico,
    la rentabilidad no se calcula para evitar
    mostrar información incorrecta.
    """

    tipo_periodo, fecha_desde, fecha_hasta = (
        _obtener_rango_periodo(
            periodo,
            desde,
            hasta
        )
    )

    ventas = obtener_ventas_completadas(
        fecha_desde.isoformat(),
        fecha_hasta.isoformat()
    )

    facturacion = 0.0
    costo_vendido = 0.0

    detalles_sin_costo_historico = 0

    # --------------------------------------------------
    # PROCESAR VENTAS
    # --------------------------------------------------

    for venta in ventas:

        facturacion += float(
            venta.get("total", 0)
        )

        detalles = venta.get(
            "detalle_venta",
            []
        )

        for detalle in detalles:

            costo_unitario = detalle.get(
                "costo_unitario"
            )

            if costo_unitario is None:

                detalles_sin_costo_historico += 1
                continue

            cantidad = int(
                detalle.get("cantidad", 0)
            )

            costo_vendido += (
                float(costo_unitario)
                * cantidad
            )

    cantidad_ventas = len(ventas)

    periodo_respuesta = _crear_periodo_respuesta(
        tipo_periodo,
        fecha_desde,
        fecha_hasta
    )

    # --------------------------------------------------
    # VENTAS ANTIGUAS SIN COSTO HISTÓRICO
    # --------------------------------------------------

    if detalles_sin_costo_historico > 0:

        return {
            "periodo": periodo_respuesta,
            "facturacion": round(
                facturacion,
                2
            ),
            "costo_vendido": None,
            "ganancia_bruta": None,
            "margen_bruto": None,
            "cantidad_ventas": cantidad_ventas,
            "rentabilidad_calculable": False,
            "detalles_sin_costo_historico":
                detalles_sin_costo_historico,
            "advertencia": (
                "Existen ventas sin costo histórico. "
                "La rentabilidad no puede calcularse "
                "de forma confiable para este período."
            )
        }

    # --------------------------------------------------
    # RENTABILIDAD
    # --------------------------------------------------

    ganancia_bruta = (
        facturacion - costo_vendido
    )

    if facturacion > 0:

        margen_bruto = (
            ganancia_bruta
            / facturacion
        ) * 100

    else:

        margen_bruto = 0.0

    return {
        "periodo": periodo_respuesta,
        "facturacion": round(
            facturacion,
            2
        ),
        "costo_vendido": round(
            costo_vendido,
            2
        ),
        "ganancia_bruta": round(
            ganancia_bruta,
            2
        ),
        "margen_bruto": round(
            margen_bruto,
            2
        ),
        "cantidad_ventas": cantidad_ventas,
        "rentabilidad_calculable": True,
        "detalles_sin_costo_historico": 0
    }


# ======================================================
# CAJA
# ======================================================

def calcular_caja(
    periodo=None,
    desde=None,
    hasta=None
):
    """
    Calcula los movimientos de caja correspondientes
    al período solicitado.

    Entradas:
    - VENTA
    - COBRO
    - AJUSTE_ENTRADA

    Salidas:
    - ANULACION_VENTA
    - ANULACION_COBRO
    - AJUSTE_SALIDA
    """

    tipo_periodo, fecha_desde, fecha_hasta = (
        _obtener_rango_periodo(
            periodo,
            desde,
            hasta
        )
    )

    movimientos = obtener_movimientos_financieros(
        fecha_desde,
        fecha_hasta
    )

    # --------------------------------------------------
    # ACUMULADORES
    # --------------------------------------------------

    total_entradas = 0.0
    total_salidas = 0.0

    cantidad_entradas = 0
    cantidad_salidas = 0

    ventas_cobradas = 0.0
    cobros_clientes = 0.0
    ajustes_entrada = 0.0

    anulaciones_venta = 0.0
    anulaciones_cobro = 0.0
    ajustes_salida = 0.0

    # --------------------------------------------------
    # PROCESAR MOVIMIENTOS
    # --------------------------------------------------

    for movimiento in movimientos:

        tipo = movimiento.get(
            "tipo_movimiento"
        )

        monto = float(
            movimiento.get("monto", 0)
        )

        # ==============================================
        # ENTRADAS
        # ==============================================

        if tipo == "VENTA":

            total_entradas += monto
            cantidad_entradas += 1

            ventas_cobradas += monto

        elif tipo == "COBRO":

            total_entradas += monto
            cantidad_entradas += 1

            cobros_clientes += monto

        elif tipo == "AJUSTE_ENTRADA":

            total_entradas += monto
            cantidad_entradas += 1

            ajustes_entrada += monto

        # ==============================================
        # SALIDAS
        # ==============================================

        elif tipo == "ANULACION_VENTA":

            total_salidas += monto
            cantidad_salidas += 1

            anulaciones_venta += monto

        elif tipo == "ANULACION_COBRO":

            total_salidas += monto
            cantidad_salidas += 1

            anulaciones_cobro += monto

        elif tipo == "AJUSTE_SALIDA":

            total_salidas += monto
            cantidad_salidas += 1

            ajustes_salida += monto

    saldo_neto = (
        total_entradas - total_salidas
    )

    periodo_respuesta = _crear_periodo_respuesta(
        tipo_periodo,
        fecha_desde,
        fecha_hasta
    )

    return {
        "periodo": periodo_respuesta,

        "total_entradas": round(
            total_entradas,
            2
        ),

        "total_salidas": round(
            total_salidas,
            2
        ),

        "saldo_neto": round(
            saldo_neto,
            2
        ),

        "cantidad_entradas":
            cantidad_entradas,

        "cantidad_salidas":
            cantidad_salidas,

        "desglose": {

            "entradas": {
                "ventas_cobradas": round(
                    ventas_cobradas,
                    2
                ),
                "cobros_clientes": round(
                    cobros_clientes,
                    2
                ),
                "ajustes_entrada": round(
                    ajustes_entrada,
                    2
                )
            },

            "salidas": {
                "anulaciones_venta": round(
                    anulaciones_venta,
                    2
                ),
                "anulaciones_cobro": round(
                    anulaciones_cobro,
                    2
                ),
                "ajustes_salida": round(
                    ajustes_salida,
                    2
                )
            }
        }
    }


# ======================================================
# ESTADÍSTICAS DE VENTAS
# ======================================================

def calcular_estadisticas_ventas(
    periodo=None,
    desde=None,
    hasta=None
):
    """
    Calcula las estadísticas generales de ventas.

    Indicadores:
    - Facturación.
    - Cantidad de ventas.
    - Ticket promedio.
    - Unidades vendidas.
    """

    tipo_periodo, fecha_desde, fecha_hasta = (
        _obtener_rango_periodo(
            periodo,
            desde,
            hasta
        )
    )

    ventas = obtener_ventas_completadas(
        fecha_desde.isoformat(),
        fecha_hasta.isoformat()
    )

    facturacion = 0.0
    unidades_vendidas = 0

    # --------------------------------------------------
    # PROCESAR VENTAS
    # --------------------------------------------------

    for venta in ventas:

        facturacion += float(
            venta["total"]
        )

        for detalle in venta.get(
            "detalle_venta",
            []
        ):

            unidades_vendidas += int(
                detalle["cantidad"]
            )

    cantidad_ventas = len(ventas)

    # --------------------------------------------------
    # TICKET PROMEDIO
    # --------------------------------------------------

    if cantidad_ventas > 0:

        ticket_promedio = (
            facturacion
            / cantidad_ventas
        )

    else:

        ticket_promedio = 0.0

    periodo_respuesta = _crear_periodo_respuesta(
        tipo_periodo,
        fecha_desde,
        fecha_hasta
    )

    return {
        "periodo": periodo_respuesta,
        "facturacion": round(
            facturacion,
            2
        ),
        "cantidad_ventas":
            cantidad_ventas,
        "ticket_promedio": round(
            ticket_promedio,
            2
        ),
        "unidades_vendidas":
            unidades_vendidas
    }


# ======================================================
# EVOLUCIÓN DE VENTAS
# ======================================================

def calcular_evolucion_ventas(
    periodo=None,
    desde=None,
    hasta=None
):
    """
    Calcula la evolución de las ventas dentro
    del período seleccionado.

    Agrupación:
    - Hoy: por hora.
    - Semana: por día.
    - Mes: por día.
    - Año: por mes.
    - Personalizado: por día.

    Cada punto contiene:
    - Facturación.
    - Cantidad de ventas.
    - Unidades vendidas.
    """

    tipo_periodo, fecha_desde, fecha_hasta = (
        _obtener_rango_periodo(
            periodo,
            desde,
            hasta
        )
    )

    ventas = obtener_ventas_completadas(
        fecha_desde.isoformat(),
        fecha_hasta.isoformat()
    )

    evolucion = {}

    # --------------------------------------------------
    # PROCESAR VENTAS
    # --------------------------------------------------

    for venta in ventas:

        # Conversión robusta de la fecha recibida
        # desde Supabase.
        fecha_venta = _convertir_fecha_supabase(
            venta["fecha_venta"]
        )

        # --------------------------------------------------
        # DETERMINAR AGRUPACIÓN
        # --------------------------------------------------

        if tipo_periodo == "hoy":

            clave = fecha_venta.strftime(
                "%H:00"
            )

        elif tipo_periodo == "anio":

            clave = fecha_venta.strftime(
                "%Y-%m"
            )

        else:

            # Semana, mes y personalizado.
            clave = fecha_venta.strftime(
                "%Y-%m-%d"
            )

        # --------------------------------------------------
        # CREAR GRUPO
        # --------------------------------------------------

        if clave not in evolucion:

            evolucion[clave] = {
                "facturacion": 0.0,
                "cantidad_ventas": 0,
                "unidades_vendidas": 0
            }

        # --------------------------------------------------
        # FACTURACIÓN
        # --------------------------------------------------

        evolucion[clave]["facturacion"] += float(
            venta.get("total", 0)
        )

        # Cada registro representa una venta.
        evolucion[clave]["cantidad_ventas"] += 1

        # --------------------------------------------------
        # UNIDADES
        # --------------------------------------------------

        for detalle in venta.get(
            "detalle_venta",
            []
        ):

            evolucion[clave][
                "unidades_vendidas"
            ] += int(
                detalle.get(
                    "cantidad",
                    0
                )
            )

    # --------------------------------------------------
    # CONVERTIR DICCIONARIO A LISTA
    # --------------------------------------------------

    datos = []

    for clave in sorted(evolucion.keys()):

        datos.append({
            "periodo": clave,
            "facturacion": round(
                evolucion[clave][
                    "facturacion"
                ],
                2
            ),
            "cantidad_ventas":
                evolucion[clave][
                    "cantidad_ventas"
                ],
            "unidades_vendidas":
                evolucion[clave][
                    "unidades_vendidas"
                ]
        })

    periodo_respuesta = _crear_periodo_respuesta(
        tipo_periodo,
        fecha_desde,
        fecha_hasta
    )

    # --------------------------------------------------
    # TIPO DE AGRUPACIÓN
    # --------------------------------------------------

    if tipo_periodo == "hoy":
        agrupacion = "hora"

    elif tipo_periodo == "anio":
        agrupacion = "mes"

    else:
        agrupacion = "dia"

    return {
        "periodo": periodo_respuesta,
        "agrupacion": agrupacion,
        "evolucion": datos
    }




# ======================================================
# ESTADÍSTICAS DE PRODUCTOS
# ======================================================

def calcular_estadisticas_productos(
    periodo=None,
    desde=None,
    hasta=None
):
    """
    Calcula las estadísticas financieras de los productos
    vendidos durante el período solicitado.

    Genera rankings de:
    - Más vendidos.
    - Mayor facturación.
    - Mayor ganancia bruta.
    - Mayor margen bruto.
    - Menos vendidos.

    La rentabilidad utiliza el costo histórico almacenado
    en detalle_venta.costo_unitario.
    """

    tipo_periodo, fecha_desde, fecha_hasta = (
        _obtener_rango_periodo(
            periodo,
            desde,
            hasta
        )
    )

    ventas = obtener_ventas_completadas(
        fecha_desde.isoformat(),
        fecha_hasta.isoformat()
    )

    productos = {}

    # --------------------------------------------------
    # PROCESAR VENTAS
    # --------------------------------------------------

    for venta in ventas:

        for detalle in venta.get(
            "detalle_venta",
            []
        ):

            id_producto = detalle.get(
                "id_producto"
            )

            cantidad = int(
                detalle.get("cantidad", 0)
            )

            subtotal = float(
                detalle.get("subtotal", 0)
            )

            costo_unitario = detalle.get(
                "costo_unitario"
            )

            producto_relacionado = detalle.get(
                "productos"
            ) or {}

            nombre_producto = producto_relacionado.get(
                "nombre_producto",
                f"Producto {id_producto}"
            )

            # ------------------------------------------
            # CREAR PRODUCTO
            # ------------------------------------------

            if id_producto not in productos:

                productos[id_producto] = {
                    "id_producto": id_producto,
                    "nombre_producto": nombre_producto,
                    "cantidad_vendida": 0,
                    "facturacion": 0.0,
                    "costo_vendido": 0.0,
                    "detalles_sin_costo_historico": 0
                }

            producto = productos[id_producto]

            # ------------------------------------------
            # CANTIDAD Y FACTURACIÓN
            # ------------------------------------------

            producto["cantidad_vendida"] += cantidad

            producto["facturacion"] += subtotal

            # ------------------------------------------
            # COSTO HISTÓRICO
            # ------------------------------------------

            if costo_unitario is None:

                producto[
                    "detalles_sin_costo_historico"
                ] += 1

            else:

                producto["costo_vendido"] += (
                    float(costo_unitario)
                    * cantidad
                )

    # --------------------------------------------------
    # CALCULAR RENTABILIDAD POR PRODUCTO
    # --------------------------------------------------

    datos_productos = []

    for producto in productos.values():

        facturacion = producto["facturacion"]

        if producto[
            "detalles_sin_costo_historico"
        ] > 0:

            costo_vendido = None
            ganancia_bruta = None
            margen_bruto = None
            rentabilidad_calculable = False

        else:

            costo_vendido = producto[
                "costo_vendido"
            ]

            ganancia_bruta = (
                facturacion - costo_vendido
            )

            if facturacion > 0:

                margen_bruto = (
                    ganancia_bruta
                    / facturacion
                ) * 100

            else:

                margen_bruto = 0.0

            rentabilidad_calculable = True

        datos_productos.append({
            "id_producto":
                producto["id_producto"],

            "nombre_producto":
                producto["nombre_producto"],

            "cantidad_vendida":
                producto["cantidad_vendida"],

            "facturacion": round(
                facturacion,
                2
            ),

            "costo_vendido": (
                round(costo_vendido, 2)
                if costo_vendido is not None
                else None
            ),

            "ganancia_bruta": (
                round(ganancia_bruta, 2)
                if ganancia_bruta is not None
                else None
            ),

            "margen_bruto": (
                round(margen_bruto, 2)
                if margen_bruto is not None
                else None
            ),

            "rentabilidad_calculable":
                rentabilidad_calculable
        })

    # --------------------------------------------------
    # RANKINGS
    # --------------------------------------------------

    mas_vendidos = sorted(
        datos_productos,
        key=lambda producto:
            producto["cantidad_vendida"],
        reverse=True
    )

    mayor_facturacion = sorted(
        datos_productos,
        key=lambda producto:
            producto["facturacion"],
        reverse=True
    )

    productos_con_rentabilidad = [
        producto
        for producto in datos_productos
        if producto["rentabilidad_calculable"]
    ]

    mayor_ganancia = sorted(
        productos_con_rentabilidad,
        key=lambda producto:
            producto["ganancia_bruta"],
        reverse=True
    )

    mayor_margen = sorted(
        productos_con_rentabilidad,
        key=lambda producto:
            producto["margen_bruto"],
        reverse=True
    )

    menos_vendidos = sorted(
        datos_productos,
        key=lambda producto:
            producto["cantidad_vendida"]
    )

    periodo_respuesta = _crear_periodo_respuesta(
        tipo_periodo,
        fecha_desde,
        fecha_hasta
    )

    return {
        "periodo": periodo_respuesta,
        "cantidad_productos":
            len(datos_productos),

        "rankings": {
            "mas_vendidos":
                mas_vendidos,

            "mayor_facturacion":
                mayor_facturacion,

            "mayor_ganancia":
                mayor_ganancia,

            "mayor_margen":
                mayor_margen,

            "menos_vendidos":
                menos_vendidos
        }
    }



# ======================================================
# ESTADÍSTICAS DE PROVEEDORES
# ======================================================

def calcular_estadisticas_proveedores(
    periodo=None,
    desde=None,
    hasta=None
):
    """
    Calcula las estadísticas de compras realizadas
    a proveedores durante el período solicitado.

    También calcula:
    - Ranking de proveedores.
    - Deuda actual con proveedores.
    - Productos comprados.
    - Cantidad comprada por producto.
    - Total comprado por producto.
    - Precio promedio de compra.
    """

    # --------------------------------------------------
    # OBTENER PERÍODO
    # --------------------------------------------------

    tipo_periodo, fecha_desde, fecha_hasta = (
        _obtener_rango_periodo(
            periodo,
            desde,
            hasta
        )
    )

    # --------------------------------------------------
    # OBTENER COMPRAS DEL PERÍODO
    # --------------------------------------------------

    compras = obtener_compras_completadas(
        fecha_desde.isoformat(),
        fecha_hasta.isoformat()
    )

    proveedores = {}
    productos = {}

    total_comprado = 0.0

    # --------------------------------------------------
    # PROCESAR COMPRAS
    # --------------------------------------------------

    for compra in compras:

        id_proveedor = compra.get("id_proveedor")

        total_compra = float(
            compra.get("total_compra", 0)
        )

        proveedor_relacionado = (
            compra.get("proveedores") or {}
        )

        nombre_proveedor = proveedor_relacionado.get(
            "nombre_proveedor",
            f"Proveedor {id_proveedor}"
        )

        total_comprado += total_compra

        # ==============================================
        # PROVEEDOR
        # ==============================================

        if id_proveedor not in proveedores:

            proveedores[id_proveedor] = {
                "id_proveedor": id_proveedor,
                "nombre_proveedor": nombre_proveedor,
                "cantidad_compras": 0,
                "total_comprado": 0.0
            }

        proveedores[id_proveedor][
            "cantidad_compras"
        ] += 1

        proveedores[id_proveedor][
            "total_comprado"
        ] += total_compra

        # ==============================================
        # PRODUCTOS COMPRADOS
        # ==============================================

        detalles = compra.get(
            "detalle_compra",
            []
        )

        for detalle in detalles:

            id_producto = detalle.get(
                "id_producto"
            )

            cantidad = int(
                detalle.get("cantidad", 0)
            )

            precio_unitario = float(
                detalle.get("precio_unitario", 0)
            )

            subtotal = float(
                detalle.get("subtotal", 0)
            )

            producto_relacionado = (
                detalle.get("productos") or {}
            )

            nombre_producto = producto_relacionado.get(
                "nombre_producto",
                f"Producto {id_producto}"
            )

            # ------------------------------------------
            # CREAR PRODUCTO
            # ------------------------------------------

            if id_producto not in productos:

                productos[id_producto] = {
                    "id_producto": id_producto,
                    "nombre_producto": nombre_producto,
                    "cantidad_comprada": 0,
                    "total_comprado": 0.0,
                    "proveedores": {}
                }

            producto = productos[id_producto]

            # ------------------------------------------
            # ACUMULAR PRODUCTO
            # ------------------------------------------

            producto[
                "cantidad_comprada"
            ] += cantidad

            producto[
                "total_comprado"
            ] += subtotal

            # ------------------------------------------
            # PRODUCTO POR PROVEEDOR
            # ------------------------------------------

            if id_proveedor not in producto["proveedores"]:

                producto["proveedores"][
                    id_proveedor
                ] = {
                    "id_proveedor": id_proveedor,
                    "nombre_proveedor": nombre_proveedor,
                    "cantidad_comprada": 0,
                    "total_comprado": 0.0,
                    "ultimo_precio_compra": precio_unitario
                }

            proveedor_producto = (
                producto["proveedores"][
                    id_proveedor
                ]
            )

            proveedor_producto[
                "cantidad_comprada"
            ] += cantidad

            proveedor_producto[
                "total_comprado"
            ] += subtotal

            proveedor_producto[
                "ultimo_precio_compra"
            ] = precio_unitario


    

    # ==================================================
    # RANKING DE PROVEEDORES
    # ==================================================

    datos_proveedores = []

    for proveedor in proveedores.values():

        datos_proveedores.append({
            "id_proveedor":
                proveedor["id_proveedor"],

            "nombre_proveedor":
                proveedor["nombre_proveedor"],

            "cantidad_compras":
                proveedor["cantidad_compras"],

            "total_comprado": round(
                proveedor["total_comprado"],
                2
            )
        })

    ranking = sorted(
        datos_proveedores,
        key=lambda proveedor:
            proveedor["total_comprado"],
        reverse=True
    )

    # ==================================================
    # PRODUCTOS COMPRADOS
    # ==================================================

    productos_comprados = []

    for producto in productos.values():

        cantidad_comprada = producto[
            "cantidad_comprada"
        ]

        total_producto = producto[
            "total_comprado"
        ]

        # Precio promedio ponderado
        if cantidad_comprada > 0:

            precio_promedio_compra = (
                total_producto
                / cantidad_comprada
            )

        else:

            precio_promedio_compra = 0.0

        # ----------------------------------------------
        # PROVEEDORES DEL PRODUCTO
        # ----------------------------------------------

        proveedores_producto = []

        for proveedor_producto in (
            producto["proveedores"].values()
        ):

            cantidad_proveedor = (
                proveedor_producto[
                    "cantidad_comprada"
                ]
            )

            total_proveedor = (
                proveedor_producto[
                    "total_comprado"
                ]
            )

            if cantidad_proveedor > 0:

                precio_promedio_proveedor = (
                    total_proveedor
                    / cantidad_proveedor
                )

            else:

                precio_promedio_proveedor = 0.0

            proveedores_producto.append({
                "id_proveedor":
                    proveedor_producto[
                        "id_proveedor"
                    ],

                "nombre_proveedor":
                    proveedor_producto[
                        "nombre_proveedor"
                    ],

                "cantidad_comprada":
                    cantidad_proveedor,

                "total_comprado": round(
                    total_proveedor,
                    2
                ),

                "precio_promedio_compra": round(
                    precio_promedio_proveedor,
                    2
                ),

                "ultimo_precio_compra": round(
                    proveedor_producto[
                        "ultimo_precio_compra"
                    ],
                    2
                )
            })

        proveedores_producto = sorted(
            proveedores_producto,
            key=lambda proveedor:
                proveedor["total_comprado"],
            reverse=True
        )

        productos_comprados.append({
            "id_producto":
                producto["id_producto"],

            "nombre_producto":
                producto["nombre_producto"],

            "cantidad_comprada":
                cantidad_comprada,

            "total_comprado": round(
                total_producto,
                2
            ),

            "precio_promedio_compra": round(
                precio_promedio_compra,
                2
            ),

            "proveedores":
                proveedores_producto
        })

    # ==================================================
    # EVOLUCIÓN DE COSTOS
    # ==================================================

    evolucion_costos = {}

    for compra in compras:

        fecha_compra = compra.get(
            "fecha_compra"
        )

        id_proveedor = compra.get(
            "id_proveedor"
        )

        proveedor_relacionado = (
            compra.get("proveedores") or {}
        )

        nombre_proveedor = proveedor_relacionado.get(
            "nombre_proveedor",
            f"Proveedor {id_proveedor}"
        )

        detalles = compra.get(
            "detalle_compra",
            []
        )

        for detalle in detalles:

            id_producto = detalle.get(
                "id_producto"
            )

            precio_unitario = float(
                detalle.get(
                    "precio_unitario",
                    0
                )
            )

            producto_relacionado = (
                detalle.get("productos") or {}
            )

            nombre_producto = producto_relacionado.get(
                "nombre_producto",
                f"Producto {id_producto}"
            )

            if id_producto not in evolucion_costos:

                evolucion_costos[id_producto] = {
                    "id_producto": id_producto,
                    "nombre_producto": nombre_producto,
                    "historial": []
                }

            evolucion_costos[
                id_producto
            ]["historial"].append({
                "fecha_compra":
                    fecha_compra,

                "id_proveedor":
                    id_proveedor,

                "nombre_proveedor":
                    nombre_proveedor,

                "precio_compra": round(
                    precio_unitario,
                    2
                )
            })

    # --------------------------------------------------
    # CALCULAR VARIACIÓN POR PRODUCTO
    # --------------------------------------------------

    evolucion_costos_respuesta = []

    for producto in evolucion_costos.values():

        historial = producto[
            "historial"
        ]

        if not historial:
            continue

        primer_precio = float(
            historial[0]["precio_compra"]
        )

        ultimo_precio = float(
            historial[-1]["precio_compra"]
        )

        # ----------------------------------------------
        # VARIACIÓN PORCENTUAL
        # ----------------------------------------------

        if primer_precio > 0:

            variacion_porcentual = (
                (
                    ultimo_precio
                    - primer_precio
                )
                / primer_precio
            ) * 100

        else:

            variacion_porcentual = None

        # ----------------------------------------------
        # TENDENCIA
        # ----------------------------------------------

        if ultimo_precio > primer_precio:

            tendencia = "SUBIO"

        elif ultimo_precio < primer_precio:

            tendencia = "BAJO"

        else:

            tendencia = "SIN_CAMBIOS"

        evolucion_costos_respuesta.append({
            "id_producto":
                producto["id_producto"],

            "nombre_producto":
                producto["nombre_producto"],

            "precio_inicial": round(
                primer_precio,
                2
            ),

            "precio_final": round(
                ultimo_precio,
                2
            ),

            "variacion_porcentual": (
                round(
                    variacion_porcentual,
                    2
                )
                if variacion_porcentual is not None
                else None
            ),

            "tendencia":
                tendencia,

            "cantidad_registros":
                len(historial),

            "historial":
                historial
        })

    # ==================================================
    # DEUDA ACTUAL CON PROVEEDORES
    # ==================================================

    todos_proveedores = obtener_proveedores()

    deudas_proveedores = []

    deuda_total_proveedores = 0.0

    for proveedor in todos_proveedores:

        id_proveedor = proveedor[
            "id_proveedor"
        ]

        saldo_proveedor = (
            consultar_saldo_proveedor(
                id_proveedor
            )
        )

        saldo = float(
            saldo_proveedor["saldo"]
        )

        if saldo > 0:

            deuda_total_proveedores += saldo

            deudas_proveedores.append({
                "id_proveedor":
                    id_proveedor,

                "nombre_proveedor":
                    proveedor[
                        "nombre_proveedor"
                    ],

                "total_compras": round(
                    float(
                        saldo_proveedor[
                            "total_compras"
                        ]
                    ),
                    2
                ),

                "total_pagos": round(
                    float(
                        saldo_proveedor[
                            "total_pagos"
                        ]
                    ),
                    2
                ),

                "saldo_pendiente": round(
                    saldo,
                    2
                )
            })

    deudas_proveedores = sorted(
        deudas_proveedores,
        key=lambda proveedor:
            proveedor["saldo_pendiente"],
        reverse=True
    )

    # ==================================================
    # PERÍODO DE RESPUESTA
    # ==================================================

    periodo_respuesta = (
        _crear_periodo_respuesta(
            tipo_periodo,
            fecha_desde,
            fecha_hasta
        )
    )

    # ==================================================
    # RESPUESTA
    # ==================================================

    return {
        "periodo":
            periodo_respuesta,

        "total_comprado": round(
            total_comprado,
            2
        ),

        "cantidad_compras":
            len(compras),

        "cantidad_proveedores":
            len(datos_proveedores),

        "ranking_proveedores":
            ranking,

        "deuda_total_proveedores": round(
            deuda_total_proveedores,
            2
        ),

        "deudas_proveedores":
            deudas_proveedores,

        "cantidad_productos_comprados":
            len(productos_comprados),

        "productos_comprados":
            productos_comprados,

        "evolucion_costos":
            evolucion_costos_respuesta
    }


    # ======================================================
# ESTADÍSTICAS DE CLIENTES
# ======================================================

def calcular_estadisticas_clientes(
    periodo=None,
    desde=None,
    hasta=None
):
    """
    Calcula las estadísticas comerciales de los clientes
    durante el período solicitado.

    Indicadores:
    - Facturación por cliente.
    - Cantidad de compras.
    - Ticket promedio.
    - Ranking por facturación.
    - Ranking por cantidad de compras.
    """

    tipo_periodo, fecha_desde, fecha_hasta = (
        _obtener_rango_periodo(
            periodo,
            desde,
            hasta
        )
    )

    ventas = obtener_ventas_completadas(
        fecha_desde.isoformat(),
        fecha_hasta.isoformat()
    )

    clientes = {}

    # --------------------------------------------------
    # PROCESAR VENTAS
    # --------------------------------------------------

    for venta in ventas:

        id_cliente = venta.get(
            "id_cliente"
        )

        cliente_relacionado = (
            venta.get("clientes") or {}
        )

        nombre_cliente = cliente_relacionado.get(
            "nombre_completo",
            f"Cliente {id_cliente}"
        )

        total_venta = float(
            venta.get("total", 0)
        )

        # ----------------------------------------------
        # CREAR CLIENTE
        # ----------------------------------------------

        if id_cliente not in clientes:

            clientes[id_cliente] = {
                "id_cliente": id_cliente,
                "nombre_completo": nombre_cliente,
                "cantidad_compras": 0,
                "facturacion": 0.0
            }

        # ----------------------------------------------
        # ACUMULAR
        # ----------------------------------------------

        clientes[id_cliente][
            "cantidad_compras"
        ] += 1

        clientes[id_cliente][
            "facturacion"
        ] += total_venta

    # --------------------------------------------------
    # PREPARAR RESULTADOS
    # --------------------------------------------------

    datos_clientes = []

    for cliente in clientes.values():

        cantidad_compras = cliente[
            "cantidad_compras"
        ]

        facturacion = cliente[
            "facturacion"
        ]

        if cantidad_compras > 0:

            ticket_promedio = (
                facturacion
                / cantidad_compras
            )

        else:

            ticket_promedio = 0.0

        datos_clientes.append({
            "id_cliente":
                cliente["id_cliente"],

            "nombre_completo":
                cliente["nombre_completo"],

            "cantidad_compras":
                cantidad_compras,

            "facturacion": round(
                facturacion,
                2
            ),

            "ticket_promedio": round(
                ticket_promedio,
                2
            )
        })

    # --------------------------------------------------
    # RANKINGS
    # --------------------------------------------------

    ranking_facturacion = sorted(
        datos_clientes,
        key=lambda cliente:
            cliente["facturacion"],
        reverse=True
    )

    ranking_compras = sorted(
        datos_clientes,
        key=lambda cliente:
            cliente["cantidad_compras"],
        reverse=True
    )

    # --------------------------------------------------
    # SALDOS ACTUALES DE CLIENTES
    # --------------------------------------------------

    clientes_con_deuda = []
    total_por_cobrar = 0.0

    for cliente in datos_clientes:

        id_cliente = cliente["id_cliente"]

        # CLIENTE GENERAL siempre opera al contado
        if id_cliente == 1:
            continue

        saldo_cliente = consultar_saldo_cliente(
            id_cliente
        )

        saldo = float(
            saldo_cliente.get("saldo", 0)
        )

        situacion = saldo_cliente.get(
            "situacion"
        )

        if situacion == "DEUDA" and saldo > 0:

            clientes_con_deuda.append({
                "id_cliente":
                    id_cliente,

                "nombre_completo":
                    cliente["nombre_completo"],

                "saldo":
                    round(saldo, 2)
            })

            total_por_cobrar += saldo

    clientes_con_deuda.sort(
        key=lambda cliente: cliente["saldo"],
        reverse=True
    )

    periodo_respuesta = _crear_periodo_respuesta(
        tipo_periodo,
        fecha_desde,
        fecha_hasta
    )

    return {
        "periodo":
            periodo_respuesta,

        "cantidad_clientes":
            len(datos_clientes),

        "ranking_facturacion":
            ranking_facturacion,

        "ranking_compras":
            ranking_compras,

        "total_por_cobrar":
            round(total_por_cobrar, 2),

        "cantidad_clientes_con_deuda":
            len(clientes_con_deuda),

        "clientes_con_deuda":
            clientes_con_deuda
    }



# ======================================================
# STOCK FINANCIERO
# ======================================================

def calcular_estadisticas_stock(
    periodo=None,
    desde=None,
    hasta=None
):
    """
    Calcula la valorización financiera del stock actual
    y analiza la rotación de los productos según las ventas
    del período solicitado.
    """

    # --------------------------------------------------
    # OBTENER PERÍODO
    # --------------------------------------------------

    tipo_periodo, fecha_desde, fecha_hasta = (
        _obtener_rango_periodo(
            periodo,
            desde,
            hasta
        )
    )

    # --------------------------------------------------
    # OBTENER PRODUCTOS Y VENTAS
    # --------------------------------------------------

    productos = obtener_productos()

    ventas = obtener_ventas_completadas(
        fecha_desde.isoformat(),
        fecha_hasta.isoformat()
    )

    # --------------------------------------------------
    # CALCULAR UNIDADES VENDIDAS POR PRODUCTO
    # --------------------------------------------------

    unidades_vendidas = {}

    for venta in ventas:

        detalles_venta = venta.get(
            "detalle_venta",
            []
        )

        for detalle_venta in detalles_venta:

            id_producto = detalle_venta.get(
                "id_producto"
            )

            cantidad = int(
                detalle_venta.get(
                    "cantidad",
                    0
                ) or 0
            )

            if id_producto not in unidades_vendidas:
                unidades_vendidas[id_producto] = 0

            unidades_vendidas[id_producto] += cantidad

    # --------------------------------------------------
    # ACUMULADORES
    # --------------------------------------------------

    cantidad_productos = 0
    unidades_en_stock = 0

    valor_stock_costo = 0.0
    valor_stock_venta = 0.0

    capital_inmovilizado = 0.0

    detalle_productos = []

    productos_sin_ventas = []
    productos_baja_rotacion = []
    productos_media_rotacion = []
    productos_alta_rotacion = []

    # --------------------------------------------------
    # ANALIZAR CADA PRODUCTO
    # --------------------------------------------------

    for producto in productos:

        id_producto = producto.get(
            "id_producto"
        )

        nombre_producto = producto.get(
            "nombre_producto"
        )

        stock = int(
            producto.get(
                "stock",
                0
            ) or 0
        )

        precio_costo = float(
            producto.get(
                "precio_costo",
                0
            ) or 0
        )

        precio_venta = float(
            producto.get(
                "precio_venta",
                0
            ) or 0
        )

        # Ignorar productos sin stock actual
        if stock <= 0:
            continue

        vendidas = unidades_vendidas.get(
            id_producto,
            0
        )

        # --------------------------------------------------
        # VALORIZACIÓN
        # --------------------------------------------------

        valor_costo_producto = (
            stock * precio_costo
        )

        valor_venta_producto = (
            stock * precio_venta
        )

        ganancia_potencial_producto = (
            valor_venta_producto
            - valor_costo_producto
        )

        # --------------------------------------------------
        # ÍNDICE DE ROTACIÓN ESTIMADO
        # --------------------------------------------------

        unidades_disponibles_estimadas = (
            stock + vendidas
        )

        if unidades_disponibles_estimadas > 0:

            indice_rotacion = (
                vendidas
                / unidades_disponibles_estimadas
            ) * 100

        else:

            indice_rotacion = 0.0

        # --------------------------------------------------
        # CLASIFICACIÓN
        # --------------------------------------------------

        if vendidas == 0:

            rotacion = "SIN_VENTAS"

            capital_inmovilizado += (
                valor_costo_producto
            )

        elif indice_rotacion < 20:

            rotacion = "BAJA"

        elif indice_rotacion <= 50:

            rotacion = "MEDIA"

        else:

            rotacion = "ALTA"

        # --------------------------------------------------
        # DETALLE DEL PRODUCTO
        # --------------------------------------------------

        detalle_producto = {
            "id_producto":
                id_producto,

            "nombre_producto":
                nombre_producto,

            "stock":
                stock,

            "unidades_vendidas_periodo":
                vendidas,

            "indice_rotacion_porcentaje":
                round(
                    indice_rotacion,
                    2
                ),

            "rotacion":
                rotacion,

            "precio_costo":
                round(
                    precio_costo,
                    2
                ),

            "precio_venta":
                round(
                    precio_venta,
                    2
                ),

            "valor_stock_costo":
                round(
                    valor_costo_producto,
                    2
                ),

            "valor_stock_venta":
                round(
                    valor_venta_producto,
                    2
                ),

            "ganancia_potencial":
                round(
                    ganancia_potencial_producto,
                    2
                )
        }

        # Guardar producto en listado general
        detalle_productos.append(
            detalle_producto
        )

        # --------------------------------------------------
        # AGRUPAR POR ROTACIÓN
        # --------------------------------------------------

        if rotacion == "SIN_VENTAS":

            productos_sin_ventas.append(
                detalle_producto
            )

        elif rotacion == "BAJA":

            productos_baja_rotacion.append(
                detalle_producto
            )

        elif rotacion == "MEDIA":

            productos_media_rotacion.append(
                detalle_producto
            )

        elif rotacion == "ALTA":

            productos_alta_rotacion.append(
                detalle_producto
            )

        # --------------------------------------------------
        # ACUMULAR TOTALES
        # --------------------------------------------------

        cantidad_productos += 1

        unidades_en_stock += stock

        valor_stock_costo += (
            valor_costo_producto
        )

        valor_stock_venta += (
            valor_venta_producto
        )

    # --------------------------------------------------
    # TOTALES
    # --------------------------------------------------

    ganancia_potencial = (
        valor_stock_venta
        - valor_stock_costo
    )

    periodo_respuesta = (
        _crear_periodo_respuesta(
            tipo_periodo,
            fecha_desde,
            fecha_hasta
        )
    )

    # --------------------------------------------------
    # RESPUESTA
    # --------------------------------------------------

    return {
        "periodo_rotacion":
            periodo_respuesta,

        "cantidad_productos":
            cantidad_productos,

        "unidades_en_stock":
            unidades_en_stock,

        "valor_stock_costo":
            round(
                valor_stock_costo,
                2
            ),

        "valor_stock_venta":
            round(
                valor_stock_venta,
                2
            ),

        "ganancia_potencial":
            round(
                ganancia_potencial,
                2
            ),

        "rotacion": {

            "cantidad_sin_ventas":
                len(
                    productos_sin_ventas
                ),

            "cantidad_baja_rotacion":
                len(
                    productos_baja_rotacion
                ),

            "cantidad_media_rotacion":
                len(
                    productos_media_rotacion
                ),

            "cantidad_alta_rotacion":
                len(
                    productos_alta_rotacion
                ),

            "capital_inmovilizado_sin_ventas":
                round(
                    capital_inmovilizado,
                    2
                ),

            "productos_sin_ventas":
                productos_sin_ventas,

            "productos_baja_rotacion":
                productos_baja_rotacion,

            "productos_media_rotacion":
                productos_media_rotacion,

            "productos_alta_rotacion":
                productos_alta_rotacion
        },

        "productos":
            detalle_productos
    }



# ======================================================
# DASHBOARD FINANCIERO
# ======================================================

def calcular_dashboard_financiero(
    periodo=None,
    desde=None,
    hasta=None
):
    """
    Genera el resumen principal del módulo financiero.

    El dashboard reutiliza los cálculos ya existentes de:
    - Ventas.
    - Rentabilidad.
    - Caja.
    - Productos.
    - Proveedores.
    - Clientes.
    - Stock.

    No realiza cálculos financieros nuevos.
    Su función es centralizar la información más importante
    para la pantalla principal del sistema.
    """

    # --------------------------------------------------
    # OBTENER INFORMACIÓN DE LOS MÓDULOS FINANCIEROS
    # --------------------------------------------------

    ventas = calcular_estadisticas_ventas(
        periodo=periodo,
        desde=desde,
        hasta=hasta
    )

    rentabilidad = calcular_rentabilidad(
        periodo=periodo,
        desde=desde,
        hasta=hasta
    )

    caja = calcular_caja(
        periodo=periodo,
        desde=desde,
        hasta=hasta
    )

    productos = calcular_estadisticas_productos(
        periodo=periodo,
        desde=desde,
        hasta=hasta
    )

    proveedores = calcular_estadisticas_proveedores(
        periodo=periodo,
        desde=desde,
        hasta=hasta
    )

    clientes = calcular_estadisticas_clientes(
        periodo=periodo,
        desde=desde,
        hasta=hasta
    )

    stock = calcular_estadisticas_stock(
        periodo=periodo,
        desde=desde,
        hasta=hasta
    )

    # --------------------------------------------------
    # RANKINGS PRINCIPALES
    # --------------------------------------------------

    ranking_productos = (
        productos
        .get("rankings", {})
        .get("mas_vendidos", [])
    )

    ranking_clientes = clientes.get(
        "ranking_facturacion",
        []
    )

    ranking_proveedores = proveedores.get(
        "ranking_proveedores",
        []
    )

    producto_mas_vendido = (
        ranking_productos[0]
        if ranking_productos
        else None
    )

    mejor_cliente = (
        ranking_clientes[0]
        if ranking_clientes
        else None
    )

    principal_proveedor = (
        ranking_proveedores[0]
        if ranking_proveedores
        else None
    )

    # --------------------------------------------------
    # RESPUESTA DEL DASHBOARD
    # --------------------------------------------------

    return {
        "periodo":
            ventas.get("periodo"),

        "ventas": {
            "facturacion":
                ventas.get("facturacion", 0),

            "cantidad_ventas":
                ventas.get("cantidad_ventas", 0),

            "ticket_promedio":
                ventas.get("ticket_promedio", 0),

            "unidades_vendidas":
                ventas.get("unidades_vendidas", 0)
        },

        "rentabilidad": {
            "costo_vendido":
                rentabilidad.get("costo_vendido"),

            "ganancia_bruta":
                rentabilidad.get("ganancia_bruta"),

            "margen_bruto":
                rentabilidad.get("margen_bruto"),

            "rentabilidad_calculable":
                rentabilidad.get(
                    "rentabilidad_calculable",
                    False
                ),

            "detalles_sin_costo_historico":
                rentabilidad.get(
                    "detalles_sin_costo_historico",
                    0
                )
        },

        "caja": {
            "total_entradas":
                caja.get("total_entradas", 0),

            "total_salidas":
                caja.get("total_salidas", 0),

            "saldo_neto":
                caja.get("saldo_neto", 0)
        },

        "clientes": {
            "total_por_cobrar":
                clientes.get(
                    "total_por_cobrar",
                    0
                ),

            "cantidad_clientes_con_deuda":
                clientes.get(
                    "cantidad_clientes_con_deuda",
                    0
                )
        },

        "proveedores": {
            "total_comprado":
                proveedores.get(
                    "total_comprado",
                    0
                ),

            "deuda_total_proveedores":
                proveedores.get(
                    "deuda_total_proveedores",
                    0
                )
        },

        "stock": {
            "unidades_en_stock":
                stock.get(
                    "unidades_en_stock",
                    0
                ),

            "valor_stock_costo":
                stock.get(
                    "valor_stock_costo",
                    0
                ),

            "valor_stock_venta":
                stock.get(
                    "valor_stock_venta",
                    0
                ),

            "ganancia_potencial":
                stock.get(
                    "ganancia_potencial",
                    0
                ),

            "capital_inmovilizado_sin_ventas":
                stock.get(
                    "rotacion",
                    {}
                ).get(
                    "capital_inmovilizado_sin_ventas",
                    0
                )
        },

        "rankings": {
            "producto_mas_vendido":
                producto_mas_vendido,

            "mejor_cliente":
                mejor_cliente,

            "principal_proveedor":
                principal_proveedor
        }
    }