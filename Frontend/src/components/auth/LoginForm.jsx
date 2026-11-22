import { useState } from 'react'
import { api } from '../../shared/api/client.js'

export default function LoginForm({ notice, onLogin }) {
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
        email: String(fields.get('email') || '').trim(),
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

  return <form className="aionix-login-form" onSubmit={handleSubmit}>
    {notice && !error && <p role="status" className="aionix-message">{notice}</p>}
    <label htmlFor="aionix-email">Correo electrónico</label>
    <input id="aionix-email" name="email" type="email" placeholder="Correo electrónico" autoComplete="username" required />
    <label htmlFor="aionix-password">Contraseña</label>
    <input id="aionix-password" name="password" type="password" placeholder="Contraseña" autoComplete="current-password" required />
    <button type="submit" className="aionix-primary-button" disabled={submitting}>
      {submitting ? 'Ingresando…' : 'Iniciar sesión'}
    </button>
    {error && <p role="alert" className="aionix-error">{error}</p>}
  </form>
}
