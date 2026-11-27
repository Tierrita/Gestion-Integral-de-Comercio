import ActionButton from './ActionButton.jsx'
import Alert from './Alert.jsx'
import styles from './StockAdjustmentFields.module.css'
import { formatStockQuantity, parseStockQuantity, validStockQuantity } from '../utils/stockQuantity.js'

export default function StockAdjustmentFields({ unit, currentStock, type, onTypeChange, amount, onAmountChange, onSubmit, onCancel, saving = false, error = '' }) {
  const valid = validStockQuantity(amount, unit)
  const quantity = parseStockQuantity(amount)
  const exceeds = type === 'DISMINUIR' && valid && quantity > Number(currentStock)
  const projected = valid && !exceeds && Number.isFinite(Number(currentStock))
    ? Math.round((Number(currentStock) + (type === 'AUMENTAR' ? quantity : -quantity)) * 1000) / 1000
    : null
  const suffix = unit === 'KG' ? 'kg' : 'un.'

  return <form className={styles.form} onSubmit={onSubmit}>
    <div className={styles.balance}>
      <span>Stock actual</span>
      <strong>{formatStockQuantity(currentStock, unit)} {suffix}</strong>
    </div>
    <div className={styles.fields}>
      <label>Tipo de movimiento
        <select value={type} disabled={saving} onChange={(event) => onTypeChange(event.target.value)}>
          <option value="AUMENTAR">Entrada (+)</option>
          <option value="DISMINUIR">Salida (−)</option>
        </select>
      </label>
      <label>Cantidad ({suffix})
        <input autoFocus type="text" inputMode={unit === 'KG' ? 'decimal' : 'numeric'} required disabled={saving} value={amount} onChange={(event) => onAmountChange(event.target.value)} placeholder={unit === 'KG' ? 'Ej. 1,250' : 'Ej. 5'} />
      </label>
    </div>
    {projected !== null && <div className={styles.balance}><span>Stock resultante</span><strong>{formatStockQuantity(projected, unit)} {suffix}</strong></div>}
    {exceeds && <Alert type="error">La salida supera el stock disponible.</Alert>}
    {error && <Alert type="error">{error}</Alert>}
    <div className={styles.actions}>
      <ActionButton variant="secondary" type="button" disabled={saving} onClick={onCancel}>Cancelar</ActionButton>
      <ActionButton variant="primary" type="submit" disabled={saving || !valid || exceeds || !Number.isFinite(Number(currentStock))}>{saving ? 'Guardando…' : 'Confirmar ajuste'}</ActionButton>
    </div>
  </form>
}
