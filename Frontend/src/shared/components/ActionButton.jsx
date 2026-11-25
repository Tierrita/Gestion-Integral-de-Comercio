import styles from './ActionButton.module.css'

/** Acciones y enlaces de navegación con una apariencia visual uniforme. */
export default function ActionButton({ as: Component = 'button', variant = 'secondary', size = 'default', className = '', type = 'button', children, ...props }) {
  const variantClass = variant === 'primary' ? styles.primary : variant === 'danger' ? styles.danger : styles.secondary
  const classes = `${styles.button} ${variantClass} ${size === 'compact' ? styles.compact : ''} ${className}`.trim()
  if (Component === 'button') {
    return <button type={type} className={classes} {...props}>{children}</button>
  }
  return <Component className={classes} {...props}>{children}</Component>
}
