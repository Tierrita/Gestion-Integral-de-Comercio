-- Ajuste de stock e historial en una unica transaccion.
-- Invocacion exclusiva desde Flask con clave secreta del backend.
create or replace function public.ajustar_stock_atomico(
  p_id_producto integer,
  p_id_comercio integer,
  p_id_usuario integer,
  p_cantidad numeric,
  p_tipo_ajuste text
)
returns jsonb
language plpgsql
security invoker
set search_path = ''
as $$
declare
  v_producto public.productos%rowtype;
  v_stock_nuevo numeric(12,3);
  v_tipo_movimiento text;
begin
  if p_id_producto is null or p_id_comercio is null or p_id_usuario is null then
    raise exception 'Identificadores obligatorios';
  end if;
  if not exists (
    select 1 from public.usuarios
    where id_usuario = p_id_usuario and id_comercio = p_id_comercio and estado = true
  ) then
    raise exception 'Usuario no autorizado para este comercio';
  end if;
  if p_tipo_ajuste is null or p_tipo_ajuste not in ('AUMENTAR', 'DISMINUIR') then
    raise exception 'Tipo de ajuste inválido. Debe ser AUMENTAR o DISMINUIR';
  end if;
  if p_cantidad is null or p_cantidad <= 0 or p_cantidad > 999999999
     or p_cantidad <> trunc(p_cantidad, 3) then
    raise exception 'Cantidad inválida';
  end if;

  select * into v_producto
  from public.productos
  where id_producto = p_id_producto and id_comercio = p_id_comercio
  for update;

  if not found then
    raise exception 'Producto no encontrado';
  end if;
  if not v_producto.estado then
    raise exception 'No se puede ajustar el stock de un producto inactivo';
  end if;
  if v_producto.unidad_de_medida not in ('UNIDAD', 'KG') then
    raise exception 'La unidad de medida debe ser UNIDAD o KG';
  end if;
  if v_producto.unidad_de_medida = 'UNIDAD' and p_cantidad <> trunc(p_cantidad) then
    raise exception 'La cantidad en unidades debe ser entera';
  end if;

  if p_tipo_ajuste = 'AUMENTAR' then
    v_stock_nuevo := v_producto.stock + p_cantidad;
    v_tipo_movimiento := 'AJUSTE_ENTRADA';
  else
    v_stock_nuevo := v_producto.stock - p_cantidad;
    v_tipo_movimiento := 'AJUSTE_SALIDA';
  end if;
  if v_stock_nuevo < 0 then
    raise exception 'El stock no puede quedar negativo';
  end if;

  update public.productos
  set stock = v_stock_nuevo
  where id_producto = p_id_producto and id_comercio = p_id_comercio;

  insert into public.historial_movimiento
    (id_producto, id_usuario, tipo_movimiento, cantidad,
     stock_anterior, stock_nuevo, observaciones)
  values
    (p_id_producto, p_id_usuario, v_tipo_movimiento, p_cantidad,
     v_producto.stock, v_stock_nuevo, 'Ajuste manual de stock');

  return jsonb_build_object(
    'id_producto', p_id_producto,
    'nombre_producto', v_producto.nombre_producto,
    'stock_anterior', v_producto.stock,
    'stock_nuevo', v_stock_nuevo,
    'cantidad', p_cantidad,
    'tipo_movimiento', v_tipo_movimiento
  );
end;
$$;

revoke all on function public.ajustar_stock_atomico(integer,integer,integer,numeric,text)
from public, anon, authenticated;
grant execute on function public.ajustar_stock_atomico(integer,integer,integer,numeric,text)
to service_role;