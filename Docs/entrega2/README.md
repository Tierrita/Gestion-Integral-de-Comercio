# Entrega 2 – Estructura modular y organización de rutas

**Fecha:** 7 de septiembre de 2026  
**Proyecto:** E-Commerce Kiosco

## Objetivo

Organizar el backend de Flask en módulos y verificar que la ruta inicial funcionara mediante un Blueprint registrado en una Application Factory.

## Qué se hizo

Se trabajó sobre la estructura creada en la Entrega 1 para separar las responsabilidades del backend. El paquete `app/` quedó organizado en carpetas para rutas, controladores, servicios y modelos. También se mantuvieron las carpetas de configuración, componentes compartidos, utilidades y pruebas para las siguientes etapas.

En `app/__init__.py` se implementó la función `create_app()`. Esta función crea la aplicación Flask y registra el Blueprint principal, llamado `main_bp`. De esta manera, las rutas pueden definirse en sus propios módulos e incorporarse a la aplicación desde un punto central.

La ruta de prueba `GET /` se definió dentro de `main_bp` para devolver una respuesta JSON:

```json
{"message": "Backend funcionando"}
```

Durante la implementación se corrigió un problema de importación al registrar el Blueprint. Se utilizó una importación relativa, `from .routes import main_bp`, para que pudiera encontrarse correctamente dentro del paquete `app`.

## Prueba realizada

Se verificó que `create_app()` creara la aplicación y registrara `main_bp`. Al consultar `GET /`, se obtuvo una respuesta **HTTP 200** con el JSON esperado.

## Resultado

La estructura modular quedó implementada y el Blueprint principal respondió correctamente. El backend quedó preparado para incorporar rutas de productos y otros módulos. La integración del punto de entrada `app.py` con `create_app()` se abordará en la siguiente entrega.