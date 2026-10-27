ENTREGA 20 – ARQUITECTURA MULTI-COMERCIO Y PREPARACIÓN DE AUTENTICACIÓN

Objetivo:
Preparar el sistema Gestión Integral de Comercio para soportar múltiples comercios de forma aislada, manteniendo los datos históricos existentes y dejando preparada la arquitectura para implementar autenticación, usuarios, roles y permisos.

--------------------------------------------------
1. CREACIÓN DE COMERCIOS
--------------------------------------------------

Se creó la tabla comercios para representar cada negocio registrado dentro del sistema.

Campos principales:
- id_comercio
- nombre_comercio
- razon_social
- cuit
- telefono
- direccion
- localidad
- provincia
- logo_url
- estado
- fecha_alta

El id_comercio funciona como identificador interno global del negocio.

También se agregó una restricción de unicidad para CUIT cuando este se encuentre informado.

--------------------------------------------------
2. ROLES Y PERMISOS
--------------------------------------------------

Se crearon las tablas:

- roles
- permisos
- rol_permiso

Relación:

COMERCIO
   ↓
ROLES
   ↓
PERMISOS

Cada comercio podrá crear sus propios roles, por ejemplo:

- Cajero
- Vendedor
- Encargado
- Administrador

Los permisos serán definidos por el sistema y podrán asignarse a los distintos roles.

El propietario será un usuario especial y tendrá acceso total sin depender de un rol convencional.

--------------------------------------------------
3. ADAPTACIÓN DE USUARIOS
--------------------------------------------------

La tabla usuarios fue preparada para la nueva arquitectura.

Se agregaron:

- id_comercio
- id_rol
- nombre_completo
- dni
- direccion
- es_propietario
- estado

Se agregaron relaciones:

usuarios → comercios
usuarios → roles

También se incorporaron restricciones para impedir que un comercio tenga más de un propietario.

El usuario administrador existente fue asociado al comercio inicial y configurado como propietario.

--------------------------------------------------
4. MIGRACIÓN A ARQUITECTURA MULTI-COMERCIO
--------------------------------------------------

Se agregó id_comercio a:

- categorias
- proveedores
- productos
- clientes
- cuentas
- ventas
- compras

Todos los datos históricos existentes fueron asociados inicialmente a:

id_comercio = 1

Se verificó que no quedaran registros sin comercio.

Posteriormente se configuró id_comercio como NOT NULL y se agregaron las Foreign Keys correspondientes hacia la tabla comercios.

De esta forma, cada registro principal del sistema pertenece obligatoriamente a un comercio.

--------------------------------------------------
5. NUMERACIÓN INDEPENDIENTE POR COMERCIO
--------------------------------------------------

Se separó el ID interno de PostgreSQL del número visible para cada comercio.

Se agregaron:

productos.numero_producto
clientes.numero_cliente
proveedores.numero_proveedor
ventas.numero_venta
compras.numero_compra

Ejemplo:

COMERCIO A
Producto #1
Producto #2
Producto #3

COMERCIO B
Producto #1
Producto #2
Producto #3

Internamente PostgreSQL continúa utilizando IDs globales diferentes.

Se agregaron restricciones únicas:

(id_comercio, numero_producto)
(id_comercio, numero_cliente)
(id_comercio, numero_proveedor)
(id_comercio, numero_venta)
(id_comercio, numero_compra)

--------------------------------------------------
6. CONTADORES POR COMERCIO
--------------------------------------------------

Se creó:

contadores_comercio

Esta tabla permite administrar la numeración independiente de las entidades de cada comercio.

También se creó la función PostgreSQL:

obtener_siguiente_numero(
    p_id_comercio,
    p_entidad
)

La función obtiene de forma segura el próximo número correspondiente a una entidad dentro de un comercio.

Los contadores iniciales fueron sincronizados con los registros históricos existentes.

Esto permite manejar correctamente operaciones concurrentes y evita números duplicados dentro del mismo comercio.

--------------------------------------------------
7. PRIMERA ADAPTACIÓN DEL BACKEND
--------------------------------------------------

Se comenzó la migración del backend para trabajar con id_comercio.

Archivo modificado:

Backend/app/models/producto_model.py

Las consultas de productos comenzaron a prepararse para filtrar los registros según el comercio correspondiente.

También se incorporó al modelo la utilización de:

obtener_siguiente_numero_producto(id_comercio)

que utiliza la función PostgreSQL obtener_siguiente_numero.

La migración del módulo Productos todavía se encuentra en progreso.

Las capas Service y Controller deberán adaptarse posteriormente para obtener el comercio desde el usuario autenticado.

--------------------------------------------------
8. PREPARACIÓN DE AUTENTICACIÓN JWT
--------------------------------------------------

Se instaló:

PyJWT==2.14.0

Se comenzó a preparar:

Backend/core/auth.py

Este módulo será responsable de:

- generar tokens JWT
- validar tokens JWT
- proteger endpoints
- identificar al usuario autenticado
- determinar el comercio del usuario

También se preparó la utilización de:

JWT_SECRET_KEY

mediante variables de entorno.

La clave privada no se almacena directamente dentro del código fuente.

Arquitectura prevista:

LOGIN
   ↓
Email + contraseña
   ↓
Validación del usuario
   ↓
Generación JWT
   ↓
Usuario autenticado
   ↓
id_usuario + id_comercio
   ↓
Validación de permisos
   ↓
Operación

--------------------------------------------------
9. PRINCIPIO DE SEGURIDAD MULTI-COMERCIO
--------------------------------------------------

El frontend NO será responsable de indicar qué comercio está realizando una operación.

El backend obtendrá el id_comercio a partir del usuario autenticado.

Esto evita confiar en valores enviados manualmente desde React o Postman.

En cada operación protegida, el backend deberá validar:

- usuario autenticado
- usuario activo
- comercio activo
- comercio al que pertenece el usuario
- rol actual
- permisos actuales
- pertenencia del recurso al comercio

Objetivo:

Un usuario perteneciente al COMERCIO A no podrá consultar, modificar ni operar información perteneciente al COMERCIO B, incluso intentando modificar manualmente una petición HTTP.

--------------------------------------------------
ESTADO DE LA ENTREGA
--------------------------------------------------

COMPLETADO:

✓ Creación de comercios
✓ Creación de roles
✓ Creación de permisos
✓ Relación rol-permiso
✓ Adaptación inicial de usuarios
✓ Asociación del administrador al comercio inicial
✓ Incorporación de id_comercio a las entidades principales
✓ Migración de los datos históricos
✓ Foreign Keys de comercio
✓ id_comercio obligatorio
✓ Numeración independiente por comercio
✓ Contadores por comercio
✓ Función obtener_siguiente_numero
✓ Primera adaptación de producto_model.py
✓ Instalación de PyJWT
✓ Preparación inicial de autenticación JWT
✓ Configuración de JWT_SECRET_KEY mediante variables de entorno

--------------------------------------------------
PENDIENTE
--------------------------------------------------

- Implementar contraseñas hasheadas
- Crear usuario_model.py
- Crear auth_service.py
- Crear auth_controller.py
- Crear auth_routes.py
- Implementar POST /auth/login
- Validar usuario activo
- Validar comercio activo
- Implementar roles y permisos en backend
- Proteger endpoints
- Adaptar progresivamente todos los módulos a id_comercio
- Eliminar dependencia de id_usuario enviado manualmente por frontend
- Completar aislamiento entre comercios
- Implementar posteriormente el registro de nuevos comercios

--------------------------------------------------
PRÓXIMO HITO
--------------------------------------------------

AUTENTICACIÓN + AISLAMIENTO REAL POR COMERCIO

El próximo objetivo será implementar el inicio de sesión completo mediante email y contraseña.

Una vez autenticado el usuario, el backend podrá conocer automáticamente:

- id_usuario
- id_comercio
- si es propietario
- rol
- permisos

A partir de esta información se comenzarán a proteger y adaptar los módulos existentes.

El objetivo final de esta etapa será garantizar que cada comercio pueda operar únicamente sobre sus propios datos.