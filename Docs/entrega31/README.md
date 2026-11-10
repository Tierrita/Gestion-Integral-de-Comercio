# Entrega 31 – Validación Integral Multicomercio

## Objetivo

Realizar una prueba integral del backend utilizando dos comercios independientes para verificar que la arquitectura multicomercio funcione correctamente y que ningún usuario pueda acceder, consultar o modificar información perteneciente a otro comercio.

La validación se realizó utilizando autenticación mediante JWT y ejecutando las solicitudes desde Postman.

---

# 1. Escenario de prueba

Se utilizaron dos comercios independientes.

## Comercio 1

- ID comercio: 1
- Comercio principal utilizado durante el desarrollo
- Posee productos, clientes, proveedores, ventas, compras, cuentas y movimientos financieros históricos.

## Comercio 2

- ID comercio: 3
- Nombre: Comercio Prueba 2
- Usuario propietario: ID 3
- Email: propietario2@comercio.com

El Comercio 2 fue creado específicamente para realizar pruebas de aislamiento multicomercio.

---

# 2. Autenticación del Comercio 2

Se inició sesión mediante:

POST /auth/login

El backend devolvió correctamente un JWT correspondiente a:

- id_usuario: 3
- id_comercio: 3
- es_propietario: true

A partir de este momento todas las operaciones del Comercio 2 fueron realizadas utilizando este token.

---

# 3. Seguridad basada en JWT

Durante diferentes pruebas se enviaron deliberadamente datos falsificados dentro del Body:

```json
{
    "id_usuario": 1,
    "id_comercio": 1
}
```

aunque el JWT pertenecía a:

```text
id_usuario = 3
id_comercio = 3
```

El backend ignoró correctamente los identificadores enviados por el cliente y utilizó la identidad obtenida desde el JWT.

Esto evita que un usuario pueda cambiar manualmente el comercio o usuario responsable desde Postman, React u otro cliente HTTP.

---

# 4. Productos

Se comprobó que el Comercio 2 inicialmente no podía visualizar productos pertenecientes al Comercio 1.

GET /productos

Resultado inicial:

```json
[]
```

También se intentó acceder directamente a un producto perteneciente al Comercio 1:

GET /productos/1

Resultado:

```json
{
    "error": "Producto no encontrado"
}
```

También se intentó modificar dicho producto desde el Comercio 2 y la operación fue bloqueada.

Posteriormente se creó un producto propio:

- ID global: 15
- Número local: 1
- Comercio: 3
- Nombre: PRODUCTO PRUEBA COMERCIO 2
- Precio costo: $1.500
- Precio venta: $2.500

Aunque el Body intentó enviar `id_comercio = 1`, el producto fue registrado correctamente con:

```text
id_comercio = 3
```

También se realizó la prueba inversa:

Comercio 1 intentando acceder al producto 15 del Comercio 2.

Resultado:

```json
{
    "error": "Producto no encontrado"
}
```

Por lo tanto, el aislamiento de productos funciona en ambos sentidos.

---

# 5. Categorías

El Comercio 2 inicialmente no poseía categorías.

Se creó:

- ID global: 7
- Nombre: BEBIDAS COMERCIO 2
- Comercio: 3

Durante la creación se intentó falsificar `id_comercio = 1`.

El backend ignoró dicho valor y registró correctamente la categoría dentro del comercio autenticado.

---

# 6. Stock

El listado de stock del Comercio 2 mostró únicamente:

- Producto 15
- Número local 1
- Comercio 3

No se visualizaron productos pertenecientes al Comercio 1.

Se realizó un ajuste:

```text
Stock anterior: 0
Cantidad: +10
Stock nuevo: 10
Movimiento: AJUSTE_ENTRADA
```

Posteriormente se intentó ajustar desde el Comercio 2 el producto 1 perteneciente al Comercio 1.

Resultado:

```json
{
    "error": "Producto no encontrado"
}
```

También se consultaron las alertas:

GET /stock/alertas

Resultado:

```json
[]
```

Las alertas del Comercio 1 tampoco fueron expuestas.

---

# 7. Proveedores

Se creó un proveedor propio del Comercio 2:

- ID global: 7
- Número local: 1
- Nombre: PROVEEDOR PRUEBA COMERCIO 2
- Comercio: 3

Aunque se intentó enviar `id_comercio = 1`, el backend utilizó el comercio proveniente del JWT.

Se realizaron pruebas de acceso cruzado.

Comercio 1 → Proveedor Comercio 2:

```json
{
    "error": "Proveedor no encontrado"
}
```

Comercio 2 → Proveedor Comercio 1:

```json
{
    "error": "Proveedor no encontrado"
}
```

El aislamiento bidireccional quedó validado.

---

# 8. Clientes

Inicialmente:

GET /clientes

desde Comercio 2 devolvió:

```json
[]
```

Se creó posteriormente:

- ID global: 7
- Número local: 1
- Nombre: CLIENTE PRUEBA COMERCIO 2
- Comercio: 3

Nuevamente se enviaron identificadores falsos correspondientes al Comercio 1.

El backend registró correctamente:

```text
id_comercio = 3
numero_cliente = 1
```

---

# 9. Compras

Se registró una compra utilizando:

- Proveedor: 7
- Producto: 15
- Cantidad: 5
- Precio unitario: $1.500

Resultado:

```text
ID global compra: 14
Número local compra: 1
Comercio: 3
Usuario: 3
Total: $7.500
```

El stock fue actualizado correctamente:

```text
10 → 15 unidades
```

Los valores falsificados:

```text
id_usuario = 1
id_comercio = 1
```

fueron ignorados.

El backend utilizó:

```text
id_usuario = 3
id_comercio = 3
```

provenientes del JWT.

---

# 10. Ventas

Se registró una venta a cuenta corriente:

- Cliente: 7
- Producto: 15
- Cantidad: 2
- Precio unitario: $2.500

Resultado:

```text
ID global venta: 16
Número local venta: 1
Total: $5.000
Usuario: 3
Comercio: 3
```

El stock fue actualizado:

```text
15 → 13 unidades
```

Al tratarse de una venta a cuenta corriente no se generó inmediatamente un ingreso de caja.

También se intentó acceder desde Comercio 2 a una venta perteneciente al Comercio 1:

GET /ventas/1

Resultado:

```json
{
    "error": "Venta no encontrada"
}
```

---

# 11. Cuentas

Al consultar:

GET /cuentas

desde Comercio 2 se obtuvo únicamente:

```text
ID cuenta: 5
Nombre: CAJA PRINCIPAL
Comercio: 3
Saldo inicial: $0
```

La CAJA PRINCIPAL perteneciente al Comercio 1 no fue expuesta.

---

# 12. Cobros

Se registró un cobro parcial correspondiente al cliente 7.

Monto:

```text
$2.000
```

Resultado:

```text
ID cobro: 14
ID comercio: 3
ID usuario: 3
ID cuenta: 5
ID movimiento financiero: 30

Saldo anterior: $0
Saldo nuevo: $2.000
```

La deuda generada por la venta era:

```text
$5.000
```

Luego del cobro parcial:

```text
Cobrado: $2.000
Saldo pendiente: $3.000
```

Esto confirmó el flujo:

```text
Venta a cuenta corriente
        ↓
Deuda del cliente
        ↓
Cobro
        ↓
Cuenta
        ↓
Movimiento financiero
```

---

# 13. Finanzas

Se consultó:

GET /finanzas/dashboard

utilizando el JWT del propietario del Comercio 2.

El dashboard devolvió exclusivamente información correspondiente al Comercio 2.

## Ventas

```text
Cantidad ventas: 1
Facturación: $5.000
Ticket promedio: $5.000
Unidades vendidas: 2
```

## Rentabilidad

```text
Facturación: $5.000
Costo vendido: $3.000
Ganancia bruta: $2.000
Margen bruto: 40%
```

## Caja

```text
Entradas: $2.000
Salidas: $0
Saldo neto: $2.000
```

## Clientes

```text
Clientes con deuda: 1
Total por cobrar: $3.000
```

## Proveedores

```text
Total comprado: $7.500
Deuda proveedores: $7.500
```

## Stock

```text
Unidades en stock: 13
Valor a costo: $19.500
Valor a venta: $32.500
Ganancia potencial: $13.000
```

## Rankings

El dashboard identificó correctamente como entidades principales del Comercio 2:

- Cliente 7
- Proveedor 7
- Producto 15

No apareció información financiera perteneciente al Comercio 1.

---

# 14. Corrección detectada durante la prueba integral

Durante la preparación del segundo comercio se detectó una restricción de base de datos que impedía crear una cuenta llamada:

```text
CAJA PRINCIPAL
```

en más de un comercio.

La causa era un índice UNIQUE global basado únicamente en el nombre de la cuenta.

La restricción anterior no era compatible con una arquitectura multicomercio, ya que diferentes comercios deben poder utilizar nombres iguales para sus propias cuentas.

Se reemplazó por una restricción de unicidad compuesta:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS uq_cuentas_comercio_nombre_lower
ON public.cuentas (
    id_comercio,
    LOWER(TRIM(nombre_cuenta))
);
```

A partir de esta modificación, cada comercio puede poseer su propia:

```text
CAJA PRINCIPAL
```

sin generar conflictos con otros comercios.

---

# 15. Numeración local

La prueba integral también permitió verificar la estrategia de identificadores.

Las entidades poseen un ID global utilizado internamente por la base de datos y, cuando corresponde, un número local visible dentro de cada comercio.

En Comercio 2 se obtuvo:

```text
Producto:
ID global = 15
Número local = 1

Proveedor:
ID global = 7
Número local = 1

Cliente:
ID global = 7
Número local = 1

Compra:
ID global = 14
Número local = 1

Venta:
ID global = 16
Número local = 1
```

Esto confirma que cada comercio puede comenzar su numeración comercial desde 1 independientemente de los registros existentes en otros comercios.

---

# 16. Resultado final

La prueba integral permitió validar correctamente:

- Autenticación mediante JWT.
- Obtención segura del usuario autenticado.
- Obtención segura del comercio autenticado.
- Aislamiento de productos.
- Aislamiento de categorías.
- Aislamiento de stock.
- Aislamiento de proveedores.
- Aislamiento de clientes.
- Aislamiento de compras.
- Aislamiento de ventas.
- Aislamiento de cobros.
- Aislamiento de cuentas.
- Aislamiento de información financiera.
- Numeración local independiente por comercio.
- Protección frente a manipulación de `id_usuario`.
- Protección frente a manipulación de `id_comercio`.
- Acceso directo por ID limitado al comercio autenticado.

---

# Conclusión

La arquitectura multicomercio quedó validada utilizando dos comercios reales dentro de la misma base de datos.

Las pruebas demostraron que el backend no confía en identificadores de usuario o comercio enviados por el cliente y utiliza el contexto autenticado mediante JWT.

Cada comercio mantiene aislados sus productos, categorías, proveedores, clientes, stock, compras, ventas, cobros, cuentas e información financiera.

También se comprobó el funcionamiento de numeraciones locales independientes y se corrigió una restricción de base de datos detectada durante la prueba integral.

Con esta validación, el backend queda preparado para realizar la revisión final correspondiente a la versión Backend V1 antes de comenzar el desarrollo del frontend en React.