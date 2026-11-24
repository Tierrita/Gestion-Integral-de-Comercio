# Auditoría de integridad financiera y stock — AIOnix

Fecha: 2026-11-24. Rama: audit/integridad-financiera-stock. Alcance: consultas SQL de solo lectura a Supabase y revisión de GitHub main. **No se aplicaron migraciones ni cambios de datos.**

## Hallazgos

### A-01 — truncamiento de cantidades en dashboard (confirmado)
La función desplegada public.obtener_dashboard_estadisticas aplica trunc(stock) a unidades y valores de inventario, y trunc(d.cantidad) al ranking y costo de producto más vendido. Los productos KG permiten tres decimales en public.registrar_venta_transaccional y productos.stock es numeric.

Consulta agregada de control sobre productos: 2 productos con stock positivo fraccionario; valor a costo calculado con stock real: 363763492.94400; con trunc(stock): 363757488.00; diferencia: 6004.94400 ARS. Estos importes son de toda la base consultada, no de un comercio ni período específico; no deben presentarse como diferencia de un dashboard individual. El elevado valor total requiere inspección de datos de prueba/atípicos.

### A-02 — ventas no financiadas incluidas en deuda (confirmado en SQL)
La RPC usa cli_ventas sum(total) donde estado<>'ANULADA' sin filtrar metodo_pago='CUENTA_CORRIENTE'. Cobros completados se descuentan. En cambio el servicio de saldos de clientes calcula deuda por ventas a cuenta corriente.

Control agregado: 7 clientes con diferencias entre ambos criterios, por 3593533.36 ARS en ventas no CC incluidas. La cifra es una diferencia entre criterios agregados, **no** una deuda confirmada de un comercio ni un ajuste que deba contabilizarse. La RPC además filtra clientes con actividad en el período, por lo que el resultado real de un período depende de ese filtro.

### A-03 — alcance temporal de deuda (pendiente de decisión)
La RPC solo incluye en cli_saldos clientes presentes en ventas del período consultado (exists select 1 from v). Una deuda histórica de un cliente sin compras recientes puede no aparecer en el dashboard del período. Definir si el KPI debe mostrar deuda actual total o deuda atribuible a clientes activos en el período.

### A-04 — rankings de KG (confirmado)
El ranking top_producto usa sum(trunc(d.cantidad)) y costo sum(trunc(d.cantidad)*d.costo_unitario), pudiendo subestimar cantidades/costos de productos KG. Probar rankings con cantidades fraccionarias.

## Verificaciones realizadas
- Proyecto Supabase activo; funciones SQL inspeccionadas mediante pg_get_functiondef.
- Columnas stock, precio_costo, precio_venta, monto y totales son numeric.
- 22 productos en la base: 3 KG y 19 UNIDAD.
- Conteos globales: 34 ventas, 29 compras, 19 cobros y 8 pagos a proveedores. Son metadatos agregados, no validación transaccional.
- Rama de auditoría creada desde main. Ningún cambio en producción.

## Próximos pasos
1. Definir contrato exacto del KPI de deuda: saldo actual total independiente del período versus métrica del período.
2. Comparar por comercio y con el servicio de saldos, sin revelar datos de clientes.
3. Preparar pruebas automáticas para 1.750 KG, venta CC, venta efectivo, cobro parcial, anulación y ranking.
4. Proponer corrección versionada de la RPC en rama, revisando GRANT/REVOKE y dependencias antes de aplicar.
5. Validar en entorno de pruebas y ejecutar regresión; recién entonces considerar merge y despliegue.

## Validación adicional (2026-11-24) — consultas SELECT sin aplicar función

Se evaluó el cuerpo SQL de la propuesta como subconsulta SELECT contra datos existentes, comparando su JSON con la RPC desplegada. **Esto no instaló la función propuesta ni escribió datos.**

- Comercio 1, noviembre: deuda actual RPC 14.924.199,00; propuesta 12.684.199,00. Stock valor costo actual 250.437.488,00; propuesta 250.443.492,94. Unidades mezcladas actual 22.561; propuesta 22.562,434.
- Comercio 1, octubre: deuda RPC 1.419.999,00 (2 clientes); propuesta 12.684.199,00 (5 clientes). Confirma que la propuesta mantiene deuda actual sin depender del período. El capital inmovilizado sí varía por período porque su definición depende de ventas del rango.
- Comercio 3, noviembre: deuda RPC 1.500.000,03 (2 clientes); propuesta 166.666,67 (1 cliente).
- Se mantuvieron sin diferencias en estas comparaciones los otros campos JSON no listados.
- Se ejecutaron 7/7 casos SQL sintéticos de solo lectura, todos true.

**Limitación:** esta comparación evalúa el SELECT propuesto, pero no valida la creación de función, sus permisos, rendimiento, seguridad o pruebas transaccionales end-to-end. Se necesita un entorno aislado para cerrar la auditoría. No desplegar todavía.

**Pendiente de autorización:** la creación de rama Supabase solicitó confirmación de costos; no se creó ninguna rama de base de datos.

## Verificaciones de consistencia adicionales

Se consultaron registros existentes de los comercios 1 y 3 (solo lectura):

- Stock negativo: 0 en ambos comercios.
- Stock nulo: 0 en ambos comercios.
- Productos UNIDAD con stock fraccionario: 0 en ambos comercios.
- Ventas que referencian cliente de otro comercio: 0.
- Cobros que referencian cliente de otro comercio: 0.
- Compras que referencian proveedor de otro comercio: 0.
- Saldos recalculados con el criterio aprobado: comercio 1: 5 deudores, 2 saldos a favor, total por cobrar 12.684.199,00; comercio 3: 1 deudor, 0 saldos a favor, total por cobrar 166.666,67.

**Interpretación:** no se encontraron inconsistencias en estas comprobaciones de datos; esto no demuestra por sí solo que todos los endpoints estén libres de fallos de autorización.

**Estado:** propuesta SQL y tests versionados; aún no desplegada. Sigue pendiente validación completa de permisos, rendimiento y regresión de UI. La instrucción anterior de no modificar producción sigue respetada.
