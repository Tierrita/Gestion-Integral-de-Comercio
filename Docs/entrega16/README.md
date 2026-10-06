ENTREGA 16 – COSTOS HISTÓRICOS Y ACTUALIZACIÓN AUTOMÁTICA DE PRECIOS

OBJETIVO

Incorporar al sistema una gestión de costos que permita conservar el costo histórico de cada venta y actualizar automáticamente los precios de los productos cuando aumenta su costo de reposición.


FUNCIONALIDADES IMPLEMENTADAS

1. REGISTRO DEL COSTO HISTÓRICO EN VENTAS

Se agregó el campo costo_unitario a la tabla detalle_venta.

Al registrar una venta, el sistema obtiene automáticamente desde la tabla productos:

- precio_venta → se guarda como precio_unitario en detalle_venta.
- precio_costo → se guarda como costo_unitario en detalle_venta.

De esta manera, cada venta conserva el precio de venta y el costo correspondientes al momento exacto en que fue realizada.

Esto permitirá posteriormente calcular correctamente:

- Facturación.
- Costo de mercadería vendida.
- Ganancia bruta.
- Margen bruto.

Los cambios futuros en el costo o precio del producto no modifican las ventas históricas.


2. PRECIO DE VENTA CONTROLADO POR EL BACKEND

El precio de venta utilizado al registrar una venta se obtiene directamente desde la tabla productos.

De esta manera, el frontend o Postman no determinan el precio de venta del producto.

Esto mejora la integridad de los datos y evita que una venta pueda registrarse accidentalmente con un precio incorrecto enviado desde el cliente.


3. ACTUALIZACIÓN AUTOMÁTICA DEL COSTO

Al registrar una compra, el sistema compara el nuevo costo de compra con el precio de costo actual del producto.

Regla implementada:

Si nuevo costo > costo actual:
- Se actualiza el precio de costo.
- Se recalcula automáticamente el precio de venta.

Si nuevo costo <= costo actual:
- Se mantiene el precio de costo actual.
- Se mantiene el precio de venta actual.
- El stock aumenta normalmente.

De esta manera, una compra realizada a un precio inferior queda registrada históricamente con su costo real, pero no provoca una reducción automática del precio comercial del producto.


4. CONSERVACIÓN DEL PORCENTAJE DE RECARGO

Cuando aumenta el costo de un producto, el sistema conserva el mismo porcentaje de recargo o markup que tenía anteriormente.

Fórmula utilizada:

Markup = (Precio de venta - Precio de costo) / Precio de costo

Ejemplo:

Costo anterior: $500
Precio de venta anterior: $900

Markup:

(900 - 500) / 500 = 0,80

Markup = 80%

Si posteriormente el producto se compra a $600:

Nuevo precio de venta:

600 × (1 + 0,80) = $1.080

Resultado:

Costo anterior: $500
Nuevo costo: $600
Precio de venta anterior: $900
Nuevo precio de venta: $1.080
Markup conservado: 80%


5. COMPRA CON COSTO INFERIOR

También se verificó el comportamiento del sistema cuando una nueva compra posee un costo inferior al costo actual del producto.

Ejemplo:

Costo actual: $600
Precio de venta actual: $1.080
Nuevo costo de compra: $550

Resultado:

Costo del producto: $600
Precio de venta: $1.080
Costo registrado en detalle_compra: $550
Stock: aumentado correctamente
Precio actualizado: false

Esto permite conservar el costo de referencia más alto sin perder el costo histórico real de cada compra.


6. ACTUALIZACIÓN DE STOCK

Cada compra continúa aumentando automáticamente el stock disponible del producto.

Fórmula:

stock_nuevo = stock_anterior + cantidad_comprada

Además, cada ingreso de mercadería continúa registrándose en historial_movimiento con el tipo de movimiento:

COMPRA


7. ANULACIÓN DE COMPRAS

La funcionalidad de anulación continúa permitiendo:

- Revertir el stock incorporado por la compra.
- Registrar el movimiento ANULACION_COMPRA.
- Cambiar el estado de la compra a ANULADA.

La anulación no reduce automáticamente el precio de costo ni el precio de venta actual del producto.

De esta manera se mantiene la política definida para el costo de referencia.


ARCHIVOS MODIFICADOS

app/
├── models/
│   ├── venta_model.py
│   └── compra_model.py
│
└── services/
    ├── venta_service.py
    └── compra_service.py


MODIFICACIÓN EN BASE DE DATOS

Tabla: detalle_venta

Se incorporó:

costo_unitario

Este campo permite conservar el costo que tenía el producto al momento de realizar cada venta.


PRUEBAS REALIZADAS

PRUEBA 1 – VENTA CON COSTO HISTÓRICO

Producto: Alfajor de chocolate
Cantidad: 2
Costo unitario: $500
Precio de venta unitario: $900

Resultado:

Facturación: $1.800
Costo de mercadería vendida: $1.000
Ganancia bruta: $800
Margen bruto: 44,44%

El costo de $500 quedó almacenado en detalle_venta.


PRUEBA 2 – COMPRA CON AUMENTO DE COSTO

Producto: Alfajor de chocolate

Costo anterior: $500
Precio de venta anterior: $900
Nuevo costo de compra: $600

Resultado:

Nuevo costo: $600
Nuevo precio de venta: $1.080
Markup conservado: 80%
Stock actualizado correctamente.
Precio actualizado: true.


PRUEBA 3 – COMPRA CON COSTO INFERIOR

Costo actual: $600
Precio de venta actual: $1.080
Nuevo costo de compra: $550

Resultado:

Costo final: $600
Precio de venta final: $1.080
La compra quedó registrada a $550 por unidad.
El stock aumentó correctamente.
Precio actualizado: false.


RESULTADO DE LA ENTREGA

El sistema dispone ahora de una base consistente para el futuro módulo financiero.

Las ventas conservan su costo histórico, permitiendo calcular la rentabilidad real de las operaciones realizadas.

Las compras actualizan automáticamente el costo de referencia cuando existe un aumento y recalculan el precio de venta manteniendo el mismo porcentaje de recargo.

Cuando una compra se realiza a un costo inferior, el sistema conserva el costo y precio de venta actuales, pero registra correctamente el costo real de dicha compra.

Con esta implementación quedan preparados los datos necesarios para desarrollar el módulo de rentabilidad financiera.


PRÓXIMO PASO

Desarrollar la rama RENTABILIDAD del módulo FINANZAS.

Primera ruta propuesta:

GET /finanzas/rentabilidad

La consulta permitirá obtener inicialmente:

- Facturación.
- Costo de mercadería vendida.
- Ganancia bruta.
- Margen bruto.

Posteriormente se incorporarán filtros por:

- Día.
- Semana.
- Mes.
- Año.
- Período personalizado.