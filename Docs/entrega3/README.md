# Entrega 3 – Integración del backend con Supabase

**Fecha:** 16 de septiembre de 2026  
**Proyecto:** E-Commerce Kiosco

## Objetivo

Conectar el backend Flask con la base de datos PostgreSQL alojada en Supabase y comprobar la conexión mediante una consulta real de productos.

## Qué se hizo

Se unificó el inicio del backend para que `app.py` ejecutara la aplicación creada por `create_app()`. La configuración y el registro de los Blueprints quedaron centralizados en `app/__init__.py`.

Para conectar con Supabase, se incorporaron las variables de entorno `SUPABASE_URL` y `SUPABASE_KEY`. Se configuró su carga desde `.env` y se agregó este archivo a `.gitignore` para mantener las credenciales fuera del repositorio. También se creó `core/supabase_client.py`, encargado de inicializar el cliente de Supabase y ponerlo a disposición de los módulos que consultan datos.

La primera consulta real se expuso mediante **`GET /productos`**. La petición recorre las capas del backend: la ruta recibe la solicitud, el controlador prepara la respuesta, el servicio coordina la operación y el modelo consulta la tabla `productos` en Supabase. La consulta esencial fue:

```python
supabase.table("productos").select("*").execute()
```

Los resultados regresan al cliente como una respuesta JSON.

## Prueba realizada

Se inició el servidor local en el puerto **5001** y se consultó `GET /productos`. El endpoint devolvió en formato JSON los datos obtenidos desde Supabase. También se verificó que `GET /` continuara respondiendo con el mensaje de funcionamiento del backend.

## Resultado

El backend quedó conectado con Supabase y pudo consultar datos reales mediante su estructura modular. Esta integración dejó preparada la base para desarrollar las demás operaciones del módulo de productos.