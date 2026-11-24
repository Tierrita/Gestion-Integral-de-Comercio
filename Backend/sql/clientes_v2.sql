-- AIOnix | Clientes V2
-- Migración aditiva. NO ejecutar hasta validar backup, entorno y despliegue.
-- Mantiene las columnas, PK, FK, números locales y registros existentes.
BEGIN;

ALTER TABLE public.clientes
  ADD COLUMN IF NOT EXISTS tipo_cliente varchar(20) NOT NULL DEFAULT 'PARTICULAR',
  ADD COLUMN IF NOT EXISTS nombre_comercial varchar(150),
  ADD COLUMN IF NOT EXISTS tipo_documento varchar(20),
  ADD COLUMN IF NOT EXISTS numero_documento varchar(30),
  ADD COLUMN IF NOT EXISTS condicion_iva varchar(50),
  ADD COLUMN IF NOT EXISTS email varchar(254),
  ADD COLUMN IF NOT EXISTS whatsapp varchar(50),
  ADD COLUMN IF NOT EXISTS direccion varchar(200),
  ADD COLUMN IF NOT EXISTS localidad varchar(100),
  ADD COLUMN IF NOT EXISTS provincia varchar(100),
  ADD COLUMN IF NOT EXISTS codigo_postal varchar(20),
  ADD COLUMN IF NOT EXISTS referencia_entrega text,
  ADD COLUMN IF NOT EXISTS observaciones text;

-- La clasificación no impide usar la API V1: los clientes anteriores
-- quedan clasificados como PARTICULAR y pueden reclasificarse después.
ALTER TABLE public.clientes
  ADD CONSTRAINT clientes_v2_tipo_cliente_chk
  CHECK (tipo_cliente IN ('PARTICULAR','COMERCIO','EMPRESA','INSTITUCION'));

ALTER TABLE public.clientes
  ADD CONSTRAINT clientes_v2_tipo_documento_chk
  CHECK (tipo_documento IS NULL OR tipo_documento IN ('DNI','CUIT','CUIL','PASAPORTE','OTRO'));

-- No se agregan UNIQUE sobre documentos: pueden existir clientes sin documento
-- y se debe revisar el criterio de duplicados por comercio antes de imponerlo.
COMMIT;

-- Validación de solo lectura posterior:
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_schema='public' AND table_name='clientes'
-- ORDER BY ordinal_position;
