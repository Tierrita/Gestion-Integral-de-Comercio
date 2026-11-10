import { useState } from 'react'
import { api } from './shared/api/client.js'

export default function App() {
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [profile, setProfile] = useState(null)

  async function handleLogin(event) {
    event.preventDefault()
    if (submitting) return

    const form = event.currentTarget
    const fields = new FormData(form)

    setSubmitting(true)
    setErrorMessage('')

    try {
      const { data } = await api.post('/auth/login', {
        email: fields.get('email').trim(),
        password: fields.get('password'),
      })

      if (!data?.token || !data.usuario || !data.comercio) {
        setErrorMessage('La API devolvió una respuesta de acceso incompleta.')
        return
      }

      form.reset()
      setProfile({
        name: data.usuario.nombre_completo || data.usuario.email,
        business: data.comercio.nombre_comercio,
      })
    } catch (error) {
      const status = error.response?.status

      if (status === 400 || status === 403) {
        setErrorMessage(error.response.data?.error || 'Flask rechazó el acceso.')
      } else if (!status || status === 502 || status === 504) {
        setErrorMessage('No se pudo conectar con Flask. Verificá que esté activo.')
      } else {
        setErrorMessage('No pudimos iniciar sesión. Volvé a intentar.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main>
      <h1>Gestión Integral de Comercio</h1>

      {profile ? (
        <p role="status">
          Acceso verificado para {profile.name} en {profile.business}.
        </p>
      ) : (
        <form onSubmit={handleLogin}>
          <p>
            <label htmlFor="email">Correo electrónico</label>
            <br />
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="username"
              required
            />
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
          {errorMessage && <p role="alert">{errorMessage}</p>}
        </form>
      )}
    </main>
  )
}