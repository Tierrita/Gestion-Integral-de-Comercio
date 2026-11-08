# Entrega 25 — Seguridad multicomercio y permisos en Stock

## Objetivo

Adaptar el módulo de Stock del Sistema de Gestión Integral de Comercio a la arquitectura multicomercio, incorporando autenticación mediante JWT, control de permisos por rol, aislamiento de datos por comercio y trazabilidad de los ajustes realizados.

---

## Funcionalidades implementadas

### 1. Consulta general de stock

Endpoint:

GET /stock

Permite consultar el stock de los productos pertenecientes al comercio del usuario autenticado.

Requiere:

- Usuario autenticado mediante JWT.
- Permiso `stock.ver`.

El `id_comercio` no es recibido desde el frontend, sino que se obtiene desde el usuario autenticado.

De esta manera, cada comercio solamente puede consultar sus propios productos.

---

### 2. Búsqueda de productos dentro del stock

Endpoint:

GET /stock?buscar=texto

Permite buscar productos por nombre dentro del stock del comercio autenticado.

Ejemplo:

GET /stock?buscar=Coca

La búsqueda mantiene el aislamiento multicomercio, por lo que solamente consulta productos pertenecientes al comercio del usuario.

Requiere:

- JWT válido.
- Permiso `stock.ver`.

---

### 3. Alertas de stock mínimo

Endpoint:

GET /stock/alertas

Devuelve los productos activos cuyo stock actual sea menor o igual al stock mínimo configurado.

Condición utilizada:

stock <= stock_minimo

Los productos inactivos no generan alertas operativas.

Requiere:

- JWT válido.
- Permiso `stock.ver`.

---

### 4. Ajuste manual de stock

Endpoint:

PATCH /stock/<id_producto>/ajustar

Permite aumentar o disminuir manualmente el stock de un producto.

Ejemplo de entrada:

{
    "cantidad": 5,
    "tipo_ajuste": "AUMENTAR"
}

Tipos permitidos:

- `AUMENTAR`
- `DISMINUIR`

Requiere:

- JWT válido.
- Permiso `stock.ajustar`.

El sistema valida que:

- La cantidad sea un número entero.
- La cantidad sea mayor a cero.
- El tipo de ajuste sea válido.
- El producto exista.
- El producto pertenezca al comercio autenticado.
- El producto se encuentre activo.
- El stock resultante no sea negativo.

---

## Seguridad mediante JWT

El usuario que realiza el movimiento no se recibe desde el Body de la petición.

El backend obtiene automáticamente desde el JWT:

- `id_usuario`
- `id_comercio`

Esto evita que un cliente pueda intentar enviar manualmente otro usuario o comercio para modificar información que no le corresponde.

---

## Control de permisos

Se utilizaron los permisos:

### stock.ver

Permite:

- Consultar stock.
- Buscar productos en stock.
- Consultar alertas de stock mínimo.

### stock.ajustar

Permite:

- Realizar ajustes manuales de entrada y salida.

Los permisos se verifican mediante los decoradores de seguridad del backend.

Ejemplo:

@login_requerido
@permiso_requerido("stock.ajustar")

Esto permite controlar las operaciones disponibles para cada rol.

---

## Aislamiento multicomercio

Todas las consultas sobre productos incluyen el comercio autenticado.

Conceptualmente:

id_producto = producto solicitado
AND
id_comercio = comercio autenticado

El frontend no decide sobre qué comercio operar.

El comercio se determina utilizando la información del usuario autenticado.

Esto evita que un usuario pueda acceder o modificar directamente el stock perteneciente a otro comercio.

---

## Historial de movimientos

Cada ajuste manual genera automáticamente un registro en:

historial_movimiento

Se almacena:

- Producto.
- Usuario responsable.
- Tipo de movimiento.
- Cantidad.
- Stock anterior.
- Stock nuevo.
- Fecha del movimiento.
- Observaciones.

Para aumentos manuales se registra:

AJUSTE_ENTRADA

Para disminuciones manuales:

AJUSTE_SALIDA

Esto permite mantener trazabilidad sobre las modificaciones realizadas en el inventario.

---

## Pruebas realizadas

### Consulta general

Se realizó:

GET /stock

Resultado:

200 OK

El sistema devolvió únicamente productos correspondientes al comercio autenticado.

---

### Búsqueda

Se realizó:

GET /stock?buscar=Coca

Resultado:

200 OK

Se obtuvo correctamente:

Coca-Cola 500ml

---

### Alertas

Se realizó:

GET /stock/alertas

El sistema detectó correctamente:

Coca-Cola 500ml

Stock actual: 0
Stock mínimo: 5

Debido a que:

0 <= 5

---

### Control de permisos

Se utilizó un empleado con rol CAJERO.

Inicialmente poseía:

stock.ver

pero no:

stock.ajustar

El empleado pudo realizar:

GET /stock

Resultado:

200 OK

Al intentar realizar un ajuste:

PATCH /stock/2/ajustar

el servidor respondió:

403 Forbidden

con:

{
    "error": "No tiene permisos para realizar esta operación"
}

Esto confirmó que el control de permisos funciona correctamente.

---

### Asignación dinámica del permiso

Se agregó al rol CAJERO:

stock.ajustar

Luego el mismo empleado pudo realizar correctamente ajustes manuales sin necesidad de modificar el código del módulo.

---

### Ajuste de entrada

Producto utilizado:

Sprite 500ml

Stock inicial:

28

Se realizó un aumento de:

5 unidades

Resultado:

Stock anterior: 28
Stock nuevo: 33
Tipo de movimiento: AJUSTE_ENTRADA

---

### Verificación del historial

El movimiento quedó registrado correctamente en `historial_movimiento`.

Datos verificados:

id_producto: 2
id_usuario: 2
tipo_movimiento: AJUSTE_ENTRADA
cantidad: 5
stock_anterior: 28
stock_nuevo: 33
observaciones: Ajuste manual de stock

Esto confirmó que `id_usuario` fue obtenido automáticamente desde el usuario autenticado mediante JWT.

---

### Ajuste de salida

Finalmente se realizó una disminución de 5 unidades.

Resultado:

Stock anterior: 33
Stock nuevo: 28
Tipo de movimiento: AJUSTE_SALIDA

De esta manera el producto quedó nuevamente con su stock original después de finalizar las pruebas.

---

## Arquitectura utilizada

El módulo mantiene la arquitectura del proyecto:

Route
↓
Controller
↓
Service
↓
Model
↓
Supabase / PostgreSQL

### Route

Define los endpoints y aplica autenticación y permisos.

### Controller

Recibe las solicitudes HTTP y utiliza la información del usuario autenticado.

### Service

Contiene las reglas de negocio y validaciones relacionadas con stock.

### Model

Realiza las consultas y modificaciones en Supabase aplicando el aislamiento por comercio.

---

## Archivos modificados

Backend/app/models/stock_model.py

Backend/app/services/stock_service.py

Backend/app/controllers/stock_controller.py

Backend/app/routes/stock_routes.py

---

## Resultado final

El módulo de Stock quedó integrado a la arquitectura segura y multicomercio del sistema.

Actualmente permite:

- Consultar stock por comercio.
- Buscar productos.
- Detectar stock mínimo.
- Realizar ajustes manuales.
- Controlar operaciones mediante permisos.
- Identificar al usuario mediante JWT.
- Evitar que el frontend controle el comercio o usuario de una operación.
- Registrar movimientos para mantener trazabilidad del inventario.

Con esta entrega, el módulo de Stock queda preparado para integrarse posteriormente con el frontend React del Sistema de Gestión Integral de Comercio.
