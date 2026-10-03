# Entrega 6 – Consultas de stock

**Fecha:** 27 de septiembre de 2026  
**Proyecto:** E-Commerce Kiosco

## Objetivo

Permitir la consulta del inventario, la búsqueda de productos por nombre y la identificación de productos con stock bajo.

## Qué se hizo

Se implementó `GET /stock` para listar los productos ordenados por nombre, junto con su stock actual, stock mínimo y unidad de medida.

A esa misma ruta se le agregó el parámetro `buscar`. Por ejemplo, `GET /stock?buscar=coca` devuelve los productos cuyo nombre coincide con la búsqueda. El usuario puede encontrarlos por nombre sin conocer su ID; el identificador permanece en la respuesta para operaciones internas, como el ajuste de stock.

También se implementó `GET /stock/alertas`, que devuelve los productos cuyo **stock es menor o igual al stock mínimo**. Las tres formas de consulta se resolvieron con dos rutas HTTP, manteniendo la organización del backend en rutas, controlador, servicio y modelo.

## Pruebas realizadas

Se probaron las consultas en Postman. La consulta general devolvió los productos registrados; la búsqueda de «coca» encontró “Coca-Cola 500ml”, y una búsqueda sin coincidencias devolvió `[]`.

La consulta de alertas inicialmente devolvió `[]`. Para comprobarla con un caso real, se utilizó el ajuste manual desarrollado en la Entrega 5 y se redujo el stock de Coca-Cola de **42 a 2 unidades**. Al repetir `GET /stock/alertas`, el producto apareció con `stock: 2` y `stock_minimo: 5`.

## Resultado

Las consultas general, por nombre y por alertas quedaron funcionando y fueron verificadas en Postman. La última prueba confirmó que los cambios realizados mediante un ajuste se reflejan en la información del inventario.