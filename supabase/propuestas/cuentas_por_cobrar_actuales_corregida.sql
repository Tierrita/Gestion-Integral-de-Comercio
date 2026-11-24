-- Corregir la RPC que consume la tarjeta del frontend. Alineada con dashboard.
CREATE OR REPLACE FUNCTION public.obtener_cuentas_por_cobrar_actuales(p_id_comercio integer)
 RETURNS jsonb
 LANGUAGE sql
 STABLE
 SET search_path TO ''
AS $function$
with clientes_comercio as (
 select id_cliente from public.clientes where id_comercio=p_id_comercio and numero_cliente is distinct from 1
), ventas_cliente as (
 select v.id_cliente,sum(v.total) total from public.ventas v join clientes_comercio cl on cl.id_cliente=v.id_cliente
 where v.id_comercio=p_id_comercio and v.estado='COMPLETADA' and v.metodo_pago='CUENTA_CORRIENTE' group by v.id_cliente
), cobros_cliente as (
 select c.id_cliente,sum(c.monto) total from public.cobros c join clientes_comercio cl on cl.id_cliente=c.id_cliente
 where c.id_comercio=p_id_comercio and upper(c.estado)='COMPLETADO' group by c.id_cliente
), saldos as (
 select coalesce(v.total,0)-coalesce(c.total,0) saldo from clientes_comercio cl left join ventas_cliente v using(id_cliente) left join cobros_cliente c using(id_cliente)
)
select jsonb_build_object('total_por_cobrar',coalesce(sum(greatest(saldo,0)),0),'cantidad_clientes_con_deuda',count(*) filter(where saldo>0)) from saldos
$function$
;
REVOKE ALL ON FUNCTION public.obtener_cuentas_por_cobrar_actuales(integer) FROM PUBLIC,anon,authenticated;
GRANT EXECUTE ON FUNCTION public.obtener_cuentas_por_cobrar_actuales(integer) TO service_role;
