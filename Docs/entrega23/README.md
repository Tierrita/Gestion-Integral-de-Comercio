# ENTREGA 23 – ENDURECIMIENTO MULTICOMERCIO Y PERMISOS DEL MÓDULO PRODUCTOS

## OBJETIVO

En esta entrega se avanzó con la adaptación completa del módulo Productos a la arquitectura multicomercio del sistema.

El objetivo principal fue garantizar que las operaciones sobre productos se realicen siempre dentro del comercio correspondiente al usuario autenticado, utilizando JWT para determinar el comercio y el sistema de roles y permisos para controlar qué acciones puede realizar cada usuario.

De esta manera, el backend deja de confiar en identificadores de comercio enviados desde el cliente y aplica el aislamiento multicomercio directamente desde el servidor.

Además, se completó la gestión del estado de los productos, permitiendo activarlos y desactivarlos sin eliminarlos físicamente de la base de datos.


## 1. INTEGRACIÓN DE PRODUCTOS CON EL COMERCIO AUTENTICADO

Se modificaron las capas Model, Service, Controller y Routes del módulo Productos para trabajar con `id_comercio`.

El comercio ya no se recibe desde Postman o, en el futuro, desde React.

El backend obtiene automáticamente el comercio correspondiente al usuario autenticado mediante:

```python
g.id_comercio
```

Este valor se establece después de validar el token JWT.

Por lo tanto, las consultas de productos se realizan utilizando conjuntamente:

```text
id_producto + id_comercio autenticado
```

Esto evita que conocer el ID global de un producto sea suficiente para consultar o modificar productos pertenecientes a otro comercio.


## 2. NUMERACIÓN LOCAL DE PRODUCTOS

Se mantuvo la separación entre:

```text
id_producto
```

Identificador global e interno de la base de datos.

Y:

```text
numero_producto
```

Número comercial/local correspondiente a cada comercio.

La numeración local se genera desde el backend mediante la RPC:

```text
obtener_siguiente_numero
```

Por lo tanto, el cliente no puede decidir manualmente ni el comercio ni el número local que tendrá un producto.

Durante las pruebas se intentó crear un producto enviando:

```json
{
    "id_comercio": 999,
    "numero_producto": 9999
}
```

El backend ignoró esos valores y asignó automáticamente:

```json
{
    "id_comercio": 1,
    "numero_producto": 13
}
```

Esto permitió comprobar que ambos valores quedan bajo control del servidor.


## 3. ESTADO DE LOS PRODUCTOS

Se incorporó a la tabla `productos` el campo:

```sql
estado BOOLEAN NOT NULL DEFAULT TRUE
```

Esto permite manejar productos activos e inactivos sin eliminarlos físicamente de la base de datos.

Los estados utilizados son:

```text
true  → producto activo
false → producto inactivo
```

Esta decisión permite conservar ventas, compras, movimientos de stock y demás información histórica asociada al producto.


## 4. PROTECCIÓN DE LAS RUTAS DE PRODUCTOS

Las rutas del módulo Productos fueron protegidas mediante autenticación JWT y permisos.

Actualmente se encuentran implementadas:

```text
GET   /productos
GET   /productos/<id>
POST  /productos
PATCH /productos/<id>
PATCH /productos/<id>/estado
```

Para acceder a ellas se utilizan permisos específicos:

```text
productos.ver
productos.crear
productos.modificar
productos.estado
productos.ver_costos
```

Primero se valida que exista una sesión válida mediante:

```python
@login_requerido
```

Posteriormente se controla el permiso correspondiente mediante:

```python
@permiso_requerido(...)
```

Una petición sin token válido no puede acceder a las operaciones protegidas del módulo.


## 5. VALIDACIÓN DE CATEGORÍAS Y PROVEEDORES

Al crear o modificar un producto, el backend verifica que la categoría y el proveedor indicados:

- Existan.
- Pertenezcan al mismo comercio.
- Se encuentren activos.

De esta manera, un producto de un comercio no puede quedar relacionado accidentalmente con una categoría o proveedor perteneciente a otro comercio.


## 6. MODIFICACIÓN SEGURA DE PRODUCTOS

Se implementó:

```http
PATCH /productos/<id>
```

Esta ruta permite modificar datos comerciales autorizados del producto, como:

- `nombre_producto`
- `precio_costo`
- `precio_venta`
- `id_categoria`
- `id_proveedor`
- `unidad_de_medida`
- `stock_minimo`

Sin embargo, determinados campos sensibles no pueden modificarse mediante este endpoint:

- `id_producto`
- `id_comercio`
- `numero_producto`
- `stock`
- `estado`
- `fecha_alta`

El stock se mantiene dentro de las operaciones específicas del módulo Stock, mientras que el estado posee su propio endpoint.

Se realizaron pruebas intentando alterar manualmente:

```json
{
    "id_comercio": 999,
    "numero_producto": 9999,
    "stock": 999999,
    "estado": false,
    "fecha_alta": "1990-01-01"
}
```

El backend ignoró correctamente estos campos y conservó sus valores originales.


## 7. PROTECCIÓN DEL PRECIO DE COSTO

Se agregó una validación adicional mediante el permiso:

```text
productos.ver_costos
```

Se incorporó una función auxiliar que permite consultar dinámicamente si el usuario autenticado posee un permiso determinado sin bloquear automáticamente toda la petición.

Esto permite separar:

```text
productos.modificar
```

de:

```text
productos.ver_costos
```

Por ejemplo, un empleado puede tener autorización para modificar información de un producto y su precio de venta sin necesariamente tener acceso al costo de compra.

Si el usuario no posee `productos.ver_costos`, el campo:

```text
precio_costo
```

se elimina de las respuestas del backend.

Además, si intenta modificar directamente el precio de costo, el servidor responde:

```json
{
    "error": "No tiene permisos para modificar el precio de costo"
}
```


## 8. PRUEBAS DE ROLES Y PERMISOS

Para verificar este comportamiento se utilizó el rol CAJERO.

Inicialmente el rol no poseía:

```text
productos.modificar
productos.ver_costos
```

Por lo tanto, al intentar modificar un producto el servidor rechazó la operación por falta de permisos.

Posteriormente, utilizando las propias rutas de administración de roles, el propietario agregó:

```text
productos.modificar
```

sin otorgar:

```text
productos.ver_costos
```

El resultado fue:

```text
Modificar precio de venta      → PERMITIDO
Consultar precio de costo      → OCULTO
Modificar precio de costo      → BLOQUEADO
```

Esto permite manejar permisos independientes y construir roles personalizados para cada comercio.


## 9. PRUEBAS DE MODIFICACIÓN REALIZADAS EN POSTMAN

Se realizaron pruebas sobre:

```http
PATCH /productos/<id>
```

para verificar diferentes escenarios.

Resultados:

```text
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
```

También se comprobó que los permisos de un rol pueden administrarse mediante las APIs existentes, sin necesidad de modificar directamente las tablas de Supabase.


## 10. ACTIVACIÓN Y DESACTIVACIÓN DE PRODUCTOS

Para completar la gestión del ciclo de vida de los productos se implementó:

```http
PATCH /productos/<id>/estado
```

Este endpoint permite activar o desactivar un producto sin eliminarlo físicamente.

Ejemplo para desactivar:

```json
{
    "estado": false
}
```

Ejemplo para activar:

```json
{
    "estado": true
}
```

La operación utiliza el permiso específico:

```text
productos.estado
```

Esto permite separar la modificación de los datos comerciales de la posibilidad de activar o desactivar productos.


## 11. SEPARACIÓN DE PERMISOS ENTRE MODIFICACIÓN Y ESTADO

La modificación general utiliza:

```http
PATCH /productos/<id>
```

con:

```text
productos.modificar
```

Mientras que el cambio de estado utiliza:

```http
PATCH /productos/<id>/estado
```

con:

```text
productos.estado
```

De esta manera, un comercio puede crear un rol que tenga autorización para modificar determinada información de los productos pero que no pueda activarlos o desactivarlos.

Esta separación permite construir un sistema de permisos más granular y adaptable a las necesidades de cada comercio.


## 12. VALIDACIONES DEL CAMBIO DE ESTADO

Antes de modificar el estado de un producto, el backend verifica:

- Que el producto exista.
- Que pertenezca al comercio autenticado.
- Que el campo `estado` haya sido enviado.
- Que `estado` sea estrictamente booleano.
- Que el producto no se encuentre ya en el estado solicitado.
- Que el usuario posea el permiso `productos.estado`.

Por ejemplo:

```json
{
    "estado": false
}
```

es válido.

En cambio:

```json
{
    "estado": "false"
}
```

es rechazado porque `"false"` es un texto y no un valor booleano.


## 13. SEGURIDAD MULTICOMERCIO DEL CAMBIO DE ESTADO

El cambio de estado reutiliza la actualización segura del Model.

La actualización se realiza filtrando simultáneamente por:

```text
id_producto
+
id_comercio
```

Por lo tanto, aunque un usuario conozca el ID global de un producto perteneciente a otro comercio, no puede modificar su estado.

El comercio tampoco se recibe mediante el body de la petición.

Se obtiene exclusivamente desde:

```python
g.id_comercio
```

establecido a partir del usuario autenticado.


## 14. PRUEBAS DEL CAMBIO DE ESTADO EN POSTMAN

Se realizaron pruebas sobre:

```http
PATCH /productos/14/estado
```

### Desactivación como propietario

Se envió:

```json
{
    "estado": false
}
```

Resultado:

```text
200 OK
estado: true → false
```

El resto de la información del producto permaneció sin modificaciones.


### Intento de desactivar nuevamente el producto

Resultado:

```text
400 Bad Request
El producto ya se encuentra inactivo
```

Esto evita ejecutar actualizaciones innecesarias.


### Reactivación del producto

Se envió:

```json
{
    "estado": true
}
```

Resultado:

```text
200 OK
estado: false → true
```


### Empleado sin productos.estado

Se utilizó el usuario asociado al rol CAJERO sin el permiso:

```text
productos.estado
```

Resultado:

```text
403 Forbidden
No tiene permisos para realizar esta operación
```


### Empleado con productos.estado

Posteriormente se agregó al rol CAJERO el permiso:

```text
productos.estado
```

La misma operación fue ejecutada nuevamente.

Resultado:

```text
200 OK
```

El empleado pudo modificar el estado correctamente.


### Verificación del ocultamiento del costo

El usuario CAJERO tenía permiso para modificar el estado, pero no poseía:

```text
productos.ver_costos
```

La operación fue autorizada, pero la respuesta del backend no incluyó:

```text
precio_costo
```

Esto comprobó que ambos permisos funcionan de manera independiente.


### Petición sin JWT

Resultado:

```text
401 Unauthorized
Token de autenticación requerido
```


### Producto inexistente

Se probó:

```http
PATCH /productos/999999/estado
```

Resultado:

```text
404 Not Found
Producto no encontrado
```


### Estado enviado como texto

Se envió:

```json
{
    "estado": "false"
}
```

Resultado:

```text
400 Bad Request
El estado debe ser true o false
```


### Body sin estado

Se envió:

```json
{}
```

Resultado:

```text
400 Bad Request
El estado es obligatorio
```

Finalmente, el producto utilizado durante las pruebas fue reactivado correctamente y quedó nuevamente con:

```text
estado: true
```


## 15. ARQUITECTURA RESULTANTE

El módulo continúa respetando la arquitectura:

```text
Route
  ↓
Controller
  ↓
Service
  ↓
Model
  ↓
Supabase/PostgreSQL
```

A esto se suma la capa transversal de seguridad:

```text
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
```

En el caso específico del cambio de estado:

```text
PATCH /productos/<id>/estado
        ↓
login_requerido
        ↓
productos.estado
        ↓
Controller
        ↓
Service
        ↓
Model
        ↓
Supabase
```

De esta forma, la seguridad multicomercio no depende del frontend, sino que se aplica directamente desde el backend.


## ESTADO DE LA ENTREGA

Con esta entrega quedan implementadas y probadas en Productos:

```text
GET   /productos                 → COMPLETADO
GET   /productos/<id>            → COMPLETADO
POST  /productos                 → COMPLETADO
PATCH /productos/<id>            → COMPLETADO
PATCH /productos/<id>/estado     → COMPLETADO
```

También quedaron comprobados:

```text
Autenticación JWT                    → OK
Aislamiento por comercio             → OK
Numeración local por comercio        → OK
productos.ver                        → OK
productos.crear                      → OK
productos.modificar                  → OK
productos.estado                     → OK
productos.ver_costos                 → OK
Protección de campos sensibles       → OK
Validación categoría/comercio        → OK
Validación proveedor/comercio        → OK
Ocultamiento de costos               → OK
Activación/desactivación             → OK
Baja lógica sin eliminar producto    → OK
```


## RESULTADO FINAL

El módulo Productos queda adaptado a la arquitectura multicomercio y al sistema de autenticación y autorización implementado.

El backend determina automáticamente el comercio del usuario mediante JWT, aplica permisos específicos según cada operación y evita que el frontend pueda controlar campos sensibles como `id_comercio`, `numero_producto`, `stock` o `estado` mediante operaciones no autorizadas.

Además, los productos pueden ser activados y desactivados mediante una operación independiente, manteniendo intacta la información histórica del sistema.

**ESTADO DEL MÓDULO PRODUCTOS: COMPLETADO PARA LA ETAPA ACTUAL DEL BACKEND.**


## PRÓXIMO PASO

Finalizado el endurecimiento del módulo Productos, el siguiente paso será continuar aplicando el mismo esquema de:

- Autenticación JWT.
- Aislamiento multicomercio.
- Roles y permisos.
- Validaciones de negocio.
- Protección de campos sensibles.

al siguiente módulo del sistema, manteniendo la misma arquitectura y criterios de seguridad.