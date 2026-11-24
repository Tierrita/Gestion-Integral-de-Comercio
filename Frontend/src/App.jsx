import AuthPage from './pages/AuthPage.jsx'
import { useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { api, clearToken, readToken, saveToken } from './shared/api/client.js'
import PrivateLayout from './app/PrivateLayout.jsx'
import OwnerDashboard from './features/dashboard/OwnerDashboard.jsx'
import Productos from './features/productos/Productos.jsx'
import Inventario from './features/inventario/Inventario.jsx'
import HistorialMovimientos from './features/inventario/HistorialMovimientos.jsx'
import ProductoFormulario from './features/productos/ProductoFormulario.jsx'
import Ventas from './features/ventas/Ventas.jsx'
import NuevaVenta from './features/ventas/NuevaVenta.jsx'
import ComprobanteVenta from './features/ventas/ComprobanteVenta.jsx'
import Compras from './features/compras/Compras.jsx'
import NuevaCompra from './features/compras/NuevaCompra.jsx'
import Clientes from './features/clientes/Clientes.jsx'
import Categorias from './features/categorias/Categorias.jsx'
import Proveedores from './features/proveedores/Proveedores.jsx'


function SessionRoutes() {
  const [token, setToken] = useState(readToken)
  const [profile, setProfile] = useState(null)
  const [notice, setNotice] = useState('')
  const [validationError, setValidationError] = useState('')
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    if (!token) return

    const controller = new AbortController()

    async function validateSession() {
      try {
        const { data } = await api.get('/auth/me', { signal: controller.signal })
        if (controller.signal.aborted) return

        if (!data?.usuario || !data.comercio) {
          setValidationError('Flask devolvió un perfil incompleto.')
          return
        }

        setProfile(data)
      } catch (error) {
        if (controller.signal.aborted) return

        const status = error.response?.status
        if (status === 401 || status === 403) {
          clearToken()
          setToken(null)
          setProfile(null)
          setNotice(
            status === 401
              ? 'Tu sesión venció o dejó de ser válida. Volvé a ingresar.'
              : error.response.data?.error || 'Tu cuenta ya no tiene acceso.',
          )
          return
        }

        setValidationError('No pudimos validar tu sesión. Verificá que Flask esté activo.')
      }
    }

    validateSession()
    return () => controller.abort()
  }, [token, attempt])

  function handleLogin(newToken) {
    saveToken(newToken)
    setNotice('')
    setValidationError('')
    setToken(newToken)
  }

  function handleLogout() {
  clearToken()
  setToken(null)
  setProfile(null)
  setValidationError('')
  setNotice('Cerraste sesión.')
}


  function retryValidation() {
    setValidationError('')
    setAttempt((previous) => previous + 1)
  }

  if (token && !profile) {
    return (
      <main>
        <h1>Gestión Integral de Comercio</h1>
        {validationError ? (
          <>
            <p role="alert">{validationError}</p>
            <button type="button" onClick={retryValidation}>Reintentar</button>
          </>
        ) : (
          <p role="status">Validando sesión…</p>
        )}
      </main>
    )
  }

  return (
    <Routes>
      <Route
        path="/login/*"
        element={profile ? <Navigate to="/inicio" replace /> : (
          <AuthPage notice={notice} onLogin={handleLogin} />
        )}
      />
      <Route
  element={profile ? <PrivateLayout profile={profile} onLogout={handleLogout} /> : <Navigate to="/login" replace />}
>
  <Route
    path="/inicio"
    element={
      profile?.usuario.es_propietario === true ? (
        <OwnerDashboard />
      ) : (
        <section>
          <h1>Inicio</h1>
          <p>Comercio activo: {profile?.comercio.nombre_comercio}</p>
        </section>
      )
    }
  />
  <Route path="/productos" element={<Productos />} />
  <Route path="/inventario" element={<Inventario />} />
  <Route path="/inventario/historial" element={<HistorialMovimientos />} />
  <Route path="/productos/nuevo" element={<ProductoFormulario />} />
  <Route path="/productos/:id/editar" element={<ProductoFormulario />} />
  <Route path="/ventas"
    element={
      <Ventas
        esPropietario={profile?.usuario?.es_propietario === true}
      />
    }
  />
  <Route path="/ventas/nueva" element={<NuevaVenta />} />
  <Route path="/ventas/:id/comprobante" element={<ComprobanteVenta />} />
  <Route path="/clientes" element={<Clientes esPropietario={profile?.usuario?.es_propietario === true} />} />
  <Route path="/categorias" element={<Categorias />} />
  <Route path="/proveedores" element={<Proveedores esPropietario={profile?.usuario?.es_propietario === true} />} />
  <Route path="/compras" element={<Compras esPropietario={profile?.usuario?.es_propietario === true} />} />
  <Route path="/compras/nueva" element={<NuevaCompra />} />
  <Route path="/perfil"
    element={
      <section>
        <h1>Mi perfil</h1>
        <dl>
          <dt>Nombre</dt>
          <dd>{profile?.usuario.nombre_completo || profile?.usuario.email}</dd>

          <dt>Correo electrónico</dt>
          <dd>{profile?.usuario.email}</dd>

          <dt>Comercio</dt>
          <dd>{profile?.comercio.nombre_comercio}</dd>

          <dt>Tipo de cuenta</dt>
          <dd>{profile?.usuario.es_propietario ? 'Propietario' : 'Empleado'}</dd>
        </dl>
      </section>
    }
  />
</Route>
      <Route path="/" element={<Navigate to={profile ? '/inicio' : '/login'} replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <SessionRoutes />
    </BrowserRouter>
  )
}