create or replace function public.registrar_ajuste_manual_stock(
    p_id_producto integer, p_id_comercio integer, p_id_usuario integer,
    p_stock_anterior integer, p_stock_nuevo integer, p_cantidad integer,
    p_tipo text, p_observaciones text
)
returns jsonb
language plpgsql
security invoker
set search_path = ''
as $$
declare
    producto_nombre text;
begin
    update public.productos
    set stock = p_stock_nuevo
    where id_producto = p_id_producto
      and id_comercio = p_id_comercio
      and estado is true
      and stock = p_stock_anterior
    returning nombre_producto into producto_nombre;

    if not found then
        return null;
    end if;

    insert into public.historial_movimiento (
        id_producto, id_usuario, tipo_movimiento, cantidad,
        stock_anterior, stock_nuevo, observaciones
    ) values (
        p_id_producto, p_id_usuario, p_tipo, p_cantidad,
        p_stock_anterior, p_stock_nuevo, p_observaciones
    );

    return jsonb_build_object(
        'id_producto', p_id_producto, 'nombre_producto', producto_nombre,
        'stock_anterior', p_stock_anterior, 'stock_nuevo', p_stock_nuevo,
        'cantidad', p_cantidad, 'tipo_movimiento', p_tipo
    );
end;
$$;

revoke all on function public.registrar_ajuste_manual_stock(integer, integer, integer, integer, integer, integer, text, text)
    from public, anon, authenticated;
grant execute on function public.registrar_ajuste_manual_stock(integer, integer, integer, integer, integer, integer, text, text)
    to service_role;
