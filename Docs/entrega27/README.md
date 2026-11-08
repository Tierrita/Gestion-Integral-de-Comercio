# Entrega 27 - Seguridad multicomercio y permisos en Clientes

## Objetivo

Adaptar el módulo de clientes a la arquitectura multicomercio del sistema, incorporando aislamiento de datos por comercio, autenticación JWT, permisos por rol y protección de campos sensibles.

## Arquitectura utilizada

El módulo mantiene la arquitectura general del backend:

Route → Controller → Service → Model → Supabase

La identidad del comercio y del usuario se obtiene desde el JWT autenticado y no desde datos enviados por el frontend.

---

## Funcionalidades implementadas

### Listar clientes

GET /clientes

Permiso requerido:

clientes.ver

Los clientes son filtrados automáticamente por el comercio del usuario autenticado.

---

### Consultar cliente

GET /clientes/<id_cliente>

Permiso requerido:

clientes.ver

El cliente solamente puede ser consultado si pertenece al comercio autenticado.

---

### Crear cliente

POST /clientes

Permiso requerido:

clientes.crear

El backend controla automáticamente:

- id_comercio
- numero_cliente
- estado inicial

El número visible del cliente se genera utilizando el contador independiente de cada comercio.

El frontend no puede seleccionar manualmente el comercio ni el número local del cliente.

Los nuevos clientes se crean activos por defecto.

---

### Modificar cliente

PATCH /clientes/<id_cliente>

Permiso requerido:

clientes.modificar

Los únicos campos modificables mediante esta ruta son:

- nombre_completo
- telefono

Los campos sensibles enviados por el frontend son ignorados.

Entre ellos:

- id_comercio
- numero_cliente
- estado

El estado posee una ruta específica.

---

### Modificar estado

PATCH /clientes/<id_cliente>/estado

Permiso requerido:

clientes.modificar

Permite activar o desactivar clientes.

Se incorporó una regla especial para CLIENTE GENERAL.

CLIENTE GENERAL no puede ser desactivado.

Dentro de cada comercio se identifica actualmente mediante:

numero_cliente = 1

---

### Historial de ventas del cliente

GET /clientes/<id_cliente>/ventas

Permiso requerido:

clientes.ver

Devuelve:

- datos del cliente
- cantidad de ventas
- ventas realizadas
- detalles de cada venta

Las ventas son filtradas por cliente y por comercio, evitando acceder al historial perteneciente a otro comercio.

---

## Seguridad multicomercio

Todas las operaciones utilizan el comercio obtenido desde el usuario autenticado.

El backend no confía en valores de id_comercio enviados desde el frontend.

Esto evita que un usuario pueda consultar o modificar clientes pertenecientes a otro comercio manipulando manualmente las peticiones HTTP.

---

## Permisos utilizados

- clientes.ver
- clientes.crear
- clientes.modificar
- clientes.ver_deuda

Durante las pruebas se verificó también que un empleado sin los permisos correspondientes recibe:

403 Forbidden

Posteriormente se habilitaron los permisos necesarios al rol CAJERO para continuar las pruebas del módulo.

---

## Pruebas realizadas en Postman

### 1. Listado de clientes

Se consultó:

GET /clientes

Resultado:

200 OK

Se obtuvieron únicamente los clientes correspondientes al comercio autenticado.

---

### 2. Validación de permisos

Se intentaron realizar operaciones de creación y modificación utilizando un empleado que inicialmente no poseía los permisos necesarios.

Resultado:

403 Forbidden

Respuesta:

{
    "error": "No tiene permisos para realizar esta operación"
}

Esto confirmó el funcionamiento del sistema de autorización por permisos.

---

### 3. Creación segura de cliente

Se envió intencionalmente:

{
    "nombre_completo": "Cliente Prueba Entrega 27",
    "telefono": "2474123456",
    "id_comercio": 999,
    "numero_cliente": 999,
    "estado": false
}

Resultado almacenado:

- id_cliente: 6
- id_comercio: 1
- numero_cliente: 6
- estado: true

El backend ignoró correctamente los valores sensibles enviados por el cliente HTTP.

---

### 4. Historial de ventas

Se consultó el historial del cliente con id_cliente 3.

Resultado:

200 OK

Se recuperaron correctamente 5 ventas junto con sus respectivos detalles.

Las ventas pertenecían al comercio autenticado.

---

### 5. Protección de CLIENTE GENERAL

Se intentó ejecutar:

PATCH /clientes/1/estado

con:

{
    "estado": false
}

Resultado:

400 Bad Request

Respuesta:

{
    "error": "CLIENTE GENERAL no puede ser desactivado"
}

La regla de negocio funcionó correctamente.

---

### 6. Modificación segura

Se modificó el cliente de prueba id_cliente 6 enviando:

{
    "nombre_completo": "Cliente Prueba Editado",
    "telefono": "2474000000",
    "id_comercio": 999,
    "numero_cliente": 999,
    "estado": false
}

Resultado final:

- id_cliente: 6
- id_comercio: 1
- numero_cliente: 6
- estado: true
- nombre_completo: Cliente Prueba Editado
- telefono: 2474000000

Se comprobó que solamente fueron modificados los campos permitidos.

---

## Resultado final

El módulo de clientes quedó integrado con:

- autenticación JWT
- permisos por rol
- arquitectura multicomercio
- aislamiento de datos
- numeración local por comercio
- protección de campos sensibles
- protección de CLIENTE GENERAL
- historial de ventas aislado por comercio

El módulo queda preparado para ser consumido posteriormente desde el frontend React.
