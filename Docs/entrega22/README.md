# Entrega 22 — Gestión de Usuarios y Empleados

## Objetivo

En esta entrega se completó el módulo de gestión de usuarios y empleados del Sistema de Gestión Integral de Comercio.

El módulo permite administrar los empleados pertenecientes a cada comercio, asignarles roles, activar o suspender su acceso y restablecer sus contraseñas.

La gestión se encuentra integrada con el sistema de autenticación JWT, roles y permisos desarrollado en las entregas anteriores.

---

## Arquitectura utilizada

El módulo mantiene la arquitectura general del backend:

```text
Route
  ↓
Controller
  ↓
Service
  ↓
Model
  ↓
Supabase / PostgreSQL
```

### Route

Define los endpoints HTTP y aplica las protecciones de autenticación y autorización.

### Controller

Recibe la petición HTTP, obtiene los datos enviados y genera la respuesta JSON correspondiente.

### Service

Contiene las reglas de negocio relacionadas con usuarios, empleados, roles, estados y contraseñas.

### Model

Realiza las consultas y modificaciones sobre la tabla `usuarios` almacenada en Supabase.

---

# 1. Usuarios por comercio

Cada usuario pertenece a un comercio mediante:

```text
id_comercio
```

Esto permite mantener separados los empleados de cada negocio dentro de la arquitectura multicomercio.

Las consultas de empleados verifican el comercio autenticado para evitar acceder a usuarios pertenecientes a otro comercio.

---

# 2. Listado de usuarios

Se implementó:

```http
GET /usuarios
```

Permite obtener los usuarios pertenecientes al comercio autenticado.

La respuesta no devuelve la contraseña ni su hash.

El endpoint requiere:

```text
usuarios.gestionar
```

El propietario posee acceso automáticamente.

---

# 3. Consulta individual

Se implementó:

```http
GET /usuarios/<id_usuario>
```

Permite consultar un empleado específico verificando que pertenezca al comercio autenticado.

Si el usuario no existe dentro del comercio, se devuelve un error.

---

# 4. Creación de empleados

Se implementó:

```http
POST /usuarios
```

Permite crear nuevos empleados dentro del comercio.

Datos principales:

```json
{
    "nombre_completo": "JUAN PEREZ",
    "email": "juan@ecommercekiosco.com",
    "password": "Juan1234!",
    "telefono": "2364000000",
    "direccion": "Rojas, Buenos Aires",
    "id_rol": 1
}
```

Durante la creación se valida:

- Nombre válido.
- Email válido.
- Email no registrado previamente.
- Contraseña de al menos 8 caracteres.
- Existencia del rol.
- Que el rol pertenezca al mismo comercio.
- Que el rol se encuentre activo.

La contraseña nunca se almacena en texto plano.

Se utiliza:

```python
generate_password_hash(
    password,
    method="pbkdf2:sha256"
)
```

---

# 5. Modificación de empleados

Se implementó:

```http
PATCH /usuarios/<id_usuario>
```

Permite modificar información básica de un empleado.

Actualmente pueden modificarse:

```text
nombre_completo
telefono
direccion
```

No se permite utilizar este endpoint para modificar:

```text
password
id_rol
estado
id_comercio
es_propietario
dni
```

Estas operaciones se encuentran separadas para mantener responsabilidades claras y aplicar reglas de seguridad específicas.

---

# 6. Activación y suspensión de empleados

Se implementó:

```http
PATCH /usuarios/<id_usuario>/estado
```

Ejemplo:

```json
{
    "estado": false
}
```

Los usuarios no se eliminan físicamente de la base de datos.

En su lugar pueden encontrarse:

```text
estado = true
```

o:

```text
estado = false
```

Esto permite conservar el historial de operaciones realizadas por cada empleado.

Un usuario inactivo no puede iniciar sesión.

Prueba realizada:

```text
Empleado activo
    ↓
Propietario lo desactiva
    ↓
estado = false
    ↓
Empleado intenta iniciar sesión
    ↓
403
"El usuario se encuentra inactivo"
```

Luego de volver a activarlo, el empleado pudo iniciar sesión nuevamente.

---

# 7. Cambio de rol

Se implementó:

```http
PATCH /usuarios/<id_usuario>/rol
```

Ejemplo:

```json
{
    "id_rol": 2
}
```

Esta operación es exclusiva del propietario.

Se utiliza:

```python
@solo_propietario
```

Esto significa que un empleado con permiso:

```text
usuarios.gestionar
```

puede gestionar empleados, pero no puede cambiar sus roles.

Antes de asignar un rol se verifica:

- Que exista.
- Que pertenezca al mismo comercio.
- Que se encuentre activo.
- Que el usuario objetivo no sea el propietario.

Durante las pruebas se modificó correctamente un empleado:

```text
VENDEDOR
id_rol = 1

        ↓

CAJERO
id_rol = 2
```

---

# 8. Roles utilizados durante las pruebas

Se trabajó con los siguientes roles:

```text
VENDEDOR
CAJERO
```

Los permisos no se almacenan directamente dentro del usuario.

La relación utilizada es:

```text
USUARIO
   ↓
ROL
   ↓
ROL_PERMISO
   ↓
PERMISO
```

Esto permite modificar los permisos asociados a un rol sin modificar individualmente cada usuario.

---

# 9. Autorización mediante permisos

Los endpoints generales de gestión utilizan:

```python
@login_requerido
@permiso_requerido("usuarios.gestionar")
```

El backend valida los permisos en cada petición.

El propietario posee acceso automático.

Los empleados dependen del rol que tengan asignado.

Durante las pruebas, un empleado sin:

```text
usuarios.gestionar
```

intentó consultar:

```http
GET /usuarios
```

y recibió:

```json
{
    "error": "No tiene permisos para realizar esta operación"
}
```

con código HTTP:

```text
403 Forbidden
```

---

# 10. Restablecimiento de contraseña

Se implementó:

```http
PATCH /usuarios/<id_usuario>/password
```

Ejemplo:

```json
{
    "password": "JuanNueva123!"
}
```

El sistema:

1. Verifica que el empleado exista.
2. Verifica que pertenezca al mismo comercio.
3. Verifica las restricciones de gestión.
4. Valida que la nueva contraseña tenga al menos 8 caracteres.
5. Genera un nuevo hash.
6. Actualiza la contraseña.
7. Nunca devuelve el hash en la respuesta.

---

# 11. Prueba del cambio de contraseña

Se restableció correctamente la contraseña de un empleado.

Luego se intentó iniciar sesión utilizando la contraseña anterior.

Resultado:

```json
{
    "error": "Email o contraseña incorrectos"
}
```

Posteriormente se utilizó la nueva contraseña.

Resultado:

```text
200 OK
Inicio de sesión correcto
JWT generado correctamente
```

Esto confirmó que la contraseña anterior dejó de ser válida y que el nuevo hash fue almacenado correctamente.

---

# 12. Integración con JWT

Los empleados utilizan el mismo sistema de autenticación JWT implementado anteriormente.

Después del login, el token identifica al usuario mediante:

```text
id_usuario
```

El backend utiliza esa identidad para consultar la información actual del usuario.

Esto permite trabajar con:

```text
id_usuario
id_comercio
id_rol
es_propietario
estado
```

y realizar las validaciones correspondientes antes de permitir una operación protegida.

---

# 13. Seguridad implementada

El módulo actualmente contempla:

- Contraseñas almacenadas mediante hash.
- Contraseñas nunca devueltas en las respuestas.
- Usuarios separados por comercio.
- Validación del comercio autenticado.
- Usuarios activos e inactivos.
- Usuarios inactivos sin posibilidad de iniciar sesión.
- Roles asociados al comercio.
- Roles activos obligatorios para asignación.
- Control de permisos por endpoint.
- Acciones exclusivas del propietario.
- Protección especial del propietario.
- Empleados conservados históricamente sin eliminación física.

---

# 14. Endpoints de la entrega

| Método | Endpoint | Función |
|---|---|---|
| GET | `/usuarios` | Listar usuarios |
| GET | `/usuarios/<id>` | Consultar usuario |
| POST | `/usuarios` | Crear empleado |
| PATCH | `/usuarios/<id>` | Modificar empleado |
| PATCH | `/usuarios/<id>/estado` | Activar/desactivar empleado |
| PATCH | `/usuarios/<id>/rol` | Cambiar rol |
| PATCH | `/usuarios/<id>/password` | Restablecer contraseña |

---

# 15. Organización en Postman

```text
14 - Usuarios
├── Consultas
│   ├── Listar usuarios
│   └── Obtener usuario por ID
├── Alta
│   └── Crear usuario
├── Gestión
│   ├── Modificar usuario
│   ├── Cambiar estado
│   └── Cambiar rol
└── Seguridad
    └── Restablecer contraseña
```

---

# Resultado de la entrega

Con esta entrega queda implementada la administración principal de empleados del comercio.

El propietario puede administrar los usuarios de su negocio y el sistema controla el acceso utilizando:

```text
JWT
+
Comercio
+
Usuario
+
Rol
+
Permisos
```

De esta manera, la aplicación cuenta con una base de autenticación y autorización preparada para conectar posteriormente el frontend React con distintos tipos de usuarios.