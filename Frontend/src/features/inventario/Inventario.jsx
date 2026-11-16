import { useEffect, useMemo, useState } from 'react'
import { api } from '../../shared/api/client.js'
import styles from './Inventario.module.css'

const errorText = (error) => error.response?.data?.error || (error.response?.status === 403 ? 'Tu usuario no tiene permiso para realizar esta operación.' : 'No se pudo conectar con el servidor Flask.')
const classify = (p) => p.estado === false ? 'inactivo' : Number(p.stock) <= Number(p.stock_minimo) ? 'alerta' : 'normal'

export default function Inventario() {
  const [items, setItems] = useState([])
  const [alerts, setAlerts] = useState([])
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('todos')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [selected, setSelected] = useState(null)
  const [adjustType, setAdjustType] = useState('AUMENTAR')
  const [amount, setAmount] = useState('')
  const [saving, setSaving] = useState(false)

  async function reload() {
    setLoading(true)
    setError('')
    const [stockResult, alertResult] = await Promise.allSettled([api.get('/stock'), api.get('/stock/alertas')])
    if (stockResult.status === 'fulfilled' && Array.isArray(stockResult.value.data)) setItems(stockResult.value.data)
    else setError(stockResult.status === 'rejected' ? errorText(stockResult.reason) : 'Flask devolvió un listado de stock inválido.')
    if (alertResult.status === 'fulfilled' && Array.isArray(alertResult.value.data)) setAlerts(alertResult.value.data)
    else setError((prev) => [prev, 'No se pudieron consultar las alertas de stock.'].filter(Boolean).join(' '))
    setLoading(false)
  }

  useEffect(() => {
    const timer = setTimeout(() => { void reload() }, 0)
    return () => clearTimeout(timer)
  }, [])

  const visible = useMemo(() => items.filter((p) => {
    const query = search.trim().toLocaleLowerCase('es-AR')
    const match = [p.nombre_producto, p.numero_producto, p.id_producto].some((value) => String(value ?? '').toLocaleLowerCase('es-AR').includes(query))
    return match && (filter === 'todos' || classify(p) === filter)
  }), [items, search, filter])

  const activeCount = items.filter((p) => p.estado !== false).length
  const zeroCount = items.filter((p) => p.estado !== false && Number(p.stock) === 0).length

  function openAdjustment(product) {
    setSelected(product)
    setAdjustType('AUMENTAR')
    setAmount('')
    setError('')
    setNotice('')
  }

  async function submit(event) {
    event.preventDefault()
    if (!selected || saving) return
    const quantity = Number(amount)
    if (!Number.isSafeInteger(quantity) || quantity <= 0) {
      setError('Ingresá una cantidad entera mayor a cero.')
      return
    }
    if (adjustType === 'DISMINUIR' && quantity > Number(selected.stock)) {
      setError('No podés retirar más unidades que el stock disponible.')
      return
    }
    setSaving(true)
    setError('')
    try {
      const { data } = await api.patch('/stock/' + selected.id_producto + '/ajustar', {
        cantidad: quantity,
        tipo_ajuste: adjustType,
      })
      setSelected(null)
      setNotice(`${data.message || 'Stock actualizado.'} ${data.data?.nombre_producto || ''}: ${data.data?.stock_anterior ?? '—'} → ${data.data?.stock_nuevo ?? '—'}`)
      await reload()
    } catch (err) { setError(errorText(err)) }
    finally { setSaving(false) }
  }

  return <section className={styles.page}>
    <header className={styles.heading}>
      <div><p className={styles.eyebrow}>CONTROL DE EXISTENCIAS</p><h1>Inventario</h1><p className={styles.muted}>Consultá existencias, detectá faltantes y registrá ajustes manuales.</p></div>
      <button className={styles.secondary} onClick={reload} type="button" disabled={loading}>↻ Actualizar</button>
    </header>
    <div className={styles.metrics}>
      <div><span>Productos registrados</span><strong>{items.length}</strong></div>
      <div><span>Productos activos</span><strong>{activeCount}</strong></div>
      <div><span>Alertas de stock</span><strong>{alerts.length}</strong></div>
      <div><span>Activos sin stock</span><strong>{zeroCount}</strong></div>
    </div>
    {notice && <p className={styles.success} role="status">{notice}</p>}
    {error && <p className={styles.error} role="alert">{error}</p>}
    <section className={styles.panel}>
      <div className={styles.toolbar}>
        <label>Buscar producto<input type="search" placeholder="Nombre o número" value={search} onChange={(e) => setSearch(e.target.value)} /></label>
        <label>Situación<select value={filter} onChange={(e) => setFilter(e.target.value)}><option value="todos">Todos</option><option value="normal">Stock normal</option><option value="alerta">Stock bajo / mínimo</option><option value="inactivo">Inactivos</option></select></label>
      </div>
      {loading ? <p className={styles.empty}>Cargando inventario…</p> : error && !items.length ? <p className={styles.empty}>No se pudo cargar el inventario.</p> : !visible.length ? <p className={styles.empty}>No hay productos que coincidan con los filtros.</p> : <div className={styles.scroll}><table><thead><tr><th>N.º</th><th>Producto</th><th>Existencias</th><th>Mínimo</th><th>Situación</th><th>Acción</th></tr></thead><tbody>{visible.map((p) => <tr key={p.id_producto}><td>#{p.numero_producto ?? p.id_producto}</td><td><strong>{p.nombre_producto}</strong><small>{p.unidad_de_medida}</small></td><td className={styles.quantity}>{p.stock ?? '—'}</td><td>{p.stock_minimo ?? '—'}</td><td><span className={classify(p) === 'alerta' ? styles.alert : classify(p) === 'inactivo' ? styles.inactive : styles.ok}>{classify(p) === 'alerta' ? 'Stock bajo' : classify(p) === 'inactivo' ? 'Inactivo' : 'Normal'}</span></td><td><button className={styles.secondary} type="button" disabled={p.estado === false} onClick={() => openAdjustment(p)}>Ajustar stock</button></td></tr>)}</tbody></table></div>}
    </section>
    <p className={styles.muted}>Los ajustes manuales quedan registrados por Flask. La consulta del historial estará disponible cuando el backend exponga una ruta para leerlo.</p>
    {selected && <div className={styles.overlay} onMouseDown={(e) => { if (e.target === e.currentTarget && !saving) setSelected(null) }}>
      <section className={styles.dialog} role="dialog" aria-modal="true" aria-labelledby="adjust-title">
        <div className={styles.dialogHead}><div><p className={styles.eyebrow}>MOVIMIENTO MANUAL</p><h2 id="adjust-title">Ajustar stock</h2></div><button type="button" className={styles.secondary} onClick={() => setSelected(null)} disabled={saving} aria-label="Cerrar">✕</button></div>
        <p><strong>{selected.nombre_producto}</strong></p><p className={styles.muted}>Stock actual: <strong>{selected.stock}</strong> {selected.unidad_de_medida}</p>
        <form className={styles.form} onSubmit={submit}>
          <label>Tipo de movimiento<select value={adjustType} onChange={(e) => setAdjustType(e.target.value)}><option value="AUMENTAR">Entrada (+)</option><option value="DISMINUIR">Salida (−)</option></select></label>
          <label>Cantidad<input autoFocus type="number" min="1" step="1" required value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="Ej. 5" /></label>
          {amount && Number.isSafeInteger(Number(amount)) && Number(amount) > 0 && <p className={styles.preview}>Stock resultante: <strong>{Number(selected.stock) + (adjustType === 'AUMENTAR' ? Number(amount) : -Number(amount))}</strong></p>}
          {error && <p className={styles.error} role="alert">{error}</p>}
          <div className={styles.actions}><button className={styles.secondary} type="button" disabled={saving} onClick={() => setSelected(null)}>Cancelar</button><button className={styles.primary} disabled={saving} type="submit">{saving ? 'Guardando…' : 'Confirmar ajuste'}</button></div>
        </form>
      </section>
    </div>}
  </section>
}
