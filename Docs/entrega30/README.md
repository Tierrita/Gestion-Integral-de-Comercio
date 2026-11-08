# Entrega 30 — Seguridad multicomercio en Cobros, Cuentas y Finanzas

## Objetivo

Adaptar los módulos de Cobros, Cuentas y Finanzas a la arquitectura multicomercio, incorporando aislamiento de datos, autenticación mediante JWT, control de permisos y protección de operaciones financieras sensibles.

---

## 1. Cobros

Se adaptó el módulo de cobros para trabajar dentro del comercio correspondiente al usuario autenticado.

### Mejoras implementadas

- Incorporación de `id_comercio` en los cobros.
- Aislamiento de consultas por comercio.
- Registro de cobros mediante RPC transaccional.
- Validación del cliente, cuenta y usuario dentro del mismo comercio.
- El `id_usuario` utilizado para registrar el cobro se obtiene desde el JWT.
- El `id_comercio` se obtiene desde el JWT.
- El backend no confía en valores sensibles enviados por el frontend.
- Registro automático del movimiento financiero asociado.
- Actualización automática del saldo de la cuenta.
- Anulación de cobros mediante RPC.
- Reversión del saldo financiero al anular.
- Registro del usuario responsable de la anulación.
- Protección contra doble anulación.
- La anulación de cobros queda reservada exclusivamente al propietario.

### Permisos

Los empleados pueden acceder según los permisos:

- `cobros.ver`
- `cobros.registrar`
- `clientes.ver_deuda`

La anulación de cobros es exclusiva del propietario.

---

## 2. Cuentas financieras

Se adaptó el módulo de cuentas para trabajar de manera independiente dentro de cada comercio.

### Mejoras implementadas

- Cada cuenta pertenece a un `id_comercio`.
- Las consultas quedan limitadas al comercio autenticado.
- Creación de cuentas con saldo inicial igual a 0.
- Activación y desactivación de cuentas.
- Una cuenta con saldo disponible no puede ser desactivada.
- Ajustes manuales de saldo.
- Registro automático de movimientos financieros.
- Identificación del usuario responsable mediante JWT.
- El backend ignora cualquier `id_usuario` manipulado desde el frontend.
- Consulta del historial de movimientos por cuenta.

### Seguridad

Los empleados autenticados pueden consultar las cuentas disponibles para utilizarlas en operaciones comerciales.

Las operaciones administrativas quedan reservadas al propietario:

- Crear cuentas.
- Editar cuentas.
- Cambiar estado.
- Ajustar saldo.
- Consultar historial administrativo.

---

## 3. Finanzas

Se adaptó completamente el módulo financiero a la arquitectura multicomercio.

### Mejoras implementadas

Todas las consultas financieras reciben el `id_comercio` correspondiente al usuario autenticado.

Se adaptaron:

- Rentabilidad.
- Caja.
- Estadísticas de ventas.
- Evolución de ventas.
- Estadísticas de productos.
- Estadísticas de proveedores.
- Estadísticas de clientes.
- Valorización financiera del stock.
- Dashboard financiero.

El dashboard consolida información exclusivamente del comercio autenticado.

### Seguridad

Todos los endpoints `/finanzas/*` requieren:

1. JWT válido.
2. Usuario activo.
3. Comercio activo.
4. Ser propietario del comercio.

Los empleados no pueden acceder a información financiera global.

---

## 4. Base de datos

Se realizaron las modificaciones necesarias para completar el aislamiento multicomercio.

### Cobros

Se incorporó:

- `id_comercio`.
- Foreign Key con comercios.
- Índices para consultas por comercio y cliente.
- Migración de los cobros históricos al comercio correspondiente.

### RPC registrar_cobro

La función valida:

- Usuario.
- Comercio.
- Cliente.
- Cuenta.
- Monto.
- Estado de las entidades.
- Pertenencia al mismo comercio.

Luego ejecuta de manera transaccional:

1. Registro del cobro.
2. Actualización del saldo de la cuenta.
3. Registro del movimiento financiero.

### RPC anular_cobro

La función valida:

- Cobro existente.
- Comercio correspondiente.
- Usuario responsable.
- Estado del cobro.
- Cuenta financiera.
- Fondos disponibles.
- Motivo de anulación.

Luego:

1. Anula el cobro.
2. Revierte el saldo.
3. Registra el movimiento financiero de anulación.

---

## 5. Pruebas realizadas con Postman

Se verificaron los principales escenarios funcionales y de seguridad.

### Cobros

- Empleado autorizado puede listar cobros.
- Empleado autorizado puede registrar cobros.
- Se enviaron intencionalmente `id_usuario = 999` e `id_comercio = 999`.
- El backend ignoró los valores manipulados.
- El cobro quedó registrado con el usuario y comercio obtenidos desde el JWT.
- Consulta individual de cobro funcionando.
- Consulta de saldo de cliente funcionando.
- Empleado no puede anular cobros.
- Propietario puede anular cobros.
- No se permite volver a anular un cobro ya anulado.

### Cuentas

- Empleado puede consultar cuentas.
- Empleado no puede crear cuentas.
- Propietario puede crear cuentas.
- Propietario puede ajustar saldos.
- Se comprobó que un `id_usuario` manipulado desde el frontend es ignorado.
- Los movimientos registraron correctamente al usuario autenticado.
- Ajuste de entrada funcionando.
- Ajuste de salida funcionando.
- Consulta de movimientos funcionando.
- Empleado no puede desactivar cuentas.
- No se permite desactivar una cuenta con saldo disponible.
- Propietario puede desactivar una cuenta con saldo 0.

### Finanzas

- Empleado intentando acceder al dashboard recibe `403 Forbidden`.
- Propietario puede acceder al dashboard.
- Dashboard financiero funcionando correctamente bajo arquitectura multicomercio.

---

## 6. Arquitectura de seguridad resultante

El flujo utilizado queda:

Route
→ autenticación JWT
→ autorización/permisos
→ Controller
→ Service
→ Model
→ Supabase/PostgreSQL

Los datos sensibles como:

- `id_usuario`
- `id_comercio`

no dependen de información enviada por el frontend.

Se obtienen del usuario autenticado mediante el JWT y el contexto de Flask.

Esto evita que un usuario pueda modificar manualmente una petición para operar como otro usuario o acceder a información perteneciente a otro comercio.

---

## Estado final

Cobros: COMPLETADO

Cuentas: COMPLETADO

Finanzas: COMPLETADO

Seguridad JWT: COMPLETADA

Permisos: COMPLETADOS

Aislamiento multicomercio: COMPLETADO

Entrega 30 finalizada correctamente.