"""Módulo de rutas de la aplicación.

Este módulo contiene las rutas o endpoints del backend.

Su función es definir qué URLs del proyecto existen y qué
respuesta o acción debe ejecutarse cuando llega una solicitud.

En este punto se organizan las peticiones del frontend y se las
envía hacia los controladores correspondientes.

Más adelante, aquí se colocarán las rutas relacionadas con la API
principal del E-Commerce Kiosco, sin mezclar la lógica de negocio
con la definición de endpoints.
"""

from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return jsonify({"message": "Backend funcionando"})


@main_bp.get("/test-supabase")
def test_supabase():
    """Endpoint temporal para verificar comunicación real con Supabase.
    
    Realiza una consulta de lectura SELECT sobre la tabla `productos`
    y retorna un registro con los campos id_producto y nombre_producto.
    
    Este endpoint es técnico y temporal: solo comprueba que la comunicación
    entre Flask, el cliente de Supabase y la base de datos PostgreSQL funciona
    correctamente. No implementa lógica de negocio ni CRUD.
    """
    try:
        from core.supabase_client import get_client
        
        # Obtener el cliente ya inicializado
        client = get_client()
        
        # Realizar consulta de lectura: SELECT id_producto, nombre_producto
        # FROM productos LIMIT 1
        response = client.table('productos').select('id_producto, nombre_producto').limit(1).execute()
        
        # Retornar respuesta exitosa con datos reales de Supabase
        return jsonify({
            "success": True,
            "message": "Comunicación con Supabase verificada",
            "data": response.data
        }), 200
        
    except Exception as e:
        # Retornar error sin ocultar detalles para debugging
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
