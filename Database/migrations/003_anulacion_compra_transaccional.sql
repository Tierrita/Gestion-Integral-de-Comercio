
-- ============================================================
-- MIGRACION 003
-- ANULACION TRANSACCIONAL DE COMPRAS
-- Gestion Integral de Comercio
-- ============================================================

BEGIN;

CREATE OR REPLACE FUNCTION public.anular_compra_transaccional(
    p_id_compra INTEGER,
    p_id_comercio INTEGER,
    p_id_usuario_anulacion INTEGER
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = ''
AS $function$

DECLARE
    v_compra RECORD;
    v_producto RECORD;
    v_detalle RECORD;

    v_stock_anterior NUMERIC(12,3);
    v_stock_nuevo NUMERIC(12,3);

    v_productos_revertidos JSONB := '[]'::JSONB;
    v_compra_actualizada JSONB;

BEGIN

    -- ========================================================
    -- 1. VALIDAR PARAMETROS
    -- ========================================================

    IF p_id_compra IS NULL
       OR p_id_comercio IS NULL
       OR p_id_usuario_anulacion IS NULL
       OR p_id_compra <= 0
       OR p_id_comercio <= 0
       OR p_id_usuario_anulacion <= 0
    THEN
        RAISE EXCEPTION
            'Los identificadores deben ser enteros positivos';
    END IF;

    -- ========================================================
    -- 2. VALIDAR COMERCIO Y PROPIETARIO
    -- ========================================================

    IF NOT EXISTS (
        SELECT 1
        FROM public.usuarios u
        JOIN public.comercios c
          ON c.id_comercio = u.id_comercio
        WHERE u.id_usuario = p_id_usuario_anulacion
          AND u.id_comercio = p_id_comercio
          AND u.estado = TRUE
          AND u.es_propietario = TRUE
          AND c.estado = TRUE
    ) THEN
        RAISE EXCEPTION
            'Usuario no autorizado para anular compras';
    END IF;

    -- ========================================================
    -- 3. BLOQUEAR COMPRA
    -- Evita anulaciones simultaneas de la misma compra.
    -- ========================================================

    SELECT *
    INTO v_compra
    FROM public.compras
    WHERE id_compra = p_id_compra
      AND id_comercio = p_id_comercio
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'La compra no existe en este comercio';
    END IF;

    IF UPPER(TRIM(v_compra.estado)) = 'ANULADA' THEN
        RAISE EXCEPTION
            'La compra ya fue anulada';
    END IF;

    IF UPPER(TRIM(v_compra.estado)) <> 'COMPLETADA' THEN
        RAISE EXCEPTION
            'Solo se pueden anular compras completadas';
    END IF;

    -- ========================================================
    -- 4. COMPROBAR DETALLES
    -- ========================================================

    IF NOT EXISTS (
        SELECT 1
        FROM public.detalle_compra
        WHERE id_compra = p_id_compra
    ) THEN
        RAISE EXCEPTION
            'La compra no tiene detalles registrados';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM public.detalle_compra
        WHERE id_compra = p_id_compra
          AND (cantidad IS NULL OR cantidad <= 0)
    ) THEN
        RAISE EXCEPTION
            'La compra contiene cantidades invalidas';
    END IF;

    -- ========================================================
    -- 5. BLOQUEAR PRODUCTOS EN ORDEN ASCENDENTE
    -- ========================================================

    FOR v_detalle IN
        SELECT DISTINCT id_producto
        FROM public.detalle_compra
        WHERE id_compra = p_id_compra
        ORDER BY id_producto
    LOOP

        PERFORM 1
        FROM public.productos
        WHERE id_producto = v_detalle.id_producto
          AND id_comercio = p_id_comercio
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'Producto % no pertenece al comercio',
                v_detalle.id_producto;
        END IF;

    END LOOP;

    -- ========================================================
    -- 6. VALIDAR STOCK SUFICIENTE
    -- Se agrupan cantidades por producto para soportar
    -- compras historicas con detalles repetidos.
    -- ========================================================

    FOR v_detalle IN
        SELECT
            id_producto,
            SUM(cantidad) AS cantidad_total
        FROM public.detalle_compra
        WHERE id_compra = p_id_compra
        GROUP BY id_producto
        ORDER BY id_producto
    LOOP

        SELECT *
        INTO STRICT v_producto
        FROM public.productos
        WHERE id_producto = v_detalle.id_producto
          AND id_comercio = p_id_comercio;

        IF v_producto.stock < v_detalle.cantidad_total THEN
            RAISE EXCEPTION
                'Stock insuficiente para anular producto %. Disponible: %, requerido: %',
                v_detalle.id_producto,
                v_producto.stock,
                v_detalle.cantidad_total;
        END IF;

    END LOOP;

    -- ========================================================
    -- 7. REVERTIR STOCK Y REGISTRAR HISTORIAL
    -- ========================================================

    FOR v_detalle IN
        SELECT
            id_producto,
            SUM(cantidad) AS cantidad_total
        FROM public.detalle_compra
        WHERE id_compra = p_id_compra
        GROUP BY id_producto
        ORDER BY id_producto
    LOOP

        SELECT *
        INTO STRICT v_producto
        FROM public.productos
        WHERE id_producto = v_detalle.id_producto
          AND id_comercio = p_id_comercio;

        v_stock_anterior := v_producto.stock;

        v_stock_nuevo :=
            v_stock_anterior - v_detalle.cantidad_total;

        UPDATE public.productos
        SET stock = v_stock_nuevo
        WHERE id_producto = v_detalle.id_producto
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
            v_detalle.id_producto,
            p_id_usuario_anulacion,
            'ANULACION_COMPRA',
            v_detalle.cantidad_total,
            v_stock_anterior,
            v_stock_nuevo,
            FORMAT(
                'Anulacion compra #%s (ID global %s)',
                v_compra.numero_compra,
                p_id_compra
            )
        );

        v_productos_revertidos :=
            v_productos_revertidos ||
            jsonb_build_array(
                jsonb_build_object(
                    'id_producto', v_detalle.id_producto,
                    'cantidad', v_detalle.cantidad_total,
                    'stock_anterior', v_stock_anterior,
                    'stock_nuevo', v_stock_nuevo
                )
            );

    END LOOP;

    -- ========================================================
    -- 8. ACTUALIZAR ESTADO DE LA COMPRA
    -- ========================================================

    UPDATE public.compras
    SET estado = 'ANULADA'
    WHERE id_compra = p_id_compra
      AND id_comercio = p_id_comercio;

    -- No revertimos precios de costo ni de venta.
    -- Una compra posterior puede haberlos actualizado.

    -- ========================================================
    -- 9. DEVOLVER RESULTADO
    -- ========================================================

    SELECT to_jsonb(c)
    INTO v_compra_actualizada
    FROM public.compras c
    WHERE c.id_compra = p_id_compra
      AND c.id_comercio = p_id_comercio;

    RETURN jsonb_build_object(
        'compra', v_compra_actualizada,
        'productos_revertidos', v_productos_revertidos
    );

END;
$function$;

-- ============================================================
-- PERMISOS
-- Ejecutable solo mediante el backend con service_role.
-- ============================================================

REVOKE ALL ON FUNCTION
public.anular_compra_transaccional(
    INTEGER, INTEGER, INTEGER
)
FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION
public.anular_compra_transaccional(
    INTEGER, INTEGER, INTEGER
)
TO service_role;

COMMIT;
