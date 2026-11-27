import Modal from './Modal.jsx'
import Alert from './Alert.jsx'
import ActionButton from './ActionButton.jsx'
import styles from './ConfirmDialog.module.css'

export default function ConfirmDialog({
  open, onClose, onConfirm, title = '¿Confirmar operación?',
  description = 'Revisá los datos antes de continuar.',
  details = [], warning, error, busy = false,
  confirmLabel = 'Confirmar', cancelLabel = 'Cancelar',
  destructive = false,
}) {
  const handleClose = () => {
    if (!busy) onClose?.()
  }

  const handleConfirm = () => {
    if (!busy) onConfirm?.()
  }

  return (
    <Modal open={open} onClose={handleClose} title={title} description={description}
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
        <ActionButton type="button" variant="secondary" onClick={handleClose} disabled={busy}>{cancelLabel}</ActionButton>
        <ActionButton variant={destructive ? 'danger' : 'primary'}
          type="button" onClick={handleConfirm} disabled={busy} aria-busy={busy}>
          {busy ? 'Procesando…' : confirmLabel}
        </ActionButton>
      </div>
    </Modal>
  )
}
