-- Pruebas puras de lógica financiera y stock. Solo SELECT, sin tablas ni escrituras.
-- Ejecutar manualmente en entorno de pruebas. Todas las filas deben devolver true.
WITH
productos(stock,costo,venta) AS (VALUES (2.750::numeric,10000::numeric,15000::numeric)),
ventas(id_cliente,estado,metodo,total) AS (VALUES
 (10,'COMPLETADA','EFECTIVO',15000::numeric),
 (10,'COMPLETADA','CUENTA_CORRIENTE',20000::numeric),
 (10,'ANULADA','CUENTA_CORRIENTE',7000::numeric),
 (11,'COMPLETADA','CUENTA_CORRIENTE',3000::numeric)),
cobros(id_cliente,estado,monto) AS (VALUES
 (10,'COMPLETADO',5000::numeric),
 (10,'ANULADO',2000::numeric)),
clientes(id_cliente,numero_cliente) AS (VALUES (10,2),(11,3),(12,1)),
saldos AS (
 SELECT c.id_cliente,coalesce(sum(v.total) filter(where v.estado='COMPLETADA' and v.metodo='CUENTA_CORRIENTE'),0)
  -coalesce((select sum(x.monto) from cobros x where x.id_cliente=c.id_cliente and x.estado='COMPLETADO'),0) saldo
 FROM clientes c left join ventas v on v.id_cliente=c.id_cliente
 WHERE c.numero_cliente<>1 GROUP BY c.id_cliente
),
casos(nombre,correcto) AS (VALUES
 ('stock fraccionario valor costo',(SELECT stock*costo=27500 FROM productos)),
 ('stock fraccionario valor venta',(SELECT stock*venta=41250 FROM productos)),
 ('deuda cliente 10: efectivo excluido, cobro parcial y anulaciones',(SELECT saldo=15000 FROM saldos WHERE id_cliente=10)),
 ('cliente 11 conserva deuda aunque no compre en periodo',(SELECT saldo=3000 FROM saldos WHERE id_cliente=11)),
 ('cliente general excluido',(SELECT count(*)=0 FROM saldos WHERE id_cliente=12)),
 ('deuda total actual',(SELECT sum(greatest(saldo,0))=18000 FROM saldos)),
 ('cantidad de clientes deudores',(SELECT count(*) filter(where saldo>0)=2 FROM saldos))
)
SELECT nombre,correcto FROM casos ORDER BY nombre;

-- Pruebas pendientes en ambiente aislado (no ejecutar sobre producción):
-- 1. Validar RPC propuesta con datos transaccionales y rango temporal variable;
--    Total por cobrar debe permanecer constante cuando solo cambia el rango.
-- 2. Ranking top_producto con ventas de 1.750 KG; costo histórico sin truncamiento.
-- 3. Venta CC anulada y cobro anulado, conciliando con módulo Clientes V2.
-- 4. Aislamiento entre comercios; CLIENTE GENERAL es numero_cliente=1 por comercio.
-- 5. Contrato de campos y permisos EXECUTE para service_role, sin ampliar acceso.
