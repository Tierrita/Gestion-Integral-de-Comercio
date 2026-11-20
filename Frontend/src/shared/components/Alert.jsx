import styles from './Alert.module.css'

const tipos = {
  success: { icono: '✓', titulo: 'Operación completada', rol: 'status' },
  error: { icono: '!', titulo: 'No se pudo completar la operación', rol: 'alert' },
  warning: { icono: '!', titulo: 'Revisá los datos', rol: 'alert' },
  info: { icono: 'i', titulo: 'Información', rol: 'status' },
}

export default function Alert({ type = 'info', title, children, onClose, className = '' }) {
  const tipo = tipos[type] || tipos.info
  return (
    <div className={`${styles.alert} ${styles[type] || styles.info} ${className}`.trim()} role={tipo.rol}>
      <span className={styles.icono} aria-hidden="true">{tipo.icono}</span>
      <div className={styles.contenido}>
        <strong>{title || tipo.titulo}</strong>
        {children && <div className={styles.descripcion}>{children}</div>}
      </div>
      {onClose && (
        <button className={styles.cerrar} type="button" onClick={onClose} aria-label="Cerrar aviso">×</button>
      )}
    </div>
  )
}
