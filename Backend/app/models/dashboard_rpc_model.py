"""Acceso de solo lectura a la RPC de indicadores del dashboard.

No reemplaza la implementación financiera existente hasta completar
las pruebas de equivalencia. La autorización permanece en Flask.
"""
from core.supabase_client import get_client


def obtener_dashboard_rpc(id_comercio, fecha_desde, fecha_hasta):
    """Devuelve el JSON agregado por PostgreSQL para un comercio y período.

    Requiere que el cliente Supabase del backend utilice service_role;
    nunca se debe exponer esa credencial en el frontend.
    """
    if not isinstance(id_comercio, int) or isinstance(id_comercio, bool) or id_comercio <= 0:
        raise ValueError("El comercio debe ser un identificador válido")

    if fecha_desde is None or fecha_hasta is None or fecha_desde >= fecha_hasta:
        raise ValueError("El rango de fechas es inválido")

    respuesta = get_client().rpc(
        "obtener_dashboard_estadisticas",
        {
            "p_id_comercio": id_comercio,
            "p_desde": fecha_desde.isoformat(),
            "p_hasta": fecha_hasta.isoformat(),
        },
    ).execute()

    if not isinstance(respuesta.data, dict):
        raise RuntimeError("La RPC devolvió una respuesta inesperada")

    return respuesta.data
