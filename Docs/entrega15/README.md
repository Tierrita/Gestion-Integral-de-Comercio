# ENTREGA 15 – MÓDULO DE CLIENTES

## 1. Objetivo de la entrega

En esta entrega se desarrolló el módulo de Clientes del sistema Gestión Integral de Comercio.

El objetivo principal fue permitir la administración de los clientes del negocio y preparar su integración con los módulos de Ventas y Financiero.

El módulo permite:

- Registrar clientes.
- Consultar todos los clientes.
- Consultar un cliente por ID.
- Editar los datos de un cliente.
- Activar o desactivar clientes.
- Proteger al CLIENTE GENERAL.
- Consultar el historial de ventas de un cliente.
- Relacionar clientes con ventas.
- Preparar la integración con cobros y cuenta corriente.


---

## 2. Arquitectura utilizada

Se mantuvo la arquitectura modular utilizada en todo el backend:

Route → Controller → Service → Model → Supabase

Se crearon/completaron los siguientes archivos:

app/models/cliente_model.py

app/services/cliente_service.py

app/controllers/cliente_controller.py

app/routes/cliente_routes.py


---

## 3. Tabla clientes

El módulo utiliza la tabla `clientes` almacenada en Supabase.

Campos principales:

- id_cliente
- nombre_completo
- telefono
- estado
- fecha_de_alta

El campo `id_cliente` identifica de forma única a cada cliente.

El campo `nombre_completo` es obligatorio.

El teléfono es opcional.

El campo `estado` permite mantener clientes activos o inactivos sin eliminarlos físicamente.

La fecha de alta se genera automáticamente al registrar un nuevo cliente.


---

## 4. Cliente General

Se mantiene un cliente especial denominado:

CLIENTE GENERAL

ID:

1

Este cliente representa las ventas realizadas a consumidores que no necesitan ser registrados individualmente en el sistema.

De esta manera, una venta siempre puede estar relacionada con un cliente sin necesidad de crear un registro nuevo para cada venta de mostrador.

Se agregó además una regla de negocio que impide desactivar al CLIENTE GENERAL.

Esto evita dejar al sistema sin el cliente utilizado para las ventas generales.


---

## 5. Creación de clientes

Se implementó la creación de clientes mediante:

POST /clientes

Ejemplo:

{
    "nombre_completo": "FRANCO CUENCA",
    "telefono": "2474 475013"
}

El sistema valida que:

- Se hayan enviado datos.
- `nombre_completo` exista.
- El nombre sea texto.
- El nombre no esté vacío.
- El teléfono sea texto cuando se proporciona.
- Un teléfono vacío pueda almacenarse como null.

Al crear un cliente:

estado = true

automáticamente.


---

## 6. Prueba de creación

Se realizó una prueba mediante Postman.

Cliente creado:

id_cliente: 3

nombre_completo: FRANCO CUENCA

telefono: 2474 475013

estado: true

La API respondió:

{
    "cliente": {
        "estado": true,
        "fecha_de_alta": "2026-10-05T12:23:51.843572+00:00",
        "id_cliente": 3,
        "nombre_completo": "FRANCO CUENCA",
        "telefono": "2474 475013"
    },
    "message": "Cliente registrado correctamente"
}

Resultado:

CREACIÓN DE CLIENTE CORRECTA.


---

## 7. Consulta general de clientes

Se implementó:

GET /clientes

Esta ruta permite consultar todos los clientes registrados.

Durante la prueba se obtuvieron:

CLIENTE GENERAL

JUAN PEREZ

FRANCO CUENCA

Los clientes fueron devueltos correctamente con:

- ID
- Nombre
- Teléfono
- Estado
- Fecha de alta


---

## 8. Consulta de cliente por ID

Se implementó:

GET /clientes/<id_cliente>

Ejemplo:

GET /clientes/3

Respuesta obtenida:

{
    "estado": true,
    "fecha_de_alta": "2026-10-05T12:23:51.843572+00:00",
    "id_cliente": 3,
    "nombre_completo": "FRANCO CUENCA",
    "telefono": "2474 475013"
}

Resultado:

CONSULTA INDIVIDUAL CORRECTA.


---

## 9. Edición de clientes

Se implementó:

PATCH /clientes/<id_cliente>

Esta operación permite modificar los datos editables del cliente.

Actualmente pueden modificarse:

- nombre_completo
- telefono

No se permite modificar directamente mediante esta operación:

- id_cliente
- estado
- fecha_de_alta

El estado posee una operación independiente.


---

## 10. Prueba de edición

Se modificó el cliente con ID 3.

Datos enviados:

{
    "nombre_completo": "FRANCO ANGEL CUENCA",
    "telefono": "2474475013"
}

Respuesta:

{
    "cliente": {
        "estado": true,
        "fecha_de_alta": "2026-10-05T12:23:51.843572+00:00",
        "id_cliente": 3,
        "nombre_completo": "FRANCO ANGEL CUENCA",
        "telefono": "2474475013"
    },
    "message": "Cliente actualizado correctamente"
}

Se verificó que:

- El nombre fue actualizado.
- El teléfono fue actualizado.
- El ID no cambió.
- La fecha de alta no cambió.
- El estado no cambió.

Resultado:

EDICIÓN DE CLIENTE CORRECTA.


---

## 11. Estado de clientes

En lugar de eliminar físicamente clientes, se utiliza un sistema de estados.

Cada cliente puede encontrarse:

ACTIVO

o

INACTIVO

Esto permite conservar todo su historial comercial.


---

## 12. Actualización del estado

Se implementó:

PATCH /clientes/<id_cliente>/estado

Ejemplo para desactivar:

{
    "estado": false
}

Ejemplo para activar:

{
    "estado": true
}


---

## 13. Prueba de desactivación

Se desactivó correctamente el cliente con ID 3.

Respuesta:

{
    "cliente": {
        "estado": false,
        "fecha_de_alta": "2026-10-05T12:23:51.843572+00:00",
        "id_cliente": 3,
        "nombre_completo": "FRANCO ANGEL CUENCA",
        "telefono": "2474475013"
    },
    "message": "Estado del cliente actualizado correctamente"
}

Resultado:

DESACTIVACIÓN CORRECTA.


---

## 14. Protección del Cliente General

Se implementó una regla especial para el cliente con ID 1.

CLIENTE GENERAL no puede ser desactivado.

Se realizó la prueba:

PATCH /clientes/1/estado

Body:

{
    "estado": false
}

Respuesta obtenida:

{
    "error": "CLIENTE GENERAL no puede ser desactivado"
}

Resultado:

PROTECCIÓN DE CLIENTE GENERAL CORRECTA.


---

## 15. Historial de ventas por cliente

Se desarrolló la funcionalidad:

GET /clientes/<id_cliente>/ventas

Esta operación permite recuperar las ventas relacionadas con un cliente.

El historial está diseñado para incluir:

- Datos del cliente.
- Cantidad de ventas.
- Información de cada venta.
- Detalle de productos de cada venta.
- Cantidades.
- Precios unitarios.
- Subtotales.

De esta manera, desde el futuro frontend será posible ingresar al perfil de un cliente y visualizar sus compras anteriores.

La funcionalidad quedó implementada en backend y pendiente de su prueba final mediante Postman.


---

## 16. Relación Clientes – Ventas

La tabla `ventas` posee:

id_cliente

Cada venta queda asociada a un cliente.

Esto permite diferenciar entre:

CLIENTE GENERAL

y

CLIENTES IDENTIFICADOS.

La relación permite posteriormente obtener:

Cliente → Ventas → Detalle de cada venta


---

## 17. Integración con cuenta corriente

El módulo de clientes fue diseñado para integrarse con el sistema financiero desarrollado previamente.

La lógica utilizada diferencia:

VENTA ≠ COBRO

Una venta representa una operación comercial.

Un cobro representa el ingreso efectivo de dinero proveniente de un cliente.

Esto permite manejar correctamente ventas financiadas y pagos parciales.


---

## 18. Cobros de clientes

El sistema ya dispone del módulo de cobros.

Las operaciones desarrolladas incluyen:

POST /cobros

GET /cobros

GET /cobros/<id_cobro>

GET /clientes/<id_cliente>/cobros

PATCH /cobros/<id_cobro>/anular

Los cobros se relacionan directamente con un cliente y con una cuenta financiera.


---

## 19. Cuenta corriente del cliente

El saldo de un cliente no se almacena directamente.

Se calcula utilizando:

SALDO = TOTAL VENTAS VÁLIDAS - TOTAL COBROS VÁLIDOS

Esto evita inconsistencias y permite reconstruir siempre la situación financiera del cliente.


---

## 20. Interpretación del saldo

Si:

saldo > 0

el cliente tiene:

DEUDA

Si:

saldo = 0

el cliente se encuentra:

AL_DIA

Si:

saldo < 0

el cliente posee:

SALDO_A_FAVOR


---

## 21. Consulta del saldo

Se dispone de:

GET /clientes/<id_cliente>/saldo

Esta operación permite conocer la situación financiera actual del cliente.

La respuesta incluye:

- Cliente.
- Total de ventas válidas.
- Total de cobros válidos.
- Saldo.
- Situación financiera.


---

## 22. Pagos parciales

El diseño permite registrar pagos parciales.

Ejemplo:

Venta:

$100.000

Cliente paga:

$60.000

Resultado:

Total ventas = $100.000

Total cobros = $60.000

Saldo = $40.000

Situación:

DEUDA


---

## 23. Saldo a favor

El sistema también permite que un cliente entregue más dinero del que actualmente debe.

Ejemplo:

Deuda:

$20.000

Cobro:

$30.000

Resultado:

Saldo = -$10.000

Situación:

SALDO_A_FAVOR

Este saldo se absorbe automáticamente mediante el cálculo de la cuenta corriente cuando se registran nuevas ventas.


---

## 24. Anulación de cobros

Los cobros no se eliminan físicamente.

Cuando existe un error se utiliza:

PATCH /cobros/<id_cobro>/anular

La anulación:

- Cambia el estado del cobro.
- Conserva el historial.
- Registra el usuario que realizó la anulación.
- Registra la fecha.
- Registra el motivo.
- Revierte el efecto financiero correspondiente.


---

## 25. Arquitectura final del módulo

El flujo utilizado para Clientes es:

HTTP Request
      ↓
cliente_routes.py
      ↓
cliente_controller.py
      ↓
cliente_service.py
      ↓
cliente_model.py
      ↓
Supabase

Cada capa posee una responsabilidad específica.


---

## 26. Responsabilidad del Model

cliente_model.py se encarga exclusivamente del acceso a los datos.

Entre sus operaciones se encuentran:

- insertar_cliente()
- obtener_clientes()
- obtener_cliente_por_id()
- actualizar_cliente()
- actualizar_estado_cliente()
- obtener_ventas_cliente()
- obtener_detalles_venta_cliente()


---

## 27. Responsabilidad del Service

cliente_service.py contiene las reglas de negocio.

Entre ellas:

- Validar nombre.
- Validar teléfono.
- Verificar existencia del cliente.
- Controlar campos editables.
- Activar/desactivar clientes.
- Proteger CLIENTE GENERAL.
- Construir historial de ventas.


---

## 28. Responsabilidad del Controller

cliente_controller.py se encarga de:

- Recibir las solicitudes HTTP.
- Obtener los datos JSON.
- Ejecutar los servicios correspondientes.
- Devolver respuestas JSON.
- Asignar códigos HTTP.
- Manejar errores provenientes de validaciones y Supabase.


---

## 29. Responsabilidad de Routes

cliente_routes.py define los endpoints disponibles para el módulo.

Rutas desarrolladas:

POST /clientes

GET /clientes

GET /clientes/<id_cliente>

PATCH /clientes/<id_cliente>

PATCH /clientes/<id_cliente>/estado

GET /clientes/<id_cliente>/ventas


---

## 30. Endpoints relacionados con la cuenta corriente

Además del CRUD de Clientes, el sistema dispone de:

POST /cobros

GET /cobros

GET /cobros/<id_cobro>

GET /clientes/<id_cliente>/cobros

PATCH /cobros/<id_cobro>/anular

GET /clientes/<id_cliente>/saldo


---

## 31. Pruebas realizadas

Se verificó mediante Postman:

- Creación de cliente.
- Consulta general.
- Consulta individual.
- Edición.
- Desactivación.
- Activación.
- Protección de CLIENTE GENERAL.

Todas las pruebas realizadas respondieron correctamente.

La consulta del historial de ventas por cliente quedó implementada y pendiente de la prueba final mediante Postman.


---

## 32. Resultado de la entrega

El módulo de Clientes quedó desarrollado siguiendo la arquitectura general del proyecto.

Actualmente permite administrar clientes sin eliminar información histórica y se encuentra integrado conceptualmente con:

- Ventas.
- Detalle de ventas.
- Cobros.
- Cuentas financieras.
- Cuenta corriente.

Estado actual:

CRUD CLIENTES: COMPLETADO Y PROBADO ✅

PROTECCIÓN CLIENTE GENERAL: COMPLETADA Y PROBADA ✅

HISTORIAL DE VENTAS: IMPLEMENTADO – PENDIENTE PRUEBA FINAL ⏳

COBROS DE CLIENTES: IMPLEMENTADOS Y PROBADOS ✅

SALDO / CUENTA CORRIENTE: IMPLEMENTADO Y PROBADO ✅


---

## 33. Próximo paso

Realizar la prueba final de:

GET /clientes/<id_cliente>/ventas

Luego realizar una prueba integral:

CLIENTE
↓
VENTA
↓
COBRO PARCIAL
↓
SALDO PENDIENTE
↓
HISTORIAL
↓
ANULACIÓN

Una vez completada esta prueba podrá considerarse cerrado el flujo completo de Clientes y Cuenta Corriente.