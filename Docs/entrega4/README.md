# Entrega 4 – Desarrollo inicial del módulo de productos

**Fecha:** 20 de septiembre de 2026  
**Proyecto:** E-Commerce Kiosco

## Objetivo

Desarrollar las primeras operaciones del módulo de productos sobre la conexión con Supabase: consultar productos y registrar nuevos, con validaciones y respuestas claras ante errores.

## Qué se hizo

Se consolidó la consulta general `GET /productos` y se agregó `GET /productos/<id_producto>` para obtener un producto específico. Cuando el ID consultado no existe, la API devuelve **HTTP 404** con el mensaje «Producto no encontrado».

También se implementó `POST /productos`, que recibe los datos en formato JSON y registra el producto en la tabla `productos` de Supabase. Una creación correcta devuelve **HTTP 201**. Estas operaciones siguen la estructura del backend: ruta, controlador, servicio, modelo y base de datos.

Para el alta se incorporaron validaciones de datos obligatorios, valores numéricos y cantidades no negativas. Se controlaron además los errores producidos cuando se intenta asociar un producto con una categoría o un proveedor inexistente. Las solicitudes inválidas reciben una respuesta **HTTP 400** con un mensaje que indica el problema.

## Pruebas realizadas

Se probaron las rutas mediante `curl`: consulta general, consulta por ID existente e inexistente, alta válida y distintos casos con datos faltantes o incorrectos. También se verificó en Supabase que el producto creado desde la API quedara almacenado.

Después de probar los errores, se realizó una nueva alta válida para comprobar que las validaciones no afectaran el funcionamiento normal.

## Resultado

El módulo permite **listar productos, consultar uno por ID y crear nuevos productos** con validaciones iniciales. Las operaciones de modificación y baja quedan para una etapa posterior.