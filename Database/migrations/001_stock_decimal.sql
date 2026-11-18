-- Gestión Integral de Comercio
-- Migración de cantidades enteras a cantidades decimales
-- BORRADOR: NO EJECUTAR hasta adaptar y probar backend y funciones RPC.
-- Requiere respaldo previo del esquema public y ventana de mantenimiento.

BEGIN;

-- Normalizar las unidades existentes sin cambiar el stock.
UPDATE public.productos
SET unidad_de_medida = UPPER(TRIM(unidad_de_medida))
WHERE unidad_de_medida IS DISTINCT FROM UPPER(TRIM(unidad_de_medida));

-- Si existen unidades diferentes a UNIDAD y KG, cancelar la migración.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM public.productos
        WHERE unidad_de_medida NOT IN ('UNIDAD', 'KG')
    ) THEN
        RAISE EXCEPTION 'Existen unidades de medida no contempladas';
    END IF;
END;
$$;

ALTER TABLE public.productos
    ALTER COLUMN stock TYPE NUMERIC(12,3) USING stock::NUMERIC(12,3),
    ALTER COLUMN stock_minimo TYPE NUMERIC(12,3) USING stock_minimo::NUMERIC(12,3);

ALTER TABLE public.detalle_compra
    ALTER COLUMN cantidad TYPE NUMERIC(12,3) USING cantidad::NUMERIC(12,3);

ALTER TABLE public.detalle_venta
    ALTER COLUMN cantidad TYPE NUMERIC(12,3) USING cantidad::NUMERIC(12,3);

ALTER TABLE public.historial_movimiento
    ALTER COLUMN cantidad TYPE NUMERIC(12,3) USING cantidad::NUMERIC(12,3),
    ALTER COLUMN stock_anterior TYPE NUMERIC(12,3) USING stock_anterior::NUMERIC(12,3),
    ALTER COLUMN stock_nuevo TYPE NUMERIC(12,3) USING stock_nuevo::NUMERIC(12,3);

ALTER TABLE public.productos
    ADD CONSTRAINT productos_unidad_de_medida_valida
    CHECK (unidad_de_medida IN ('UNIDAD', 'KG'));

-- La aplicación y las RPC deben validar cantidades enteras para UNIDAD,
-- y hasta tres decimales para KG. No se añade aquí un CHECK transversal
-- porque detalle_compra/detalle_venta no contienen unidad_de_medida.
-- También se deben adaptar registrar_compra y registrar_movimiento_stock,
-- que actualmente reciben p_cantidad integer y usan variables INT.

COMMIT;
