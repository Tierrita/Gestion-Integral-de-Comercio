# Entrega 28 - Seguridad multicomercio y permisos en Compras

## Objetivo

Adaptar el módulo de Compras del Sistema de Gestión Integral de Comercio
a la arquitectura multicomercio, incorporando autenticación mediante JWT,
control de permisos, aislamiento de datos por comercio y reglas de seguridad.

---

## Arquitectura

El módulo mantiene la arquitectura por capas:

Route → Controller → Service → Model → Supabase

La información del usuario y del comercio autenticado se obtiene desde el
token JWT mediante el contexto `g` de Flask.

El frontend no puede decidir qué usuario o comercio realiza una compra.

---

## Rutas implementadas

### GET /compras

Permite consultar las compras pertenecientes al comercio autenticado.

Requiere:

- Usuario autenticado.
- Permiso `compras.ver`.

Las compras se filtran mediante `id_comercio`.

---

### GET /compras/<id_compra>

Permite consultar una compra específica junto con sus detalles.

Requiere:

- Usuario autenticado.
- Permiso `compras.ver`.

La compra solamente puede ser consultada si pertenece al comercio
del usuario autenticado.

---

### POST /compras

Permite registrar una nueva compra.

Requiere:

- Usuario autenticado.
- Permiso `compras.registrar`.

El backend controla automáticamente:

- `id_usuario`
- `id_comercio`
- `numero_compra`
- `estado`
- `total_compra`

Por lo tanto, estos valores no pueden ser manipulados desde el frontend.

El número de compra se genera mediante el contador local del comercio
utilizando la RPC `obtener_siguiente_numero`.

Cada comercio mantiene su propia numeración de compras.

Ejemplo:

Comercio 1:

- Compra #1
- Compra #2
- Compra #3

Comercio 2:

- Compra #1
- Compra #2
- Compra #3

Los IDs globales de la base de datos continúan siendo únicos.

---

## Validación del proveedor

Antes de registrar una compra se verifica que:

- El proveedor exista.
- Pertenezca al comercio autenticado.
- Se encuentre activo.

Esto evita registrar compras utilizando proveedores pertenecientes
a otros comercios.

---

## Validación de productos

Cada producto incluido en una compra debe:

- Existir.
- Pertenecer al comercio autenticado.
- Encontrarse activo.
- Tener una cantidad válida.
- Tener un precio unitario válido.

También se evita incluir el mismo producto más de una vez dentro
de una misma compra.

---

## Actualización automática de stock

Al registrar una compra se incrementa automáticamente el stock
de cada producto.

También se registra el movimiento correspondiente en
`historial_movimiento`.

Tipo de movimiento:

`COMPRA`

El movimiento almacena:

- Producto.
- Usuario autenticado.
- Cantidad.
- Stock anterior.
- Stock nuevo.
- Número local de compra.
- ID global de la compra.

---

## Actualización de precios

Si el nuevo precio de compra es superior al costo actual del producto,
el sistema actualiza el precio de costo.

También recalcula el precio de venta manteniendo el porcentaje de
recargo existente.

Si el nuevo costo es igual o inferior al costo actual, los precios
existentes se mantienen.

---

## Anulación de compras

### PATCH /compras/<id_compra>/anular

La anulación de compras es una operación exclusiva del propietario.

Un empleado no puede anular una compra aunque tenga permisos para
consultar o registrar compras.

Al anular una compra:

1. Se verifica que pertenezca al comercio autenticado.
2. Se verifica que no haya sido anulada anteriormente.
3. Se obtienen sus productos.
4. Se valida que exista stock suficiente para revertirla.
5. Se descuenta del stock la cantidad incorporada por la compra.
6. Se registra un movimiento `ANULACION_COMPRA`.
7. La compra cambia a estado `ANULADA`.

La anulación no reduce automáticamente los precios actuales
del producto.

---

## Seguridad multicomercio

Todas las operaciones principales utilizan el `id_comercio`
obtenido desde el usuario autenticado.

El frontend no puede seleccionar manualmente el comercio sobre
el cual operar.

Esto evita que un usuario pueda consultar o modificar información
perteneciente a otro comercio mediante manipulación de IDs.

---

## Permisos utilizados

### compras.ver

Permite:

- Listar compras.
- Consultar una compra individual.

### compras.registrar

Permite:

- Registrar nuevas compras.

### Anular compra

Operación exclusiva del propietario.

---

## Pruebas realizadas en Postman

### 1. Listado de compras como propietario

Se realizó:

GET /compras

Resultado:

- HTTP 200.
- Se obtuvieron únicamente compras del comercio autenticado.

---

### 2. Validación inicial de permisos del empleado

Se intentó listar y registrar compras con un empleado que todavía
no poseía los permisos correspondientes.

Resultado:

HTTP 403

Mensaje:

`No tiene permisos para realizar esta operación`

Esto permitió comprobar que el sistema de permisos estaba funcionando.

Posteriormente se agregaron al rol CAJERO:

- `compras.ver`
- `compras.registrar`

---

### 3. Registro seguro de compra

Se realizó una compra utilizando un empleado.

En el Body se enviaron intencionalmente valores manipulados:

- `id_usuario = 999`
- `id_comercio = 999`
- `numero_compra = 999`
- `estado = ANULADA`

El backend ignoró estos valores.

Resultado real:

- id_usuario: 2
- id_comercio: 1
- numero_compra: 13
- estado: COMPLETADA
- id_proveedor: 2
- total_compra: 1700

Esto demuestra que los campos sensibles son controlados
por el backend.

---

## Prueba de stock

Producto utilizado:

Sprite 500ml

Antes de la compra:

Stock: 28

Cantidad comprada:

2

Después de registrar la compra:

Stock: 30

El costo enviado fue igual al costo actual:

850

Por lo tanto:

- El costo permaneció en 850.
- El precio de venta permaneció en 1400.
- `precio_actualizado` fue false.

---

## Consulta individual

Se consultó:

GET /compras/13

Resultado:

- Compra encontrada correctamente.
- numero_compra: 13.
- id_comercio: 1.
- id_usuario: 2.
- total_compra: 1700.
- Detalle correctamente asociado.

---

## Intento de anulación por empleado

Se realizó:

PATCH /compras/13/anular

utilizando el token del empleado.

Resultado:

HTTP 403

Mensaje:

`Esta operación es exclusiva del propietario`

La compra permaneció COMPLETADA.

---

## Anulación por propietario

Se realizó la misma operación utilizando el token del propietario.

Resultado:

- HTTP 200.
- Estado de compra: ANULADA.
- Stock Sprite: 30 → 28.

El movimiento de anulación fue ejecutado por el usuario autenticado
que realizó la operación.

---

## Protección contra doble anulación

Se intentó anular nuevamente la compra #13.

Resultado:

HTTP 400

Mensaje:

`La compra ya se encuentra anulada`

Esto evita descontar el stock más de una vez.

---

## Estado final de la prueba

Compra:

- id_compra: 13
- numero_compra: 13
- id_comercio: 1
- id_usuario: 2
- id_proveedor: 2
- total_compra: 1700
- estado: ANULADA

Producto Sprite 500ml:

- Stock inicial: 28
- Stock después de compra: 30
- Stock después de anulación: 28

---

## Resultado final

El módulo de Compras quedó adaptado a la arquitectura multicomercio.

Se implementaron:

- Autenticación JWT.
- Permisos por rol.
- Aislamiento por comercio.
- Numeración local de compras.
- Protección de campos sensibles.
- Validación de proveedores.
- Validación de productos.
- Actualización automática de stock.
- Registro de movimientos.
- Actualización controlada de precios.
- Anulación exclusiva del propietario.
- Protección contra doble anulación.

El módulo queda preparado para integrarse posteriormente con el
frontend React del Sistema de Gestión Integral de Comercio.