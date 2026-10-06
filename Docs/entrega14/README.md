# ENTREGA 14 – PAGOS Y CUENTA CORRIENTE DE PROVEEDORES

## 1. Objetivo

En esta entrega se desarrolló la gestión financiera asociada a los proveedores del sistema **Gestión Integral de Comercio**.

El objetivo principal fue permitir registrar y controlar los pagos realizados a proveedores y calcular automáticamente la situación de cuenta corriente de cada uno.

Se estableció como regla principal:

COMPRA ≠ PAGO

Una compra representa mercadería adquirida y aumenta la deuda con el proveedor, mientras que un pago representa una cancelación total o parcial de dicha deuda.

---

## 2. Arquitectura utilizada

Se mantuvo la arquitectura modular utilizada en el resto del backend:

Route → Controller → Service → Model → Supabase

Se trabajó principalmente con los siguientes archivos:

app/
├── models/
│   ├── compra_model.py
│   ├── proveedor_model.py
│   └── pago_proveedor_model.py
├── services/
│   └── pago_proveedor_service.py
├── controllers/
│   └── pago_proveedor_controller.py
└── routes/
    └── pago_proveedor_routes.py

---

## 3. Tabla pagos_proveedor

Se incorporó una tabla específica para almacenar los pagos realizados a los proveedores.

La información principal registrada incluye:

- id_pago
- id_proveedor
- id_usuario
- monto
- fecha_pago
- estado
- observaciones
- id_usuario_anulacion
- fecha_anulacion
- motivo_anulacion

De esta manera, los pagos poseen su propio historial y no modifican directamente las compras originales.

---

## 4. Estados de un pago

Se definieron dos estados principales:

- COMPLETADO
- ANULADO

Un pago COMPLETADO participa en el cálculo de la cuenta corriente.

Un pago ANULADO permanece almacenado como información histórica, pero deja de afectar el saldo del proveedor.

---

## 5. Registro de pagos

Se implementó el registro de pagos mediante:

POST /pagos-proveedor

Ejemplo de solicitud:

{
    "id_proveedor": 1,
    "id_usuario": 1,
    "monto": 30000,
    "observaciones": "Pago parcial de prueba al proveedor"
}

El sistema valida:

- Proveedor obligatorio.
- Proveedor existente.
- Usuario obligatorio.
- Monto obligatorio.
- Monto numérico.
- Monto mayor a cero.
- Observaciones opcionales.

---

## 6. Pagos parciales

El sistema permite realizar pagos parciales a los proveedores.

Ejemplo:

Deuda proveedor: $100.000
Pago realizado:   $30.000
Deuda restante:   $70.000

No es necesario cancelar una compra completa para registrar un pago.

---

## 7. Pagos globales al proveedor

Se decidió que los pagos no se asignen directamente a una compra determinada.

Un proveedor puede tener múltiples compras y múltiples pagos independientes.

Los pagos reducen la deuda global mantenida con el proveedor.

Esto permite manejar una verdadera cuenta corriente.

---

## 8. Consulta general de pagos

Se implementó:

GET /pagos-proveedor

Permite consultar todos los pagos registrados a proveedores.

---

## 9. Consulta individual de pago

Se implementó:

GET /pagos-proveedor/<id_pago>

Permite recuperar un pago determinado mediante su identificador.

---

## 10. Historial de pagos por proveedor

Se implementó:

GET /proveedores/<id_proveedor>/pagos

Permite visualizar todos los pagos relacionados con un proveedor específico.

---

## 11. Anulación de pagos

Los pagos no se eliminan físicamente.

Se implementó:

PATCH /pagos-proveedor/<id_pago>/anular

Al anular un pago se registra:

- Estado = ANULADO.
- Usuario que realizó la anulación.
- Fecha de anulación.
- Motivo de la anulación.

Esto permite mantener trazabilidad sobre las operaciones financieras realizadas.

---

## 12. Motivo de anulación

Para mantener trazabilidad, la anulación requiere una justificación.

Se estableció como regla que el motivo de anulación debe contener al menos 5 caracteres.

Esto evita anulaciones sin explicación.

---

## 13. Protección contra doble anulación

El Service verifica el estado actual del pago.

Si el pago ya se encuentra en estado ANULADO, el sistema rechaza una nueva solicitud de anulación.

---

## 14. Registro automático de fecha de anulación

Se incorporó lógica en PostgreSQL mediante un trigger para registrar automáticamente la fecha en la que un pago pasa al estado ANULADO.

De esta manera, la fecha de anulación no depende de que sea enviada manualmente desde el cliente o frontend.

---

# CUENTA CORRIENTE DEL PROVEEDOR

## 15. Concepto

La cuenta corriente se construyó utilizando las operaciones reales realizadas con cada proveedor.

La fórmula implementada es:

SALDO = COMPRAS VÁLIDAS - PAGOS COMPLETADOS

No se creó una columna saldo dentro de la tabla de proveedores.

El saldo se calcula dinámicamente a partir de las operaciones registradas.

---

## 16. Compras consideradas

Para calcular la deuda se recuperan las compras correspondientes al proveedor.

Las compras con estado ANULADA son excluidas.

Por lo tanto:

COMPLETADA → suma deuda.

ANULADA → no suma deuda.

---

## 17. Pagos considerados

Solamente participan del cálculo los pagos cuyo estado sea COMPLETADO.

Los pagos ANULADOS permanecen en el historial, pero no reducen la deuda del proveedor.

---

## 18. Interpretación del saldo

Se definieron tres situaciones posibles:

Saldo > 0 → DEUDA

Saldo = 0 → AL_DIA

Saldo < 0 → SALDO_A_FAVOR

Esto permite representar tanto una deuda pendiente como un posible crédito disponible con el proveedor.

---

## 19. Saldo a favor

El sistema permite que los pagos realizados superen la deuda existente.

Ejemplo:

Compras: $48.400
Pagos:   $50.000
Saldo:   -$1.600

Resultado:

SALDO_A_FAVOR

Ese crédito queda representado automáticamente por el cálculo de la cuenta corriente y puede ser utilizado frente a futuras compras.

---

## 20. Consulta de saldo del proveedor

Se implementó:

GET /proveedores/<id_proveedor>/saldo

Ejemplo de respuesta obtenida:

{
    "proveedor": {
        "id_proveedor": 1,
        "nombre_proveedor": "Distribuidora Central"
    },
    "saldo": -1600.0,
    "situacion": "SALDO_A_FAVOR",
    "total_compras": 48400.0,
    "total_pagos": 50000.0
}

---

# PRUEBAS DE INTEGRACIÓN

## 21. Primera situación probada

Para el proveedor:

ID: 1

Nombre: Distribuidora Central

El sistema tenía inicialmente:

Compras válidas: $48.400

Pagos completados: $50.000

El cálculo automático produjo:

$48.400 - $50.000 = -$1.600

Resultado:

SALDO_A_FAVOR

---

## 22. Prueba de absorción del saldo a favor

Para comprobar el comportamiento de la cuenta corriente se registró una nueva compra.

Datos:

Compra: #8

Proveedor: #1

Usuario: #1

Total: $10.000

Estado: COMPLETADA

Observación: "Compra prueba cuenta corriente proveedor"

Detalle utilizado:

Producto: #2

Cantidad: 10

Precio unitario: $1.000

Subtotal: $10.000

---

## 23. Impacto de la nueva compra

Antes de registrar la compra:

Compras: $48.400

Pagos: $50.000

Saldo: -$1.600

Situación: SALDO_A_FAVOR

Luego se registró una nueva compra por $10.000.

El sistema pasó automáticamente a:

Compras: $58.400

Pagos: $50.000

Saldo: $8.400

Situación: DEUDA

---

## 24. Resultado obtenido

La consulta:

GET /proveedores/1/saldo

devolvió correctamente:

{
    "proveedor": {
        "id_proveedor": 1,
        "nombre_proveedor": "Distribuidora Central"
    },
    "saldo": 8400.0,
    "situacion": "DEUDA",
    "total_compras": 58400.0,
    "total_pagos": 50000.0
}

El saldo a favor anterior de $1.600 fue absorbido automáticamente por la nueva compra de $10.000.

La deuda resultante fue de $8.400.

Esto permitió verificar que la cuenta corriente funciona de manera dinámica y no requiere modificar manualmente ningún saldo.

---

# INTEGRACIÓN CON STOCK

## 25. Compra y stock

La nueva compra también utilizó la lógica existente del módulo de Compras.

Al registrar una compra se realiza el siguiente flujo:

Compra
→ Detalle de compra
→ Aumento de stock
→ Registro en historial de movimientos de stock

Por lo tanto, una compra representa tanto la entrada física de mercadería como el aumento de la deuda comercial con el proveedor.

---

# MANEJO DE FECHAS

## 26. Normalización de fechas

Durante el desarrollo del módulo financiero se revisó el manejo de fechas de la base de datos.

Se detectó que diferentes columnas utilizaban:

timestamp without time zone

Se decidió migrarlas a:

timestamp with time zone

En PostgreSQL:

timestamptz

---

## 27. Estrategia de zona horaria

El sistema almacena los instantes utilizando UTC.

Ejemplo:

2026-10-05T11:49:31.418436+00:00

El sufijo +00:00 representa UTC.

La conversión a la zona horaria correspondiente al usuario será responsabilidad del frontend.

Para Argentina se podrá utilizar:

America/Argentina/Buenos_Aires

De esta manera no es necesario modificar manualmente las horas desde Flask y el sistema queda preparado para trabajar correctamente independientemente de la ubicación del servidor.

---

## 28. Tablas normalizadas

Se normalizaron las fechas correspondientes a las siguientes tablas:

- categorias
- clientes
- cobros
- compras
- cuentas
- historial_movimiento
- movimientos_financieros
- pagos_proveedor
- productos
- usuarios
- ventas

Las columnas correspondientes quedaron utilizando timestamp with time zone.

---

# REGLAS DE NEGOCIO DEFINIDAS

## 29. Reglas principales

Durante esta entrega quedaron establecidas las siguientes reglas:

- COMPRA ≠ PAGO.
- Una compra aumenta la deuda con el proveedor.
- Un pago disminuye la deuda.
- Los pagos pueden ser parciales.
- Un pago no pertenece obligatoriamente a una compra específica.
- Una compra anulada no genera deuda.
- Un pago anulado no reduce deuda.
- Los pagos no se eliminan físicamente.
- Las anulaciones quedan auditadas.
- Puede existir saldo a favor.
- Una nueva compra consume automáticamente el saldo a favor existente.
- El saldo del proveedor no se almacena manualmente.
- El saldo se calcula a partir de las operaciones reales.
- El historial financiero se conserva para mantener trazabilidad.

---

# ENDPOINTS IMPLEMENTADOS

## 30. Rutas principales

POST /pagos-proveedor

GET /pagos-proveedor

GET /pagos-proveedor/<id_pago>

GET /proveedores/<id_proveedor>/pagos

PATCH /pagos-proveedor/<id_pago>/anular

GET /proveedores/<id_proveedor>/saldo

Estas rutas complementan las funcionalidades existentes del módulo de Compras:

POST /compras

GET /compras

GET /compras/<id_compra>

PATCH /compras/<id_compra>/anular

---

# RESULTADO FINAL

## 31. Flujo financiero conseguido

El módulo permite actualmente representar el siguiente flujo:

PROVEEDOR
    ↓
COMPRAS
    ↓
Generan deuda
    ↓
CUENTA CORRIENTE
    ↑
PAGOS
    ↑
Reducen deuda

La cuenta corriente se determina mediante:

COMPRAS VÁLIDAS - PAGOS COMPLETADOS

El resultado puede representar:

- DEUDA
- AL_DIA
- SALDO_A_FAVOR

---

## 32. Estado de la entrega

ENTREGA 14 – PAGOS Y CUENTA CORRIENTE DE PROVEEDORES: COMPLETADA ✅

Se logró integrar correctamente:

Proveedores
→ Compras
→ Stock
→ Pagos
→ Anulaciones
→ Cuenta corriente
→ Saldo dinámico

La prueba final confirmó que un saldo a favor de $1.600 fue utilizado automáticamente frente a una nueva compra de $10.000, dejando una deuda final de $8.400.

Con esto, la funcionalidad de pagos y cuenta corriente de proveedores queda cerrada de punta a punta y preparada para su futura integración con el frontend desarrollado en React + Vite.