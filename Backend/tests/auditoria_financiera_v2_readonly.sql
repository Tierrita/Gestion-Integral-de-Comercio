-- Auditoría de integridad financiera V2 (SOLO LECTURA).
-- Ejecutar en Supabase SQL Editor. No modifica registros.
WITH cobro_mov AS (
 SELECT c.id_cobro, c.estado,
   count(m.id_movimiento) FILTER (WHERE m.tipo_movimiento = 'COBRO') AS registros,
   count(m.id_movimiento) FILTER (WHERE m.tipo_movimiento = 'ANULACION_COBRO') AS anulaciones
 FROM public.cobros c
 LEFT JOIN public.movimientos_financieros m
   ON m.tipo_origen = 'COBRO' AND m.id_origen = c.id_cobro
 GROUP BY c.id_cobro, c.estado
)
SELECT count(*) AS cobros_total,
 count(*) FILTER (WHERE registros <> 1) AS cobros_sin_unico_registro,
 count(*) FILTER (WHERE estado = 'ANULADO' AND anulaciones <> 1) AS anulados_sin_unica_reversion,
 count(*) FILTER (WHERE estado = 'COMPLETADO' AND anulaciones <> 0) AS completos_con_reversion
FROM cobro_mov;

SELECT
 (SELECT count(*) FROM public.pagos_proveedor) AS pagos_proveedor_total,
 (SELECT count(*) FROM public.movimientos_financieros
   WHERE tipo_origen ILIKE '%PAGO%PROVEEDOR%'
      OR tipo_movimiento ILIKE '%PAGO%PROVEEDOR%') AS movimientos_etiquetados_como_pago_proveedor,
 (SELECT count(*) FROM public.cobros c
   JOIN public.clientes cl ON cl.id_cliente=c.id_cliente
   JOIN public.cuentas cu ON cu.id_cuenta=c.id_cuenta
   WHERE c.id_comercio<>cl.id_comercio OR c.id_comercio<>cu.id_comercio) AS cobros_comercio_inconsistente,
 (SELECT count(*) FROM public.pagos_proveedor pp
   JOIN public.proveedores p ON p.id_proveedor=pp.id_proveedor
   JOIN public.usuarios u ON u.id_usuario=pp.id_usuario
   WHERE p.id_comercio<>u.id_comercio) AS pagos_usuario_otro_comercio;

-- LIMITACIONES:
-- 1. Los movimientos identificados por etiqueta no prueban causalidad histórica.
-- 2. Los conteos no prueban ausencia de carreras concurrentes.
-- 3. Para pruebas de escritura y concurrencia usar una base aislada.
