# Entrega 5 – Ajuste manual de stock

**Fecha:** septiembre de 2026  
**Proyecto:** E-Commerce Kiosco

## Objetivo

Iniciar el módulo de stock con una funcionalidad que permita aumentar o disminuir manualmente las existencias de un producto y registrar el cambio realizado.

## Qué se hizo

Se implementó la ruta `PATCH /stock/<id_producto>/ajustar`. La petición recibe la cantidad, el tipo de ajuste (`AUMENTAR` o `DISMINUIR`) y el ID del usuario que realiza la operación.

El servicio busca el producto, obtiene su stock actual y calcula el nuevo valor. Antes de actualizarlo, valida que la cantidad sea un entero mayor que cero, que el producto exista y que una disminución no deje el stock en negativo.

Cuando el ajuste es válido, se actualiza el producto en Supabase y se registra un movimiento en `historial_movimiento`. El registro incluye la cantidad, el stock anterior y el nuevo, el usuario y el tipo de movimiento: `AJUSTE_ENTRADA` o `AJUSTE_SALIDA`.

La funcionalidad se organizó en las capas de rutas, controlador, servicio y modelo. También se registró el Blueprint de stock en la aplicación Flask.

## Pruebas realizadas

Se probó el endpoint en Postman con estos casos:

- **Aumento:** un producto pasó de 10 a 15 unidades al sumar 5.
- **Disminución:** pasó de 15 a 12 unidades al restar 3.
- **Stock insuficiente:** se intentó restar 20 unidades cuando había 12. La API rechazó la operación con **HTTP 400** y el mensaje «El stock no puede quedar negativo».

Los ajustes válidos devolvieron **HTTP 200**. Se verificó además el registro de los movimientos correspondientes en el historial.

## Resultado

El ajuste manual quedó implementado y probado: permite sumar o restar existencias, aplica las validaciones de negocio y registra los cambios. El siguiente paso del módulo es incorporar las consultas de stock.