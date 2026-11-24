# Cierre Cobros y Pagos V2 — plan de integración

## Decisiones invariables
- Cobros de clientes: afectan la cuenta y crean movimiento financiero.
- Pagos a proveedores: afectan únicamente la deuda del proveedor; nunca cuentas ni movimientos financieros.
- Se reutiliza el sistema existente de autenticación, roles y permisos.
- No usar datos comerciales reales para las pruebas de escritura.

## Auditoría realizada
- Cobros: las RPC registrar_cobro y anular_cobro utilizan bloqueo FOR UPDATE sobre cuentas; anular_cobro bloquea también el cobro y rechaza ANULADO.
- Pagos: actualización de anulación condicionada a estado COMPLETADO y proveedor previamente validado en el comercio.
- Los importes individuales se validan frente a NUMERIC(12,2).
- El límite del saldo acumulado queda protegido por la columna NUMERIC(12,2), pero se debe verificar rollback transaccional.
- Las pruebas existentes son unitarias con mocks: no demuestran integración real ni concurrencia.

## Batería única de integración (entorno aislado)
1. Crear datos de prueba para dos comercios, cada uno con cliente, proveedor, cuenta y usuario de prueba.
2. Registrar cobro de 15.25: verificar cobro COMPLETADO, saldo de cuenta +15.25 y exactamente un movimiento COBRO.
3. Anular cobro: verificar ANULADO, saldo restaurado y exactamente un movimiento ANULACION_COBRO.
4. Reintentar anulación: debe rechazarse sin modificar saldo ni agregar movimiento.
5. Ejecutar dos anulaciones concurrentes del mismo cobro: solo una debe tener éxito y generar un movimiento de reversión.
6. Forzar error de límite NUMERIC(12,2) en saldo de cuenta: verificar que no persistan cobro ni movimiento.
7. Registrar pago a proveedor: deuda disminuye por el importe; saldos de cuentas y movimientos financieros sin cambios.
8. Anular pago proveedor y reintentar: deuda se restaura una sola vez, sin cambios en cuentas.
9. Verificar aislamiento entre comercios con identificadores del otro comercio en lecturas y escrituras.
10. Validar casos de anticipos y pagos parciales en la interfaz y API.

## Criterio de cierre
- Todas las pruebas unitarias y de integración aprobadas.
- No hay cambios inesperados en cuentas ni movimientos financieros.
- Ninguna prueba altera datos comerciales reales.
- Ejecutar lint/build frontend y suite backend completa.
- Solo después evaluar merge a main.
