# Entrega 29 — Seguridad Multicomercio y Permisos en Ventas

## Objetivo

Adaptar el módulo de ventas al funcionamiento multicomercio del sistema, incorporando autenticación mediante JWT, permisos por rol, aislamiento de información por comercio y protección de las operaciones sensibles.

Además, se integró el módulo de ventas con el control de stock y el módulo financiero, permitiendo registrar y anular una venta manteniendo la consistencia de las operaciones relacionadas.

---

## Arquitectura utilizada

El módulo mantiene la arquitectura por capas utilizada en el backend:

```text
Route
  ↓
Controller
  ↓
Service
  ↓
Model
  ↓
Supabase / PostgreSQL
```

### Responsabilidad de cada capa

- **Routes:** definición de endpoints, autenticación y permisos.
- **Controllers:** recepción de solicitudes HTTP y utilización del contexto del usuario autenticado.
- **Services:** validaciones y reglas de negocio.
- **Models:** acceso a Supabase y ejecución de operaciones sobre la base de datos.
- **Supabase/PostgreSQL:** persistencia de ventas, detalles, stock y movimientos financieros.

---

# Seguridad implementada

## Autenticación JWT

Todas las rutas del módulo de ventas requieren autenticación.

El token JWT permite identificar al usuario que realiza la solicitud y, a partir de ese usuario, determinar de manera segura:

- `id_usuario`
- `id_comercio`
- rol
- permisos
- condición de propietario

El backend no confía en valores sensibles enviados manualmente desde el frontend.

---

## Aislamiento multicomercio

Las ventas se encuentran asociadas a un comercio mediante:

```text
id_comercio
```

Las consultas y operaciones principales utilizan el comercio obtenido desde el usuario autenticado.

Esto evita que un usuario pueda consultar o modificar ventas pertenecientes a otro comercio simplemente enviando otro `id_comercio`.

---

# Permisos

Se utilizaron los permisos existentes:

```text
ventas.ver
ventas.crear
```

### `ventas.ver`

Permite:

```text
GET /ventas
GET /ventas/<id_venta>
```

### `ventas.crear`

Permite:

```text
POST /ventas
```

### Anulación de ventas

La operación:

```text
PATCH /ventas/<id_venta>/anular
```

es exclusiva del propietario del comercio.

Un empleado, incluso teniendo permisos para registrar ventas, no puede anularlas.

---

# Endpoints

## Registrar venta

```http
POST /ventas
```

Requiere:

```text
login_requerido
ventas.crear
```

El backend controla automáticamente:

- usuario que registra la venta
- comercio
- número local de venta
- estado inicial
- total
- precio de venta
- costo histórico

---

## Listar ventas

```http
GET /ventas
```

Requiere:

```text
login_requerido
ventas.ver
```

Devuelve únicamente las ventas pertenecientes al comercio autenticado.

---

## Consultar venta

```http
GET /ventas/<id_venta>
```

Requiere:

```text
login_requerido
ventas.ver
```

La venta solamente puede obtenerse si pertenece al comercio del usuario autenticado.

También se devuelven sus detalles.

---

## Anular venta

```http
PATCH /ventas/<id_venta>/anular
```

Requiere:

```text
login_requerido
solo_propietario
```

La operación:

1. verifica que la venta pertenezca al comercio;
2. verifica que no se encuentre anulada;
3. obtiene sus productos;
4. revierte el movimiento financiero cuando corresponde;
5. devuelve los productos al stock;
6. registra los movimientos de anulación;
7. cambia el estado de la venta a `ANULADA`.

---

# Numeración local de ventas

Cada comercio mantiene su propia numeración de ventas.

Se utiliza la función RPC:

```text
obtener_siguiente_numero
```

con:

```text
entidad = VENTA
```

De esta manera se diferencia:

```text
id_venta
```

como identificador global de la base de datos, de:

```text
numero_venta
```

como número visible y correlativo dentro de cada comercio.

La combinación:

```text
(id_comercio, numero_venta)
```

es única.

---

# Validación del cliente

Antes de registrar una venta se verifica que:

- el cliente exista;
- pertenezca al comercio autenticado;
- se encuentre activo.

El cliente no puede obtenerse globalmente utilizando solamente su ID.

---

# Validación de productos

Antes de registrar la venta, cada producto debe:

- existir;
- pertenecer al comercio autenticado;
- encontrarse activo;
- tener precio de venta válido;
- tener precio de costo válido;
- poseer stock suficiente.

También se impide enviar dos veces el mismo producto dentro de una misma venta.

---

# Protección de precios

El backend no utiliza los precios enviados por el cliente.

Para cada producto obtiene directamente desde la base de datos:

```text
precio_venta
precio_costo
```

El precio de venta se almacena como:

```text
precio_unitario
```

y el costo actual queda almacenado como:

```text
costo_unitario
```

dentro de `detalle_venta`.

Esto permite conservar información histórica para posteriores cálculos de rentabilidad.

---

# Cálculo del total

El total de la venta es calculado exclusivamente por el backend.

Para cada producto:

```text
subtotal = cantidad × precio_unitario
```

Luego:

```text
total_venta = suma de subtotales
```

Por lo tanto, un cliente no puede modificar manualmente el total de una venta.

---

# Control de stock

Al registrar una venta:

```text
stock_nuevo = stock_anterior - cantidad
```

Además se registra un movimiento:

```text
VENTA
```

en `historial_movimiento`.

El movimiento almacena:

- producto
- usuario
- cantidad
- stock anterior
- stock nuevo
- referencia a la venta

---

# Integración financiera

## Venta cobrada

Cuando el método de pago no es:

```text
CUENTA_CORRIENTE
```

la venta debe indicar una cuenta financiera válida.

Antes de registrar el ingreso se verifica que la cuenta:

- exista;
- pertenezca al comercio autenticado;
- se encuentre activa.

Luego se ejecuta:

```text
registrar_ingreso_venta
```

La función RPC:

- aumenta el saldo de la cuenta;
- registra el movimiento financiero;
- vincula el movimiento con la venta.

---

## Venta en cuenta corriente

Cuando:

```text
metodo_pago = CUENTA_CORRIENTE
```

la venta no genera un ingreso financiero inmediato.

La deuda queda asociada al cliente y posteriormente puede cancelarse mediante el módulo de cobros.

---

# Anulación de ventas

La anulación es una operación sensible y solamente puede realizarla el propietario.

Antes de anular se verifica:

- existencia de la venta;
- pertenencia al comercio;
- estado actual;
- productos relacionados.

---

## Reversión financiera

Si la venta había generado un ingreso se utiliza:

```text
anular_ingreso_venta
```

La función revierte el ingreso correspondiente.

Si la venta era en cuenta corriente y no había generado un ingreso financiero inmediato, no existe movimiento de ingreso para revertir.

---

## Restauración de stock

Por cada producto:

```text
stock_nuevo = stock_actual + cantidad_vendida
```

Se registra un movimiento:

```text
ANULACION_VENTA
```

El usuario registrado en la operación es el usuario autenticado que realiza la anulación.

---

## Prevención de doble anulación

Si la venta ya tiene:

```text
estado = ANULADA
```

una nueva solicitud de anulación es rechazada.

Esto evita:

- duplicar stock;
- generar movimientos repetidos;
- realizar múltiples reversiones financieras.

---

# Pruebas realizadas

## Consulta de ventas como propietario

```http
GET /ventas
```

Resultado:

```text
200 OK
```

Las ventas fueron obtenidas correctamente.

---

## Consulta de ventas como empleado

Se utilizó un empleado con permiso:

```text
ventas.ver
```

Resultado:

```text
200 OK
```

---

# Prueba de seguridad en creación

Se realizó una venta enviando intencionalmente valores manipulados:

```json
{
    "id_usuario": 999,
    "id_comercio": 999,
    "numero_venta": 999,
    "total": 1,
    "estado": "ANULADA",
    "id_cliente": 3,
    "metodo_pago": "EFECTIVO",
    "id_cuenta": 1,
    "productos": [
        {
            "id_producto": 2,
            "cantidad": 2,
            "precio_unitario": 1,
            "costo_unitario": 1
        }
    ]
}
```

El backend ignoró los campos manipulados.

Resultado real:

```text
id_venta = 14
numero_venta = 14
id_usuario = 2
id_comercio = 1
estado = COMPLETADA
total = 2800
precio_unitario = 1400
costo_unitario = 850
```

Esto confirmó que los datos sensibles son controlados por el backend.

---

# Prueba de stock

Producto utilizado:

```text
Sprite 500ml
```

Antes:

```text
stock = 28
```

Venta:

```text
cantidad = 2
```

Después:

```text
stock = 26
```

Resultado correcto.

---

# Prueba financiera

La venta generó:

```text
$2.800
```

de ingreso.

Cuenta financiera:

```text
saldo anterior = 864300
saldo nuevo = 867100
```

Movimiento financiero:

```text
id_movimiento = 22
```

Resultado correcto.

---

# Prueba de seguridad de anulación

El empleado intentó:

```http
PATCH /ventas/14/anular
```

Resultado:

```text
403 Forbidden
```

Respuesta:

```json
{
    "error": "Esta operación es exclusiva del propietario"
}
```

Resultado correcto.

---

# Anulación realizada por propietario

El propietario ejecutó:

```http
PATCH /ventas/14/anular
```

Resultado:

```text
200 OK
```

La venta pasó a:

```text
ANULADA
```

---

# Restauración de stock

Antes de anular:

```text
Sprite 500ml = 26
```

Después:

```text
Sprite 500ml = 28
```

Resultado correcto.

---

# Reversión financiera

Antes:

```text
saldo = 867100
```

Después:

```text
saldo = 864300
```

Monto revertido:

```text
2800
```

Movimiento de reversión:

```text
id_movimiento = 23
```

Resultado correcto.

---

# Doble anulación

Se intentó anular nuevamente la misma venta.

Resultado:

```text
400 Bad Request
```

Respuesta:

```json
{
    "error": "La venta ya se encuentra anulada"
}
```

El sistema evitó correctamente duplicar la operación.

---

# Archivos modificados

```text
Backend/app/models/venta_model.py
Backend/app/services/venta_service.py
Backend/app/controllers/venta_controller.py
Backend/app/routes/venta_routes.py
```

Documentación:

```text
Docs/entrega29/README.md
```

---

# Resultado final

El módulo de ventas quedó adaptado a la arquitectura multicomercio del sistema.

Se implementaron:

- autenticación JWT;
- permisos por rol;
- aislamiento por comercio;
- numeración local;
- validación de clientes;
- validación de productos;
- validación de cuentas;
- protección de precios y costos;
- cálculo seguro del total;
- control automático de stock;
- historial de movimientos;
- integración financiera;
- soporte para cuenta corriente;
- anulación exclusiva del propietario;
- restauración de stock;
- reversión financiera;
- prevención de doble anulación.

La funcionalidad fue probada mediante Postman utilizando tanto un usuario propietario como un empleado con permisos limitados.

**Entrega 29 completada.**