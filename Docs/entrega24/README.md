# ENTREGA 24 – ENDURECIMIENTO MULTICOMERCIO Y PERMISOS DEL MÓDULO CATEGORÍAS

## OBJETIVO

Adaptar completamente el módulo de categorías a la arquitectura multicomercio del sistema, incorporando autenticación JWT, aislamiento de datos por comercio, control de permisos por rol, protección de campos sensibles y reglas de negocio para la activación y desactivación de categorías.

---

## 1. INTEGRACIÓN DE CATEGORÍAS CON EL COMERCIO AUTENTICADO

Se adaptó el módulo de categorías para trabajar utilizando el comercio correspondiente al usuario autenticado.

El backend obtiene el comercio mediante:

`g.id_comercio`

Este valor es establecido durante la validación del token JWT.

De esta forma, el cliente no decide sobre qué comercio operar.

Todas las consultas del modelo de categorías fueron modificadas para incluir el filtro por:

`id_comercio`

Esto permite mantener aislados los datos pertenecientes a diferentes comercios.

---

## 2. PROTECCIÓN DE RUTAS MEDIANTE JWT

Todas las rutas del módulo de categorías requieren autenticación.

Se incorporó:

`@login_requerido`

en los siguientes endpoints:

- `GET /categorias`
- `GET /categorias/<id_categoria>`
- `POST /categorias`
- `PATCH /categorias/<id_categoria>`
- `PATCH /categorias/<id_categoria>/estado`

Una solicitud sin un token JWT válido no puede acceder al módulo.

---

## 3. CONTROL DE PERMISOS

Se integró el sistema de permisos previamente desarrollado.

Se utilizaron los siguientes permisos:

### categorias.ver

Permite:

- consultar todas las categorías;
- consultar una categoría específica.

Se aplica sobre:

- `GET /categorias`
- `GET /categorias/<id_categoria>`

### categorias.gestionar

Permite:

- crear categorías;
- modificar categorías;
- activar categorías;
- desactivar categorías.

Se aplica sobre:

- `POST /categorias`
- `PATCH /categorias/<id_categoria>`
- `PATCH /categorias/<id_categoria>/estado`

Esto permite separar los usuarios que solamente pueden consultar información de aquellos autorizados a modificarla.

---

## 4. AISLAMIENTO MULTICOMERCIO

Las operaciones sobre categorías utilizan simultáneamente el identificador de la categoría y el comercio autenticado.

Por ejemplo, una búsqueda utiliza conceptualmente:

`id_categoria + id_comercio`

Por lo tanto, conocer el ID global de una categoría perteneciente a otro comercio no es suficiente para acceder a ella.

El backend solamente devuelve categorías pertenecientes al comercio autenticado.

---

## 5. CREACIÓN SEGURA DE CATEGORÍAS

Se modificó la creación de categorías para que determinados campos sean controlados exclusivamente por el backend.

El cliente puede proporcionar:

- `nombre_categoria`
- `descripcion`

El backend establece automáticamente:

- `id_comercio`
- `estado = true`

Se realizó una prueba enviando intencionalmente:

`id_comercio = 999`

y:

`estado = false`

El backend ignoró ambos valores y creó correctamente la categoría con:

`id_comercio = 1`

y:

`estado = true`

Esto impide que un cliente pueda crear categorías dentro de otro comercio o alterar el estado inicial.

---

## 6. MODIFICACIÓN SEGURA DE CATEGORÍAS

El endpoint:

`PATCH /categorias/<id_categoria>`

permite modificar únicamente:

- `nombre_categoria`
- `descripcion`

No permite modificar mediante este endpoint:

- `id_categoria`
- `id_comercio`
- `estado`
- `fecha_alta`

Se realizó una prueba intentando modificar estos campos protegidos y el backend respondió:

`No se enviaron campos válidos para actualizar`

De esta forma se evita la manipulación de información sensible desde el cliente.

---

## 7. GESTIÓN INDEPENDIENTE DEL ESTADO

La activación y desactivación de categorías se realiza mediante un endpoint específico:

`PATCH /categorias/<id_categoria>/estado`

Body esperado:

```json
{
    "estado": false
}