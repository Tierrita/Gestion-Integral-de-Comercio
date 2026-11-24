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
