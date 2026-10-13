ENTREGA 18 – MÓDULO FINANCIERO: ANÁLISIS COMERCIAL

Proyecto: Gestión Integral de Comercio


OBJETIVO DE LA ENTREGA:

Continuar el desarrollo del módulo financiero iniciado en la Entrega 17,
incorporando herramientas de análisis comercial sobre ventas, productos,
proveedores y clientes.

El objetivo es transformar la información registrada por las operaciones
del sistema en indicadores útiles para la toma de decisiones del comercio.

Se incorporaron consultas por período, rankings comerciales, análisis de
productos vendidos y comprados, evolución de costos, deuda con proveedores
y saldos pendientes de clientes.


--------------------------------------------------
1. ESTADÍSTICAS DE VENTAS
--------------------------------------------------

Se implementó el endpoint:

GET /finanzas/ventas

Esta ruta permite analizar las ventas completadas durante un período.

Indicadores calculados:

- Facturación total.
- Cantidad de ventas.
- Ticket promedio.
- Cantidad de unidades vendidas.


Períodos disponibles:

HOY

GET /finanzas/ventas?periodo=hoy


SEMANA

GET /finanzas/ventas?periodo=semana


MES

GET /finanzas/ventas?periodo=mes


AÑO

GET /finanzas/ventas?periodo=anio


PERSONALIZADO

GET /finanzas/ventas?desde=2026-10-01&hasta=2026-10-31


Si no se especifica un período, se utiliza el mes actual.


--------------------------------------------------
2. EVOLUCIÓN DE VENTAS
--------------------------------------------------

Se incorporó una consulta específica para analizar la evolución de las
ventas dentro de un período.

Endpoint:

GET /finanzas/ventas/evolucion

La información permite observar cómo se distribuyeron las ventas a lo
largo del tiempo.

Para cada intervalo se pueden obtener indicadores como:

- Facturación.
- Cantidad de ventas.
- Unidades vendidas.

Esto permitirá posteriormente representar la evolución mediante gráficos
en el Dashboard del frontend.


--------------------------------------------------
3. VALIDACIÓN DE ESTADÍSTICAS DE VENTAS
--------------------------------------------------

Durante las pruebas del mes se obtuvo:

Cantidad de ventas:
8

Facturación:
$96.880

Unidades vendidas:
17

Ticket promedio:
$12.110


Validación:

$96.880 / 8 ventas = $12.110


Esto confirma que los indicadores generales de ventas se calculan
correctamente.


--------------------------------------------------
4. ESTADÍSTICAS DE PRODUCTOS
--------------------------------------------------

Se implementó el endpoint:

GET /finanzas/productos

El objetivo es analizar el rendimiento comercial de cada producto a partir
de las ventas completadas.

Se incorporaron indicadores por producto como:

- Cantidad vendida.
- Facturación generada.
- Costo histórico vendido.
- Ganancia bruta.
- Margen bruto.


Además, se generan rankings que permiten identificar:

- Productos más vendidos.
- Productos con mayor facturación.
- Productos con mayor ganancia.
- Productos con mayor margen.
- Productos menos vendidos.


--------------------------------------------------
5. COSTO HISTÓRICO EN ESTADÍSTICAS DE PRODUCTOS
--------------------------------------------------

Para calcular la rentabilidad de cada producto se utiliza:

detalle_venta.costo_unitario

De esta forma, los rankings de ganancia no utilizan el costo actual del
producto, sino el costo que existía al momento de cada venta.

Esto evita modificar artificialmente la rentabilidad histórica cuando
cambia el costo actual de un producto.


Si un detalle de venta antiguo no posee costo histórico, el sistema evita
utilizarlo para calcular indicadores de rentabilidad no confiables.


--------------------------------------------------
6. VALIDACIÓN DE PRODUCTOS
--------------------------------------------------

Durante las pruebas del período mensual se registraron:

Sprite 500ml:
- 12 unidades vendidas.
- Facturación: $54.000.

Alfajor de chocolate:
- 3 unidades vendidas.
- Facturación: $2.880.
- Costo histórico vendido: $1.600.
- Ganancia bruta: $1.280.
- Margen bruto: 44,44 %.

Coca-Cola 500ml:
- 2 unidades vendidas.
- Facturación: $40.000.


Total:

17 unidades vendidas.

Facturación:

$96.880


Los valores coinciden con las estadísticas generales de Ventas.


--------------------------------------------------
7. ESTADÍSTICAS DE PROVEEDORES
--------------------------------------------------

Se implementó el endpoint:

GET /finanzas/proveedores

Esta ruta permite analizar las compras realizadas a proveedores durante
un período y combinar esa información con la situación financiera actual
de cada proveedor.

Indicadores incorporados:

- Total comprado.
- Cantidad de compras.
- Cantidad de proveedores.
- Ranking de proveedores.
- Productos comprados.
- Deuda actual con proveedores.
- Evolución de costos de compra.


--------------------------------------------------
8. RANKING DE PROVEEDORES
--------------------------------------------------

Se incorporó un ranking según el total comprado a cada proveedor.

Para cada proveedor se informa:

- ID del proveedor.
- Nombre.
- Cantidad de compras.
- Total comprado.


Esto permite identificar cuáles son los proveedores con mayor participación
dentro del abastecimiento del comercio.


--------------------------------------------------
9. DEUDA CON PROVEEDORES
--------------------------------------------------

El módulo financiero reutiliza la lógica existente de saldo de proveedores.

Para cada proveedor se consideran:

- Compras válidas.
- Pagos completados.
- Saldo pendiente.


Durante las pruebas se obtuvo:

Distribuidora Norte:
Saldo pendiente: $17.500

Distribuidora Central:
Saldo pendiente: $8.400

Distribuidora Norte Rojas:
Saldo pendiente: $4.250


Deuda total con proveedores:

$30.150


La deuda representa el saldo actual del proveedor y no solamente las
operaciones realizadas dentro del período consultado.


--------------------------------------------------
10. PRODUCTOS COMPRADOS
--------------------------------------------------

Dentro de las estadísticas de proveedores se incorporó el análisis de
productos comprados.

Para cada producto se informa:

- Cantidad comprada.
- Total comprado.
- Precio promedio de compra.
- Proveedores utilizados.


Además, para cada proveedor del producto se informa:

- Cantidad comprada.
- Total comprado.
- Precio promedio de compra.
- Último precio de compra.


Esto permite comparar el abastecimiento de un mismo producto entre
diferentes proveedores.


--------------------------------------------------
11. PRECIO PROMEDIO DE COMPRA
--------------------------------------------------

El precio promedio informado por Finanzas representa un promedio histórico
ponderado de las compras realizadas durante el período.

Este indicador no reemplaza el precio de costo actual del producto.

El costo actual continúa siendo administrado por la lógica de Compras
implementada anteriormente.


Ejemplo mensual:

Sprite 500ml:

Cantidad comprada:
15 unidades

Total comprado:
$14.250

Precio promedio:
$950


Alfajor de chocolate:

Cantidad comprada:
30 unidades

Total comprado:
$17.500

Precio promedio:
$583,33


--------------------------------------------------
12. EVOLUCIÓN DE COSTOS
--------------------------------------------------

Se incorporó un historial de precios de compra por producto.

Para cada producto se informa:

- Precio inicial del período.
- Precio final del período.
- Variación porcentual.
- Tendencia.
- Cantidad de registros.
- Historial de compras.


Las tendencias posibles son:

SUBIO
BAJO
SIN_CAMBIOS


Ejemplo:

Sprite 500ml:

Precio inicial:
$1.000

Precio final:
$850

Variación:
-15 %

Tendencia:
BAJO


Alfajor de chocolate:

Precio inicial:
$600

Precio final:
$550

Variación:
-8,33 %

Tendencia:
BAJO


--------------------------------------------------
13. ESTADÍSTICAS DE CLIENTES
--------------------------------------------------

Se implementó el endpoint:

GET /finanzas/clientes

El objetivo es analizar el comportamiento comercial de los clientes.

Indicadores incorporados:

- Facturación por cliente.
- Cantidad de compras.
- Ticket promedio.
- Ranking por facturación.
- Ranking por cantidad de compras.
- Clientes con deuda.
- Total por cobrar.


--------------------------------------------------
14. RANKING DE CLIENTES
--------------------------------------------------

Durante las pruebas mensuales se obtuvo:

Gabriel Silva:

Cantidad de compras:
5

Facturación:
$55.080

Ticket promedio:
$11.016


Cristina:

Cantidad de compras:
1

Facturación:
$20.000

Ticket promedio:
$20.000


Cristian:

Cantidad de compras:
1

Facturación:
$20.000

Ticket promedio:
$20.000


CLIENTE GENERAL:

Cantidad de compras:
1

Facturación:
$1.800

Ticket promedio:
$1.800


La suma de las operaciones coincide con:

8 ventas

Facturación total:

$96.880


--------------------------------------------------
15. CUENTAS POR COBRAR
--------------------------------------------------

Se integró la lógica existente de saldo de clientes dentro del análisis
financiero.

Durante las pruebas:

Cliente:
Cristina

Saldo pendiente:
$10.000


Total por cobrar:

$10.000


CLIENTE GENERAL participa de los rankings comerciales, pero no se considera
como cliente deudor debido a que opera mediante ventas al contado.


--------------------------------------------------
16. FILTROS POR PERÍODO
--------------------------------------------------

Las nuevas estadísticas reutilizan el sistema de períodos desarrollado
en la Entrega 17.

Períodos disponibles:

- Hoy.
- Semana.
- Mes.
- Año.
- Personalizado.


Esto mantiene una única lógica temporal dentro del módulo financiero y
permite que las distintas estadísticas sean comparables.


--------------------------------------------------
17. PRUEBAS EN POSTMAN
--------------------------------------------------

Se ampliaron las pruebas de la colección:

Gestión Integral de Comercio


Dentro de:

11 - Finanzas


Se incorporaron consultas para:

- Ventas.
- Evolución de ventas.
- Productos.
- Proveedores.
- Productos comprados.
- Clientes.


Cada módulo fue probado utilizando:

- Hoy.
- Semana.
- Mes.
- Año.
- Período personalizado.


--------------------------------------------------
18. VALIDACIÓN DE PRODUCTOS COMPRADOS
--------------------------------------------------

Durante la validación anual se detectó inicialmente una diferencia entre:

Total comprado:
$70.250

Suma de productos detallados:
$55.250


Diferencia:

$15.000


Se investigó la información histórica y se identificó la causa.

La compra:

ID Compra:
3

Total:
$15.000

Estado:
COMPLETADA


no posee registros asociados en detalle_compra.


La consulta:

GET /compras/3


devolvió:

"detalles": []


Por lo tanto, la diferencia corresponde a un dato histórico de prueba
generado durante las primeras etapas de desarrollo del módulo de Compras.

No se modificó la lógica financiera, ya que el comportamiento actual es
correcto:

- total_comprado utiliza las compras registradas.
- productos_comprados utiliza los detalles reales de esas compras.

Esto permitió además verificar que Finanzas no genera productos o detalles
inexistentes para completar una compra inconsistente.


--------------------------------------------------
19. CORRECCIÓN DE ESTRUCTURA DEL SERVICIO FINANCIERO
--------------------------------------------------

Durante la incorporación de las estadísticas de Clientes se detectó una
regresión en:

GET /finanzas/proveedores


La respuesta devolvía:

"proveedores": null


Se identificó que la función:

calcular_estadisticas_clientes()


había sido ubicada accidentalmente antes de finalizar completamente:

calcular_estadisticas_proveedores()


Esto provocaba que la función de Proveedores finalizara sin retornar sus
estadísticas.


Se reorganizó:

app/services/finanza_service.py


dejando cada función completamente independiente.

Estructura resultante:

calcular_estadisticas_proveedores()
        ↓
return estadísticas proveedores

calcular_estadisticas_clientes()
        ↓
return estadísticas clientes


Posteriormente se volvieron a ejecutar ambas consultas y se comprobó el
funcionamiento correcto de Proveedores y Clientes.


--------------------------------------------------
20. ARQUITECTURA
--------------------------------------------------

Se mantiene la arquitectura modular utilizada por el proyecto:

Route
  ↓
Controller
  ↓
Service
  ↓
Model
  ↓
Supabase


Los componentes principales del módulo financiero continúan organizados en:

app/models/finanza_model.py

app/services/finanza_service.py

app/controllers/finanza_controller.py

app/routes/finanza_routes.py


El módulo reutiliza además servicios existentes para evitar duplicar
reglas de negocio, por ejemplo:

- Saldo de clientes.
- Saldo de proveedores.
- Ventas completadas.
- Compras completadas.


--------------------------------------------------
21. RESULTADO DE LA ENTREGA
--------------------------------------------------

Con esta entrega el módulo financiero permite:

- Analizar ventas por período.
- Calcular facturación.
- Calcular cantidad de ventas.
- Calcular ticket promedio.
- Calcular unidades vendidas.
- Analizar evolución de ventas.
- Analizar rendimiento de productos.
- Generar rankings de productos.
- Analizar rentabilidad por producto mediante costo histórico.
- Analizar compras por proveedor.
- Generar ranking de proveedores.
- Consultar deuda actual con proveedores.
- Analizar productos comprados.
- Calcular precios promedio históricos de compra.
- Comparar proveedores por producto.
- Analizar evolución de costos.
- Detectar subas o bajas de costos.
- Analizar clientes.
- Generar rankings de clientes.
- Calcular ticket promedio por cliente.
- Consultar clientes con deuda.
- Calcular el total pendiente por cobrar.
- Consultar todos los indicadores utilizando diferentes períodos.


--------------------------------------------------
22. ESTADO ACTUAL DEL MÓDULO FINANCIERO
--------------------------------------------------

FINANZAS

Rentabilidad                         COMPLETADO
Caja                                 COMPLETADO
Ventas                               COMPLETADO
Evolución de ventas                  COMPLETADO
Productos                            COMPLETADO
Proveedores                          COMPLETADO
Productos comprados                  COMPLETADO
Evolución de costos                  COMPLETADO
Clientes                             COMPLETADO
Stock financiero                     PENDIENTE
Dashboard / Resumen general          PENDIENTE


Las comparaciones contra períodos anteriores continúan registradas como
una mejora futura.


--------------------------------------------------
23. PRÓXIMOS PASOS
--------------------------------------------------

La próxima etapa será:

FINANZAS → STOCK


Se planificó incorporar inicialmente:

- Valor actual del stock a costo.
- Valor actual del stock a precio de venta.
- Ganancia potencial del stock.
- Detalle financiero por producto.


Posteriormente se analizará:

- Rotación de productos.
- Productos de baja rotación.
- Capital inmovilizado en stock.


Una vez finalizado Stock se desarrollará:

FINANZAS → DASHBOARD


El Dashboard utilizará los indicadores desarrollados en las distintas
etapas del módulo financiero para presentar una visión general del estado
comercial del negocio.