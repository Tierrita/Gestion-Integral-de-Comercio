import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import Modal from '../../shared/components/Modal.jsx'
import Alert from '../../shared/components/Alert.jsx'
import ActionButton from '../../shared/components/ActionButton.jsx'
import { formatoMoneda } from '../../shared/utils/formatters.js'
import styles from './DetalleProducto.module.css'
import StockAdjustmentFields from '../../shared/components/StockAdjustmentFields.jsx'
import { formatStockQuantity, parseStockQuantity, validStockQuantity } from '../../shared/utils/stockQuantity.js'

const errorOf = (error) => error.response?.data?.error || (error.response?.status === 403 ? 'No tenés permiso para ajustar el stock.' : 'No se pudo completar la operación.')
export default function DetalleProducto({ producto, onClose, onUpdated, onStatus }) {
  const [type, setType] = useState('AUMENTAR')
  const [amount, setAmount] = useState('')
  const [adjusting, setAdjusting] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [stock, setStock] = useState(null)
  const [stockLoading, setStockLoading] = useState(true)
  const [stockError, setStockError] = useState('')
  const [historyOpen, setHistoryOpen] = useState(false)
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState('')

  useEffect(() => {
    if (!producto) return
    let active = true
    api.get('/stock').then(({ data }) => {
      if (!active) return
      if (!Array.isArray(data)) throw new Error('Formato de existencias inválido')
      const item = data.find((row) => String(row.id_producto) === String(producto.id_producto))
      if (!item || item.stock == null || !Number.isFinite(Number(item.stock))) throw new Error('No se pudo obtener el stock actualizado de este producto.')
      setStock(item)
    }).catch((err) => {
      if (active) setStockError(err.response ? errorOf(err) : (err.message || 'No se pudo consultar el stock actualizado.'))
    }).finally(() => { if (active) setStockLoading(false) })
    return () => { active = false }
  }, [producto])

  async function loadHistory() {
    if (!producto) return
    setHistoryLoading(true)
    setHistoryError('')
    try {
      const { data } = await api.get('/stock/historial')
      if (!Array.isArray(data)) throw new Error('Formato de historial inválido')
      setHistory(data.filter((row) => String(row.id_producto) === String(producto.id_producto)).sort((a, b) => (Date.parse(b.fecha_movimiento ?? b.fecha ?? b.created_at) || 0) - (Date.parse(a.fecha_movimiento ?? a.fecha ?? a.created_at) || 0)))
    } catch (err) {
      setHistoryError(errorOf(err))
    } finally {
      setHistoryLoading(false)
    }
  }

  if (!producto) return null
  const current = stock ?? producto
  const unit = producto.unidad_de_medida
  const quantity = parseStockQuantity(amount)
  const valid = validStockQuantity(amount, unit)
  const exceeds = type === 'DISMINUIR' && valid && quantity > Number(current.stock)
  const projected = valid && !exceeds ? Math.round((Number(current.stock) + (type === 'AUMENTAR' ? quantity : -quantity)) * 1000) / 1000 : null

  async function submit(event) {
    event.preventDefault()
    if (saving || producto.estado === false || stockLoading || stockError || !stock || !valid || exceeds) return
    setSaving(true)
    setError('')
    setNotice('')
    try {
      const { data } = await api.patch(`/stock/${producto.id_producto}/ajustar`, { cantidad: quantity, tipo_ajuste: type })
      setNotice(data.message || 'Stock actualizado correctamente.')
      setStock((previous) => ({ ...current, ...previous, stock: data.data?.stock_nuevo ?? projected }))
      setAmount('')
      setAdjusting(false)
      try { await onUpdated?.() } catch { setError('El ajuste se guardó, pero no se pudo actualizar el listado. Usá Actualizar para sincronizarlo.') }
      if (historyOpen) void loadHistory()
    } catch (err) {
      setError(errorOf(err))
    } finally {
      setSaving(false)
    }
  }

  return <Modal open={Boolean(producto)} onClose={onClose} busy={saving} size="large" title={producto.nombre_producto} description={`Detalle comercial · Producto N.º ${producto.numero_producto ?? '—'}`}>
    <div className={styles.content}>
      {notice && <Alert type="success">{notice}</Alert>}
      {error && !adjusting && <Alert type="error">{error}</Alert>}
      {stockLoading && <Alert type="info">Consultando el stock actualizado…</Alert>}
      {stockError && <Alert type="error">{stockError} Cerrá y volvé a abrir el detalle para reintentar.</Alert>}
      <div className={styles.metrics}>
        <article><span>Stock actual</span><strong>{formatStockQuantity(current.stock, unit)}</strong><small>Mínimo: {formatStockQuantity(producto.stock_minimo, unit)} {unit === 'KG' ? 'kg' : 'un.'}</small></article>
        <article><span>Precio de venta</span><strong>{formatoMoneda(producto.precio_venta)}</strong><small>Precio vigente</small></article>
        <article><span>Precio de costo</span><strong>{producto.precio_costo == null ? 'Sin acceso' : formatoMoneda(producto.precio_costo)}</strong><small>Según permisos</small></article>
      </div>
      <div className={styles.meta}>
        <div><span>Estado</span><strong>{producto.estado === false ? 'Inactivo' : 'Activo'}</strong></div>
        <div><span>Unidad</span><strong>{unit || '—'}</strong></div>
        <div><span>Situación</span><strong>{producto.estado === false ? 'Inactivo' : Number(current.stock) <= Number(producto.stock_minimo) ? 'Stock bajo' : 'Normal'}</strong></div>
      </div>
      {!adjusting ? <div className={styles.actions}>
        <ActionButton variant="primary" disabled={producto.estado === false || stockLoading || Boolean(stockError) || !stock} onClick={() => { setAdjusting(true); setError(''); setNotice('') }}>Ajustar stock</ActionButton>
        <ActionButton variant="secondary" type="button" onClick={() => { if (!historyOpen) void loadHistory(); setHistoryOpen(!historyOpen) }}>{historyOpen ? 'Ocultar movimientos' : 'Ver movimientos'}</ActionButton>
        <ActionButton as={Link} variant="secondary" to={`/productos/${producto.id_producto}/editar`}>Editar producto</ActionButton>
      </div> : <StockAdjustmentFields unit={unit} currentStock={current.stock} type={type} onTypeChange={(value) => { setType(value); setError('') }} amount={amount} onAmountChange={(value) => { setAmount(value); setError('') }} onSubmit={submit} onCancel={() => { setAdjusting(false); setError('') }} saving={saving} error={error} />}
      {!adjusting && <div className={styles.statusAction}>
        <button type="button" onClick={() => onStatus(producto)}><span aria-hidden="true">{producto.estado === false ? '↻' : '⊘'}</span>{producto.estado === false ? 'Activar' : 'Desactivar'}</button>
      </div>}
      {historyOpen && <section className={styles.history} aria-label="Historial de movimientos del producto">
        <div className={styles.historyHead}><h3>Movimientos recientes</h3><ActionButton variant="secondary" size="compact" type="button" disabled={historyLoading} onClick={() => void loadHistory()}>Actualizar</ActionButton></div>
        {historyError && <Alert type="error">{historyError}</Alert>}
        {historyLoading ? <p role="status">Consultando movimientos…</p> : !historyError && history.length === 0 ? <p>No hay movimientos registrados para este producto.</p> : !historyError && <div className={styles.historyScroll}><table><thead><tr><th>Fecha</th><th>Tipo</th><th>Variación</th><th>Stock resultante</th></tr></thead><tbody>{history.slice(0, 10).map((row, index) => {
          const before = Number(row.stock_anterior)
          const after = Number(row.stock_nuevo)
          const difference = row.stock_anterior != null && row.stock_nuevo != null && Number.isFinite(before) && Number.isFinite(after) ? Math.round((after - before) * 1000) / 1000 : null
          const rawDate = row.fecha_movimiento ?? row.fecha ?? row.created_at
          const date = rawDate ? new Date(rawDate) : null
          const dateLabel = date && !Number.isNaN(date.getTime()) ? new Intl.DateTimeFormat('es-AR', { timeZone: 'America/Argentina/Buenos_Aires', dateStyle: 'short', timeStyle: 'short' }).format(date) : '—'
          return <tr key={row.id_movimiento ?? index}><td>{dateLabel}</td><td>{String(row.tipo_movimiento ?? 'Sin tipo').replaceAll('_', ' ')}</td><td className={difference > 0 ? styles.positive : difference < 0 ? styles.negative : ''}>{difference == null ? '—' : `${difference > 0 ? '+' : ''}${formatStockQuantity(difference, unit)}`}</td><td>{row.stock_nuevo == null ? '—' : formatStockQuantity(row.stock_nuevo, unit)}</td></tr>
        })}</tbody></table></div>}
        {!historyLoading && !historyError && history.length > 10 && <p className={styles.historyFoot}>Mostrando los últimos 10 de {history.length} movimientos. El historial completo sigue disponible en Mercadería → Movimientos.</p>}
      </section>}
    </div>
  </Modal>
}
