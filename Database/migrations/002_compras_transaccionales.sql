
-- ============================================================
-- MIGRACIÓN 002: REGISTRO TRANSACCIONAL DE COMPRAS
-- Gestión Integral de Comercio
--
-- Requisitos:
-- - Stock NUMERIC(12,3)
-- - Productos UNIDAD / KG
-- - Numeración local por comercio
-- - Índice único (id_comercio, numero_compra)
--
-- No modifica las RPC antiguas.
-- No registra compras al instalarse.
-- ============================================================

BEGIN;

CREATE OR REPLACE FUNCTION public.registrar_compra_transaccional(
    p_id_comercio INTEGER,
    p_id_usuario INTEGER,
    p_id_proveedor INTEGER,
    p_productos JSONB,
    p_observaciones TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = ''
AS $function$

DECLARE
    v_item JSONB;
    v_producto RECORD;

    v_id_producto INTEGER;
    v_cantidad NUMERIC;
    v_precio NUMERIC;
    v_subtotal NUMERIC;

    v_total NUMERIC := 0;
    v_stock_anterior NUMERIC;
    v_stock_nuevo NUMERIC;

    v_costo_actual NUMERIC;
    v_precio_venta_actual NUMERIC;
    v_nuevo_costo NUMERIC;
    v_nuevo_precio_venta NUMERIC;
    v_markup NUMERIC;

    v_numero_compra INTEGER;
    v_id_compra INTEGER;

    v_ids INTEGER[] := ARRAY[]::INTEGER[];
    v_id_bloqueo INTEGER;

    v_detalles JSONB := '[]'::JSONB;
    v_productos_actualizados JSONB := '[]'::JSONB;
    v_compra JSONB;

BEGIN

    -- ========================================================
    -- 1. VALIDACIONES GENERALES
    -- ========================================================

    IF p_id_comercio IS NULL
       OR p_id_usuario IS NULL
       OR p_id_proveedor IS NULL
       OR p_id_comercio <= 0
       OR p_id_usuario <= 0
       OR p_id_proveedor <= 0
    THEN
        RAISE EXCEPTION
            'Comercio, usuario y proveedor son obligatorios';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM public.usuarios u
        JOIN public.comercios c
          ON c.id_comercio = u.id_comercio
        WHERE u.id_usuario = p_id_usuario
          AND u.id_comercio = p_id_comercio
          AND u.estado = TRUE
          AND c.estado = TRUE
    ) THEN
        RAISE EXCEPTION
            'Usuario o comercio inválido o inactivo';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM public.proveedores pr
        WHERE pr.id_proveedor = p_id_proveedor
          AND pr.id_comercio = p_id_comercio
          AND pr.estado = TRUE
    ) THEN
        RAISE EXCEPTION
            'Proveedor inexistente o inactivo en este comercio';
    END IF;

    IF p_productos IS NULL
       OR jsonb_typeof(p_productos) <> 'array'
       OR jsonb_array_length(p_productos) = 0
    THEN
        RAISE EXCEPTION
            'La compra debe contener al menos un producto';
    END IF;

    -- ========================================================
    -- 2. VALIDAR IDENTIFICADORES
    -- ========================================================

    FOR v_item IN
        SELECT value
        FROM jsonb_array_elements(p_productos)
    LOOP

        IF jsonb_typeof(v_item) <> 'object'
           OR jsonb_typeof(v_item->'id_producto') <> 'number'
           OR (v_item->>'id_producto') !~ '^[0-9]+$'
        THEN
            RAISE EXCEPTION
                'Cada producto debe tener un ID entero válido';
        END IF;

        v_id_producto := (v_item->>'id_producto')::INTEGER;

        IF v_id_producto <= 0 THEN
            RAISE EXCEPTION 'ID de producto inválido';
        END IF;

        IF v_id_producto = ANY(v_ids) THEN
            RAISE EXCEPTION
                'Producto repetido: %', v_id_producto;
        END IF;

        v_ids := array_append(v_ids, v_id_producto);

    END LOOP;

    -- ========================================================
    -- 3. BLOQUEAR PRODUCTOS EN ORDEN ESTABLE
    -- ========================================================

    FOR v_id_bloqueo IN
        SELECT DISTINCT id
        FROM unnest(v_ids) AS t(id)
        ORDER BY id
    LOOP

        PERFORM 1
        FROM public.productos
        WHERE id_producto = v_id_bloqueo
          AND id_comercio = p_id_comercio
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'Producto % no pertenece al comercio',
                v_id_bloqueo;
        END IF;

    END LOOP;

    -- ========================================================
    -- 4. VALIDAR CANTIDADES Y CALCULAR TOTAL
    -- ========================================================

    FOR v_item IN
        SELECT value
        FROM jsonb_array_elements(p_productos)
    LOOP

        v_id_producto := (v_item->>'id_producto')::INTEGER;

        SELECT *
        INTO STRICT v_producto
        FROM public.productos
        WHERE id_producto = v_id_producto
          AND id_comercio = p_id_comercio;

        IF v_producto.estado IS DISTINCT FROM TRUE THEN
            RAISE EXCEPTION
                'El producto % está inactivo',
                v_id_producto;
        END IF;

        IF jsonb_typeof(v_item->'cantidad') <> 'number'
           OR jsonb_typeof(v_item->'precio_unitario') <> 'number'
        THEN
            RAISE EXCEPTION
                'Cantidad y precio deben ser numéricos';
        END IF;

        v_cantidad := (v_item->>'cantidad')::NUMERIC;
        v_precio := (v_item->>'precio_unitario')::NUMERIC;

        IF v_cantidad <= 0 THEN
            RAISE EXCEPTION
                'La cantidad debe ser mayor que cero';
        END IF;

        IF v_cantidad > 999999999.999 THEN
            RAISE EXCEPTION
                'Cantidad fuera del rango permitido';
        END IF;

        IF v_precio <= 0 THEN
            RAISE EXCEPTION
                'El precio unitario debe ser mayor que cero';
        END IF;

        IF v_precio > 999999999999 THEN
            RAISE EXCEPTION
                'Precio unitario fuera del rango permitido';
        END IF;

        CASE UPPER(TRIM(v_producto.unidad_de_medida))

            WHEN 'UNIDAD' THEN
                IF v_cantidad <> TRUNC(v_cantidad) THEN
                    RAISE EXCEPTION
                        'El producto % requiere unidades enteras',
                        v_id_producto;
                END IF;

            WHEN 'KG' THEN
                IF v_cantidad <> ROUND(v_cantidad, 3) THEN
                    RAISE EXCEPTION
                        'El producto % admite hasta 3 decimales',
                        v_id_producto;
                END IF;

            ELSE
                RAISE EXCEPTION
                    'Unidad de medida no admitida para producto %',
                    v_id_producto;

        END CASE;

        IF v_producto.stock + v_cantidad > 999999999.999 THEN
            RAISE EXCEPTION
                'El stock resultante excede el límite permitido';
        END IF;

        IF v_producto.precio_costo IS NULL
           OR v_producto.precio_venta IS NULL
        THEN
            RAISE EXCEPTION
                'El producto % no tiene precios configurados',
                v_id_producto;
        END IF;

        IF v_precio > v_producto.precio_costo
           AND v_producto.precio_costo <= 0
        THEN
            RAISE EXCEPTION
                'No se puede calcular el recargo del producto %',
                v_id_producto;
        END IF;

        v_subtotal := ROUND(v_cantidad * v_precio, 2);
        v_total := v_total + v_subtotal;

    END LOOP;

    -- ========================================================
    -- 5. GENERAR NÚMERO E INSERTAR CABECERA
    -- ========================================================

    v_numero_compra := public.obtener_siguiente_numero(
        p_id_comercio,
        'COMPRA'::VARCHAR
    );

    INSERT INTO public.compras (
        id_proveedor,
        id_usuario,
        id_comercio,
        numero_compra,
        total_compra,
        estado,
        observaciones
    )
    VALUES (
        p_id_proveedor,
        p_id_usuario,
        p_id_comercio,
        v_numero_compra,
        v_total,
        'COMPLETADA',
        p_observaciones
    )
    RETURNING id_compra
    INTO v_id_compra;

    -- ========================================================
    -- 6. DETALLES, PRECIOS, STOCK E HISTORIAL
    -- ========================================================

    FOR v_item IN
        SELECT value
        FROM jsonb_array_elements(p_productos)
    LOOP

        v_id_producto := (v_item->>'id_producto')::INTEGER;
        v_cantidad := (v_item->>'cantidad')::NUMERIC;
        v_precio := (v_item->>'precio_unitario')::NUMERIC;
        v_subtotal := ROUND(v_cantidad * v_precio, 2);

        SELECT *
        INTO STRICT v_producto
        FROM public.productos
        WHERE id_producto = v_id_producto
          AND id_comercio = p_id_comercio;

        v_stock_anterior := v_producto.stock;
        v_stock_nuevo := v_stock_anterior + v_cantidad;

        v_costo_actual := v_producto.precio_costo;
        v_precio_venta_actual := v_producto.precio_venta;

        v_nuevo_costo := v_costo_actual;
        v_nuevo_precio_venta := v_precio_venta_actual;
        v_markup := NULL;

        IF v_precio > v_costo_actual THEN

            v_markup := (
                v_precio_venta_actual - v_costo_actual
            ) / v_costo_actual;

            v_nuevo_costo := v_precio;

            v_nuevo_precio_venta := ROUND(
                v_nuevo_costo * (1 + v_markup),
                2
            );

        END IF;

        INSERT INTO public.detalle_compra (
            id_compra,
            id_producto,
            cantidad,
            precio_unitario,
            subtotal
        )
        VALUES (
            v_id_compra,
            v_id_producto,
            v_cantidad,
            v_precio,
            v_subtotal
        );

        UPDATE public.productos
        SET
            stock = v_stock_nuevo,
            precio_costo = v_nuevo_costo,
            precio_venta = v_nuevo_precio_venta
        WHERE id_producto = v_id_producto
          AND id_comercio = p_id_comercio;

        INSERT INTO public.historial_movimiento (
            id_producto,
            id_usuario,
            tipo_movimiento,
            cantidad,
            stock_anterior,
            stock_nuevo,
            observaciones
        )
        VALUES (
            v_id_producto,
            p_id_usuario,
            'COMPRA',
            v_cantidad,
            v_stock_anterior,
            v_stock_nuevo,
            FORMAT(
                'Compra #%s (ID global %s)',
                v_numero_compra,
                v_id_compra
            )
        );

        v_detalles := v_detalles || jsonb_build_array(
            jsonb_build_object(
                'id_producto', v_id_producto,
                'cantidad', v_cantidad,
                'precio_unitario', v_precio,
                'subtotal', v_subtotal
            )
        );

        v_productos_actualizados :=
            v_productos_actualizados || jsonb_build_array(
                jsonb_build_object(
                    'id_producto', v_id_producto,
                    'nombre_producto', v_producto.nombre_producto,
                    'stock_anterior', v_stock_anterior,
                    'stock_actual', v_stock_nuevo,
                    'costo_anterior', v_costo_actual,
                    'costo_compra', v_precio,
                    'costo_actual', v_nuevo_costo,
                    'precio_venta_anterior', v_precio_venta_actual,
                    'precio_venta_actual', v_nuevo_precio_venta,
                    'markup_porcentaje',
                        CASE
                            WHEN v_markup IS NULL THEN NULL
                            ELSE ROUND(v_markup * 100, 2)
                        END,
                    'precio_actualizado',
                        (v_precio > v_costo_actual)
                )
            );

    END LOOP;

    -- ========================================================
    -- 7. RESPUESTA
    -- ========================================================

    SELECT to_jsonb(c)
    INTO v_compra
    FROM public.compras c
    WHERE c.id_compra = v_id_compra;

    RETURN jsonb_build_object(
        'compra', v_compra,
        'detalles', v_detalles,
        'productos_actualizados', v_productos_actualizados
    );

END;
$function$;

-- ============================================================
-- PERMISOS
-- Solo el backend con service_role debe poder invocarla.
-- Flask debe validar su propio JWT antes de llamar a la RPC.
-- ============================================================

REVOKE ALL ON FUNCTION public.registrar_compra_transaccional(
    INTEGER, INTEGER, INTEGER, JSONB, TEXT
) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION public.registrar_compra_transaccional(
    INTEGER, INTEGER, INTEGER, JSONB, TEXT
) TO service_role;

COMMIT;
