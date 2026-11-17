import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import styles from './Inventario.module.css'
import h from './HistorialMovimientos.module.css'
import MercaderiaNav from '../productos/MercaderiaNav.jsx'

const stamp = (row) => row.fecha_movimiento ?? row.fecha ?? row.created_at ?? ''
const formatDate = (value) => {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? String(value) : new Intl.DateTimeFormat('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }).format(date).replace(',', ' ·')
}
const signedChange = (row) => {
  const before = Number(row.stock_anterior)
  const after = Number(row.stock_nuevo)
  if (Number.isFinite(before) && Number.isFinite(after) && row.stock_anterior != null && row.stock_nuevo != null) return after - before
  return null
}
const responsibleLabel = (row) => row.nombre_responsable || (row.id_usuario == null ? 'Sin identificar' : 'Usuario #' + row.id_usuario)
const movementLabel = (value) => String(value ?? 'SIN TIPO').replaceAll('_', ' ')
const isPositive = (row) => signedChange(row) > 0
const isNegative = (row) => signedChange(row) < 0
const exportCell = (value) => '"' + String(value ?? '').replaceAll('"', '""') + '"'

export default function HistorialMovimientos() {
  const [rows, setRows] = useState([])
  const [products, setProducts] = useState([])
  const [productId, setProductId] = useState('')
  const [type, setType] = useState('')
  const [direction, setDirection] = useState('')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [userId, setUserId] = useState('')
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [refresh, setRefresh] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    async function load() {
      try {
        const [history, stock] = await Promise.all([
          api.get('/stock/historial', { signal: controller.signal }),
          api.get('/stock', { signal: controller.signal }),
        ])
        if (!Array.isArray(history.data) || !Array.isArray(stock.data)) throw new Error('Formato inesperado')
        if (!controller.signal.aborted) {
          setRows(history.data)
          setProducts(stock.data)
          setError('')
        }
      } catch (err) {
        if (!controller.signal.aborted) setError(err.response?.data?.error || 'No se pudo consultar el historial. Revisá la conexión con Flask.')
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }
    void load()
    return () => controller.abort()
  }, [refresh])

  const filtered = useMemo(() => rows.filter((row) => {
    const date = stamp(row)
    const day = date ? date.slice(0, 10) : ''
    const change = signedChange(row)
    return (!productId || String(row.id_producto) === productId)
      && (!type || row.tipo_movimiento === type)
      && (!userId || String(row.id_usuario ?? '') === userId)
      && (!from || (day && day >= from))
      && (!to || (day && day <= to))
      && (!direction || (direction === 'entrada' ? change > 0 : change < 0))
  }).sort((a, b) => (Date.parse(stamp(b)) || 0) - (Date.parse(stamp(a)) || 0)), [rows, productId, type, direction, from, to, userId])

  const types = [...new Set(rows.map((row) => row.tipo_movimiento).filter(Boolean))].sort()
  const users = [...new Set(rows.map((row) => row.id_usuario).filter((id) => id != null))].sort((a, b) => Number(a) - Number(b))
  const entries = filtered.filter(isPositive).length
  const exits = filtered.filter(isNegative).length
  const hasFilters = Boolean(productId || type || direction || from || to || userId)

  function clearFilters() {
    setProductId('')
    setType('')
    setDirection('')
    setFrom('')
    setTo('')
    setUserId('')
  }

  function exportCsv() {
    const header = ['Fecha', 'Producto', 'Tipo', 'Cantidad', 'Stock anterior', 'Stock nuevo', 'Responsable', 'Usuario ID', 'Observaciones']
    const data = filtered.map((row) => [formatDate(stamp(row)), row.nombre_producto, movementLabel(row.tipo_movimiento), row.cantidad, row.stock_anterior, row.stock_nuevo, responsibleLabel(row), row.id_usuario, row.observaciones])
    const csv = '\uFEFF' + [header, ...data].map((line) => line.map(exportCell).join(';')).join('\r\n')
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = 'historial-inventario.csv'
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
  }

  return <section className={styles.page}>
    <MercaderiaNav />
    <header className={styles.heading}>
      <div>
        <p className={styles.eyebrow}>INVENTARIO / AUDITORÍA</p>
        <h1>Historial de movimientos</h1>
        <p className={styles.muted}>Trazabilidad de compras, ventas, anulaciones y ajustes de stock.</p>
      </div>
      <div className={h.headerActions}>
        <Link className={styles.secondary} to="/inventario">← Volver a inventario</Link>
        <button type="button" className={styles.secondary} disabled={loading} onClick={() => { setLoading(true); setRefresh((n) => n + 1) }}>↻ Actualizar</button>
        <button type="button" className={styles.primary} disabled={loading || !filtered.length} onClick={exportCsv}>Exportar CSV</button>
      </div>
    </header>

    <div className={h.metrics}>
      <div><span>Movimientos encontrados</span><strong>{loading ? '—' : filtered.length}</strong></div>
      <div><span>Entradas de stock</span><strong className={h.positive}>{loading ? '—' : entries}</strong></div>
      <div><span>Salidas de stock</span><strong className={h.negative}>{loading ? '—' : exits}</strong></div>
    </div>

    <section className={styles.panel}>
      <div className={h.filters}>
        <label>Producto<select value={productId} onChange={(e) => setProductId(e.target.value)}><option value="">Todos los productos</option>{products.map((p) => <option key={p.id_producto} value={String(p.id_producto)}>{p.nombre_producto}</option>)}</select></label>
        <label>Tipo<select value={type} onChange={(e) => setType(e.target.value)}><option value="">Todos los tipos</option>{types.map((t) => <option key={t} value={t}>{movementLabel(t)}</option>)}</select></label>
        <label>Dirección<select value={direction} onChange={(e) => setDirection(e.target.value)}><option value="">Entradas y salidas</option><option value="entrada">Solo entradas (+)</option><option value="salida">Solo salidas (−)</option></select></label>
        <label>Desde<input type="date" value={from} max={to || undefined} onChange={(e) => setFrom(e.target.value)} /></label>
        <label>Hasta<input type="date" value={to} min={from || undefined} onChange={(e) => setTo(e.target.value)} /></label>
        <label>Usuario<select value={userId} onChange={(e) => setUserId(e.target.value)}><option value="">Todos los usuarios</option>{users.map((id) => <option key={id} value={String(id)}>{responsibleLabel(rows.find((row) => row.id_usuario === id) || { id_usuario: id })}</option>)}</select></label>
        {hasFilters && <button type="button" className={styles.secondary} onClick={clearFilters}>Limpiar filtros</button>}
      </div>
      {error && <p className={styles.error} role="alert">{error}</p>}
      {loading ? <p className={styles.empty}>Consultando movimientos…</p> : error ? <p className={styles.empty}>No se pudo actualizar el historial.</p> : !filtered.length ? <p className={styles.empty}>No hay movimientos que coincidan con los filtros.</p> : <div className={styles.scroll}>
        <table className={h.table}>
          <thead><tr><th>Fecha</th><th>Producto</th><th>Movimiento</th><th>Cambio</th><th>Stock anterior</th><th>Stock nuevo</th><th>Responsable</th><th>Detalle</th></tr></thead>
          <tbody>{filtered.map((row, index) => {
            const change = signedChange(row)
            return <tr key={row.id_movimiento ?? index}>
              <td>{formatDate(stamp(row))}</td>
              <td><strong>{row.nombre_producto ?? ('Producto #' + row.id_producto)}</strong><small>#{row.numero_producto ?? row.id_producto}</small></td>
              <td><span className={isPositive(row) ? h.entryBadge : isNegative(row) ? h.exitBadge : h.neutralBadge}>{movementLabel(row.tipo_movimiento)}</span></td>
              <td><strong className={isPositive(row) ? h.positive : isNegative(row) ? h.negative : ''}>{change === null ? row.cantidad ?? '—' : (change > 0 ? '+' : '') + change}</strong></td>
              <td>{row.stock_anterior ?? '—'}</td><td>{row.stock_nuevo ?? '—'}</td><td>{responsibleLabel(row)}</td>
              <td><button type="button" className={h.detailButton} onClick={() => setSelected(row)}>Ver detalle</button></td>
            </tr>
          })}</tbody>
        </table>
      </div>}
      {!loading && !error && <p className={h.footer}>Se muestran {filtered.length} movimientos de los {rows.length} recibidos del servidor. Los filtros y el CSV se aplican a esos registros.</p>}
    </section>

    {selected && <div className={styles.overlay} onMouseDown={(e) => { if (e.target === e.currentTarget) setSelected(null) }}>
      <section className={styles.dialog} role="dialog" aria-modal="true" aria-labelledby="movement-title">
        <div className={styles.dialogHead}><h2 id="movement-title">Detalle del movimiento</h2><button type="button" className={styles.secondary} onClick={() => setSelected(null)} aria-label="Cerrar detalle">✕</button></div>
        <dl className={h.detailGrid}>
          <div><dt>Producto</dt><dd>{selected.nombre_producto ?? ('#' + selected.id_producto)}</dd></div>
          <div><dt>Fecha</dt><dd>{formatDate(stamp(selected))}</dd></div>
          <div><dt>Operación</dt><dd>{movementLabel(selected.tipo_movimiento)}</dd></div>
          <div><dt>Responsable</dt><dd>{responsibleLabel(selected)}{selected.id_usuario != null ? ' (#' + selected.id_usuario + ')' : ''}</dd></div>
          <div><dt>Cantidad registrada</dt><dd>{selected.cantidad ?? '—'}</dd></div>
          <div><dt>Variación real</dt><dd>{signedChange(selected) ?? '—'}</dd></div>
          <div><dt>Stock anterior</dt><dd>{selected.stock_anterior ?? '—'}</dd></div>
          <div><dt>Stock nuevo</dt><dd>{selected.stock_nuevo ?? '—'}</dd></div>
          <div className={h.fullWidth}><dt>Observaciones</dt><dd className={h.notes}>{selected.observaciones || 'Sin observaciones'}</dd></div>
        </dl>
      </section>
    </div>}
  </section>
}
