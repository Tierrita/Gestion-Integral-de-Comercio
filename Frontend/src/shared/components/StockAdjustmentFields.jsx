import ActionButton from './ActionButton.jsx'
import Alert from './Alert.jsx'
import styles from './StockAdjustmentFields.module.css'

export const formatStockQuantity = (value, unit) => new Intl.NumberFormat('es-AR', { maximumFractionDigits: unit === 'KG' ? 3 : 0 }).format(Number(value ?? 0))

export function validStockQuantity(value, unit) {
  if (!/^\\d+(?:\\.\\d+)?$/.test(String(value))) return false
  const number = Number(value)
  if (!Number.isFinite(number) || number <= 0) return false
  if (unit === 'KG') return Number.isSafeInteger(Math.round(number * 1000)) && Math.abs(number * 1000 - Math.round(number * 1000)) < 1e-7
  return unit === 'UNIDAD' && Number.isSafeInteger(number)
}

export default function StockAdjustmentFields({ unit, currentStock, type, onTypeChange, amount, onAmountChange, onSubmit, onCancel, saving = false, error = '' }) {
  const valid = validStockQuantity(amount, unit)
  const quantity = Number(amount)
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
        <input autoFocus type="number" min={unit === 'KG' ? '0.001' : '1'} step={unit === 'KG' ? '0.001' : '1'} required disabled={saving} value={amount} onChange={(event) => onAmountChange(event.target.value)} placeholder={unit === 'KG' ? 'Ej. 1.250' : 'Ej. 5'} />
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
