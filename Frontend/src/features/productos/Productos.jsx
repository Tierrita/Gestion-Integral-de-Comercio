import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from '../../shared/api/client.js'
import styles from './Productos.module.css'

const empty = { nombre_producto: '', precio_costo: '', precio_venta: '', id_categoria: '', id_proveedor: '', unidad_de_medida: 'UNIDAD', stock: '0', stock_minimo: '0' }
const money = (value) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(Number(value) || 0)
const messageOf = (error) => error.response?.data?.error || (error.response?.status === 403 ? 'No tenés permiso para realizar esta operación.' : 'No se pudo completar la operación. Revisá la conexión con Flask.')
const asArray = (value) => Array.isArray(value) ? value : []

export default function Productos() {
  const [productos, setProductos] = useState([])
  const [categorias, setCategorias] = useState([])
  const [proveedores, setProveedores] = useState([])
  const [catalogErrors, setCatalogErrors] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('todos')
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(empty)
  const [saving, setSaving] = useState(false)
  const [changingId, setChangingId] = useState(null)
  const [showForm, setShowForm] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    const results = await Promise.allSettled([
      api.get('/productos'), api.get('/categorias'), api.get('/proveedores'),
    ])
    const [p, c, s] = results
    if (p.status === 'fulfilled') setProductos(asArray(p.value.data))
    else setError(messageOf(p.reason))
    setCategorias(c.status === 'fulfilled' ? asArray(c.value.data) : [])
    setProveedores(s.status === 'fulfilled' ? asArray(s.value.data) : [])
    setCatalogErrors([
      ...(c.status === 'rejected' ? ['No se pudieron cargar las categorías: ' + messageOf(c.reason)] : []),
      ...(s.status === 'rejected' ? ['No se pudieron cargar los proveedores: ' + messageOf(s.reason)] : []),
    ])
    setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  const visible = useMemo(() => productos.filter((p) => {
    const matchesState = filter === 'todos' || (filter === 'activos' ? p.estado !== false : p.estado === false)
    return matchesState && [p.nombre_producto, p.numero_producto, p.id_producto].some((v) => String(v ?? '').toLowerCase().includes(query.trim().toLowerCase()))
  }), [productos, query, filter])

  function startCreate() {
    setEditing(null)
    setForm(empty)
    setError('')
    setShowForm(true)
  }

  async function startEdit(producto) {
    setError('')
    try {
      const { data } = await api.get('/productos/' + producto.id_producto)
      setEditing(data)
      setForm({
        nombre_producto: data.nombre_producto ?? '',
        precio_costo: data.precio_costo == null ? '' : String(data.precio_costo),
        precio_venta: String(data.precio_venta ?? ''),
        id_categoria: String(data.id_categoria ?? ''),
        id_proveedor: String(data.id_proveedor ?? ''),
        unidad_de_medida: data.unidad_de_medida ?? 'UNIDAD',
        stock: String(data.stock ?? 0),
        stock_minimo: String(data.stock_minimo ?? 0),
      })
      setShowForm(true)
    } catch (err) { setError(messageOf(err)) }
  }

  function changeField(event) {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
  }

  async function submit(event) {
    event.preventDefault()
    if (saving) return
    setSaving(true)
    setError('')
    setNotice('')
    const payload = {
      nombre_producto: form.nombre_producto.trim(),
      precio_venta: Number(form.precio_venta),
      id_categoria: Number(form.id_categoria),
      id_proveedor: Number(form.id_proveedor),
      unidad_de_medida: form.unidad_de_medida.trim(),
      stock_minimo: Number(form.stock_minimo),
    }
    if (!editing) {
      payload.precio_costo = Number(form.precio_costo)
      payload.stock = Number(form.stock)
    } else if (editing.precio_costo != null && form.precio_costo !== '' && Number(form.precio_costo) !== Number(editing.precio_costo)) {
      payload.precio_costo = Number(form.precio_costo)
    }
    try {
      const response = editing
        ? await api.patch('/productos/' + editing.id_producto, payload)
        : await api.post('/productos', payload)
      setNotice(response.data?.message || 'Producto guardado.')
      setShowForm(false)
      setEditing(null)
      await load()
    } catch (err) { setError(messageOf(err)) }
    finally { setSaving(false) }
  }

  async function changeStatus(producto) {
    const active = producto.estado !== false
    if (!window.confirm(`¿${active ? 'Desactivar' : 'Activar'} "${producto.nombre_producto}"?`)) return
    setChangingId(producto.id_producto)
    setError('')
    setNotice('')
    try {
      const { data } = await api.patch('/productos/' + producto.id_producto + '/estado', { estado: !active })
      setNotice(data.message || 'Estado actualizado.')
      await load()
    } catch (err) { setError(messageOf(err)) }
    finally { setChangingId(null) }
  }

  const activeCategories = categorias.filter((c) => c.estado !== false || String(c.id_categoria) === form.id_categoria)
  const activeSuppliers = proveedores.filter((p) => p.estado !== false || String(p.id_proveedor) === form.id_proveedor)
  const canCreate = !catalogErrors.length && activeCategories.length > 0 && activeSuppliers.length > 0

  return (
    <section className={styles.page}>
      <header className={styles.heading}>
        <div><p className={styles.eyebrow}>CATÁLOGO COMERCIAL</p><h1>Productos</h1><p className={styles.muted}>Administrá tu catálogo, precios y estado de los productos.</p></div>
        <button className={styles.primary} type="button" onClick={startCreate} disabled={!canCreate}>+ Nuevo producto</button>
      </header>
      <div className={styles.metrics}>
        <div><span>Total de productos</span><strong>{productos.length}</strong></div>
        <div><span>Activos</span><strong>{productos.filter((p) => p.estado !== false).length}</strong></div>
        <div><span>Inactivos</span><strong>{productos.filter((p) => p.estado === false).length}</strong></div>
      </div>
      {notice && <p role="status" className={styles.success}>{notice}</p>}
      {error && <p role="alert" className={styles.error}>{error}</p>}
      {catalogErrors.map((msg) => <p key={msg} role="alert" className={styles.error}>{msg}</p>)}
      <div className={styles.panel}>
        <div className={styles.toolbar}>
          <label>Buscar producto<input type="search" placeholder="Nombre o número de producto" value={query} onChange={(event) => setQuery(event.target.value)} /></label>
          <label>Estado<select value={filter} onChange={(event) => setFilter(event.target.value)}><option value="todos">Todos</option><option value="activos">Activos</option><option value="inactivos">Inactivos</option></select></label>
          <button type="button" className={styles.secondary} onClick={load} disabled={loading}>Actualizar</button>
        </div>
        {loading ? <p role="status" className={styles.empty}>Cargando productos…</p> : error && productos.length === 0 ? <p className={styles.empty}>No se pudo cargar el listado.</p> : visible.length === 0 ? <p className={styles.empty}>No hay productos para mostrar.</p> : (
          <div className={styles.tableScroll}><table><thead><tr><th>N.º</th><th>Producto</th><th>Precio de venta</th><th>Stock</th><th>Estado</th><th>Acciones</th></tr></thead>
            <tbody>{visible.map((p) => <tr key={p.id_producto}>
              <td>#{p.numero_producto ?? p.id_producto}</td><td><strong>{p.nombre_producto}</strong><small>{p.unidad_de_medida}</small></td>
              <td>{money(p.precio_venta)}</td><td>{p.stock ?? '—'}</td><td><span className={p.estado === false ? styles.inactive : styles.active}>{p.estado === false ? 'Inactivo' : 'Activo'}</span></td>
              <td><div className={styles.actions}><button type="button" className={styles.secondary} onClick={() => startEdit(p)}>Editar</button><button type="button" className={styles.secondary} disabled={changingId === p.id_producto} onClick={() => changeStatus(p)}>{changingId === p.id_producto ? 'Guardando…' : p.estado === false ? 'Activar' : 'Desactivar'}</button></div></td>
            </tr>)}</tbody></table></div>
        )}
      </div>
      {showForm && <div className={styles.overlay} role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget && !saving) setShowForm(false) }}>
        <section className={styles.dialog} role="dialog" aria-modal="true" aria-labelledby="product-form-title">
          <div className={styles.dialogHeader}><h2 id="product-form-title">{editing ? 'Editar producto' : 'Nuevo producto'}</h2><button type="button" className={styles.secondary} disabled={saving} onClick={() => setShowForm(false)} aria-label="Cerrar formulario">✕</button></div>
          <form onSubmit={submit} className={styles.form}>
            <label>Nombre del producto<input autoFocus name="nombre_producto" minLength="2" required value={form.nombre_producto} onChange={changeField} /></label>
            <div className={styles.fields}>
              <label>Precio de venta<input name="precio_venta" type="number" min="0" step="0.01" required value={form.precio_venta} onChange={changeField} /></label>
              {(!editing || editing.precio_costo != null) && <label>Precio de costo<input name="precio_costo" type="number" min="0" step="0.01" required={!editing} value={form.precio_costo} onChange={changeField} /></label>}
            </div>
            <div className={styles.fields}>
              <label>Categoría<select name="id_categoria" required value={form.id_categoria} onChange={changeField}><option value="">Seleccionar</option>{activeCategories.map((c) => <option key={c.id_categoria} value={c.id_categoria}>{c.nombre_categoria}</option>)}</select></label>
              <label>Proveedor<select name="id_proveedor" required value={form.id_proveedor} onChange={changeField}><option value="">Seleccionar</option>{activeSuppliers.map((p) => <option key={p.id_proveedor} value={p.id_proveedor}>{p.nombre_proveedor}</option>)}</select></label>
            </div>
            <div className={styles.fields}>
              <label>Unidad de medida<input name="unidad_de_medida" required value={form.unidad_de_medida} onChange={changeField} /></label>
              <label>Stock mínimo<input name="stock_minimo" type="number" min="0" step="1" required value={form.stock_minimo} onChange={changeField} /></label>
            </div>
            {!editing && <label>Stock inicial<input name="stock" type="number" min="0" step="1" required value={form.stock} onChange={changeField} /></label>}
            {editing && <p className={styles.muted}>El stock se modifica desde Inventario. El estado se cambia desde el listado.</p>}
            {error && <p role="alert" className={styles.error}>{error}</p>}
            <div className={styles.formActions}><button type="button" className={styles.secondary} disabled={saving} onClick={() => setShowForm(false)}>Cancelar</button><button type="submit" className={styles.primary} disabled={saving}>{saving ? 'Guardando…' : editing ? 'Guardar cambios' : 'Crear producto'}</button></div>
          </form>
        </section>
      </div>}
    </section>
  )
}
