# Entrega 8 – Módulo de Compras

## Objetivo de la entrega

En esta entrega se desarrolló y completó el **Módulo de Compras** del sistema de Gestión Integral de Comercio.

El objetivo principal fue permitir registrar compras de productos a proveedores, almacenar sus detalles, actualizar automáticamente el stock, generar un historial de movimientos y permitir posteriormente consultar o anular las compras realizadas.

Se mantuvo la arquitectura modular utilizada en el backend:

**Route → Controller → Service → Model → Supabase**

---

## 1. Registro de compras

Se implementó el endpoint:

**POST `/compras`**

Este endpoint permite registrar una nueva compra indicando:

- Proveedor.
- Usuario responsable.
- Productos incluidos.
- Cantidad de cada producto.
- Precio unitario.
- Observaciones.

El sistema calcula automáticamente el subtotal correspondiente a cada producto y el total general de la compra.

### Ejemplo de solicitud

```json
{
  "id_proveedor": 1,
  "id_usuario": 1,
  "observaciones": "Prueba compra desde Postman",
  "productos": [
    {
      "id_producto": 2,
      "cantidad": 5,
      "precio_unitario": 850
    }
  ]
}
```

Para este ejemplo:

**5 × $850 = $4.250**

Por lo tanto, el sistema registra automáticamente un `total_compra` de **$4.250**.

---

## 2. Registro del detalle de compra

Una vez creada la compra principal, cada producto incluido se registra en la tabla:

`detalle_compra`

Para cada detalle se almacenan:

- ID de compra.
- ID de producto.
- Cantidad.
- Precio unitario.
- Subtotal.

Esto permite que una misma compra pueda contener uno o varios productos.

---

## 3. Actualización automática del stock

Luego de registrar cada detalle, el sistema consulta el stock actual del producto y suma automáticamente la cantidad comprada.

La lógica aplicada es:

**stock_nuevo = stock_anterior + cantidad_comprada**

Durante las pruebas se utilizó el producto:

**Sprite 500 ml – ID 2**

El producto tenía inicialmente:

**Stock anterior: 25**

Se registró una compra de:

**Cantidad: +5**

El sistema actualizó automáticamente:

**Stock nuevo: 30**

De esta manera, el usuario no necesita modificar manualmente el inventario luego de registrar una compra.

---

## 4. Registro en historial de movimientos

Cada modificación automática del stock producida por una compra genera además un registro en:

`historial_movimiento`

Se almacena:

- Producto.
- Usuario.
- Tipo de movimiento.
- Cantidad.
- Stock anterior.
- Stock nuevo.
- Fecha.
- Observaciones.

Ejemplo generado durante las pruebas:

```text
Tipo: COMPRA
Producto: 2
Usuario: 1
Cantidad: 5
Stock anterior: 25
Stock nuevo: 30
Observaciones: Compra #7
```

Esto permite mantener trazabilidad sobre los cambios realizados en el inventario.

---

## 5. Consulta general de compras

Se implementó:

**GET `/compras`**

Este endpoint devuelve todas las compras registradas.

Las compras son ordenadas desde la más reciente hacia la más antigua mediante su `id_compra`.

Durante las pruebas se recuperaron correctamente las compras existentes desde la compra #7 hasta la compra #1.

Esto permitirá posteriormente mostrar desde el frontend un historial general de compras.

---

## 6. Consulta individual de compra

Se implementó:

**GET `/compras/<id_compra>`**

A diferencia de la consulta general, este endpoint devuelve tanto los datos principales de la compra como todos sus detalles.

Ejemplo:

**GET `/compras/7`**

Respuesta obtenida:

```json
{
  "compra": {
    "estado": "COMPLETADA",
    "id_compra": 7,
    "id_proveedor": 1,
    "id_usuario": 1,
    "observaciones": "Prueba compra desde el gym",
    "total_compra": 4250.0
  },
  "detalles": [
    {
      "cantidad": 5,
      "id_compra": 7,
      "id_detalle_compra": 7,
      "id_producto": 2,
      "precio_unitario": 850.0,
      "subtotal": 4250.0
    }
  ]
}
```

También se incorporó validación para detectar compras inexistentes.

---

## 7. Anulación de compras

Se implementó:

**PATCH `/compras/<id_compra>/anular`**

La anulación no elimina físicamente la compra ni sus detalles.

En cambio, el sistema mantiene los registros existentes y modifica el estado:

**COMPLETADA → ANULADA**

Esto permite conservar el historial de operaciones realizadas.

---

## 8. Reversión automática del stock

Al anular una compra, el sistema obtiene todos los productos asociados y revierte automáticamente las cantidades que habían ingresado al inventario.

La lógica utilizada es:

**stock_nuevo = stock_actual - cantidad_comprada**

Durante la prueba con la compra #7:

```text
Stock antes de la compra: 25

Compra #7
+5 unidades
Stock: 30

Anulación Compra #7
-5 unidades
Stock final: 25
```

De esta manera, el inventario vuelve correctamente a la situación anterior a la compra.

---

## 9. Validaciones para la anulación

Antes de modificar el inventario se realizan diferentes controles:

- La compra debe existir.
- La compra no puede encontrarse previamente anulada.
- Debe contener productos asociados.
- Los productos deben existir.
- Debe existir stock suficiente para realizar la reversión.
- Se evita generar stock negativo.

Primero se validan todos los productos involucrados y posteriormente se realizan las modificaciones.

Esto reduce el riesgo de generar inconsistencias parciales en el inventario.

---

## 10. Historial de la anulación

La reversión del stock también genera un nuevo registro en `historial_movimiento`.

El movimiento permite identificar que la disminución del stock fue causada por la anulación de una compra.

Ejemplo:

```text
Tipo: ANULACION_COMPRA
Producto: 2
Cantidad: 5
Stock anterior: 30
Stock nuevo: 25
Observaciones: Anulación Compra #7
```

Por lo tanto, el sistema conserva tanto el movimiento original de entrada como su posterior reversión.

---

## Arquitectura implementada

El módulo mantiene la separación de responsabilidades definida para el backend.

### Routes

Define los endpoints HTTP:

```text
POST  /compras
GET   /compras
GET   /compras/<id_compra>
PATCH /compras/<id_compra>/anular
```

### Controller

Recibe las solicitudes HTTP, ejecuta los servicios correspondientes y construye las respuestas JSON con sus códigos HTTP.

### Service

Contiene la lógica de negocio:

- Validación de datos.
- Cálculo de subtotales.
- Cálculo del total.
- Registro de compras.
- Actualización del stock.
- Consulta de compras.
- Validación de anulaciones.
- Reversión del stock.
- Registro de movimientos.

### Model

Se comunica directamente con Supabase para:

- Insertar compras.
- Insertar detalles.
- Consultar compras.
- Consultar detalles.
- Consultar productos.
- Actualizar stock.
- Actualizar el estado de una compra.
- Registrar movimientos de stock.

---

## Pruebas realizadas con Postman

### Registrar compra

```text
POST http://127.0.0.1:5001/compras
```

Resultado:

**201 – Compra registrada correctamente**

### Consultar todas las compras

```text
GET http://127.0.0.1:5001/compras
```

Resultado:

**200 – Listado de compras**

### Consultar compra individual

```text
GET http://127.0.0.1:5001/compras/7
```

Resultado:

**200 – Compra y detalles recuperados correctamente**

### Anular compra

```text
PATCH http://127.0.0.1:5001/compras/7/anular
```

Resultado:

**200 – Compra anulada correctamente**

---

## Resultado final

El Módulo de Compras quedó integrado con el sistema de stock y con el historial de movimientos.

El flujo completo implementado es:

```text
REGISTRAR COMPRA
       ↓
Crear compra
       ↓
Crear detalles
       ↓
Calcular total
       ↓
Incrementar stock
       ↓
Registrar movimiento COMPRA
       ↓
Compra COMPLETADA


ANULAR COMPRA
       ↓
Validar compra
       ↓
Obtener detalles
       ↓
Validar productos y stock
       ↓
Revertir stock
       ↓
Registrar ANULACION_COMPRA
       ↓
Compra ANULADA
```

Con esta entrega, el sistema permite gestionar el ciclo principal de una compra manteniendo sincronizados los registros de compras, sus detalles, el inventario y el historial de movimientos.

## Estado de la funcionalidad

**Módulo Compras: COMPLETADO**

- Registro de compras: ✅
- Detalle de compras: ✅
- Cálculo automático de totales: ✅
- Incremento automático de stock: ✅
- Historial de movimientos: ✅
- Consulta general de compras: ✅
- Consulta individual: ✅
- Anulación de compras: ✅
- Reversión automática de stock: ✅
- Validaciones de negocio: ✅