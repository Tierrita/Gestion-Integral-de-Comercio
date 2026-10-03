ENTREGA 11 – MÓDULO DE PROVEEDORES

Objetivo de la entrega

En esta entrega se desarrolló el Módulo de Proveedores del sistema Gestión Integral de Comercio.

El objetivo principal fue implementar la lógica necesaria para crear, consultar, modificar y administrar el estado de los proveedores utilizados por el sistema.

Este módulo resulta fundamental para la gestión comercial, ya que los proveedores se encuentran relacionados con los productos y con las compras registradas dentro de la aplicación.

El módulo fue desarrollado respetando la arquitectura utilizada en el backend:

Route → Controller → Service → Model → Supabase

De esta manera, cada capa mantiene una responsabilidad específica y la lógica de negocio permanece separada del acceso a los datos.


1. ESTRUCTURA DEL MÓDULO DE PROVEEDORES

Para desarrollar el módulo se utilizaron los siguientes archivos:

app/
│
├── models/
│   └── proveedor_model.py
│
├── services/
│   └── proveedor_service.py
│
├── controllers/
│   └── proveedor_controller.py
│
└── routes/
    └── proveedor_routes.py

Cada archivo cumple una función determinada:

- proveedor_routes.py: define los endpoints disponibles.
- proveedor_controller.py: recibe las solicitudes HTTP y genera las respuestas JSON.
- proveedor_service.py: contiene la lógica de negocio y las validaciones.
- proveedor_model.py: realiza las operaciones necesarias sobre Supabase.

También se registró el Blueprint de proveedores dentro de app/__init__.py para incorporar las nuevas rutas a la aplicación Flask.


2. ESTRUCTURA DE LOS PROVEEDORES

La tabla proveedores contiene la siguiente información:

- id_proveedor.
- nombre_proveedor.
- telefono.
- email.
- direccion.
- estado.
- descripcion.

El campo id_proveedor identifica de manera única a cada proveedor.

El campo estado utiliza valores booleanos:

true → Proveedor activo.

false → Proveedor inactivo.

Esto permite desactivar proveedores sin necesidad de eliminarlos de la base de datos.


3. REGISTRO DE UN PROVEEDOR

Se implementó el endpoint:

POST /proveedores

Este endpoint permite registrar un nuevo proveedor en el sistema.

Ejemplo:

{
    "nombre_proveedor": "Distribuidora Norte",
    "telefono": "2474123456",
    "email": "ventas@distribuidoranorte.com",
    "direccion": "Rojas, Buenos Aires",
    "descripcion": "Proveedor de fiambres y quesos"
}

Antes de registrar el proveedor se realizan diferentes validaciones:

- Verifica que se hayan enviado datos.
- Verifica que exista el campo nombre_proveedor.
- Comprueba que el nombre sea de tipo texto.
- Comprueba que el nombre no se encuentre vacío.
- Elimina espacios innecesarios al comienzo y al final del nombre.
- Verifica que el estado sea un valor booleano.
- Establece estado = true por defecto cuando no se especifica.


4. PRUEBA DE CREACIÓN DE PROVEEDOR

Para comprobar el funcionamiento se realizó:

POST http://127.0.0.1:5001/proveedores

Body:

{
    "nombre_proveedor": "Distribuidora Norte",
    "telefono": "2474123456",
    "email": "ventas@distribuidoranorte.com",
    "direccion": "Rojas, Buenos Aires",
    "descripcion": "Proveedor de fiambres y quesos"
}

El proveedor fue registrado correctamente.

Resultado:

ID de proveedor: 4
Nombre: Distribuidora Norte
Teléfono: 2474123456
Email: ventas@distribuidoranorte.com
Dirección: Rojas, Buenos Aires
Estado: true
Descripción: Proveedor de fiambres y quesos

El sistema respondió:

{
    "message": "Proveedor creado correctamente"
}

Esto confirmó el correcto funcionamiento de la creación de proveedores.


5. CONSULTA GENERAL DE PROVEEDORES

Se implementó el endpoint:

GET /proveedores

Este endpoint permite consultar todos los proveedores registrados en el sistema.

Los proveedores son recuperados desde Supabase y ordenados mediante su id_proveedor.

Durante las pruebas se recuperaron correctamente los siguientes proveedores:

1 - Distribuidora Central
2 - Distribuidora Norte
3 - Alimentos del Centro
4 - Distribuidora Norte

Cada registro contiene:

- ID del proveedor.
- Nombre.
- Teléfono.
- Email.
- Dirección.
- Estado.
- Descripción.

Esta funcionalidad permitirá posteriormente mostrar desde el frontend el listado de proveedores disponibles y utilizar dicha información en otras operaciones del sistema.


6. CONSULTA INDIVIDUAL DE UN PROVEEDOR

Se implementó el endpoint:

GET /proveedores/<id_proveedor>

Este endpoint permite consultar un proveedor específico utilizando su identificador.

Por ejemplo:

GET /proveedores/1

Durante la prueba se recuperó correctamente:

ID: 1
Nombre: Distribuidora Central
Teléfono: 2364123456
Email: ventas@distribuidoracentral.com
Dirección: Av. Principal 123
Estado: true
Descripción: Proveedor de bebidas y productos de almacén

La respuesta fue obtenida correctamente desde Supabase.


7. VALIDACIÓN DE PROVEEDOR INEXISTENTE

También se agregó una validación para detectar proveedores inexistentes.

Por ejemplo:

GET /proveedores/999

Si el identificador solicitado no corresponde a ningún proveedor registrado, el sistema devuelve:

{
    "error": "Proveedor no encontrado"
}

De esta manera se evita continuar operaciones utilizando proveedores que no existen dentro de la base de datos.


8. MODIFICACIÓN DE UN PROVEEDOR

Se implementó el endpoint:

PATCH /proveedores/<id_proveedor>

Este endpoint permite modificar parcialmente los datos de un proveedor existente.

Los campos que pueden modificarse son:

- nombre_proveedor.
- telefono.
- email.
- direccion.
- descripcion.

El sistema utiliza una actualización parcial, por lo que no es necesario enviar nuevamente todos los datos del proveedor.

Solamente se modifican los campos recibidos en la solicitud.


9. PRUEBA DE MODIFICACIÓN DE PROVEEDOR

Para comprobar esta funcionalidad se modificó el proveedor con ID 4.

Endpoint:

PATCH http://127.0.0.1:5001/proveedores/4

Body:

{
    "nombre_proveedor": "Distribuidora Norte Rojas",
    "telefono": "2474555555",
    "descripcion": "Proveedor de fiambres, quesos y productos refrigerados"
}

Resultado:

Nombre:
Distribuidora Norte
→ Distribuidora Norte Rojas

Teléfono:
2474123456
→ 2474555555

Descripción:
Proveedor de fiambres y quesos
→ Proveedor de fiambres, quesos y productos refrigerados

Los campos que no fueron enviados conservaron sus valores originales:

Email:
ventas@distribuidoranorte.com

Dirección:
Rojas, Buenos Aires

Estado:
true

El sistema respondió:

{
    "message": "Proveedor actualizado correctamente"
}

Esto confirmó que la actualización parcial funciona correctamente.


10. VALIDACIONES DURANTE LA MODIFICACIÓN

Antes de actualizar un proveedor, el sistema realiza diferentes controles:

1. Verifica que el proveedor exista.
2. Verifica que se hayan enviado datos.
3. Comprueba que nombre_proveedor sea texto en caso de ser enviado.
4. Evita almacenar nombres vacíos.
5. Permite modificar únicamente los campos habilitados.
6. Verifica que exista al menos un campo válido para actualizar.

Los campos id_proveedor y estado no son modificados mediante esta operación.

El estado se administra mediante un endpoint independiente.


11. ADMINISTRACIÓN DEL ESTADO DEL PROVEEDOR

Se implementó el endpoint:

PATCH /proveedores/<id_proveedor>/estado

Este endpoint permite activar o desactivar un proveedor sin eliminarlo físicamente de la base de datos.

La columna estado utiliza valores booleanos:

true → Proveedor activo.

false → Proveedor inactivo.

Para desactivar un proveedor:

{
    "estado": false
}

Para volver a activarlo:

{
    "estado": true
}

Esto permite conservar toda la información histórica asociada al proveedor.


12. VALIDACIONES DEL ESTADO

Antes de modificar el estado, el sistema:

1. Verifica que el proveedor exista.
2. Verifica que se hayan enviado datos.
3. Comprueba que exista el campo estado.
4. Verifica que el valor recibido sea booleano.
5. Actualiza únicamente el campo estado.

Por lo tanto, el sistema acepta:

{
    "estado": true
}

o:

{
    "estado": false
}

Pero no acepta valores de texto como:

{
    "estado": "false"
}

En ese caso se genera el mensaje:

{
    "error": "El campo 'estado' debe ser true o false"
}


13. PRUEBA DE CAMBIO DE ESTADO

Para comprobar esta funcionalidad se utilizó el proveedor con ID 4.

Endpoint:

PATCH http://127.0.0.1:5001/proveedores/4/estado

Primero se realizó la desactivación:

{
    "estado": false
}

El proveedor quedó correctamente desactivado.

Posteriormente se realizó nuevamente la solicitud:

{
    "estado": true
}

El proveedor volvió a quedar activo.

Esto confirmó que el sistema permite activar y desactivar proveedores correctamente.


14. RELACIÓN CON OTROS MÓDULOS

El Módulo de Proveedores se encuentra relacionado principalmente con los módulos de Productos y Compras.

La relación puede representarse de la siguiente manera:

PROVEEDOR
    │
    ├── PRODUCTOS
    │      └── id_proveedor
    │
    └── COMPRAS
           └── id_proveedor

Cada producto puede encontrarse asociado a un proveedor.

Además, cada compra registrada contiene el identificador del proveedor correspondiente.

Por esta razón se decidió administrar la baja de proveedores mediante el campo estado y no mediante una eliminación física.

De esta forma se mantienen las relaciones existentes y se conserva el historial de operaciones.


15. ENDPOINTS IMPLEMENTADOS

El Módulo de Proveedores quedó compuesto por los siguientes endpoints:

POST /proveedores
→ Crear un nuevo proveedor.

GET /proveedores
→ Consultar todos los proveedores.

GET /proveedores/<id_proveedor>
→ Consultar un proveedor específico.

PATCH /proveedores/<id_proveedor>
→ Modificar los datos de un proveedor.

PATCH /proveedores/<id_proveedor>/estado
→ Activar o desactivar un proveedor.


16. PRUEBAS REALIZADAS

PRUEBA 1 – CREAR PROVEEDOR

POST http://127.0.0.1:5001/proveedores

Body:

{
    "nombre_proveedor": "Distribuidora Norte",
    "telefono": "2474123456",
    "email": "ventas@distribuidoranorte.com",
    "direccion": "Rojas, Buenos Aires",
    "descripcion": "Proveedor de fiambres y quesos"
}

Resultado:

Proveedor creado correctamente.
ID generado: 4.
Estado: true.


PRUEBA 2 – CONSULTAR TODOS LOS PROVEEDORES

GET http://127.0.0.1:5001/proveedores

Resultado:

Listado general de proveedores recuperado correctamente.


PRUEBA 3 – CONSULTAR PROVEEDOR POR ID

GET http://127.0.0.1:5001/proveedores/1

Resultado:

Proveedor #1 recuperado correctamente.

Nombre:
Distribuidora Central.


PRUEBA 4 – CONSULTAR PROVEEDOR INEXISTENTE

GET http://127.0.0.1:5001/proveedores/999

Resultado:

{
    "error": "Proveedor no encontrado"
}


PRUEBA 5 – MODIFICAR PROVEEDOR

PATCH http://127.0.0.1:5001/proveedores/4

Body:

{
    "nombre_proveedor": "Distribuidora Norte Rojas",
    "telefono": "2474555555",
    "descripcion": "Proveedor de fiambres, quesos y productos refrigerados"
}

Resultado:

Proveedor actualizado correctamente.


PRUEBA 6 – DESACTIVAR PROVEEDOR

PATCH http://127.0.0.1:5001/proveedores/4/estado

Body:

{
    "estado": false
}

Resultado:

Proveedor desactivado correctamente.


PRUEBA 7 – ACTIVAR PROVEEDOR

PATCH http://127.0.0.1:5001/proveedores/4/estado

Body:

{
    "estado": true
}

Resultado:

Proveedor activado correctamente.


17. RESULTADO FINAL

Con esta entrega quedó implementado el Módulo de Proveedores del sistema Gestión Integral de Comercio.

El backend ahora permite:

- Crear proveedores.
- Consultar todos los proveedores.
- Consultar un proveedor mediante su ID.
- Modificar parcialmente sus datos.
- Activar proveedores.
- Desactivar proveedores.
- Validar la existencia de los proveedores.
- Evitar modificaciones con información inválida.

El flujo general implementado puede representarse de la siguiente manera:

CREAR PROVEEDOR
       ↓
Validar datos
       ↓
Preparar información
       ↓
Registrar proveedor
       ↓
Supabase


CONSULTAR PROVEEDORES
       ↓
Solicitar información
       ↓
Consultar Supabase
       ↓
Devolver proveedores


CONSULTAR POR ID
       ↓
Recibir id_proveedor
       ↓
Buscar proveedor
       ↓
¿Existe?
   ↙          ↘
  SÍ          NO
  ↓            ↓
Devolver     Error
proveedor    "Proveedor no encontrado"


EDITAR PROVEEDOR
       ↓
Buscar proveedor
       ↓
Validar existencia
       ↓
Validar campos enviados
       ↓
Actualizar únicamente
los campos recibidos
       ↓
Supabase


CAMBIAR ESTADO
       ↓
Buscar proveedor
       ↓
Validar existencia
       ↓
Validar estado booleano
       ↓
true / false
       ↓
Actualizar proveedor


De esta manera, el Módulo de Proveedores queda completamente integrado con la arquitectura general del backend.

La utilización del campo estado permite administrar proveedores activos e inactivos sin eliminar registros de la base de datos, manteniendo las relaciones existentes con Productos y Compras.

Con esta implementación, el sistema queda preparado para utilizar los proveedores desde el frontend y continuar avanzando con los módulos financieros y estadísticos del proyecto.