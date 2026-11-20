import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import styles from './Productos.module.css'
import MercaderiaNav from './MercaderiaNav.jsx'
import { formatoMoneda } from '../../shared/utils/formatters.js'

const numeric = (value) => value == null || value === '' ? null : Number(value)
const PAGE_SIZES = [10, 25, 50]
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
  const [sortBy, setSortBy] = useState('numero_producto')
  const [sortDirection, setSortDirection] = useState('asc')
  const [pageSize, setPageSize] = useState(10)
  const [page, setPage] = useState(1)

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
  }).sort((a, b) => {
    const av = a[sortBy]
    const bv = b[sortBy]
    const result = ['nombre_producto', 'unidad_de_medida'].includes(sortBy)
      ? String(av ?? '').localeCompare(String(bv ?? ''), 'es-AR', { numeric: true })
      : (numeric(av) == null ? 1 : numeric(bv) == null ? -1 : numeric(av) - numeric(bv))
    return (sortDirection === 'asc' ? result : -result) || Number(a.id_producto) - Number(b.id_producto)
  }), [productos, query, filter, sortBy, sortDirection])
  const totalPages = Math.max(1, Math.ceil(visible.length / pageSize))
  const currentPage = Math.min(page, totalPages)
  const pageRows = visible.slice((currentPage - 1) * pageSize, currentPage * pageSize)
  const resetPage = () => setPage(1)
  function sort(column) {
    setSortDirection((previous) => sortBy === column && previous === 'asc' ? 'desc' : 'asc')
    setSortBy(column)
    resetPage()
  }
  const sortMark = (column) => sortBy === column ? (sortDirection === 'asc' ? ' ↑' : ' ↓') : ' ↕'

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
    <MercaderiaNav />
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
        <label>Buscar producto<input type="search" placeholder="Nombre o número de producto" value={query} onChange={(event) => { setQuery(event.target.value); resetPage() }} /></label>
        <label>Estado<select value={filter} onChange={(event) => { setFilter(event.target.value); resetPage() }}><option value="todos">Todos</option><option value="activos">Activos</option><option value="inactivos">Inactivos</option></select></label>
        <button type="button" className={styles.secondary} onClick={load} disabled={loading}>Actualizar</button>
      </div>
      <div className={styles.tableControls}>
        <label>Mostrar<select value={pageSize} onChange={(event) => { setPageSize(Number(event.target.value)); resetPage() }}>{PAGE_SIZES.map((size) => <option key={size} value={size}>{size} registros</option>)}</select></label>
        <span>{visible.length} productos encontrados</span>
      </div>
      {loading ? <p role="status" className={styles.empty}>Cargando productos…</p> : error && productos.length === 0 ? <p className={styles.empty}>No se pudo cargar el listado.</p> : visible.length === 0 ? <p className={styles.empty}>No hay productos para mostrar.</p> : <div className={styles.tableScroll}><table><thead><tr>
        <th><button className={styles.sortButton} type="button" onClick={() => sort('numero_producto')}>N.º{sortMark('numero_producto')}</button></th>
        <th><button className={styles.sortButton} type="button" onClick={() => sort('nombre_producto')}>Producto{sortMark('nombre_producto')}</button></th>
        <th><button className={styles.sortButton} type="button" onClick={() => sort('precio_costo')}>Precio de costo{sortMark('precio_costo')}</button></th>
        <th><button className={styles.sortButton} type="button" onClick={() => sort('precio_venta')}>Precio de venta{sortMark('precio_venta')}</button></th>
        <th><button className={styles.sortButton} type="button" onClick={() => sort('stock')}>Stock{sortMark('stock')}</button></th>
        <th>Unidad</th><th>Estado</th><th>Acciones</th>
      </tr></thead><tbody>{pageRows.map((p) => <tr key={p.id_producto}>
        <td>#{p.numero_producto ?? p.id_producto}</td><td><strong>{p.nombre_producto}</strong></td>
        <td>{p.precio_costo == null ? 'Sin acceso' : formatoMoneda(p.precio_costo)}</td>
        <td>{formatoMoneda(p.precio_venta)}</td>
        <td><strong className={p.estado !== false && Number(p.stock) <= Number(p.stock_minimo) ? styles.lowStock : ''}>{p.stock ?? '—'}</strong></td>
        <td>{p.unidad_de_medida || '—'}</td>
        <td><span className={p.estado === false ? styles.inactive : styles.active}>{p.estado === false ? 'Inactivo' : 'Activo'}</span></td>
        <td><div className={styles.actions}><Link className={styles.secondary} to={`/productos/${p.id_producto}/editar`}>Editar</Link><Link className={styles.secondary} to="/inventario">Ver inventario</Link><button type="button" className={styles.secondary} disabled={changingId === p.id_producto} onClick={() => changeStatus(p)}>{changingId === p.id_producto ? 'Guardando…' : p.estado === false ? 'Activar' : 'Desactivar'}</button></div></td>
      </tr>)}</tbody></table></div>}
      {!loading && !error && visible.length > 0 && <div className={styles.pagination}>
        <span>Mostrando {(currentPage - 1) * pageSize + 1}–{Math.min(currentPage * pageSize, visible.length)} de {visible.length}</span>
        <div className={styles.pageActions}><button type="button" className={styles.secondary} disabled={currentPage === 1} onClick={() => setPage((n) => Math.max(1, n - 1))}>Anterior</button><span>Página {currentPage} de {totalPages}</span><button type="button" className={styles.secondary} disabled={currentPage === totalPages} onClick={() => setPage((n) => Math.min(totalPages, n + 1))}>Siguiente</button></div>
      </div>}
    </div>
  </section>
}
