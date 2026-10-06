ENTREGA 13 – COBROS Y CUENTA CORRIENTE DE CLIENTES


1. OBJETIVO

El objetivo de esta entrega fue ampliar el módulo financiero del sistema incorporando la gestión de cobros de clientes y el cálculo automático de su cuenta corriente.

La implementación permite separar correctamente dos conceptos fundamentales:

VENTA ≠ COBRO

Una venta representa una operación comercial realizada al cliente, mientras que un cobro representa el ingreso efectivo de dinero.

Gracias a esta separación, el sistema permite manejar ventas pendientes de pago, pagos parciales, saldos a favor y anulaciones, manteniendo la trazabilidad de todas las operaciones.


2. ARQUITECTURA UTILIZADA

Se mantuvo la arquitectura general utilizada en el backend:

Route
↓
Controller
↓
Service
↓
Model
↓
Supabase / PostgreSQL

Para aquellas operaciones que modifican varias tablas simultáneamente, como registrar o anular un cobro, se utilizaron funciones RPC de PostgreSQL.

Esto permite ejecutar las operaciones de forma transaccional y evitar inconsistencias entre los cobros, las cuentas financieras y los movimientos registrados.


3. RELACIÓN ENTRE VENTAS Y CLIENTES

Se incorporó la relación entre una venta y el cliente que realizó la operación mediante:

ventas.id_cliente
↓
clientes.id_cliente

De esta manera, cada venta queda asociada a un cliente.

Para las ventas donde no se identifica a un cliente específico se utiliza:

CLIENTE GENERAL
id_cliente = 1

Los clientes registrados utilizan su identificador correspondiente.

Esta relación permite reconstruir posteriormente el historial comercial y financiero de cada cliente.


4. ADAPTACIÓN DEL MÓDULO DE VENTAS

El servicio de ventas fue modificado para recibir obligatoriamente el identificador del cliente.

Ejemplo:

{
    "id_cliente": 2
}

Al registrar una venta se almacenan los siguientes datos:

- id_usuario
- id_cliente
- total
- metodo_pago
- estado
- observaciones

Además, se mantiene el funcionamiento desarrollado anteriormente:

Registrar venta
↓
Registrar detalle de venta
↓
Descontar stock
↓
Registrar movimiento de stock

Esto permite que una venta quede relacionada simultáneamente con el cliente y con los productos vendidos.


5. REGISTRO DE COBROS

Se desarrolló la funcionalidad para registrar dinero recibido de un cliente.

Endpoint:

POST /cobros

Ejemplo de solicitud:

{
    "id_cliente": 2,
    "id_cuenta": 1,
    "id_usuario": 1,
    "monto": 20000,
    "observaciones": "Pago parcial del cliente"
}

Cada cobro queda asociado a:

- Cliente
- Cuenta financiera
- Usuario
- Monto
- Fecha
- Estado
- Observaciones


6. REGISTRO TRANSACCIONAL DEL COBRO

El registro de un cobro se implementó mediante una función RPC de PostgreSQL denominada:

registrar_cobro()

La operación realiza de forma conjunta:

Registrar COBRO
↓
Aumentar saldo de CUENTA
↓
Registrar MOVIMIENTO FINANCIERO

Esto evita que pueda quedar registrado un cobro sin actualizar la cuenta financiera correspondiente.

La operación se ejecuta como una única transacción.


7. MOVIMIENTOS FINANCIEROS GENERADOS

Cada cobro genera automáticamente un movimiento financiero.

El movimiento utiliza:

tipo_movimiento = COBRO
tipo_origen = COBRO
id_origen = id_cobro

Cada movimiento permite registrar:

- Cuenta
- Usuario
- Monto
- Saldo anterior
- Saldo nuevo
- Tipo de movimiento
- Tipo de origen
- ID de origen
- Fecha
- Observaciones

De esta manera es posible reconstruir cómo se modificó el dinero disponible en cada cuenta.


8. CONSULTA GENERAL DE COBROS

Se incorporó el endpoint:

GET /cobros

Permite obtener todos los cobros registrados en el sistema.

Los cobros anulados permanecen almacenados para conservar el historial y la trazabilidad financiera.


9. CONSULTA INDIVIDUAL DE COBRO

Se incorporó el endpoint:

GET /cobros/<id_cobro>

Permite consultar un cobro específico mediante su identificador.

Si el cobro solicitado no existe, el sistema devuelve el error correspondiente.


10. HISTORIAL DE COBROS POR CLIENTE

Se incorporó:

GET /clientes/<id_cliente>/cobros

Este endpoint permite obtener todos los cobros relacionados con un cliente determinado.

El historial conserva tanto los cobros completados como los anulados, ya que las operaciones anuladas no se eliminan físicamente de la base de datos.


11. ANULACIÓN DE COBROS

Los cobros confirmados no se eliminan físicamente.

Se desarrolló:

PATCH /cobros/<id_cobro>/anular

Ejemplo:

{
    "id_usuario": 1,
    "motivo_anulacion": "Cobro registrado por error"
}

Al realizar la operación, el estado del cobro cambia:

COMPLETADO
↓
ANULADO

Además, se registran:

- Usuario que realizó la anulación
- Fecha de anulación
- Motivo de anulación

El motivo de anulación debe contener como mínimo 5 caracteres.


12. REVERSIÓN FINANCIERA DEL COBRO

La anulación de un cobro no solamente modifica su estado.

También debe revertir el efecto financiero que produjo originalmente.

El proceso es:

ANULAR COBRO
↓
Restar dinero de la cuenta
↓
Registrar movimiento ANULACION_COBRO

Ejemplo:

Cuenta antes de anular: $120.000

Cobro anulado: $20.000

Cuenta después de anular: $100.000

De esta manera, el saldo financiero vuelve al valor correspondiente.


13. PREVENCIÓN DE DOBLE ANULACIÓN

Se incorporó una regla para impedir que un mismo cobro pueda ser anulado más de una vez.

Si se intenta repetir la operación, el sistema devuelve:

"El cobro ya se encuentra anulado"

Esto evita descontar dos veces el mismo importe de una cuenta financiera.


14. CONTROL DE FONDOS EN ANULACIONES

Antes de revertir un cobro, el sistema verifica que la cuenta financiera disponga del dinero necesario.

Si no existen fondos suficientes, se devuelve:

"Fondos insuficientes para revertir el cobro"

En ese caso, la operación se cancela sin modificar el cobro, la cuenta ni los movimientos financieros.


15. PRUEBA DE TRAZABILIDAD FINANCIERA

Se realizó una prueba registrando un cobro por:

$20.000

Saldo inicial de la cuenta:

$100.000

Luego de registrar el cobro:

$100.000 → $120.000

Se generó un movimiento:

Tipo: COBRO
Monto: $20.000
Saldo anterior: $100.000
Saldo nuevo: $120.000

Posteriormente se anuló el mismo cobro.

Resultado:

$120.000 → $100.000

Se generó un nuevo movimiento:

Tipo: ANULACION_COBRO
Monto: $20.000
Saldo anterior: $120.000
Saldo nuevo: $100.000

La prueba confirmó que tanto el ingreso como su posterior reversión quedan registrados en el historial financiero.


16. DISEÑO DE LA CUENTA CORRIENTE DE CLIENTES

Se decidió no almacenar directamente la deuda o saldo del cliente dentro de la tabla clientes.

En su lugar, el saldo se calcula dinámicamente utilizando las operaciones reales registradas en el sistema.

La fórmula utilizada es:

TOTAL DE VENTAS VÁLIDAS
-
TOTAL DE COBROS COMPLETADOS
=
SALDO DEL CLIENTE

Este diseño evita mantener un campo de saldo que pueda quedar desactualizado respecto del historial de operaciones.


17. INTERPRETACIÓN DEL SALDO

Se definieron tres posibles situaciones financieras para un cliente.

Si:

saldo > 0

Situación:

DEUDA

Si:

saldo = 0

Situación:

AL_DIA

Si:

saldo < 0

Situación:

SALDO_A_FAVOR

Esto permite que el sistema también contemple pagos anticipados realizados por los clientes.


18. CONSULTA DEL SALDO DEL CLIENTE

Se implementó:

GET /clientes/<id_cliente>/saldo

La respuesta incluye:

- Datos del cliente
- Total de ventas válidas
- Total de cobros completados
- Saldo actual
- Situación financiera

Ejemplo obtenido durante las pruebas:

{
    "cliente": {
        "estado": true,
        "id_cliente": 2,
        "nombre_completo": "JUAN PEREZ"
    },
    "saldo": 15000,
    "situacion": "DEUDA",
    "total_cobros": 25000,
    "total_ventas": 40000
}


19. TRATAMIENTO DE OPERACIONES ANULADAS

Las operaciones anuladas permanecen almacenadas en la base de datos para mantener la trazabilidad, pero no participan del cálculo de la cuenta corriente.

Para las ventas:

VENTA COMPLETADA → cuenta para el saldo
VENTA ANULADA → no cuenta para el saldo

Para los cobros:

COBRO COMPLETADO → cuenta para el saldo
COBRO ANULADO → no cuenta para el saldo

De esta manera se consigue mantener:

HISTORIAL COMPLETO
+
SALDO FINANCIERO CORRECTO


20. PRUEBA DE SALDO A FAVOR

Se utilizó como cliente de prueba:

JUAN PEREZ
id_cliente = 2

Inicialmente el cliente poseía:

Ventas válidas: $0
Cobros válidos: $25.000

El sistema calculó:

Saldo: -$25.000

Situación:

SALDO_A_FAVOR

Esta prueba permitió comprobar que el sistema admite pagos anticipados o dinero entregado por un cliente antes de generar una deuda.


21. PRUEBA DE GENERACIÓN DE DEUDA

Posteriormente se registró una venta de prueba por:

$40.000

La venta fue asociada a:

id_cliente = 2
JUAN PEREZ

Luego de registrar la operación, el sistema calculó automáticamente:

Ventas válidas: $40.000
Cobros válidos: $25.000

Saldo:

$40.000 - $25.000 = $15.000

Situación:

DEUDA

No fue necesario modificar manualmente ningún campo de saldo.


22. INTEGRACIÓN CON STOCK

Para la venta de prueba se utilizó:

Producto: Sprite 500ml
id_producto: 2

Stock inicial:

25 unidades

Cantidad vendida:

5 unidades

Luego de registrar la venta:

25 → 20 unidades

Además, el sistema registró el correspondiente movimiento de stock de tipo:

VENTA

Esto confirmó que la venta asociada al cliente continúa respetando toda la lógica previamente desarrollada para el control de inventario.


23. PRUEBA DE ANULACIÓN DE VENTA

Posteriormente se anuló la venta de prueba por $40.000.

El sistema realizó automáticamente las siguientes operaciones:

VENTA:

COMPLETADA → ANULADA

STOCK DE SPRITE:

20 → 25 unidades

CUENTA CORRIENTE:

Antes de anular:

Ventas válidas: $40.000
Cobros válidos: $25.000
Saldo: $15.000
Situación: DEUDA

Después de anular:

Ventas válidas: $0
Cobros válidos: $25.000
Saldo: -$25.000
Situación: SALDO_A_FAVOR

La venta anulada dejó automáticamente de participar del cálculo de la cuenta corriente.


24. DEVOLUCIÓN AUTOMÁTICA DE STOCK

La anulación de la venta también permitió comprobar la reversión del stock.

Antes de la venta:

Sprite 500ml = 25 unidades

Después de vender 5 unidades:

Sprite 500ml = 20 unidades

Después de anular la venta:

Sprite 500ml = 25 unidades

Además, se registró el movimiento correspondiente de anulación de venta dentro del historial de stock.

Esto confirmó que la anulación revierte correctamente el impacto de la operación comercial sobre el inventario.


25. INDEPENDENCIA ENTRE VENTA Y COBRO

La anulación de la venta no modificó el saldo de la cuenta financiera.

Este comportamiento es correcto porque la venta de prueba no había generado automáticamente un cobro.

De esta manera se confirmó la separación conceptual:

VENTA ≠ COBRO

Una venta afecta:

- Historial comercial
- Detalle de venta
- Stock
- Historial de movimientos de stock
- Cuenta corriente del cliente

Un cobro afecta:

- Historial de cobros
- Cuenta financiera
- Historial de movimientos financieros
- Cuenta corriente del cliente

Esta separación permite manejar correctamente ventas pendientes, pagos parciales y saldos a favor.


26. FLUJO GENERAL DE LA CUENTA CORRIENTE

El funcionamiento general implementado puede representarse de la siguiente manera:

CLIENTE
│
├── VENTAS
│      │
│      ├── COMPLETADA → suma al total comprado
│      │
│      └── ANULADA → no participa del cálculo
│
├── COBROS
│      │
│      ├── COMPLETADO → resta deuda
│      │
│      └── ANULADO → no participa del cálculo
│
↓
CUENTA CORRIENTE
│
├── Total de ventas válidas
│
├── Total de cobros completados
│
↓
SALDO ACTUAL
│
├── Saldo > 0 → DEUDA
│
├── Saldo = 0 → AL_DIA
│
└── Saldo < 0 → SALDO_A_FAVOR


27. FLUJO COMPLETO VALIDADO

El flujo completo probado quedó conformado de la siguiente manera:

CLIENTE
│
├────────────── VENTA
│                 │
│                 ├── Registrar venta
│                 ├── Registrar detalle
│                 ├── Descontar stock
│                 └── Registrar movimiento de stock
│
├────────────── COBRO
│                 │
│                 ├── Registrar cobro
│                 ├── Aumentar cuenta
│                 └── Registrar movimiento financiero
│
↓
CUENTA CORRIENTE
│
├── Ventas válidas
├── Cobros completados
│
↓
SALDO DEL CLIENTE


28. ENDPOINTS UTILIZADOS

Los principales endpoints involucrados en esta entrega fueron:

POST /cobros

GET /cobros

GET /cobros/<id_cobro>

GET /clientes/<id_cliente>/cobros

PATCH /cobros/<id_cobro>/anular

GET /clientes/<id_cliente>/saldo

POST /ventas

GET /ventas

GET /ventas/<id_venta>

PATCH /ventas/<id_venta>/anular

GET /cuentas/<id_cuenta>/movimientos

GET /productos/<id_producto>


29. VALIDACIONES IMPLEMENTADAS

Durante el desarrollo se incorporaron diferentes validaciones y reglas de negocio.

Entre ellas:

- El cliente debe existir.
- La cuenta financiera debe existir.
- La cuenta debe estar habilitada para registrar nuevos cobros.
- El monto del cobro debe ser mayor a cero.
- El usuario debe ser informado.
- Un cobro no puede anularse dos veces.
- El motivo de anulación debe tener al menos 5 caracteres.
- La cuenta debe disponer de fondos suficientes para revertir un cobro.
- Las ventas deben estar asociadas a un cliente.
- Los productos deben existir.
- La cantidad vendida debe ser mayor a cero.
- Debe existir stock suficiente.
- Una venta anulada no puede volver a anularse.
- Las operaciones anuladas no participan del cálculo del saldo.


30. RESULTADO FINAL

Con esta entrega se logró implementar una parte fundamental del circuito comercial y financiero del sistema.

Se integraron:

CLIENTES
+
VENTAS
+
COBROS
+
STOCK
+
CUENTAS FINANCIERAS
+
MOVIMIENTOS FINANCIEROS
+
ANULACIONES
+
CUENTA CORRIENTE

El sistema puede determinar automáticamente si un cliente:

- Debe dinero.
- Está al día.
- Tiene saldo a favor.

Además, conserva la trazabilidad de las ventas, cobros, anulaciones, movimientos de stock y movimientos financieros.


31. ESTADO FINAL DE LA ENTREGA

Registro de cobros: COMPLETADO

Consulta general de cobros: COMPLETADO

Consulta individual de cobros: COMPLETADO

Historial de cobros por cliente: COMPLETADO

Anulación de cobros: COMPLETADO

Reversión automática del saldo de cuenta: COMPLETADO

Registro de movimientos financieros: COMPLETADO

Prevención de doble anulación: COMPLETADO

Venta asociada a cliente: COMPLETADO

Cálculo automático de cuenta corriente: COMPLETADO

Cálculo de deuda: COMPLETADO

Manejo de saldo a favor: COMPLETADO

Exclusión de cobros anulados: COMPLETADO

Exclusión de ventas anuladas: COMPLETADO

Integración con stock: COMPLETADO

Devolución de stock al anular venta: COMPLETADO

Pruebas de punta a punta: COMPLETADO


ENTREGA 13 – COMPLETADA