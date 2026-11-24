-- PROPUESTA / NO APLICADA: revisión de RPC dashboard para auditoría.
-- Generada a partir de la instantánea versionada, cotejada con pg_get_functiondef.
-- NO ejecutar en producción hasta completar pruebas de regresión y respaldo.
-- Deuda actual: ventas COMPLETADA a CUENTA_CORRIENTE menos cobros COMPLETADO,
-- para todos los clientes del comercio excepto CLIENTE GENERAL (numero_cliente=1).
-- Se mantiene criterio de sumar solo saldos positivos para Total por cobrar.
-- Cantidades stock/KG: preservar decimales en valores y rankings.
-- NOTA: 'unidades_en_stock' mezcla UNIDAD y KG como en contrato previo;
-- requiere definición de UI en trabajo posterior.

CREATE OR REPLACE FUNCTION public.obtener_dashboard_estadisticas(p_id_comercio integer, p_desde timestamp with time zone, p_hasta timestamp with time zone)
 RETURNS jsonb
 LANGUAGE sql
 STABLE
 SET search_path TO ''
AS $function$
with
v as materialized (select id_venta,id_cliente,total from public.ventas where id_comercio=p_id_comercio and estado='COMPLETADA' and fecha_venta>=p_desde and fecha_venta<p_hasta),
d as materialized (select dv.id_producto,dv.cantidad,dv.subtotal,dv.costo_unitario from public.detalle_venta dv join v on v.id_venta=dv.id_venta),
v_tot as (select coalesce(sum(total),0) facturacion,count(*) cantidad from v),
d_tot as (select coalesce(sum(cantidad),0) unidades,coalesce(sum(cantidad*costo_unitario),0) costo,count(*) filter(where costo_unitario is null) faltantes from d),
mov as (select coalesce(sum(m.monto) filter(where m.tipo_movimiento in ('VENTA','COBRO','AJUSTE_ENTRADA')),0) entradas,coalesce(sum(m.monto) filter(where m.tipo_movimiento in ('ANULACION_VENTA','ANULACION_COBRO','AJUSTE_SALIDA')),0) salidas from public.movimientos_financieros m join public.cuentas c on c.id_cuenta=m.id_cuenta where c.id_comercio=p_id_comercio and m.fecha_movimiento>=p_desde and m.fecha_movimiento<p_hasta),
cp as (select coalesce(sum(total_compra),0) total from public.compras where id_comercio=p_id_comercio and estado='COMPLETADA' and fecha_compra>=p_desde and fecha_compra<p_hasta),
stock as (select coalesce(sum(stock) filter(where stock>0),0) unidades,coalesce(sum(stock*coalesce(precio_costo,0)) filter(where stock>0),0) costo,coalesce(sum(stock*coalesce(precio_venta,0)) filter(where stock>0),0) venta,coalesce(sum(stock*coalesce(precio_costo,0)) filter(where stock>0 and not exists(select 1 from d where d.id_producto=productos.id_producto and d.cantidad<>0)),0) inmovilizado from public.productos where id_comercio=p_id_comercio),
cli_ventas as (select id_cliente,coalesce(sum(total),0) total from public.ventas where id_comercio=p_id_comercio and estado='COMPLETADA' and metodo_pago='CUENTA_CORRIENTE' group by id_cliente),
cli_cobros as (select id_cliente,coalesce(sum(monto),0) total from public.cobros where id_comercio=p_id_comercio and estado='COMPLETADO' group by id_cliente),
cli_saldos as (select c.id_cliente,coalesce(cv.total,0)-coalesce(cc.total,0) saldo from public.clientes c left join cli_ventas cv on cv.id_cliente=c.id_cliente left join cli_cobros cc on cc.id_cliente=c.id_cliente where c.id_comercio=p_id_comercio and c.numero_cliente<>1),
cli_tot as (select coalesce(sum(saldo) filter(where saldo>0),0) deuda,count(*) filter(where saldo>0) cantidad from cli_saldos),
prov_compras as (select id_proveedor,coalesce(sum(total_compra),0) total from public.compras where id_comercio=p_id_comercio and estado<>'ANULADA' group by id_proveedor),
prov_pagos as (select pp.id_proveedor,coalesce(sum(pp.monto),0) total from public.pagos_proveedor pp join public.proveedores p on p.id_proveedor=pp.id_proveedor where p.id_comercio=p_id_comercio and pp.estado='COMPLETADO' group by pp.id_proveedor),
prov_tot as (select coalesce(sum(greatest(coalesce(pc.total,0)-coalesce(pg.total,0),0)),0) deuda from public.proveedores p left join prov_compras pc on pc.id_proveedor=p.id_proveedor left join prov_pagos pg on pg.id_proveedor=p.id_proveedor where p.id_comercio=p_id_comercio),
top_producto as (select jsonb_build_object('id_producto',p.id_producto,'nombre_producto',p.nombre_producto,'cantidad_vendida',sum(d.cantidad),'facturacion',round(sum(d.subtotal),2),'costo_vendido',case when count(*) filter(where d.costo_unitario is null)=0 then round(sum(d.cantidad*d.costo_unitario),2) end,'ganancia_bruta',case when count(*) filter(where d.costo_unitario is null)=0 then round(sum(d.subtotal)-sum(d.cantidad*d.costo_unitario),2) end,'margen_bruto',case when count(*) filter(where d.costo_unitario is null)=0 then case when sum(d.subtotal)>0 then round((sum(d.subtotal)-sum(d.cantidad*d.costo_unitario))/sum(d.subtotal)*100,2) else 0 end end,'rentabilidad_calculable',count(*) filter(where d.costo_unitario is null)=0) obj from d join public.productos p on p.id_producto=d.id_producto and p.id_comercio=p_id_comercio group by p.id_producto,p.nombre_producto order by sum(d.cantidad) desc,p.id_producto limit 1),
top_cliente as (select jsonb_build_object('id_cliente',c.id_cliente,'nombre_completo',c.nombre_completo,'facturacion',round(sum(v.total),2),'cantidad_compras',count(*),'ticket_promedio',round(sum(v.total)/count(*),2)) obj from v join public.clientes c on c.id_cliente=v.id_cliente and c.id_comercio=p_id_comercio group by c.id_cliente,c.nombre_completo order by sum(v.total) desc,c.id_cliente limit 1),
top_proveedor as (select jsonb_build_object('id_proveedor',p.id_proveedor,'nombre_proveedor',p.nombre_proveedor,'total_comprado',round(sum(c.total_compra),2),'cantidad_compras',count(*)) obj from public.compras c join public.proveedores p on p.id_proveedor=c.id_proveedor and p.id_comercio=p_id_comercio where c.id_comercio=p_id_comercio and c.estado='COMPLETADA' and c.fecha_compra>=p_desde and c.fecha_compra<p_hasta group by p.id_proveedor,p.nombre_proveedor order by sum(c.total_compra) desc,p.id_proveedor limit 1)
select jsonb_build_object(
'ventas',jsonb_build_object('facturacion',round(vt.facturacion,2),'cantidad_ventas',vt.cantidad,'ticket_promedio',case when vt.cantidad>0 then round(vt.facturacion/vt.cantidad,2) else 0 end,'unidades_vendidas',dt.unidades),
'rentabilidad',jsonb_build_object('costo_vendido',case when dt.faltantes=0 then round(dt.costo,2) end,'ganancia_bruta',case when dt.faltantes=0 then round(vt.facturacion-dt.costo,2) end,'margen_bruto',case when dt.faltantes=0 then case when vt.facturacion>0 then round((vt.facturacion-dt.costo)/vt.facturacion*100,2) else 0 end end,'rentabilidad_calculable',dt.faltantes=0,'detalles_sin_costo_historico',dt.faltantes),
'caja',jsonb_build_object('total_entradas',round(m.entradas,2),'total_salidas',round(m.salidas,2),'saldo_neto',round(m.entradas-m.salidas,2)),
'clientes',jsonb_build_object('total_por_cobrar',round(ct.deuda,2),'cantidad_clientes_con_deuda',ct.cantidad),
'proveedores',jsonb_build_object('total_comprado',round(cp.total,2),'deuda_total_proveedores',round(pt.deuda,2)),
'stock',jsonb_build_object('unidades_en_stock',s.unidades,'valor_stock_costo',round(s.costo,2),'valor_stock_venta',round(s.venta,2),'ganancia_potencial',round(s.venta-s.costo,2),'capital_inmovilizado_sin_ventas',round(s.inmovilizado,2)),
'rankings',jsonb_build_object('producto_mas_vendido',(select obj from top_producto),'mejor_cliente',(select obj from top_cliente),'principal_proveedor',(select obj from top_proveedor))
)
from v_tot vt cross join d_tot dt cross join mov m cross join cp cross join stock s cross join cli_tot ct cross join prov_tot pt
$function$
;

REVOKE ALL ON FUNCTION public.obtener_dashboard_estadisticas(integer, timestamptz, timestamptz) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.obtener_dashboard_estadisticas(integer, timestamptz, timestamptz) FROM anon, authenticated;
GRANT EXECUTE ON FUNCTION public.obtener_dashboard_estadisticas(integer, timestamptz, timestamptz) TO service_role;
