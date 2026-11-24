# AIOnix — Anulación independiente de pagos de ventas (diseño previo a implementación)

Estado: diseño técnico, **no habilitado**. Rama: feat/cobros-v1.

## Objetivo
Anular el ingreso inicial de una venta pagada sin anular la venta ni devolver stock. La venta sigue COMPLETADA, el pago queda revertido y el importe pasa a deuda cobrable.

## Hallazgos en esquema real (2026-11-23)
- `ventas` tiene `total`, `metodo_pago`, `estado`, pero no `saldo_pendiente` ni entidad `pagos_venta`.
- `movimientos_financieros` restringe `tipo_movimiento` a VENTA, ANULACION_VENTA, COBRO, ANULACION_COBRO, AJUSTE_ENTRADA, AJUSTE_SALIDA.
- `anular_venta_completa` invoca `anular_ingreso_venta` para ventas EFECTIVO/TRANSFERENCIA, y esta función solo detecta ANULACION_VENTA como reversión previa.
- `cobro_service._calcular_saldo` suma solo ventas a CUENTA_CORRIENTE y resta todos los cobros completados.
- El historial de clientes filtra movimientos VENTA/ANULACION_VENTA y COBRO/ANULACION_COBRO.
- `registrar_cobro` crea un cobro por cliente sin asociarlo a una venta concreta.

## Diseño recomendado
1. Introducir entidad auditable `pagos_venta` (id, id_venta, id_comercio, id_cuenta, monto, estado, origen, usuario, fechas y motivo de anulación) con restricciones y unicidad del pago inicial por venta. No inferir pagos anulados del campo `metodo_pago`.
2. Crear una migración de conciliación que represente los ingresos de ventas históricas en `pagos_venta` sin volver a acreditar cuentas. Validar importes y movimientos originales y revertidos; nunca sobrescribir saldos históricos.
3. Crear RPC transaccional `anular_pago_venta` que valide propietario activo, comercio, venta COMPLETADA, pago vigente, cuenta del comercio, fondos suficientes y motivo; bloquee venta/pago/cuenta, registre reversión una sola vez y marque pago anulado. No tocar `detalle_venta` ni `productos`.
4. Cambiar cálculo de deuda a ventas COMPLETADAS menos pagos vigentes asociados menos cobros completados, respetando créditos/saldos a favor y ventas CUENTA_CORRIENTE. La actualización debe ser consistente en listado y detalle.
5. Adaptar `anular_venta_completa` para no intentar revertir un pago previamente anulado, y definir qué ocurre si existen cobros posteriores asociados a esa venta. No permitir dobles reversiones.
6. Exponer endpoint Flask protegido con `solo_propietario`, validación de comercio desde JWT y motivo obligatorio. Nunca aceptar id_comercio/id_usuario del frontend.
7. Mostrar `Anular pago` solo en pagos vigentes; confirmación con importe, cuenta y motivo. Refrescar caja, deuda e historial al confirmar.
8. Pruebas: anulación única, doble intento, concurrencia, falta de fondos, otro comercio, empleado sin permiso, venta anulada, cobros posteriores, venta crédito, reversión de venta completa tras anular pago, sin alteración de stock y conciliación contable.

## Bloqueos antes de activar
- Revisar políticas RLS/EXECUTE de RPC privilegiadas; no publicar funciones mutadoras que acepten IDs de usuario sin autorización robusta.
- Definir política de anulación de venta completa cuando existen cobros posteriores y anticipos.
- Crear y probar migración en entorno aislado antes de aplicarla a la base con operaciones reales.

**No se modificó la base de datos ni la venta #29 con este documento.**
