import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import styles from './Productos.module.css'

const money = (value) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(Number(value) || 0)
const messageOf = (error) => error.response?.data?.error || (error.response?.status === 403 ? 'No tenés permiso para realizar esta operación.' : 'No se pudo completar la operación. Revisá la conexión con Flask.')

export default function Productos() {
  const location = useLocation()
  const [productos, setProductos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState(location.state?.notice || '')
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('todos')
  const [changingId, setChangingId] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get('/productos')
      if (!Array.isArray(data)) throw new Error('Respuesta de productos inválida.')
      setProductos(data)
    } catch (err) { setError(messageOf(err)) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => { void load() }, 0)
    return () => clearTimeout(timer)
  }, [load])

  const visible = useMemo(() => productos.filter((p) => {
    const matchesState = filter === 'todos' || (filter === 'activos' ? p.estado !== false : p.estado === false)
    return matchesState && [p.nombre_producto, p.numero_producto, p.id_producto].some((v) => String(v ?? '').toLowerCase().includes(query.trim().toLowerCase()))
  }), [productos, query, filter])

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

  return <section className={styles.page}>
    <header className={styles.heading}>
      <div><p className={styles.eyebrow}>CATÁLOGO COMERCIAL</p><h1>Productos</h1><p className={styles.muted}>Administrá tu catálogo, precios y estado de los productos.</p></div>
      <Link className={styles.primary} to="/productos/nuevo">+ Nuevo producto</Link>
    </header>
    <div className={styles.metrics}>
      <div><span>Total de productos</span><strong>{productos.length}</strong></div>
      <div><span>Activos</span><strong>{productos.filter((p) => p.estado !== false).length}</strong></div>
      <div><span>Inactivos</span><strong>{productos.filter((p) => p.estado === false).length}</strong></div>
    </div>
    {notice && <p role="status" className={styles.success}>{notice}</p>}
    {error && <p role="alert" className={styles.error}>{error}</p>}
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <label>Buscar producto<input type="search" placeholder="Nombre o número de producto" value={query} onChange={(event) => setQuery(event.target.value)} /></label>
        <label>Estado<select value={filter} onChange={(event) => setFilter(event.target.value)}><option value="todos">Todos</option><option value="activos">Activos</option><option value="inactivos">Inactivos</option></select></label>
        <button type="button" className={styles.secondary} onClick={load} disabled={loading}>Actualizar</button>
      </div>
      {loading ? <p role="status" className={styles.empty}>Cargando productos…</p> : error && productos.length === 0 ? <p className={styles.empty}>No se pudo cargar el listado.</p> : visible.length === 0 ? <p className={styles.empty}>No hay productos para mostrar.</p> : <div className={styles.tableScroll}><table><thead><tr><th>N.º</th><th>Producto</th><th>Precio de venta</th><th>Stock</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>{visible.map((p) => <tr key={p.id_producto}>
        <td>#{p.numero_producto ?? p.id_producto}</td><td><strong>{p.nombre_producto}</strong><small>{p.unidad_de_medida}</small></td>
        <td>{money(p.precio_venta)}</td><td>{p.stock ?? '—'}</td><td><span className={p.estado === false ? styles.inactive : styles.active}>{p.estado === false ? 'Inactivo' : 'Activo'}</span></td>
        <td><div className={styles.actions}><Link className={styles.secondary} to={`/productos/${p.id_producto}/editar`}>Editar</Link><button type="button" className={styles.secondary} disabled={changingId === p.id_producto} onClick={() => changeStatus(p)}>{changingId === p.id_producto ? 'Guardando…' : p.estado === false ? 'Activar' : 'Desactivar'}</button></div></td>
      </tr>)}</tbody></table></div>}
    </div>
  </section>
}
