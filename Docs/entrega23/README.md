ENTREGA 23 – ENDURECIMIENTO MULTICOMERCIO Y PERMISOS DEL MÓDULO PRODUCTOS

OBJETIVO

En esta entrega se avanzó con la adaptación del módulo Productos a la arquitectura multicomercio del sistema.

El objetivo principal fue garantizar que las operaciones sobre productos se realicen siempre dentro del comercio correspondiente al usuario autenticado, utilizando JWT para determinar el comercio y el sistema de roles y permisos para controlar qué acciones puede realizar cada usuario.

De esta manera, el backend deja de confiar en identificadores de comercio enviados desde el cliente y aplica el aislamiento multicomercio directamente desde el servidor.


1. INTEGRACIÓN DE PRODUCTOS CON EL COMERCIO AUTENTICADO

Se modificaron las capas Model, Service, Controller y Routes del módulo Productos para trabajar con id_comercio.

El comercio ya no se recibe desde Postman o, en el futuro, desde React.

El backend obtiene automáticamente el comercio correspondiente al usuario autenticado mediante:

g.id_comercio

Este valor se establece después de validar el token JWT.

Por lo tanto, las consultas de productos se realizan utilizando conjuntamente:

id_producto + id_comercio autenticado

Esto evita que conocer el ID global de un producto sea suficiente para consultar o modificar productos pertenecientes a otro comercio.


2. NUMERACIÓN LOCAL DE PRODUCTOS

Se mantuvo la separación entre:

id_producto

Identificador global e interno de la base de datos.

Y:

numero_producto

Número comercial/local correspondiente a cada comercio.

La numeración local se genera desde el backend mediante la RPC:

obtener_siguiente_numero

Por lo tanto, el cliente no puede decidir manualmente ni el comercio ni el número local que tendrá un producto.

Durante las pruebas se intentó crear un producto enviando:

{
    "id_comercio": 999,
    "numero_producto": 9999
}

El backend ignoró esos valores y asignó automáticamente:

{
    "id_comercio": 1,
    "numero_producto": 13
}

Esto permitió comprobar que ambos valores quedan bajo control del servidor.


3. ESTADO DE LOS PRODUCTOS

Se incorporó a la tabla productos el campo:

estado BOOLEAN NOT NULL DEFAULT TRUE

Esto prepara al sistema para manejar productos activos e inactivos sin eliminarlos físicamente de la base de datos.

La decisión permite conservar ventas, compras, movimientos de stock y demás información histórica asociada al producto.


4. PROTECCIÓN DE LAS RUTAS DE PRODUCTOS

Las rutas existentes fueron protegidas mediante autenticación JWT y permisos.

Actualmente se encuentran implementadas:

GET   /productos
GET   /productos/<id>
POST  /productos
PATCH /productos/<id>

Para acceder a ellas se utilizan permisos específicos:

productos.ver
productos.crear
productos.modificar

Primero se valida que exista una sesión válida mediante:

@login_requerido

Posteriormente se controla el permiso correspondiente mediante:

@permiso_requerido(...)

Una petición sin token válido no puede acceder al módulo.


5. VALIDACIÓN DE CATEGORÍAS Y PROVEEDORES

Al crear o modificar un producto, el backend verifica que la categoría y el proveedor indicados:

- Existan.
- Pertenezcan al mismo comercio.
- Se encuentren activos.

De esta manera, un producto de un comercio no puede quedar relacionado accidentalmente con una categoría o proveedor perteneciente a otro comercio.


6. MODIFICACIÓN SEGURA DE PRODUCTOS

Se implementó:

PATCH /productos/<id>

Esta ruta permite modificar datos comerciales autorizados del producto, como:

- nombre_producto
- precio_costo
- precio_venta
- id_categoria
- id_proveedor
- unidad_de_medida
- stock_minimo

Sin embargo, determinados campos sensibles no pueden modificarse mediante este endpoint:

- id_producto
- id_comercio
- numero_producto
- stock
- estado
- fecha_alta

El stock deberá modificarse mediante las operaciones específicas del módulo Stock, mientras que el estado tendrá su propia operación.

Se realizaron pruebas intentando alterar manualmente:

{
    "id_comercio": 999,
    "numero_producto": 9999,
    "stock": 999999,
    "estado": false,
    "fecha_alta": "1990-01-01"
}

El backend ignoró correctamente estos campos y conservó sus valores originales.


7. PROTECCIÓN DEL PRECIO DE COSTO

Se agregó una validación adicional mediante el permiso:

productos.ver_costos

Se incorporó una función auxiliar que permite consultar dinámicamente si el usuario autenticado posee un permiso determinado sin bloquear automáticamente toda la petición.

Esto permite separar:

productos.modificar

de:

productos.ver_costos

Por ejemplo, un empleado puede tener autorización para modificar información de un producto y su precio de venta sin necesariamente tener acceso al costo de compra.

Si el usuario no posee productos.ver_costos, el campo:

precio_costo

se elimina de las respuestas del backend.

Además, si intenta modificar directamente el precio de costo, el servidor responde:

{
    "error": "No tiene permisos para modificar el precio de costo"
}


8. PRUEBAS DE ROLES Y PERMISOS

Para verificar este comportamiento se utilizó el rol CAJERO.

Inicialmente el rol no poseía:

productos.modificar
productos.ver_costos

Por lo tanto, al intentar modificar un producto el servidor rechazó la operación por falta de permisos.

Posteriormente, utilizando las propias rutas de administración de roles, el propietario agregó:

productos.modificar

sin otorgar:

productos.ver_costos

El resultado fue:

Modificar precio de venta      → PERMITIDO
Consultar precio de costo      → OCULTO
Modificar precio de costo      → BLOQUEADO

Esto permite manejar permisos independientes y construir roles personalizados para cada comercio.


9. PRUEBAS REALIZADAS EN POSTMAN

Se realizaron pruebas sobre PATCH /productos/<id> para verificar diferentes escenarios.

Resultados:

Modificación normal del producto             → OK
Protección de id_comercio                    → OK
Protección de numero_producto                → OK
Protección del stock                         → OK
Protección del estado                        → OK
Protección de fecha_alta                     → OK
Usuario sin productos.modificar              → 403
Usuario autorizado                           → 200
Ocultamiento del precio de costo             → OK
Modificación de costo sin permiso            → 403
Petición sin JWT                             → 401
Producto inexistente                         → 404
Categoría inexistente/otro comercio          → 400
Proveedor inexistente/otro comercio          → 400

También se comprobó que los permisos de un rol pueden administrarse mediante las APIs existentes, sin necesidad de modificar directamente las tablas de Supabase.


10. ARQUITECTURA RESULTANTE

El módulo continúa respetando la arquitectura:

Route
  ↓
Controller
  ↓
Service
  ↓
Model
  ↓
Supabase/PostgreSQL

A esto se suma la capa transversal de seguridad:

JWT
  ↓
Usuario autenticado
  ↓
Comercio
  ↓
Rol / Propietario
  ↓
Permisos
  ↓
Endpoint
  ↓
Service
  ↓
Model
  ↓
Supabase

De esta forma, la seguridad multicomercio no depende del frontend, sino que se aplica directamente desde el backend.


ESTADO DE LA ENTREGA

Con esta entrega quedan implementadas y probadas en Productos:

GET   /productos              → COMPLETADO
GET   /productos/<id>         → COMPLETADO
POST  /productos              → COMPLETADO
PATCH /productos/<id>         → COMPLETADO


PRÓXIMO PASO

El siguiente paso será implementar:

PATCH /productos/<id>/estado

utilizando el permiso:

productos.estado

Esto permitirá activar y desactivar productos sin eliminarlos de la base de datos.

Una vez finalizado este punto, se continuará aplicando el mismo esquema de autenticación, permisos y aislamiento multicomercio al resto de los módulos del sistema.