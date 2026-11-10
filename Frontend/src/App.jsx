import { useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { api, clearToken, readToken, saveToken } from './shared/api/client.js'
import PrivateLayout from './app/PrivateLayout.jsx'

function Login({ notice, onLogin }) {
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    if (submitting) return

    const form = event.currentTarget
    const fields = new FormData(form)

    setSubmitting(true)
    setError('')

    try {
      const { data } = await api.post('/auth/login', {
        email: fields.get('email').trim(),
        password: fields.get('password'),
      })

      if (typeof data?.token !== 'string' || !data.token) {
        setError('Flask devolvió una respuesta de acceso incompleta.')
        return
      }

      form.reset()
      onLogin(data.token)
    } catch (error) {
      const status = error.response?.status

      if (status === 400 || status === 403) {
        setError(error.response.data?.error || 'Flask rechazó el acceso.')
      } else if (!status || status === 502 || status === 504) {
        setError('No se pudo conectar con Flask. Verificá que esté activo.')
      } else {
        setError('No pudimos iniciar sesión. Volvé a intentar.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main>
      <h1>Gestión Integral de Comercio</h1>
      {notice && !error && <p role="status">{notice}</p>}
      <form onSubmit={handleSubmit}>
        <p>
          <label htmlFor="email">Correo electrónico</label>
          <br />
          <input id="email" name="email" type="email" autoComplete="username" required />
        </p>
        <p>
          <label htmlFor="password">Contraseña</label>
          <br />
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
          />
        </p>
        <button type="submit" disabled={submitting}>
          {submitting ? 'Ingresando…' : 'Ingresar'}
        </button>
        {error && <p role="alert">{error}</p>}
      </form>
    </main>
  )
}

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
        path="/login"
        element={profile ? <Navigate to="/inicio" replace /> : (
          <Login notice={notice} onLogin={handleLogin} />
        )}
      />
      <Route
  element={profile ? <PrivateLayout profile={profile} /> : <Navigate to="/login" replace />}
>
  <Route
    path="/inicio"
    element={
      <section>
        <h1>Inicio</h1>
        <p>Comercio activo: {profile?.comercio.nombre_comercio}</p>
      </section>
    }
  />
  <Route
    path="/perfil"
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