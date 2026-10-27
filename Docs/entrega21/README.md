# ENTREGA 21 – AUTENTICACIÓN, ROLES Y PERMISOS

## Gestión Integral de Comercio

### Objetivo de la entrega

En esta entrega se implementó la base de seguridad y autorización del sistema multi-comercio.

El sistema ahora puede identificar al usuario mediante autenticación JWT, determinar a qué comercio pertenece y controlar operaciones exclusivas del propietario.

Además, se desarrolló el módulo inicial de Roles y Permisos, que permitirá posteriormente definir qué acciones puede realizar cada empleado dentro de un comercio.

---

# 1. Autenticación mediante JWT

Se implementó autenticación utilizando:

- Flask como framework del backend.
- PyJWT como biblioteca para generar y validar tokens.
- JWT como formato del token de autenticación.
- Werkzeug para verificar contraseñas almacenadas mediante hash.

Flujo implementado:

Usuario
→ Email + contraseña
→ Backend valida credenciales
→ Backend genera JWT
→ Cliente recibe token
→ Token se utiliza en las siguientes peticiones

El JWT identifica al usuario autenticado.

---

# 2. Login

Endpoint implementado:

POST /auth/login

El backend valida:

- Existencia del usuario.
- Contraseña.
- Estado activo del usuario.
- Comercio asociado.
- Estado activo del comercio.

Si las validaciones son correctas, se genera un JWT.

El token se utiliza posteriormente mediante:

Authorization: Bearer <token>

---

# 3. Perfil del usuario autenticado

Endpoint implementado:

GET /auth/me

Permite obtener la información del usuario actualmente autenticado.

El backend obtiene nuevamente los datos actuales del usuario y del comercio.

Esto permite verificar en cada petición:

- Usuario existente.
- Usuario activo.
- Comercio existente.
- Comercio activo.
- ID del comercio.
- Rol actual.
- Si el usuario es propietario.

Se evita depender únicamente de la información almacenada dentro del JWT.

---

# 4. Contexto de autenticación

Después de validar una petición protegida, el backend dispone de:

g.id_usuario
g.id_comercio
g.id_rol
g.es_propietario
g.usuario_actual
g.comercio_actual

Esto permite que los módulos del sistema conozcan automáticamente qué usuario está realizando una operación y a qué comercio pertenece.

El frontend no debe decidir el id_comercio.

---

# 5. Seguridad multi-comercio

Se comenzó a aplicar el principio de aislamiento entre comercios.

Ejemplo:

Un usuario autenticado perteneciente al Comercio 1 solamente puede consultar o modificar roles pertenecientes al Comercio 1.

Las consultas utilizan simultáneamente:

id_rol
+
id_comercio

El id_comercio se obtiene del usuario autenticado y no de los datos enviados por el frontend.

Esto evita que un usuario pueda modificar manualmente una petición para acceder a información perteneciente a otro comercio.

---

# 6. Decorador login_requerido

Se implementó:

@login_requerido

Este decorador protege endpoints que requieren autenticación.

Valida:

- Presencia del Bearer Token.
- Validez del JWT.
- Usuario existente.
- Usuario activo.
- Comercio existente.
- Comercio activo.

Si alguna validación falla, la operación es rechazada.

---

# 7. Decorador solo_propietario

Se implementó:

@solo_propietario

Permite restringir determinadas operaciones exclusivamente al propietario del comercio.

Ejemplo:

@login_requerido
@solo_propietario

Actualmente se utiliza para proteger la administración de roles y permisos.

Posteriormente también podrá utilizarse en operaciones sensibles como:

- Finanzas.
- Anulación de ventas.
- Anulación de compras.
- Anulación de pagos a proveedores.
- Administración de roles y permisos.

---

# 8. Catálogo de permisos

Se creó el catálogo inicial de permisos del sistema.

Actualmente existen 24 permisos distribuidos entre:

- Productos.
- Stock.
- Ventas.
- Clientes.
- Cobros.
- Compras.
- Proveedores.
- Usuarios.
- Categorías.

Ejemplos:

productos.ver
productos.crear
productos.modificar
productos.ver_costos

stock.ver
stock.ajustar

ventas.ver
ventas.crear

clientes.ver
clientes.crear
clientes.modificar
clientes.ver_deuda

cobros.registrar

usuarios.gestionar

Los permisos son globales y posteriormente se asignan a los roles de cada comercio.

---

# 9. Roles por comercio

Cada comercio puede disponer de sus propios roles.

Ejemplos futuros:

- VENDEDOR.
- CAJERO.
- ENCARGADO.

Cada rol pertenece exclusivamente a un comercio mediante:

id_comercio

La relación entre roles y permisos se almacena mediante la tabla:

rol_permiso

---

# 10. Primer rol creado

Se creó mediante la API el primer rol:

VENDEDOR

Comercio:

id_comercio = 1

Permisos asignados actualmente:

- productos.ver
- stock.ver
- ventas.ver
- ventas.crear
- clientes.ver
- clientes.crear
- clientes.modificar
- clientes.ver_deuda
- cobros.registrar

El comercio no fue enviado desde Postman.

El backend utilizó automáticamente el id_comercio obtenido del usuario autenticado.

---

# 11. Endpoints de Roles y Permisos

Se implementaron y probaron:

GET /roles/permisos
Obtiene el catálogo global de permisos.

POST /roles
Crea un rol dentro del comercio autenticado y asigna sus permisos.

GET /roles
Lista los roles pertenecientes al comercio autenticado.

GET /roles/<id_rol>
Obtiene un rol específico junto con sus permisos.

PATCH /roles/<id_rol>
Permite modificar el nombre y/o los permisos de un rol.

PATCH /roles/<id_rol>/estado
Permite activar o desactivar un rol.

Todas estas operaciones están protegidas mediante JWT y actualmente son exclusivas del propietario.

---

# 12. Modificación de permisos

Se implementó la posibilidad de modificar los permisos de un rol existente.

Ejemplo:

PATCH /roles/1

El backend:

1. Verifica que el rol pertenezca al comercio autenticado.
2. Valida los permisos enviados.
3. Elimina las asignaciones anteriores.
4. Registra las nuevas asignaciones.
5. Devuelve el rol actualizado.

La prueba realizada permitió agregar correctamente el permiso:

clientes.modificar

al rol VENDEDOR.

---

# 13. Activación y desactivación de roles

Se implementó:

PATCH /roles/<id_rol>/estado

Permite cambiar:

estado = true
estado = false

Se estableció además la siguiente regla de negocio:

Un rol no podrá ser desactivado si existen usuarios que actualmente tengan ese rol asignado.

La validación de usuarios asignados ya fue preparada en la capa Model.

Se probó correctamente la desactivación del rol VENDEDOR mientras todavía no tenía empleados asociados.

Posteriormente el rol fue reactivado para continuar con el módulo de empleados.

---

# 14. Arquitectura utilizada

El módulo mantiene la arquitectura general del proyecto:

Route
↓
Controller
↓
Service
↓
Model
↓
Supabase

Responsabilidades:

Route:
Define endpoints y aplica decoradores de seguridad.

Controller:
Recibe y responde peticiones HTTP.

Service:
Contiene reglas de negocio y validaciones.

Model:
Realiza operaciones contra Supabase.

---

# 15. Pruebas realizadas en Postman

Se creó la sección:

13 - Roles y Permisos

Con las siguientes peticiones:

01 - Listar permisos
02 - Crear rol
03 - Listar roles
04 - Obtener rol por ID
05 - Modificar rol
06 - Cambiar estado del rol

Todas utilizan autenticación mediante Bearer Token.

También se configuró una variable de colección:

auth_token

El login guarda automáticamente el JWT obtenido para utilizarlo en las siguientes peticiones.

---

# 16. Estado actual

COMPLETADO:

- Login mediante email y contraseña.
- Generación de JWT.
- Validación de JWT.
- Usuario autenticado.
- Validación de usuario activo.
- Validación de comercio activo.
- Contexto del usuario mediante Flask g.
- Protección de endpoints.
- Operaciones exclusivas del propietario.
- Catálogo de 24 permisos.
- Creación de roles.
- Asignación de permisos.
- Consulta de roles.
- Consulta individual de rol.
- Modificación de roles.
- Modificación de permisos.
- Activación/desactivación de roles.
- Aislamiento de roles por comercio.
- Pruebas mediante Postman.

---

# 17. Próximo módulo

El próximo objetivo será:

USUARIOS / EMPLEADOS

Se implementará:

- Listado de empleados del comercio.
- Alta de empleados.
- Asignación de rol.
- Contraseña inicial.
- Hash de contraseña.
- Validación de email único.
- Activación/desactivación.
- Reactivación.
- Cambio de rol.
- Restablecimiento manual de contraseña.
- Protección del propietario.
- Validación de permisos del empleado.

Una vez implementado este módulo se podrá probar el sistema completo de autorización:

USUARIO
↓
ROL
↓
PERMISOS
↓
ENDPOINT AUTORIZADO / DENEGADO

Esto permitirá comenzar posteriormente a proteger los módulos existentes de Productos, Stock, Ventas, Clientes, Compras, Proveedores y Finanzas.