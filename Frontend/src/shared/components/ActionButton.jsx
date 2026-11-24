import styles from './ActionButton.module.css'

/** Botón reutilizable para acciones comerciales; conserva eventos y atributos nativos. */
export default function ActionButton({ variant = 'secondary', size = 'default', className = '', type = 'button', children, ...props }) {
  const variantClass = variant === 'primary' ? styles.primary : variant === 'danger' ? styles.danger : styles.secondary
  return <button type={type} className={`${styles.button} ${variantClass} ${size === 'compact' ? styles.compact : ''} ${className}`.trim()} {...props}>{children}</button>
}
