import { useNavigate } from 'react-router-dom'
import styles from './BackButton.module.css'

/**
 * Regresa a la pantalla anterior dentro del historial de React Router.
 * Si la página se abrió directamente, utiliza la ruta de respaldo indicada.
 */
export default function BackButton({ to = '/inicio', label = 'Volver', disabled = false }) {
  const navigate = useNavigate()

  function handleBack() {
    // React Router mantiene un índice para sus entradas de navegación.
    // Evita navigate(-1) cuando no existe una entrada anterior de la app.
    const historyIndex = window.history.state?.idx
    if (typeof historyIndex === 'number' && historyIndex > 0) {
      navigate(-1)
      return
    }
    navigate(to, { replace: true })
  }

  return (
    <button
      type="button"
      className={styles.button}
      onClick={handleBack}
      disabled={disabled}
    >
      <span aria-hidden="true">←</span>
      {label}
    </button>
  )
}
