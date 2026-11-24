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


# Contrato Clientes V2: todos los campos nuevos son opcionales.
# Los nombres de columnas coinciden con Backend/sql/clientes_v2.sql.
import re

CAMPOS_CLIENTE_V2 = {
    "nombre_completo": 150,
    "telefono": 50,
    "tipo_cliente": 20,
    "nombre_comercial": 150,
    "tipo_documento": 20,
    "numero_documento": 30,
    "condicion_iva": 50,
    "email": 254,
    "whatsapp": 50,
    "direccion": 200,
    "localidad": 100,
    "provincia": 100,
    "codigo_postal": 20,
    "referencia_entrega": 2000,
    "observaciones": 2000,
}
TIPOS_CLIENTE = {"PARTICULAR", "COMERCIO", "EMPRESA", "INSTITUCION"}
TIPOS_DOCUMENTO = {"DNI", "CUIT", "CUIL", "PASAPORTE", "OTRO"}


def validar_datos_cliente(datos, *, creacion=False, cliente_general=False):
    """Normaliza exclusivamente campos editables; nunca acepta IDs o estado."""
    if not isinstance(datos, dict) or not datos:
        raise ValueError("No se enviaron datos del cliente")

    desconocidos = set(datos) - set(CAMPOS_CLIENTE_V2)
    if desconocidos:
        raise ValueError("Campos no permitidos: " + ", ".join(sorted(desconocidos)))

    if creacion and "nombre_completo" not in datos:
        raise ValueError("El nombre completo es obligatorio")

    if cliente_general and "nombre_completo" in datos:
        raise ValueError("No se puede modificar el nombre de CLIENTE GENERAL")

    resultado = {}
    for campo, valor in datos.items():
        if valor is not None and not isinstance(valor, str):
            raise ValueError(f"El campo {campo} debe ser texto")

        limpio = valor.strip() if isinstance(valor, str) else None
        if limpio == "":
            limpio = None

        if campo == "nombre_completo" and (not limpio or len(limpio) < 2):
            raise ValueError("El nombre completo debe tener al menos 2 caracteres")
        if limpio is not None and len(limpio) > CAMPOS_CLIENTE_V2[campo]:
            raise ValueError(f"El campo {campo} supera el largo permitido")
        if campo == "tipo_cliente":
            if limpio is None or limpio.upper() not in TIPOS_CLIENTE:
                raise ValueError("Tipo de cliente inválido")
            limpio = limpio.upper()
        if campo == "tipo_documento" and limpio is not None:
            if limpio.upper() not in TIPOS_DOCUMENTO:
                raise ValueError("Tipo de documento inválido")
            limpio = limpio.upper()
        if campo == "email" and limpio is not None:
            # Validación práctica de formato; no intenta verificar existencia.
            if not re.fullmatch(r"[^\\s@]+@[^\\s@]+\\.[^\\s@]+", limpio):
                raise ValueError("El email no tiene un formato válido")
            limpio = limpio.lower()

        resultado[campo] = limpio

    return resultado


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
    """Crea un cliente sin permitir alterar identificadores del sistema."""
    campos = validar_datos_cliente(datos, creacion=True)
    numero_cliente = obtener_siguiente_numero_cliente(id_comercio)
    if numero_cliente is None:
        raise ValueError("No se pudo generar el número del cliente")

    nuevo_cliente = {
        **campos,
        "id_comercio": id_comercio,
        "numero_cliente": numero_cliente,
        "estado": True,
    }
    cliente = insertar_cliente(nuevo_cliente)
    if not cliente:
        raise ValueError("No se pudo registrar el cliente")
    return cliente


def editar_cliente(id_cliente, datos, id_comercio):
    """Actualiza solo los campos editables de un cliente del comercio."""
    cliente = obtener_cliente_por_id(id_cliente, id_comercio)
    if not cliente:
        raise ValueError("Cliente no encontrado")

    campos = validar_datos_cliente(
        datos,
        cliente_general=cliente.get("numero_cliente") == 1,
    )
    cliente_actualizado = actualizar_cliente(id_cliente, id_comercio, campos)
    if not cliente_actualizado:
        raise ValueError("No se pudo actualizar el cliente")
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

def consultar_movimientos_financieros_cliente(id_cliente, id_comercio):
    """Historial de ingresos y reversiones del cliente, sin alterar saldos.

    Primero se obtienen las operaciones del comercio autenticado y luego
    sus movimientos asociados. No se exponen movimientos de otros comercios.
    """
    from core.supabase_client import get_client

    cliente = obtener_cliente_por_id(id_cliente, id_comercio)
    if not cliente:
        raise ValueError("Cliente no encontrado")

    db = get_client()
    ventas = (db.table("ventas")
              .select("id_venta,numero_venta,fecha_venta,metodo_pago,estado,total")
              .eq("id_cliente", id_cliente).eq("id_comercio", id_comercio)
              .execute().data or [])
    cobros = (db.table("cobros")
              .select("id_cobro,fecha_cobro,estado,monto")
              .eq("id_cliente", id_cliente).eq("id_comercio", id_comercio)
              .execute().data or [])

    operaciones = []
    for origen, registros, clave in (
        ("VENTA", ventas, "id_venta"),
        ("COBRO", cobros, "id_cobro"),
    ):
        ids = [registro[clave] for registro in registros]
        if not ids:
            continue
        movimientos = (db.table("movimientos_financieros")
                       .select("id_movimiento,id_cuenta,tipo_movimiento,monto,fecha_movimiento,id_origen")
                       .eq("tipo_origen", origen).in_("id_origen", ids)
                       .order("fecha_movimiento", desc=True).execute().data or [])
        indice = {registro[clave]: registro for registro in registros}
        for movimiento in movimientos:
            original = indice.get(movimiento["id_origen"])
            if original is None:
                continue
            tipo = movimiento["tipo_movimiento"]
            permitidos = ("VENTA", "ANULACION_VENTA") if origen == "VENTA" else ("COBRO", "ANULACION_COBRO")
            if tipo not in permitidos:
                continue
            operaciones.append({
                "id_movimiento": movimiento["id_movimiento"],
                "tipo": tipo,
                "origen": origen,
                "id_operacion": movimiento["id_origen"],
                "numero_venta": original.get("numero_venta") if origen == "VENTA" else None,
                "metodo_pago": original.get("metodo_pago") if origen == "VENTA" else None,
                "estado_operacion": original["estado"],
                "monto": movimiento["monto"],
                "fecha": movimiento["fecha_movimiento"],
                "id_cuenta": movimiento["id_cuenta"],
            })

    ids_cuentas = sorted({m["id_cuenta"] for m in operaciones if m["id_cuenta"] is not None})
    nombres = {}
    if ids_cuentas:
        cuentas = (db.table("cuentas").select("id_cuenta,nombre_cuenta")
                   .eq("id_comercio", id_comercio).in_("id_cuenta", ids_cuentas)
                   .execute().data or [])
        nombres = {c["id_cuenta"]: c["nombre_cuenta"] for c in cuentas}
    for movimiento in operaciones:
        movimiento["cuenta"] = nombres.get(movimiento.pop("id_cuenta"), "Cuenta no disponible")

    operaciones.sort(key=lambda m: (m["fecha"] or "", m["id_movimiento"]), reverse=True)
    return {"movimientos": operaciones}
