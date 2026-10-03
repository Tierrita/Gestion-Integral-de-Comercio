ENTREGA 10 – MÓDULO DE CATEGORÍAS

Objetivo de la entrega

En esta entrega se desarrolló el Módulo de Categorías del sistema Gestión Integral de Comercio.

El objetivo principal fue implementar la lógica necesaria para crear, consultar, modificar y administrar el estado de las categorías utilizadas para clasificar los productos del sistema.

El módulo fue desarrollado respetando la arquitectura utilizada en el backend:

Route → Controller → Service → Model → Supabase

De esta manera, cada capa mantiene una responsabilidad específica y la lógica de negocio permanece separada del acceso a los datos.


1. ESTRUCTURA DEL MÓDULO DE CATEGORÍAS

Para desarrollar el módulo se utilizaron los siguientes archivos:

app/
│
├── models/
│   └── categoria_model.py
│
├── services/
│   └── categoria_service.py
│
├── controllers/
│   └── categoria_controller.py
│
└── routes/
    └── categoria_routes.py

Cada archivo cumple una función determinada:

- categoria_routes.py: define los endpoints disponibles.
- categoria_controller.py: recibe las solicitudes HTTP y genera las respuestas JSON.
- categoria_service.py: contiene la lógica de negocio y las validaciones.
- categoria_model.py: realiza las operaciones necesarias sobre Supabase.

También se registró el Blueprint de categorías dentro de app/__init__.py para incorporar las nuevas rutas a la aplicación Flask.


2. REGISTRO DE UNA CATEGORÍA

Se implementó el endpoint:

POST /categorias

Este endpoint permite registrar una nueva categoría en el sistema.

El sistema puede recibir información como:

{
    "nombre_categoria": "Fiambres",
    "descripcion": "Fiambres y embutidos"
}

Antes de registrar la categoría se realizan diferentes validaciones:

- Verifica que se hayan enviado datos.
- Verifica que exista el campo nombre_categoria.
- Comprueba que el nombre sea de tipo texto.
- Comprueba que el nombre no se encuentre vacío.
- Elimina espacios innecesarios al comienzo y al final del nombre.
- Establece el estado de la categoría como true por defecto.

Los campos id_categoria y fecha_alta son generados automáticamente por la base de datos.


3. PRUEBA DE CREACIÓN DE CATEGORÍA

Para comprobar el funcionamiento se realizó:

POST http://127.0.0.1:5001/categorias

Body:

{
    "nombre_categoria": "Fiambres",
    "descripcion": "Fiambres y embutidos"
}

El sistema registró correctamente la nueva categoría.

Resultado:

ID de categoría: 5
Nombre: Fiambres
Descripción: Fiambres y embutidos
Estado: true

La fecha de alta fue generada automáticamente por la base de datos.


4. CONSULTA GENERAL DE CATEGORÍAS

Se implementó el endpoint:

GET /categorias

Este endpoint permite consultar todas las categorías registradas en el sistema.

Las categorías son recuperadas desde Supabase y ordenadas mediante su id_categoria.

Durante la prueba se recuperaron correctamente las siguientes categorías:

1 - Gaseosas
2 - Golosinas
3 - Almacen
4 - Snacks
5 - Fiambres

Cada registro contiene:

- ID de categoría.
- Nombre.
- Descripción.
- Estado.
- Fecha de alta.

Esta funcionalidad permitirá posteriormente utilizar las categorías desde el frontend, por ejemplo, para mostrar listados o seleccionar la categoría correspondiente al crear o modificar un producto.


5. CONSULTA INDIVIDUAL DE UNA CATEGORÍA

Se implementó el endpoint:

GET /categorias/<id_categoria>

Este endpoint permite consultar una categoría específica utilizando su identificador.

Por ejemplo:

GET /categorias/5

El sistema busca la categoría correspondiente en Supabase y devuelve su información.

La respuesta contiene:

- id_categoria.
- nombre_categoria.
- descripcion.
- estado.
- fecha_alta.

También se agregó una validación para detectar categorías inexistentes.

Por ejemplo:

GET /categorias/999

En caso de no encontrar la categoría, el sistema devuelve:

{
    "error": "Categoría no encontrada"
}

De esta manera se evita trabajar con identificadores que no existen dentro de la base de datos.


6. MODIFICACIÓN DE UNA CATEGORÍA

Se implementó el endpoint:

PATCH /categorias/<id_categoria>

Este endpoint permite modificar los datos de una categoría existente.

La actualización se diseñó como una modificación parcial, permitiendo actualizar únicamente los campos necesarios.

Los campos permitidos son:

- nombre_categoria.
- descripcion.

Por ejemplo:

PATCH /categorias/5

Body:

{
    "nombre_categoria": "Fiambres y Quesos",
    "descripcion": "Fiambres, embutidos y quesos"
}

La categoría fue actualizada correctamente.

Resultado:

ID: 5
Nombre: Fiambres y Quesos
Descripción: Fiambres, embutidos y quesos
Estado: true

La modificación no altera campos como:

- id_categoria.
- fecha_alta.
- estado.

El estado se administra mediante un endpoint independiente.


7. VALIDACIONES DURANTE LA MODIFICACIÓN

Para la modificación de categorías se implementaron diferentes controles.

Antes de actualizar una categoría, el sistema:

1. Verifica que la categoría exista.
2. Verifica que se hayan enviado datos.
3. Comprueba que el nombre sea texto en caso de ser enviado.
4. Evita guardar nombres vacíos.
5. Permite modificar únicamente nombre_categoria y descripcion.
6. Rechaza solicitudes que no contengan campos válidos para actualizar.

Esto permite mantener un mayor control sobre la información almacenada.


8. ADMINISTRACIÓN DEL ESTADO DE UNA CATEGORÍA

Se implementó el endpoint:

PATCH /categorias/<id_categoria>/estado

Este endpoint permite activar o desactivar una categoría sin eliminarla físicamente de la base de datos.

La columna estado utiliza valores booleanos:

true → Categoría activa.

false → Categoría inactiva.

Para desactivar una categoría se puede enviar:

{
    "estado": false
}

Para volver a activarla:

{
    "estado": true
}

Esta estrategia permite conservar las categorías y sus relaciones con otros registros del sistema.


9. VALIDACIÓN DEL ESTADO

Antes de modificar el estado de una categoría, el sistema:

1. Verifica que la categoría exista.
2. Verifica que se hayan enviado datos.
3. Comprueba que exista el campo estado.
4. Verifica que el valor recibido sea booleano.
5. Actualiza únicamente el campo estado.

Por lo tanto, valores como:

{
    "estado": "INACTIVA"
}

no son aceptados.

El sistema espera específicamente:

true

o:

false


10. PRUEBA DE CAMBIO DE ESTADO

Se utilizó la Categoría #5 para comprobar esta funcionalidad.

Endpoint:

PATCH http://127.0.0.1:5001/categorias/5/estado

Para activar la categoría se utilizó:

{
    "estado": true
}

El sistema respondió correctamente y la categoría quedó:

ID: 5
Nombre: Fiambres y Quesos
Descripción: Fiambres, embutidos y quesos
Estado: true

Esto confirmó el correcto funcionamiento de la actualización del estado.


11. RELACIÓN CON EL MÓDULO DE PRODUCTOS

El Módulo de Categorías se encuentra relacionado con el Módulo de Productos.

Los productos almacenan:

id_categoria

Este campo permite asociar cada producto con una categoría determinada.

Por ejemplo:

Categoría: Gaseosas
│
├── Coca-Cola
├── Sprite
└── Fanta

La utilización de categorías permite organizar los productos y posteriormente facilitar búsquedas, filtros y selección de información desde el frontend.

El uso del campo estado también permite desactivar una categoría sin eliminarla, conservando las relaciones existentes con los productos.


12. ENDPOINTS IMPLEMENTADOS

El Módulo de Categorías quedó compuesto por los siguientes endpoints:

POST /categorias
→ Crear una nueva categoría.

GET /categorias
→ Consultar todas las categorías.

GET /categorias/<id_categoria>
→ Consultar una categoría específica.

PATCH /categorias/<id_categoria>
→ Modificar el nombre y/o descripción de una categoría.

PATCH /categorias/<id_categoria>/estado
→ Activar o desactivar una categoría.


13. PRUEBAS REALIZADAS

PRUEBA 1 – CREAR CATEGORÍA

POST http://127.0.0.1:5001/categorias

Body:

{
    "nombre_categoria": "Fiambres",
    "descripcion": "Fiambres y embutidos"
}

Resultado:

Categoría creada correctamente.
ID generado: 5.
Estado: true.


PRUEBA 2 – CONSULTAR TODAS LAS CATEGORÍAS

GET http://127.0.0.1:5001/categorias

Resultado:

Listado general de categorías recuperado correctamente.


PRUEBA 3 – CONSULTAR CATEGORÍA INDIVIDUAL

GET http://127.0.0.1:5001/categorias/5

Resultado:

Categoría #5 recuperada correctamente.


PRUEBA 4 – CONSULTAR CATEGORÍA INEXISTENTE

GET http://127.0.0.1:5001/categorias/999

Resultado:

{
    "error": "Categoría no encontrada"
}


PRUEBA 5 – MODIFICAR CATEGORÍA

PATCH http://127.0.0.1:5001/categorias/5

Body:

{
    "nombre_categoria": "Fiambres y Quesos",
    "descripcion": "Fiambres, embutidos y quesos"
}

Resultado:

Nombre:
Fiambres → Fiambres y Quesos

Descripción:
Fiambres y embutidos → Fiambres, embutidos y quesos

Categoría actualizada correctamente.


PRUEBA 6 – CAMBIAR ESTADO DE CATEGORÍA

PATCH http://127.0.0.1:5001/categorias/5/estado

Body:

{
    "estado": true
}

Resultado:

Estado de categoría actualizado correctamente.

La Categoría #5 quedó activa.


14. RESULTADO FINAL

Con esta entrega quedó implementado el Módulo de Categorías del sistema Gestión Integral de Comercio.

El backend ahora permite crear categorías, consultar todas las categorías registradas, consultar una categoría mediante su ID, modificar su información y administrar su estado.

El flujo principal implementado puede representarse de la siguiente manera:

CREAR CATEGORÍA
       ↓
Validar datos
       ↓
Preparar información
       ↓
Registrar categoría
       ↓
Supabase


CONSULTAR CATEGORÍAS
       ↓
Solicitar información
       ↓
Consultar Supabase
       ↓
Devolver categorías


EDITAR CATEGORÍA
       ↓
Buscar categoría
       ↓
Validar existencia
       ↓
Validar campos
       ↓
Actualizar información
       ↓
Supabase


CAMBIAR ESTADO
       ↓
Buscar categoría
       ↓
Validar existencia
       ↓
Validar estado booleano
       ↓
true / false
       ↓
Actualizar categoría


De esta manera, el Módulo de Categorías queda integrado con la arquitectura general del backend y preparado para relacionarse con el Módulo de Productos.

La administración mediante estados permite conservar la integridad de los datos y evita eliminar categorías que puedan encontrarse asociadas a productos existentes.