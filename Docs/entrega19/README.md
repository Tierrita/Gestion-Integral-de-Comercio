ENTREGA 19 – USUARIOS, ROLES, AUTENTICACIÓN Y PERMISOS

Proyecto: Gestión Integral de Comercio


OBJETIVO DE LA ENTREGA:

Iniciar el desarrollo del módulo de Usuarios y Seguridad del sistema
Gestión Integral de Comercio.

Esta etapa tendrá como objetivo administrar el acceso de las personas
al sistema, definiendo usuarios, roles y permisos según las funciones
que cada persona pueda realizar dentro del comercio.

El módulo será diseñado antes de comenzar su implementación para definir
correctamente las reglas de negocio, la estructura de datos y los
mecanismos de seguridad necesarios.


--------------------------------------------------
1. ESTADO ACTUAL
--------------------------------------------------

PENDIENTE DE DESARROLLO.


--------------------------------------------------
2. FUNCIONALIDADES A DEFINIR
--------------------------------------------------

Durante esta entrega se analizarán e implementarán progresivamente:

- Gestión de usuarios.
- Creación y modificación de usuarios.
- Activación y desactivación de usuarios.
- Autenticación.
- Inicio de sesión.
- Gestión de contraseñas.
- Roles.
- Permisos.
- Protección de endpoints.
- Autorización según permisos.
- Identificación del usuario que realiza cada operación.


--------------------------------------------------
3. ARQUITECTURA PREVISTA
--------------------------------------------------

Se mantendrá la arquitectura utilizada en el resto del backend:

Route
  ↓
Controller
  ↓
Service
  ↓
Model
  ↓
Supabase


La implementación deberá integrarse con los módulos ya desarrollados
sin modificar innecesariamente la lógica de negocio existente.


--------------------------------------------------
4. PRÓXIMO PASO
--------------------------------------------------

Antes de comenzar a programar se realizará el diseño completo del módulo,
definiendo:

- Qué tipos de usuarios existirán.
- Cómo funcionarán los roles.
- Cómo se asignarán los permisos.
- Cómo se realizará la autenticación.
- Qué endpoints deberán estar protegidos.
- Qué acciones podrá realizar cada usuario.


ESTADO:

ENTREGA 19 – EN DESARROLLO.