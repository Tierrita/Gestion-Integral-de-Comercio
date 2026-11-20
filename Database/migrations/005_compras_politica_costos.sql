-- Compras V2 / Migracion 005: ultimo costo sin alterar precio de venta.
-- Requiere la RPC de la migracion 002; no registra compras ni altera datos existentes.
-- Ejecutar primero en entorno de pruebas y con respaldo reciente.
BEGIN;

DO $migration$
DECLARE
    v_original text;
    v_nueva text;
    v_anterior text;
    v_reemplazo text;
    v_oid oid;
BEGIN
    v_oid := to_regprocedure('public.registrar_compra_transaccional(integer,integer,integer,jsonb,text)');
    IF v_oid IS NULL THEN
        RAISE EXCEPTION 'No existe la funcion de registro de compras esperada';
    END IF;
    SELECT pg_get_functiondef(v_oid) INTO v_original;
    v_nueva := v_original;

    -- 1. La politica anterior de recargo deja de ser necesaria.
    v_anterior := $old$
        IF v_precio > v_producto.precio_costo
           AND v_producto.precio_costo <= 0
        THEN
            RAISE EXCEPTION
                'No se puede calcular el recargo del producto %',
                v_id_producto;
        END IF;
$old$;
    v_reemplazo := $new$
        -- El precio de venta no depende de las compras.
$new$;
    IF strpos(v_nueva, v_anterior) = 0 THEN
        RAISE EXCEPTION 'La validacion de recargo no coincide; no se aplicaron cambios';
    END IF;
    v_nueva := replace(v_nueva, v_anterior, v_reemplazo);

    -- 2. Rechazar costos unitarios con mas de dos decimales.
    v_anterior := $old$
        IF v_precio <= 0 THEN
            RAISE EXCEPTION
                'El precio unitario debe ser mayor que cero';
        END IF;
$old$;
    v_reemplazo := $new$
        IF v_precio <= 0 THEN
            RAISE EXCEPTION
                'El precio unitario debe ser mayor que cero';
        END IF;

        IF v_precio <> ROUND(v_precio, 2) THEN
            RAISE EXCEPTION
                'El precio unitario admite hasta 2 decimales';
        END IF;
$new$;
    IF strpos(v_nueva, v_anterior) = 0 THEN
        RAISE EXCEPTION 'La validacion del precio no coincide; no se aplicaron cambios';
    END IF;
    v_nueva := replace(v_nueva, v_anterior, v_reemplazo);

    -- 3. Ultimo costo siempre; precio de venta inalterado.
    v_anterior := $old$
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
$old$;
    v_reemplazo := $new$
        v_nuevo_costo := v_precio;
        v_nuevo_precio_venta := v_precio_venta_actual;
        v_markup := NULL;
$new$;
    IF strpos(v_nueva, v_anterior) = 0 THEN
        RAISE EXCEPTION 'La politica de costos no coincide; no se aplicaron cambios';
    END IF;
    v_nueva := replace(v_nueva, v_anterior, v_reemplazo);

    -- 4. Respuesta compatible: precio_actualizado sigue presente, ahora
    -- indica cambio de costo; se agregan indicadores explicitos.
    v_anterior := $old$'precio_actualizado',
                        (v_precio > v_costo_actual)$old$;
    v_reemplazo := $new$'precio_actualizado',
                        (v_precio <> v_costo_actual),
                    'costo_actualizado',
                        (v_precio <> v_costo_actual),
                    'precio_venta_actualizado', FALSE$new$;
    IF strpos(v_nueva, v_anterior) = 0 THEN
        RAISE EXCEPTION 'El formato de respuesta no coincide; no se aplicaron cambios';
    END IF;
    v_nueva := replace(v_nueva, v_anterior, v_reemplazo);

    IF v_nueva = v_original THEN
        RAISE EXCEPTION 'No se realizaron reemplazos';
    END IF;
    -- CREATE OR REPLACE conserva la identidad, permisos y dependencias de la RPC.
    EXECUTE v_nueva;
END;
$migration$;

-- Confirmacion estatica sin registrar operaciones de prueba.
SELECT
    position('v_nuevo_costo := v_precio;' in pg_get_functiondef(p.oid)) > 0 AS ultimo_costo,
    position('v_nuevo_precio_venta := v_precio_venta_actual;' in pg_get_functiondef(p.oid)) > 0 AS venta_conservada,
    position('El precio unitario admite hasta 2 decimales' in pg_get_functiondef(p.oid)) > 0 AS precision_controlada,
    position('IF v_precio > v_costo_actual THEN' in pg_get_functiondef(p.oid)) = 0 AS sin_recargo_automatico
FROM pg_proc p
WHERE p.oid = 'public.registrar_compra_transaccional(integer,integer,integer,jsonb,text)'::regprocedure;

COMMIT;
