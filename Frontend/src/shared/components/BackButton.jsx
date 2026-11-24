import { useNavigate } from 'react-router-dom'
import styles from './BackButton.module.css'

/** Navegación de regreso consistente; destino explícito para evitar salir del módulo. */
export default function BackButton({ to, label = 'Volver', disabled = false }) {
  const navigate = useNavigate()

  return (
    <button
      type="button"
      className={styles.button}
      onClick={() => navigate(to)}
      disabled={disabled}
    >
      <span aria-hidden="true">←</span>
      {label}
    </button>
  )
}
