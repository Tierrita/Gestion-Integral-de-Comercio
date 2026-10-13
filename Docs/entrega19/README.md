ENTREGA 18 – MÓDULO FINANCIERO: ANÁLISIS COMERCIAL Y DASHBOARD

1. OBJETIVO DE LA ENTREGA

En esta entrega se completó el desarrollo del Módulo Financiero del sistema Gestión Integral de Comercio.

El objetivo principal fue transformar la información generada por las operaciones del sistema —ventas, compras, clientes, proveedores y stock— en información comercial útil para la toma de decisiones.

El módulo permite actualmente analizar:

- Ventas.
- Rentabilidad.
- Caja.
- Productos.
- Proveedores.
- Clientes.
- Stock financiero.
- Rankings comerciales.
- Evolución de costos.
- Deudas de clientes.
- Deudas con proveedores.
- Dashboard financiero general.

Además, los principales análisis pueden filtrarse por diferentes períodos de tiempo.


2. ARQUITECTURA IMPLEMENTADA

Se mantuvo la arquitectura utilizada en el resto del backend:

Route
  ↓
Controller
  ↓
Service
  ↓
Model
  ↓
Supabase

La lógica financiera principal se encuentra distribuida en:

Backend/
└── app/
    ├── models/
    │   └── finanza_model.py
    ├── services/
    │   └── finanza_service.py
    ├── controllers/
    │   └── finanza_controller.py
    └── routes/
        └── finanza_routes.py

Esta separación permite mantener diferenciadas las responsabilidades de acceso a datos, lógica de negocio, manejo HTTP y definición de endpoints.


3. ANÁLISIS DE VENTAS

Se desarrolló un análisis general de las ventas realizadas durante un período determinado.

El sistema permite obtener indicadores como:

- Facturación total.
- Cantidad de ventas.
- Cantidad de unidades vendidas.
- Ticket promedio.

Ejemplo validado para octubre de 2026:

Facturación:        $96.880
Cantidad ventas:    8
Unidades vendidas:  17
Ticket promedio:    $12.110

También se implementó la evolución temporal de ventas, permitiendo conocer cómo se distribuyeron las operaciones dentro del período seleccionado.


4. RENTABILIDAD

Se mantuvo y amplió el sistema de rentabilidad desarrollado anteriormente.

El cálculo utiliza el costo histórico almacenado al momento de realizar cada venta, evitando modificar la rentabilidad histórica cuando cambia posteriormente el costo actual de un producto.

Los principales indicadores son:

- Facturación.
- Costo vendido.
- Ganancia bruta.
- Margen bruto.
- Cantidad de ventas.
- Detalles sin costo histórico.

La fórmula utilizada es:

Ganancia Bruta = Facturación - Costo Vendido

Margen Bruto (%) = (Ganancia Bruta / Facturación) × 100

Cuando existen ventas antiguas que no poseen costo_unitario, el sistema informa que la rentabilidad completa del período no puede calcularse de forma confiable.

Esto evita mostrar información financiera incorrecta.


5. COSTOS HISTÓRICOS

La tabla detalle_venta utiliza el campo:

costo_unitario

Este valor representa el costo que tenía el producto en el momento exacto de realizar la venta.

Ejemplo:

Producto: Alfajor de chocolate

Costo histórico: $500
Precio venta:     $900
Cantidad:         2

Facturación:      $1.800
Costo vendido:    $1.000
Ganancia bruta:   $800
Margen bruto:     44,44 %

Aunque posteriormente el costo actual del producto cambie, esta venta conserva su rentabilidad original.


6. ACTUALIZACIÓN AUTOMÁTICA DE COSTOS

También se implementó una regla comercial para actualizar los costos actuales de los productos mediante las compras a proveedores.

La regla definida es:

Nuevo costo > costo actual
        ↓
Actualizar costo
        ↓
Recalcular precio de venta
        ↓
Mantener porcentaje de markup

Si el nuevo costo de compra es menor o igual al costo actual:

- NO se reduce el costo actual.
- NO se reduce el precio de venta.

Las ventas históricas tampoco se modifican.


7. ESTADÍSTICAS DE PRODUCTOS

Se desarrolló el análisis financiero individual de los productos vendidos.

Entre los indicadores disponibles se encuentran:

- Cantidad vendida.
- Facturación.
- Costo vendido.
- Ganancia bruta.
- Margen bruto.
- Rentabilidad calculable.

Además, se generaron rankings para identificar los productos con mejor desempeño comercial.

Durante las pruebas realizadas, el producto con mayor cantidad vendida durante octubre fue:

Sprite 500ml
Cantidad vendida: 12
Facturación: $54.000


8. ANÁLISIS DE PROVEEDORES

Se desarrolló un análisis financiero completo de proveedores.

El sistema permite obtener:

- Cantidad de proveedores.
- Cantidad de compras.
- Total comprado.
- Deuda con proveedores.
- Ranking de proveedores.
- Productos comprados.
- Precio promedio histórico.
- Evolución de costos.

Ejemplo validado para octubre:

Compras:           5
Proveedores:        3
Total comprado:     $31.750
Deuda proveedores:  $30.150


9. RANKING DE PROVEEDORES

Los proveedores pueden ordenarse según el volumen comercial generado.

Ejemplo:

Distribuidora Norte

Cantidad de compras: 3
Total comprado:      $17.500

Esto permite identificar rápidamente cuáles son los proveedores con mayor participación en las compras del comercio.


10. PRODUCTOS COMPRADOS

También se implementó un análisis de los productos adquiridos a proveedores.

Para cada producto puede obtenerse:

- Cantidad comprada.
- Total comprado.
- Precio promedio de compra.
- Proveedores relacionados.
- Último costo registrado.

El precio promedio calculado corresponde a un promedio histórico ponderado de compras.

Este valor se utiliza únicamente con fines analíticos y no reemplaza el costo actual almacenado en el producto.


11. EVOLUCIÓN DE COSTOS

El módulo permite detectar cómo evolucionó el costo de compra de cada producto.

El sistema compara:

- Costo inicial del período.
- Costo final del período.
- Variación monetaria.
- Variación porcentual.
- Cantidad de registros.
- Tendencia.

La tendencia puede indicar:

- SUBIO.
- BAJO.
- SIN_CAMBIOS.

Esto permite detectar aumentos o reducciones en los costos de proveedores.


12. ANÁLISIS DE CLIENTES

Se desarrolló el análisis comercial de clientes.

Para cada cliente pueden analizarse:

- Cantidad de compras.
- Facturación.
- Ticket promedio.
- Saldo pendiente.

Además, se generan rankings comerciales.

Ejemplo validado:

Cliente: Gabriel Silva

Compras:          5
Facturación:      $55.080
Ticket promedio:  $11.016


13. CUENTAS POR COBRAR

El módulo financiero permite conocer cuánto dinero tienen pendiente los clientes.

Durante las pruebas realizadas:

Clientes con deuda: 1
Total por cobrar:   $10.000

El cliente especial CLIENTE GENERAL no se considera deudor debido a que sus operaciones se realizan al contado.


14. STOCK FINANCIERO

Se desarrolló un análisis financiero del stock actualmente disponible.

El sistema calcula:

- Unidades actuales en stock.
- Valor del stock a costo.
- Valor potencial de venta.
- Ganancia bruta potencial.
- Capital inmovilizado.
- Rotación aproximada.

Ejemplo validado:

Unidades en stock:       169
Valor a costo:           $140.100
Valor potencial venta:   $225.560
Ganancia potencial:      $85.460

La ganancia potencial representa la diferencia entre el valor actual del stock a precio de venta y su valor a costo.

No representa una ganancia realizada hasta que la mercadería sea efectivamente vendida.


15. CAPITAL INMOVILIZADO

Se implementó un indicador para identificar productos que actualmente poseen stock pero no registraron ventas durante el período seleccionado.

Durante las pruebas de octubre:

Capital inmovilizado: $82.100

Este valor corresponde al costo actual del stock de productos que no tuvieron ventas durante dicho período.

El indicador permite detectar mercadería que mantiene capital invertido sin movimiento comercial.


16. ROTACIÓN APROXIMADA DEL STOCK

También se desarrolló un indicador operativo de movimiento del inventario.

Los productos se clasifican en:

- SIN_VENTAS.
- BAJA.
- MEDIA.
- ALTA.

Ejemplo:

Sprite 500ml

Stock actual:       28
Unidades vendidas:  12
Índice:              30 %
Rotación:            MEDIA

Alfajor de chocolate

Stock actual:       57
Unidades vendidas:  3
Índice:              5 %
Rotación:            BAJA

Este indicador se utiliza como herramienta comercial y no pretende reemplazar indicadores contables de rotación de inventario basados en inventario promedio.


17. FILTROS POR PERÍODO

Los análisis financieros desarrollados permiten trabajar con diferentes períodos.

Se implementaron:

- HOY.
- SEMANA.
- MES.
- AÑO.
- PERSONALIZADO.

Ejemplo:

GET /finanzas/ventas?periodo=mes

También pueden definirse fechas manualmente:

GET /finanzas/ventas?desde=2026-10-01&hasta=2026-10-31

El mismo sistema de períodos se reutiliza en los diferentes análisis financieros.


18. DASHBOARD FINANCIERO

Como cierre del módulo se desarrolló un Dashboard Financiero.

Su objetivo es centralizar los principales indicadores del comercio mediante una única petición.

Endpoint:

GET /finanzas/dashboard?periodo=mes

El Dashboard reutiliza los servicios financieros previamente desarrollados.

Conceptualmente:

Ventas ─────────────┐
Rentabilidad ───────┤
Caja ───────────────┤
Productos ──────────┤
Proveedores ────────┼──→ DASHBOARD
Clientes ───────────┤
Stock ──────────────┘

De esta manera se evita duplicar lógica de negocio.


19. INFORMACIÓN DEL DASHBOARD

El Dashboard devuelve información resumida sobre:

VENTAS
- Facturación.
- Cantidad de ventas.
- Ticket promedio.
- Unidades vendidas.

RENTABILIDAD
- Costo vendido.
- Ganancia bruta.
- Margen bruto.
- Estado del cálculo.

CAJA
- Entradas.
- Salidas.
- Saldo neto.

CLIENTES
- Total por cobrar.
- Clientes con deuda.

PROVEEDORES
- Total comprado.
- Deuda con proveedores.

STOCK
- Unidades.
- Valor a costo.
- Valor a venta.
- Ganancia potencial.
- Capital inmovilizado.

RANKINGS
- Producto más vendido.
- Mejor cliente.
- Principal proveedor.


20. RESULTADO DE PRUEBA DEL DASHBOARD

Durante la prueba mensual correspondiente a octubre de 2026 se obtuvieron los siguientes valores:

VENTAS
Facturación:            $96.880
Cantidad ventas:        8
Ticket promedio:        $12.110
Unidades vendidas:      17

CAJA
Entradas:               $460.580
Salidas:                $196.080
Saldo neto:             $264.500

CLIENTES
Por cobrar:             $10.000
Clientes con deuda:     1

PROVEEDORES
Total comprado:         $31.750
Deuda proveedores:      $30.150

STOCK
Valor a costo:          $140.100
Valor a venta:          $225.560
Ganancia potencial:     $85.460
Capital inmovilizado:   $82.100

RANKINGS

Producto más vendido:
Sprite 500ml

Mejor cliente:
Gabriel Silva

Principal proveedor:
Distribuidora Norte


21. VALIDACIÓN DE CONSISTENCIA

Uno de los objetivos de las pruebas fue verificar que los diferentes módulos financieros fueran consistentes entre sí.

Por ejemplo:

Ventas registradas:  8
Facturación:          $96.880
Unidades vendidas:    17

Los mismos valores son utilizados por los análisis de ventas, productos y Dashboard.

También se verificó que los valores de stock mostrados por el Dashboard coincidan con el endpoint específico de stock financiero.

Esto permite mantener una única fuente de verdad para los cálculos.


22. PRUEBAS CON POSTMAN

Las rutas financieras fueron organizadas dentro de la colección:

11 - Finanzas

Estructura:

11 - Finanzas
├── Rentabilidad Caja
├── Caja
├── Ventas
├── Evolución mes a mes
├── Top de productos
├── Estadísticas proveedores
├── Top productos comprados
├── Clientes
├── Stock financiero
└── Dashboard

Para las funcionalidades principales se realizaron pruebas utilizando:

- Hoy.
- Semana.
- Mes.
- Año.
- Personalizado.

Los endpoints respondieron correctamente durante las pruebas realizadas.


23. CONSIDERACIONES SOBRE DATOS HISTÓRICOS

Durante las pruebas se detectaron algunos registros antiguos generados antes de implementar determinadas reglas actuales del sistema.

Entre ellos:

- Ventas antiguas sin costo_unitario.
- Una compra histórica con total registrado pero sin detalles asociados.
- Registros antiguos con diferencias en la escritura del estado.

Estos datos corresponden a pruebas realizadas durante etapas anteriores del desarrollo.

La lógica financiera actual no fue modificada para compensar artificialmente estos datos, ya que hacerlo podría introducir inconsistencias en operaciones futuras.


24. RESULTADO DE LA ENTREGA

Al finalizar esta entrega, el estado del módulo financiero es:

MÓDULO FINANCIERO
│
├── Rentabilidad             ✅
├── Caja                     ✅
├── Ventas                   ✅
│   └── Evolución temporal   ✅
├── Productos                ✅
│   └── Rankings             ✅
├── Proveedores              ✅
│   ├── Compras              ✅
│   ├── Ranking              ✅
│   ├── Deudas               ✅
│   ├── Productos comprados  ✅
│   └── Evolución costos     ✅
├── Clientes                 ✅
│   ├── Rankings             ✅
│   └── Cuentas por cobrar   ✅
├── Stock financiero         ✅
│   ├── Valorización         ✅
│   ├── Ganancia potencial   ✅
│   ├── Capital inmovilizado ✅
│   └── Rotación             ✅
└── Dashboard financiero     ✅


CONCLUSIÓN

Con esta entrega se considera finalizado el desarrollo funcional del Módulo Financiero.

El sistema no se limita a registrar operaciones comerciales, sino que utiliza la información generada por ventas, compras, clientes, proveedores y stock para producir indicadores que facilitan el control y la toma de decisiones del comercio.

El Dashboard financiero funciona como punto central de esta información y permitirá posteriormente desarrollar en React una interfaz visual con tarjetas, rankings, tablas y gráficos sin trasladar la lógica financiera al frontend.

ESTADO FINAL: MÓDULO FINANCIERO COMPLETO ✅

PRÓXIMA ETAPA:
Usuarios, roles, autenticación y permisos.