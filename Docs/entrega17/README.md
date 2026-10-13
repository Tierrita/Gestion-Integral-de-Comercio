ENTREGA 17 – MÓDULO FINANCIERO: RENTABILIDAD Y CAJA

Proyecto: Gestión Integral de Comercio

Objetivo de la entrega:
Implementar la primera etapa del módulo financiero del sistema, permitiendo obtener indicadores reales de rentabilidad y analizar los movimientos de dinero del comercio por diferentes períodos.

Esta entrega se apoya en la implementación realizada en la Entrega 16, donde se incorporaron los costos históricos de venta y la actualización automática de precios ante cambios en el costo de compra.


--------------------------------------------------
1. RENTABILIDAD
--------------------------------------------------

Se implementó un nuevo endpoint:

GET /finanzas/rentabilidad

El objetivo de esta ruta es obtener los principales indicadores económicos del comercio a partir de las ventas completadas.

Indicadores calculados:

- Facturación total.
- Costo de los productos vendidos.
- Ganancia bruta.
- Margen bruto porcentual.
- Cantidad de ventas.
- Cantidad de detalles sin costo histórico.
- Estado que indica si la rentabilidad puede calcularse de forma confiable.


--------------------------------------------------
2. COSTO HISTÓRICO
--------------------------------------------------

Para calcular correctamente la rentabilidad se utiliza el campo:

detalle_venta.costo_unitario

Este valor representa el costo que tenía el producto al momento de realizar la venta.

De esta manera, una modificación futura en el precio de costo de un producto no modifica la rentabilidad histórica de las ventas anteriores.

Ejemplo:

Costo histórico: $500
Precio de venta: $900
Cantidad: 2

Facturación:
$1.800

Costo vendido:
$1.000

Ganancia bruta:
$800

Margen bruto:
44,44 %


--------------------------------------------------
3. CONTROL DE VENTAS ANTIGUAS
--------------------------------------------------

El sistema contempla la existencia de ventas realizadas antes de incorporar el costo histórico.

Si alguna venta del período no posee costo histórico:

- La facturación continúa siendo calculada.
- El costo vendido no se calcula.
- La ganancia bruta no se calcula.
- El margen bruto no se calcula.
- Se informa que la rentabilidad no es confiable.

Ejemplo:

"rentabilidad_calculable": false

Además, se devuelve una advertencia indicando la existencia de ventas sin costo histórico.

Esto evita mostrar indicadores financieros incorrectos.


--------------------------------------------------
4. FILTROS POR PERÍODO
--------------------------------------------------

Se implementó un sistema reutilizable para consultar información financiera según diferentes períodos.

Períodos disponibles:

HOY

GET /finanzas/rentabilidad?periodo=hoy


SEMANA

GET /finanzas/rentabilidad?periodo=semana


MES

GET /finanzas/rentabilidad?periodo=mes


AÑO

GET /finanzas/rentabilidad?periodo=anio


PERSONALIZADO

GET /finanzas/rentabilidad?desde=2026-10-01&hasta=2026-10-06


Si no se especifica ningún período, el sistema utiliza el mes actual por defecto.

La aplicación utiliza la zona horaria:

America/Argentina/Buenos_Aires


--------------------------------------------------
5. MÓDULO DE CAJA
--------------------------------------------------

Se implementó el segundo componente del módulo financiero:

GET /finanzas/caja

Esta ruta analiza los movimientos financieros registrados en el sistema y permite conocer las entradas y salidas de dinero durante un período determinado.

Caja no representa solamente la facturación.

Representa los movimientos reales de dinero registrados en las cuentas financieras del comercio.


--------------------------------------------------
6. MOVIMIENTOS DE ENTRADA
--------------------------------------------------

Actualmente se consideran entradas de Caja:

VENTA
Ingreso generado por una venta con pago inmediato.

COBRO
Ingreso generado cuando un cliente realiza un pago.

AJUSTE_ENTRADA
Ingreso generado mediante un ajuste manual de una cuenta.


--------------------------------------------------
7. MOVIMIENTOS DE SALIDA
--------------------------------------------------

Actualmente se consideran salidas de Caja:

ANULACION_VENTA
Reversión del ingreso generado por una venta.

ANULACION_COBRO
Reversión de un cobro previamente registrado.

AJUSTE_SALIDA
Salida generada mediante un ajuste manual de una cuenta.


--------------------------------------------------
8. INDICADORES DE CAJA
--------------------------------------------------

La consulta de Caja devuelve:

- Total de entradas.
- Total de salidas.
- Movimiento neto.
- Cantidad total de movimientos.
- Cantidad de entradas.
- Cantidad de salidas.

Además, las entradas se desglosan en:

- Ventas cobradas.
- Cobros de clientes.
- Ajustes de entrada.

Las salidas se desglosan en:

- Anulaciones de venta.
- Anulaciones de cobro.
- Ajustes de salida.


--------------------------------------------------
9. FILTROS DE CAJA
--------------------------------------------------

Caja utiliza el mismo sistema de períodos desarrollado para Rentabilidad.

Ejemplos:

GET /finanzas/caja?periodo=hoy

GET /finanzas/caja?periodo=semana

GET /finanzas/caja?periodo=mes

GET /finanzas/caja?periodo=anio

GET /finanzas/caja?desde=2026-10-06&hasta=2026-10-06


Esto permite reutilizar una única lógica de períodos dentro del módulo financiero.


--------------------------------------------------
10. INTEGRACIÓN DE VENTAS CON CAJA
--------------------------------------------------

Se modificó el registro de ventas para diferenciar correctamente una venta inmediata de una venta en cuenta corriente.

VENTA INMEDIATA:

Cuando una venta se realiza mediante un método de pago inmediato:

- Se registra la venta.
- Se descuenta el stock.
- Se registra el costo histórico.
- Se incrementa el saldo de la cuenta seleccionada.
- Se genera un movimiento financiero tipo VENTA.


VENTA EN CUENTA CORRIENTE:

Cuando el método de pago es:

CUENTA_CORRIENTE

- Se registra la venta.
- Se descuenta el stock.
- Se registra el costo histórico.
- No se modifica ninguna cuenta financiera.
- No se registra un ingreso en Caja.
- La operación queda reflejada como deuda del cliente.


--------------------------------------------------
11. ANULACIÓN FINANCIERA DE VENTAS
--------------------------------------------------

Se incorporó la reversión financiera de una venta inmediata.

Cuando se anula una venta que previamente generó un ingreso:

- Se revierte el stock.
- Se identifica el movimiento financiero original.
- Se descuenta de la cuenta el importe correspondiente.
- Se registra un movimiento ANULACION_VENTA.
- La venta pasa al estado ANULADA.

De esta forma queda trazabilidad tanto del ingreso original como de su posterior anulación.


--------------------------------------------------
12. FUNCIONES RPC EN SUPABASE
--------------------------------------------------

Para proteger las operaciones financieras se incorporaron funciones RPC en Supabase.

registrar_ingreso_venta

Responsabilidades:

- Validar la cuenta financiera.
- Validar que la cuenta esté activa.
- Incrementar su saldo.
- Registrar el movimiento financiero VENTA.


anular_ingreso_venta

Responsabilidades:

- Localizar el ingreso original.
- Evitar una doble anulación.
- Verificar fondos disponibles.
- Descontar el importe correspondiente.
- Registrar el movimiento ANULACION_VENTA.

Estas operaciones permiten mantener sincronizado el saldo de las cuentas con el historial de movimientos financieros.


--------------------------------------------------
13. PRUEBAS REALIZADAS
--------------------------------------------------

Se realizaron pruebas utilizando Postman.

PRUEBA DE VENTA INMEDIATA

Venta:
$1.080

Resultado:

Movimiento financiero:
VENTA +$1.080

Saldo de cuenta:
$0 → $1.080


PRUEBA DE ANULACIÓN

Se anuló la misma venta.

Movimiento:

ANULACION_VENTA -$1.080

Saldo:

$1.080 → $0


Resultado neto:

$0


--------------------------------------------------
14. PRUEBA DE COBRO DE CLIENTE
--------------------------------------------------

Se registró posteriormente un cobro parcial:

Monto:
$500

Resultado:

- Cobro registrado correctamente.
- Movimiento financiero generado.
- Cuenta financiera:

$0 → $500

- El total de cobros del cliente aumentó $500.
- El saldo del cliente fue actualizado.


--------------------------------------------------
15. VALIDACIÓN DE CAJA DEL DÍA
--------------------------------------------------

Durante la prueba se registraron:

Venta inmediata:
+$1.080

Anulación de venta:
-$1.080

Cobro de cliente:
+$500


Resultado obtenido por:

GET /finanzas/caja?periodo=hoy


Total entradas:
$1.580

Total salidas:
$1.080

Movimiento neto:
$500

Cantidad de entradas:
2

Cantidad de salidas:
1

Cantidad total de movimientos:
3


El resultado coincide exactamente con los movimientos financieros realizados.


--------------------------------------------------
16. DIFERENCIA ENTRE FACTURACIÓN Y CAJA
--------------------------------------------------

Uno de los puntos principales implementados en esta entrega es la separación entre ventas y movimientos reales de dinero.

FACTURACIÓN:

Representa las ventas completadas durante un período.


CAJA:

Representa los ingresos y salidas reales registrados en las cuentas financieras.


Ejemplo:

Una venta realizada en cuenta corriente aumenta la facturación, pero no aumenta Caja.

Cuando posteriormente el cliente paga esa deuda:

- No se genera una nueva venta.
- No aumenta la facturación.
- Aumenta Caja.
- Disminuye la deuda del cliente.


--------------------------------------------------
17. VALIDACIÓN DE RENTABILIDAD
--------------------------------------------------

Luego de registrar el cobro de $500 se volvió a consultar:

GET /finanzas/rentabilidad?periodo=hoy


Resultado:

Facturación:
$2.880

Costo vendido:
$1.600

Ganancia bruta:
$1.280

Margen bruto:
44,44 %

Cantidad de ventas:
2


Los valores de Rentabilidad no fueron modificados por el cobro.

Esto confirma que el sistema diferencia correctamente:

VENTA → genera facturación.

COBRO → genera movimiento de Caja.


--------------------------------------------------
18. ARQUITECTURA UTILIZADA
--------------------------------------------------

Se mantiene la arquitectura modular del proyecto:

Route
   ↓
Controller
   ↓
Service
   ↓
Model
   ↓
Supabase


Archivos principales involucrados:

app/models/finanza_model.py

app/services/finanza_service.py

app/controllers/finanza_controller.py

app/routes/finanza_routes.py

app/models/venta_model.py

app/services/venta_service.py

movimientos_financieros


--------------------------------------------------
19. RESULTADO DE LA ENTREGA
--------------------------------------------------

Con esta entrega el sistema ya permite:

- Calcular facturación.
- Calcular costo histórico vendido.
- Calcular ganancia bruta.
- Calcular margen bruto.
- Detectar ventas antiguas sin costo histórico.
- Consultar indicadores por período.
- Registrar ingresos de ventas inmediatas.
- Diferenciar ventas inmediatas de ventas en cuenta corriente.
- Revertir financieramente ventas anuladas.
- Registrar cobros de clientes.
- Analizar entradas de Caja.
- Analizar salidas de Caja.
- Calcular el movimiento neto.
- Consultar Caja por día, semana, mes, año o período personalizado.
- Mantener trazabilidad mediante movimientos financieros.


--------------------------------------------------
20. PRÓXIMOS PASOS
--------------------------------------------------

La próxima etapa del módulo financiero será:

FINANZAS → VENTAS

Se planificó incorporar:

- Facturación por período.
- Cantidad de ventas.
- Ticket promedio.
- Unidades vendidas.
- Evolución de ventas.

Posteriormente se continuará con:

- Estadísticas de productos.
- Estadísticas de proveedores.
- Estadísticas de clientes.
- Valorización de stock.
- Resumen/Dashboard financiero.


Las comparaciones contra períodos anteriores quedan registradas como una mejora futura.