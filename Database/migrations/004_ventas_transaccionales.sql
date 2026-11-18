-- Gestion Integral de Comercio - Migracion 004
-- Registro atomico de ventas. No registra ventas al instalarse.
-- Requiere funciones existentes obtener_siguiente_numero y registrar_ingreso_venta.
BEGIN;

-- Impide numeros locales duplicados. Si existen duplicados, la migracion se detiene.
CREATE UNIQUE INDEX IF NOT EXISTS ux_ventas_comercio_numero
  ON public.ventas (id_comercio, numero_venta);

CREATE OR REPLACE FUNCTION public.registrar_venta_transaccional(
  p_id_comercio integer,
  p_id_usuario integer,
  p_id_cliente integer,
  p_metodo_pago text,
  p_id_cuenta integer,
  p_productos jsonb,
  p_observaciones text DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = ''
AS $function$
DECLARE
  v_metodo text;
  v_item jsonb;
  v_ids integer[] := ARRAY[]::integer[];
  v_id integer;
  v_producto public.productos%ROWTYPE;
  v_cantidad numeric;
  v_precio numeric;
  v_costo numeric;
  v_subtotal numeric;
  v_total numeric := 0;
  v_numero integer;
  v_venta public.ventas%ROWTYPE;
  v_detalle public.detalle_venta%ROWTYPE;
  v_anterior numeric;
  v_nuevo numeric;
  v_detalles jsonb := '[]'::jsonb;
  v_actualizados jsonb := '[]'::jsonb;
  v_movimiento jsonb := NULL;
BEGIN
  IF p_id_comercio IS NULL OR p_id_comercio <= 0
     OR p_id_usuario IS NULL OR p_id_usuario <= 0
     OR p_id_cliente IS NULL OR p_id_cliente <= 0 THEN
    RAISE EXCEPTION 'Comercio, usuario y cliente son obligatorios';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM public.usuarios u
    JOIN public.comercios c ON c.id_comercio = u.id_comercio
    WHERE u.id_usuario = p_id_usuario AND u.id_comercio = p_id_comercio
      AND u.estado IS TRUE AND c.estado IS TRUE
  ) THEN
    RAISE EXCEPTION 'Usuario o comercio invalido o inactivo';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM public.clientes c
    WHERE c.id_cliente = p_id_cliente AND c.id_comercio = p_id_comercio
      AND c.estado IS TRUE
  ) THEN
    RAISE EXCEPTION 'Cliente inexistente o inactivo en este comercio';
  END IF;

  v_metodo := upper(btrim(coalesce(p_metodo_pago, '')));
  IF v_metodo NOT IN ('EFECTIVO', 'TRANSFERENCIA', 'CUENTA_CORRIENTE') THEN
    RAISE EXCEPTION 'Metodo de pago no admitido';
  END IF;

  IF v_metodo <> 'CUENTA_CORRIENTE' THEN
    IF p_id_cuenta IS NULL OR p_id_cuenta <= 0 THEN
      RAISE EXCEPTION 'La cuenta financiera es obligatoria';
    END IF;
    IF NOT EXISTS (
      SELECT 1 FROM public.cuentas c
      WHERE c.id_cuenta = p_id_cuenta AND c.id_comercio = p_id_comercio
        AND c.estado IS TRUE
    ) THEN
      RAISE EXCEPTION 'Cuenta financiera inexistente o inactiva en este comercio';
    END IF;
  END IF;

  IF p_productos IS NULL OR jsonb_typeof(p_productos) <> 'array'
     OR jsonb_array_length(p_productos) = 0 THEN
    RAISE EXCEPTION 'La venta debe contener al menos un producto';
  END IF;

  -- Validar IDs antes de tomar locks; no se admiten duplicados.
  FOR v_item IN SELECT value FROM jsonb_array_elements(p_productos) LOOP
    IF jsonb_typeof(v_item) <> 'object'
       OR jsonb_typeof(v_item->'id_producto') <> 'number'
       OR (v_item->>'id_producto') !~ '^[0-9]+$' THEN
      RAISE EXCEPTION 'ID de producto invalido';
    END IF;
    v_id := (v_item->>'id_producto')::integer;
    IF v_id <= 0 OR v_id = ANY(v_ids) THEN
      RAISE EXCEPTION 'Producto duplicado o invalido: %', v_id;
    END IF;
    v_ids := array_append(v_ids, v_id);
  END LOOP;

  -- Locks en orden estable: evita que dos ventas gasten el mismo stock.
  FOR v_id IN SELECT id FROM unnest(v_ids) AS t(id) ORDER BY id LOOP
    PERFORM 1 FROM public.productos
    WHERE id_producto = v_id AND id_comercio = p_id_comercio FOR UPDATE;
    IF NOT FOUND THEN
      RAISE EXCEPTION 'Producto % no pertenece al comercio', v_id;
    END IF;
  END LOOP;

  -- Prevalidar todo y calcular importes desde los precios de la BD.
  FOR v_item IN SELECT value FROM jsonb_array_elements(p_productos) LOOP
    v_id := (v_item->>'id_producto')::integer;
    SELECT * INTO STRICT v_producto FROM public.productos
      WHERE id_producto = v_id AND id_comercio = p_id_comercio;
    IF v_producto.estado IS DISTINCT FROM TRUE THEN
      RAISE EXCEPTION 'Producto % inactivo', v_id;
    END IF;
    IF jsonb_typeof(v_item->'cantidad') <> 'number' THEN
      RAISE EXCEPTION 'Cantidad invalida para producto %', v_id;
    END IF;
    v_cantidad := (v_item->>'cantidad')::numeric;
    IF v_cantidad <= 0 OR v_cantidad > 999999999.999 THEN
      RAISE EXCEPTION 'Cantidad fuera de rango para producto %', v_id;
    END IF;
    CASE upper(btrim(v_producto.unidad_de_medida))
      WHEN 'UNIDAD' THEN
        IF v_cantidad <> trunc(v_cantidad) THEN
          RAISE EXCEPTION 'Producto % requiere unidades enteras', v_id;
        END IF;
      WHEN 'KG' THEN
        IF v_cantidad <> round(v_cantidad, 3) THEN
          RAISE EXCEPTION 'Producto % admite hasta 3 decimales', v_id;
        END IF;
      ELSE RAISE EXCEPTION 'Unidad de medida invalida para producto %', v_id;
    END CASE;
    IF v_producto.stock IS NULL OR v_producto.stock < v_cantidad THEN
      RAISE EXCEPTION 'Stock insuficiente para producto %', v_id;
    END IF;
    v_precio := v_producto.precio_venta;
    v_costo := v_producto.precio_costo;
    IF v_precio IS NULL OR v_precio <= 0 OR v_costo IS NULL OR v_costo < 0 THEN
      RAISE EXCEPTION 'Precio o costo invalido para producto %', v_id;
    END IF;
    v_total := v_total + round(v_cantidad * v_precio, 2);
  END LOOP;
  v_total := round(v_total, 2);

  v_numero := public.obtener_siguiente_numero(p_id_comercio, 'VENTA'::varchar);
  INSERT INTO public.ventas
    (id_usuario, id_cliente, id_comercio, numero_venta, total,
     metodo_pago, estado, observaciones)
  VALUES
    (p_id_usuario, p_id_cliente, p_id_comercio, v_numero, v_total,
     v_metodo, 'COMPLETADA', p_observaciones)
  RETURNING * INTO v_venta;

  FOR v_item IN SELECT value FROM jsonb_array_elements(p_productos) LOOP
    v_id := (v_item->>'id_producto')::integer;
    v_cantidad := (v_item->>'cantidad')::numeric;
    SELECT * INTO STRICT v_producto FROM public.productos
      WHERE id_producto = v_id AND id_comercio = p_id_comercio;
    v_precio := v_producto.precio_venta;
    v_costo := v_producto.precio_costo;
    v_subtotal := round(v_cantidad * v_precio, 2);
    v_anterior := v_producto.stock;
    v_nuevo := v_anterior - v_cantidad;

    INSERT INTO public.detalle_venta
      (id_venta, id_producto, cantidad, precio_unitario, costo_unitario, subtotal)
    VALUES (v_venta.id_venta, v_id, v_cantidad, v_precio, v_costo, v_subtotal)
    RETURNING * INTO v_detalle;
    v_detalles := v_detalles || to_jsonb(v_detalle);

    UPDATE public.productos SET stock = v_nuevo
    WHERE id_producto = v_id AND id_comercio = p_id_comercio;

    INSERT INTO public.historial_movimiento
      (id_producto, id_usuario, tipo_movimiento, cantidad,
       stock_anterior, stock_nuevo, observaciones)
    VALUES
      (v_id, p_id_usuario, 'VENTA', v_cantidad, v_anterior, v_nuevo,
       'Venta #' || v_numero || ' (ID global ' || v_venta.id_venta || ')');

    v_actualizados := v_actualizados || jsonb_build_object(
      'id_producto', v_id, 'nombre_producto', v_producto.nombre_producto,
      'cantidad', v_cantidad, 'stock_anterior', v_anterior,
      'stock_actual', v_nuevo, 'precio_unitario', v_precio,
      'costo_unitario', v_costo);
  END LOOP;

  IF v_metodo <> 'CUENTA_CORRIENTE' THEN
    v_movimiento := to_jsonb(public.registrar_ingreso_venta(
      v_venta.id_venta, p_id_cuenta, p_id_usuario, v_total));
  END IF;

  RETURN jsonb_build_object(
    'venta', to_jsonb(v_venta),
    'detalles', v_detalles,
    'productos_actualizados', v_actualizados,
    'movimiento_financiero', v_movimiento);
END;
$function$;

COMMIT;
