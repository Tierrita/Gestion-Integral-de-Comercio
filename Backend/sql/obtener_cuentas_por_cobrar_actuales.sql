-- Saldo vigente por comercio, calculado en una sola consulta SQL.
-- Debe ejecutarse exclusivamente desde el backend con credenciales de servicio.
create or replace function public.obtener_cuentas_por_cobrar_actuales(p_id_comercio integer)
returns jsonb
language sql
stable
security invoker
set search_path = ''
as $$
  with clientes_comercio as (
    select id_cliente
    from public.clientes
    where id_comercio = p_id_comercio
      and numero_cliente is distinct from 1
  ),
  ventas_cliente as (
    select v.id_cliente, sum(v.total) as total
    from public.ventas v
    join clientes_comercio cl on cl.id_cliente = v.id_cliente
    where v.id_comercio = p_id_comercio
      and upper(v.estado) <> 'ANULADA'
    group by v.id_cliente
  ),
  cobros_cliente as (
    select c.id_cliente, sum(c.monto) as total
    from public.cobros c
    join clientes_comercio cl on cl.id_cliente = c.id_cliente
    where c.id_comercio = p_id_comercio
      and upper(c.estado) = 'COMPLETADO'
    group by c.id_cliente
  ),
  saldos as (
    select coalesce(v.total,0) - coalesce(c.total,0) as saldo
    from clientes_comercio cl
    left join ventas_cliente v using (id_cliente)
    left join cobros_cliente c using (id_cliente)
  )
  select jsonb_build_object(
    'total_por_cobrar', coalesce(sum(greatest(saldo,0)),0),
    'cantidad_clientes_con_deuda', count(*) filter (where saldo > 0)
  )
  from saldos;
$$;

revoke all on function public.obtener_cuentas_por_cobrar_actuales(integer) from public, anon, authenticated;
grant execute on function public.obtener_cuentas_por_cobrar_actuales(integer) to service_role;
