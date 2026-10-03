"""Cliente de Supabase (módulo de inicialización).

Este módulo centraliza la creación y provisión del cliente de Supabase
para el proyecto. Su objetivo es ser simple y educativo: leer las
credenciales desde la configuración (o variables de entorno), crear el
cliente y ofrecer funciones para inicializarlo y obtenerlo desde otros
módulos.

No contiene lógica de negocio ni realiza llamadas a tablas.
"""
from typing import Optional
import os

from supabase import create_client, Client

# Cliente singleton en este módulo. Se inicializa mediante init_supabase().
client: Optional[Client] = None


def init_supabase(app=None) -> Client:
    """Inicializa y retorna el cliente de Supabase.

    Requisitos:
    - `SUPABASE_URL` y `SUPABASE_KEY` deben estar presentes en el entorno
      o en `app.config`.

    Si faltan las credenciales, se lanza un RuntimeError con mensaje claro
    para que no se silencien errores de configuración.

    Parámetros:
    - `app` (opcional): si se pasa la app Flask, el cliente se guarda en
      `app.config['SUPABASE_CLIENT']` como referencia.

    Retorna:
    - instancia de `supabase.Client`.
    """
    global client

    # Preferir valores presentes en app.config si la app fue pasada
    url = None
    key = None
    if app is not None:
        url = app.config.get("SUPABASE_URL")
        key = app.config.get("SUPABASE_KEY")

    # Fallback a variables de entorno si no están en app.config
    url = url or os.getenv("SUPABASE_URL")
    key = key or os.getenv("SUPABASE_KEY")

    # Verificar que existan y no estén vacías
    if not url:
        raise RuntimeError("SUPABASE_URL no está configurada. Completar .env con SUPABASE_URL")
    if not key:
        raise RuntimeError("SUPABASE_KEY no está configurada. Completar .env con SUPABASE_KEY")

    # Crear el cliente (la creación del objeto no prueba la conectividad)
    client = create_client(url, key)

    # Guardar referencia en la app si fue provista
    if app is not None:
        app.config["SUPABASE_CLIENT"] = client

    return client


def get_client() -> Client:
    """Devuelve el cliente ya inicializado.

    Si no fue inicializado, lanza un RuntimeError para indicar que se
    debe llamar a `init_supabase()` primero.
    """
    if client is None:
        raise RuntimeError("Cliente de Supabase no inicializado. Llamar a init_supabase(app) primero.")
    return client
