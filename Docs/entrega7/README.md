# Entrega 7 – Registro de compras

**Fecha:** 27 de septiembre de 2026  
**Proyecto:** E-Commerce Kiosco

## Objetivo

Implementar el registro de compras permitiendo asociar varios productos a una misma operación, calcular automáticamente los subtotales y obtener el total general de la compra.

## Qué se hizo

Se implementó `POST /compras` siguiendo la arquitectura utilizada en el backend: rutas, controlador, servicio y modelo.

La petición recibe el proveedor, el usuario, el estado, las observaciones y una lista con los productos comprados. Para cada producto se recibe su `id_producto`, `cantidad` y `precio_unitario`.

La lógica del servicio valida que la compra contenga los datos necesarios y al menos un producto. También comprueba que las cantidades y los precios sean mayores a cero.

El backend calcula automáticamente el subtotal de cada producto mediante `cantidad × precio_unitario` y obtiene `total_compra` sumando todos los subtotales. De esta manera, el total no necesita ser enviado desde el cliente.

Una vez calculado el total, se genera un registro en la tabla `compras`. El `id_compra` generado se utiliza posteriormente para relacionar cada producto con la compra mediante la tabla `detalle_compra`.

También se registró el Blueprint de compras dentro de `app/__init__.py` para incorporar las nuevas rutas a la aplicación Flask.

## Pruebas realizadas

Se realizaron pruebas mediante Postman utilizando `POST /compras`.

En la prueba principal se registró una compra al proveedor con `id_proveedor: 1`, realizada por el usuario con `id_usuario: 1`, incluyendo dos productos.

El producto con `id_producto: 1` se registró con una cantidad de 10 unidades y un precio unitario de $900, generando un subtotal de $9.000.

El producto con `id_producto: 2` se registró con una cantidad de 5 unidades y un precio unitario de $1.200, generando un subtotal de $6.000.

El backend calculó automáticamente un `total_compra` de $15.000.

La operación generó correctamente la compra con `id_compra: 4` y dos registros asociados en `detalle_compra`, ambos vinculados mediante el mismo identificador de compra.

## Resultado

El registro de compras con múltiples productos quedó funcionando y fue verificado mediante Postman.

Actualmente, `POST /compras` permite registrar la información general de una compra, calcular automáticamente los subtotales y el total, y almacenar cada producto comprado en `detalle_compra`.

En esta etapa todavía no se modifica automáticamente el stock ni se generan registros en `historial_movimiento`. La siguiente etapa será integrar el módulo de Compras con la lógica de Stock para que cada compra aumente las existencias correspondientes y quede registrada en el historial de movimientos.