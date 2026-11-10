import { useState } from 'react'
import { api } from './shared/api/client.js'

export default function App() {
  const [checking, setChecking] = useState(false)
  const [message, setMessage] = useState('')

  async function checkConnection() {
    setChecking(true)
    setMessage('')

    try {
      const { data } = await api.get('/')
      setMessage(data?.message ?? 'La API devolvió una respuesta inesperada.')
    } catch (error) {
      setMessage(
        error.response
          ? `La API o el proxy respondió con HTTP ${error.response.status}.`
          : 'No se pudo obtener respuesta. Revisá que Vite y Flask estén activos.',
      )
    } finally {
      setChecking(false)
    }
  }

  return (
    <main>
      <h1>Gestión Integral de Comercio</h1>
      <button type="button" onClick={checkConnection} disabled={checking}>
        {checking ? 'Comprobando…' : 'Probar conexión con Flask'}
      </button>
      <p role="status">{message}</p>
    </main>
  )
}