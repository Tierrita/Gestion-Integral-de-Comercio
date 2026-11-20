import Modal from './Modal.jsx'
import Alert from './Alert.jsx'
import styles from './ConfirmDialog.module.css'

export default function ConfirmDialog({
  open, onClose, onConfirm, title = '¿Confirmar operación?',
  description = 'Revisá los datos antes de continuar.',
  details = [], warning, error, busy = false,
  confirmLabel = 'Confirmar', cancelLabel = 'Cancelar',
  destructive = false,
}) {
  return (
    <Modal open={open} onClose={onClose} title={title} description={description}
      busy={busy} closeOnBackdrop={false} role="alertdialog" size="small">
      {details.length > 0 && (
        <dl className={styles.datos}>
          {details.map(({ label, value }) => (
            <div key={label}><dt>{label}</dt><dd>{value}</dd></div>
          ))}
        </dl>
      )}
      {warning && <Alert type="warning" title="Antes de continuar">{warning}</Alert>}
      {error && <Alert type="error">{error}</Alert>}
      <div className={styles.acciones}>
        <button type="button" className={styles.cancelar} onClick={onClose} disabled={busy}>{cancelLabel}</button>
        <button type="button" className={destructive ? styles.peligro : styles.confirmar}
          onClick={onConfirm} disabled={busy} aria-busy={busy}>
          {busy ? 'Procesando…' : confirmLabel}
        </button>
      </div>
    </Modal>
  )
}
