import { useEffect, useMemo, useState } from 'react'
import { api } from '../../shared/api/client.js'
import styles from './Inventario.module.css'

const formatDate = (row) => {
  const value = row.fecha_movimiento ?? row.fecha ?? row.created_at
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? String(value) : new Intl.DateTimeFormat('es-AR', { dateStyle: 'short', timeStyle: 'short' }).format(date)
}

export default function HistorialMovimientos({ products, onClose }) {
  const [rows, setRows] = useState([])
  const [productId, setProductId] = useState('')
  const [type, setType] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    async function load() {
      try {
        const { data } = await api.get('/stock/historial', { signal: controller.signal })
        if (!controller.signal.aborted) {
          if (!Array.isArray(data)) throw new Error('Formato inesperado')
          setRows(data)
        }
      } catch (err) {
        if (!controller.signal.aborted) setError(err.response?.data?.error || 'No se pudo cargar el historial.')
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }
    void load()
    return () => controller.abort()
  }, [])

  const filtered = useMemo(() => rows.filter((row) =>
    (!productId || String(row.id_producto) === productId) &&
    (!type || row.tipo_movimiento === type)
  ).sort((a, b) => {
    const dateA = Date.parse(a.fecha_movimiento ?? a.fecha ?? a.created_at ?? '') || 0
    const dateB = Date.parse(b.fecha_movimiento ?? b.fecha ?? b.created_at ?? '') || 0
    return dateB - dateA
  }), [rows, productId, type])

  const types = [...new Set(rows.map((r) => r.tipo_movimiento).filter(Boolean))].sort()

  return <section className={styles.panel}>
    <div className={styles.toolbar}>
      <div style={{ flex: '1 1 100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
        <div><h2 style={{ margin: 0 }}>Historial de movimientos</h2><p className={styles.muted}>Movimientos registrados de los productos de tu comercio.</p></div>
        <button type="button" className={styles.secondary} onClick={onClose}>Cerrar</button>
      </div>
      <label>Producto<select value={productId} onChange={(e) => setProductId(e.target.value)}><option value="">Todos los productos</option>{products.map((p) => <option key={p.id_producto} value={String(p.id_producto)}>{p.nombre_producto}</option>)}</select></label>
      <label>Movimiento<select value={type} onChange={(e) => setType(e.target.value)}><option value="">Todos los tipos</option>{types.map((t) => <option key={t} value={t}>{t.replaceAll('_', ' ')}</option>)}</select></label>
    </div>
    {error && <p role="alert" className={styles.error}>{error}</p>}
    {loading ? <p className={styles.empty}>Consultando movimientos…</p> : !filtered.length ? <p className={styles.empty}>No hay movimientos para estos filtros.</p> : <div className={styles.scroll}><table><thead><tr><th>Fecha</th><th>Producto</th><th>Tipo</th><th>Cantidad</th><th>Anterior</th><th>Nuevo</th><th>Usuario ID</th><th>Observaciones</th></tr></thead><tbody>{filtered.map((row, i) => <tr key={row.id_movimiento ?? i}><td>{formatDate(row)}</td><td>{row.nombre_producto ?? ('#' + row.id_producto)}</td><td>{String(row.tipo_movimiento ?? '—').replaceAll('_', ' ')}</td><td>{row.cantidad ?? '—'}</td><td>{row.stock_anterior ?? '—'}</td><td>{row.stock_nuevo ?? '—'}</td><td>{row.id_usuario ?? '—'}</td><td>{row.observaciones ?? '—'}</td></tr>)}</tbody></table></div>}
  </section>
}
