# Entrega 26 - Proveedores y Pagos a Proveedores

## Objetivo

Adaptar el módulo de proveedores y pagos a proveedores a la arquitectura multicomercio, incorporando autenticación JWT, permisos por rol, aislamiento de datos y protección de operaciones sensibles.

---

## Arquitectura utilizada

Route → Controller → Service → Model → Supabase

El comercio no se recibe desde el frontend.

El backend obtiene automáticamente:

- id_usuario desde el JWT.
- id_comercio desde el usuario autenticado.
- permisos desde el rol del usuario.

---

## Proveedores

### GET /proveedores

Lista únicamente los proveedores pertenecientes al comercio autenticado.

Permiso requerido:

proveedores.ver

---

### GET /proveedores/<id_proveedor>

Obtiene un proveedor específico verificando que pertenezca al comercio autenticado.

Permiso requerido:

proveedores.ver

---

### POST /proveedores

Crea un proveedor dentro del comercio autenticado.

Permiso requerido:

proveedores.crear

El backend controla automáticamente:

- id_comercio
- numero_proveedor
- estado inicial

Por seguridad, estos valores no pueden ser definidos desde el frontend.

El estado inicial siempre es:

true

---

### PATCH /proveedores/<id_proveedor>

Permite modificar los datos comerciales de un proveedor.

Permiso requerido:

proveedores.modificar

Campos sensibles como id_comercio, numero_proveedor y estado no se modifican mediante este endpoint.

---

### PATCH /proveedores/<id_proveedor>/estado

Permite activar o desactivar un proveedor mediante un endpoint específico.

Permiso requerido:

proveedores.modificar

Se evita realizar cambios redundantes de estado.

---

## Numeración de proveedores

Cada comercio posee su propia numeración visible de proveedores.

La combinación:

(id_comercio, numero_proveedor)

se encuentra protegida mediante un índice UNIQUE en PostgreSQL.

Esto permite que distintos comercios puedan tener, por ejemplo, su propio proveedor número 1 sin generar conflictos.

---

# Pagos a proveedores

Los pagos no poseen directamente id_comercio.

El aislamiento multicomercio se realiza mediante la relación:

Pago → Proveedor → Comercio

De esta forma, un usuario solamente puede consultar pagos asociados a proveedores pertenecientes a su comercio.

---

### POST /pagos-proveedor

Registra un pago a un proveedor.

Permiso requerido:

proveedores.registrar_pagos

El backend obtiene id_usuario directamente desde el JWT.

El frontend no puede definir:

- id_usuario
- estado del pago

Todo pago nuevo se registra automáticamente como:

COMPLETADO

---

### GET /pagos-proveedor

Lista los pagos asociados a proveedores del comercio autenticado.

Permiso requerido:

proveedores.ver

---

### GET /pagos-proveedor/<id_pago>

Consulta un pago específico respetando el aislamiento multicomercio.

Permiso requerido:

proveedores.ver

---

### GET /proveedores/<id_proveedor>/pagos

Consulta el historial de pagos de un proveedor perteneciente al comercio autenticado.

Permiso requerido:

proveedores.ver

---

### GET /proveedores/<id_proveedor>/saldo

Calcula la situación financiera con el proveedor.

Se consideran:

- compras no anuladas;
- pagos completados.

Cálculo:

saldo = total_compras - total_pagos

Estados posibles:

- DEUDA
- AL_DIA
- SALDO_A_FAVOR

Permiso requerido:

proveedores.ver

---

### PATCH /pagos-proveedor/<id_pago>/anular

Permite anular un pago.

Esta operación es exclusiva del propietario.

Al anular se registra:

- estado = ANULADO
- id_usuario_anulacion
- fecha_anulacion
- motivo_anulacion

Esto permite conservar la trazabilidad del movimiento sin eliminar información histórica.

---

# Seguridad implementada

Se incorporaron las siguientes protecciones:

- Autenticación mediante JWT.
- Aislamiento por comercio.
- Permisos por rol.
- id_usuario obtenido desde el JWT.
- id_comercio obtenido desde el usuario autenticado.
- Estado inicial controlado por backend.
- Numeración de proveedor controlada por backend.
- Anulación de pagos exclusiva del propietario.
- Conservación del historial de pagos anulados.
- Validación de pertenencia del proveedor al comercio.
- Validación de pertenencia de pagos mediante el proveedor.

---

# Permisos utilizados

- proveedores.ver
- proveedores.crear
- proveedores.modificar
- proveedores.registrar_pagos

---

# Pruebas realizadas

## Consulta de proveedores

El propietario pudo consultar correctamente los proveedores pertenecientes a su comercio.

Resultado:

200 OK

---

## Permisos de empleado

Un empleado sin permisos de proveedores fue bloqueado.

Resultado:

403 Forbidden

Luego de asignar los permisos correspondientes pudo acceder al módulo.

---

## Seguridad en creación de proveedor

Se verificó que el backend controle:

- id_comercio
- numero_proveedor
- estado

El proveedor de prueba fue creado correctamente con:

- id_comercio = 1
- numero_proveedor = 6
- estado = true

Los valores sensibles enviados desde el frontend fueron ignorados.

---

## Seguridad al registrar pagos

Se registró un pago utilizando un empleado autenticado.

Aunque desde el Body se intentó enviar otro id_usuario y otro estado, el backend registró:

- id_usuario = 2
- estado = COMPLETADO

Esto confirma que la identidad del usuario se obtiene desde el JWT.

---

## Saldo del proveedor

Para un proveedor sin compras y con un pago completado de $1000 se obtuvo:

- total_compras = 0
- total_pagos = 1000
- saldo = -1000
- situacion = SALDO_A_FAVOR

---

## Protección de anulación

El empleado intentó anular el pago.

Resultado:

403 Forbidden

Mensaje:

"Esta operación es exclusiva del propietario"

Posteriormente, el propietario anuló correctamente el pago.

Se registraron:

- estado = ANULADO
- id_usuario_anulacion = 1
- fecha_anulacion
- motivo_anulacion

---

# Resultado final

El módulo de Proveedores y Pagos a Proveedores queda integrado a la arquitectura multicomercio y al sistema de autenticación, roles y permisos.

Los datos sensibles son controlados por el backend y las operaciones financieras críticas mantienen trazabilidad y restricciones de acceso.