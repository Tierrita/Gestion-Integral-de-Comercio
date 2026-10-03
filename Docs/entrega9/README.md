ENTREGA 9 – MÓDULO DE VENTAS

Objetivo de la entrega

En esta entrega se desarrolló el Módulo de Ventas del sistema Gestión Integral de Comercio.

El objetivo principal fue implementar la lógica necesaria para registrar y consultar ventas, controlar automáticamente el stock de los productos vendidos y permitir la anulación de una venta.

El módulo fue desarrollado respetando la arquitectura utilizada en el backend:

Route → Controller → Service → Model → Supabase

De esta manera, cada capa mantiene una responsabilidad específica y la lógica de negocio permanece separada del acceso a los datos.


1. ESTRUCTURA DEL MÓDULO DE VENTAS

Para desarrollar el módulo se utilizaron los siguientes archivos:

app/
│
├── models/
│   └── venta_model.py
│
├── services/
│   └── venta_service.py
│
├── controllers/
│   └── venta_controller.py
│
└── routes/
    └── venta_routes.py

Cada archivo cumple una función determinada:

- venta_routes.py: define los endpoints disponibles.
- venta_controller.py: recibe las solicitudes HTTP y genera las respuestas JSON.
- venta_service.py: contiene la lógica de negocio de las ventas.
- venta_model.py: realiza las operaciones necesarias sobre Supabase.


2. REGISTRO DE UNA VENTA

Se implementó el endpoint:

POST /ventas

Este endpoint permite registrar una nueva venta con uno o varios productos.

El sistema recibe información como:

{
    "id_usuario": 1,
    "metodo_pago": "EFECTIVO",
    "observaciones": "Primera prueba módulo ventas",
    "productos": [
        {
            "id_producto": 2,
            "cantidad": 3,
            "precio_unitario": 1400
        }
    ]
}

Antes de registrar la venta, el sistema realiza diferentes validaciones:

- Verifica que exista un usuario asociado.
- Verifica que se indique el método de pago.
- Verifica que exista al menos un producto.
- Valida que la cantidad sea mayor a cero.
- Valida que el precio unitario sea válido.
- Comprueba que el producto exista.
- Comprueba que exista stock suficiente para realizar la venta.

Luego se calcula automáticamente:

subtotal = cantidad × precio_unitario

Posteriormente se calcula el total general de la venta mediante la suma de todos los subtotales.


3. ACTUALIZACIÓN AUTOMÁTICA DEL STOCK

Una vez registrada correctamente la venta, el sistema descuenta automáticamente las unidades vendidas del stock.

En la prueba realizada se vendieron:

Producto: Sprite
Cantidad: 3 unidades

El stock antes de la venta era:

25 unidades

Luego de registrar la venta:

25 - 3 = 22 unidades

Resultado:

Stock anterior: 25
Stock nuevo: 22

Esto permite mantener sincronizado el inventario con las operaciones comerciales realizadas en el sistema.


4. REGISTRO EN EL HISTORIAL DE MOVIMIENTOS

Además de modificar el stock, cada venta genera automáticamente un registro en la tabla:

historial_movimiento

El movimiento generado durante la prueba fue:

Tipo de movimiento: VENTA
Producto: 2
Cantidad: 3
Stock anterior: 25
Stock nuevo: 22
Observación: Venta #2

De esta manera, el sistema mantiene trazabilidad sobre los cambios realizados en el inventario.


5. CONSULTA GENERAL DE VENTAS

Se implementó el endpoint:

GET /ventas

Este endpoint permite obtener todas las ventas registradas en el sistema.

La información recuperada incluye:

- ID de venta.
- Fecha.
- Usuario.
- Total.
- Método de pago.
- Estado.
- Observaciones.

Esto permitirá posteriormente mostrar desde el frontend un historial general de ventas.


6. CONSULTA INDIVIDUAL DE UNA VENTA

También se implementó:

GET /ventas/<id_venta>

Este endpoint permite consultar una venta específica junto con todos sus productos asociados.

Ejemplo:

GET /ventas/2

El sistema devuelve la información general de la venta y los detalles de los productos asociados.

Ejemplo de respuesta:

{
    "venta": {
        "id_venta": 2,
        "id_usuario": 1,
        "total": 4200.0,
        "metodo_pago": "EFECTIVO",
        "estado": "COMPLETADA"
    },
    "detalles": [
        {
            "id_producto": 2,
            "cantidad": 3,
            "precio_unitario": 1400.0,
            "subtotal": 4200.0
        }
    ]
}


7. ANULACIÓN DE UNA VENTA

Se implementó el endpoint:

PATCH /ventas/<id_venta>/anular

Su función es permitir la anulación de una venta sin eliminarla de la base de datos.

Al anular una venta, el sistema:

1. Busca la venta.
2. Verifica que exista.
3. Comprueba que no se encuentre previamente anulada.
4. Obtiene los productos asociados.
5. Devuelve las cantidades vendidas al stock.
6. Registra los movimientos correspondientes en el historial.
7. Cambia el estado de la venta a ANULADA.

Esto permite conservar el historial de la operación original.


8. DEVOLUCIÓN AUTOMÁTICA DEL STOCK

Para comprobar la anulación se utilizó la Venta #2.

La venta había descontado previamente 3 unidades:

25 → 22

Al realizar:

PATCH /ventas/2/anular

el sistema devolvió automáticamente las unidades:

22 + 3 = 25

Resultado:

Stock anterior: 22
Cantidad devuelta: 3
Stock nuevo: 25

Además, el estado de la venta cambió:

COMPLETADA → ANULADA


9. HISTORIAL DE ANULACIÓN

La anulación generó automáticamente un nuevo movimiento en historial_movimiento.

El registro generado fue:

Tipo de movimiento: ANULACION_VENTA
Producto: 2
Cantidad: 3
Stock anterior: 22
Stock nuevo: 25
Observaciones: Anulación Venta #2

De esta forma quedan registrados tanto el movimiento original como su posterior anulación:

VENTA
25 → 22

ANULACION_VENTA
22 → 25

Esto permite mantener una trazabilidad completa de las operaciones que modifican el inventario.


10. PROTECCIÓN CONTRA DOBLE ANULACIÓN

Se agregó una validación para impedir que una venta pueda ser anulada más de una vez.

Luego de anular la Venta #2 se volvió a ejecutar:

PATCH /ventas/2/anular

El sistema respondió:

{
    "error": "La venta ya se encuentra anulada"
}

Esta validación evita devolver nuevamente los productos al inventario.

Sin esta protección podría producirse un error como:

22 → 25 → 28

Con la validación implementada, el stock permanece correctamente en 25 unidades.


11. ENDPOINTS IMPLEMENTADOS

El módulo de ventas quedó compuesto por los siguientes endpoints:

POST /ventas
→ Registrar una nueva venta.

GET /ventas
→ Consultar todas las ventas.

GET /ventas/<id_venta>
→ Consultar una venta específica junto con sus detalles.

PATCH /ventas/<id_venta>/anular
→ Anular una venta y devolver los productos al stock.


12. PRUEBAS REALIZADAS

PRUEBA 1 – REGISTRAR VENTA

POST http://127.0.0.1:5001/ventas

Body:

{
    "id_usuario": 1,
    "metodo_pago": "EFECTIVO",
    "observaciones": "Primera prueba módulo ventas",
    "productos": [
        {
            "id_producto": 2,
            "cantidad": 3,
            "precio_unitario": 1400
        }
    ]
}

Resultado:

Venta #2 creada correctamente.
Total: $4200.
Stock: 25 → 22.
Movimiento registrado: VENTA.


PRUEBA 2 – CONSULTAR TODAS LAS VENTAS

GET http://127.0.0.1:5001/ventas

Resultado:

Listado general de ventas recuperado correctamente.


PRUEBA 3 – CONSULTAR VENTA INDIVIDUAL

GET http://127.0.0.1:5001/ventas/2

Resultado:

Venta #2 recuperada correctamente junto con sus detalles.


PRUEBA 4 – ANULAR VENTA

PATCH http://127.0.0.1:5001/ventas/2/anular

Resultado:

Estado: COMPLETADA → ANULADA.
Stock: 22 → 25.
Movimiento registrado: ANULACION_VENTA.


PRUEBA 5 – INTENTO DE DOBLE ANULACIÓN

PATCH http://127.0.0.1:5001/ventas/2/anular

Resultado:

{
    "error": "La venta ya se encuentra anulada"
}

El stock permaneció correctamente en 25 unidades.


13. RESULTADO FINAL

Con esta entrega quedó implementado el Módulo de Ventas del sistema Gestión Integral de Comercio.

El backend ahora permite registrar ventas, consultar operaciones generales e individuales, validar la disponibilidad de productos, descontar automáticamente el stock, mantener un historial de movimientos y anular ventas devolviendo correctamente las unidades al inventario.

El flujo principal implementado puede representarse de la siguiente manera:

VENTA
  ↓
Validar productos
  ↓
Validar stock
  ↓
Calcular total
  ↓
Registrar venta
  ↓
Registrar detalle
  ↓
Descontar stock
  ↓
Registrar movimiento VENTA
  ↓
Venta COMPLETADA


ANULACIÓN
  ↓
Buscar venta
  ↓
Validar estado
  ↓
Obtener detalles
  ↓
Devolver stock
  ↓
Registrar movimiento ANULACION_VENTA
  ↓
Venta ANULADA


De esta manera, el Módulo de Ventas queda integrado con la lógica de stock y el historial de movimientos, manteniendo consistencia y trazabilidad sobre las operaciones realizadas en el sistema.