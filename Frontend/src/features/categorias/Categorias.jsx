import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from '../../shared/api/client.js'
import Alert from '../../shared/components/Alert.jsx'
import Modal from '../../shared/components/Modal.jsx'
import ConfirmDialog from '../../shared/components/ConfirmDialog.jsx'
import styles from './Categorias.module.css'

const PAGE_SIZES = [10, 25, 50]
const errorMessage = (error) => error.response?.data?.error || (error.response?.status === 403
  ? 'No tenés permisos para esta operación.'
  : 'No se pudo completar la operación. Verificá la conexión con Flask.')

export default function Categorias() {
  const [categorias, setCategorias] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('todos')
  const [pageSize, setPageSize] = useState(10)
  const [page, setPage] = useState(1)
  const [sort, setSort] = useState({ key: 'id_categoria', asc: true })
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ nombre_categoria: '', descripcion: '' })
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)
  const [pending, setPending] = useState(null)
  const [statusError, setStatusError] = useState('')
  const [changing, setChanging] = useState(false)
  const [details, setDetails] = useState(null)

  const load = useCallback(async (signal) => {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get('/categorias', { signal })
      if (!Array.isArray(data)) throw new Error('Respuesta inválida')
      if (!signal?.aborted) setCategorias(data)
    } catch (err) {
      if (!signal?.aborted) setError(errorMessage(err))
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    const timer = setTimeout(() => { void load(controller.signal) }, 0)
    return () => { clearTimeout(timer); controller.abort() }
  }, [load])

  const filtered = useMemo(() => categorias.filter((c) => {
    const active = c.estado === true
    return (filter === 'todos' || (filter === 'activos' ? active : !active)) &&
      [c.id_categoria, c.nombre_categoria, c.descripcion]
        .some((v) => String(v ?? '').toLocaleLowerCase('es-AR').includes(query.trim().toLocaleLowerCase('es-AR')))
  }).sort((a, b) => {
    const av = a[sort.key] ?? ''
    const bv = b[sort.key] ?? ''
    const comparison = sort.key === 'id_categoria'
      ? Number(av) - Number(bv)
      : String(av).localeCompare(String(bv), 'es-AR', { numeric: true })
    return sort.asc ? comparison : -comparison
  }), [categorias, filter, query, sort])
  const pages = Math.max(1, Math.ceil(filtered.length / pageSize))
  const currentPage = Math.min(page, pages)
  const rows = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize)
  const changeSort = (key) => { setSort((old) => ({ key, asc: old.key === key ? !old.asc : true })); setPage(1) }
  const sortMark = (key) => sort.key === key ? (sort.asc ? ' ↑' : ' ↓') : ' ↕'

  function openForm(categoria = null) {
    setEditing(categoria || 'new')
    setForm({ nombre_categoria: categoria?.nombre_categoria ?? '', descripcion: categoria?.descripcion ?? '' })
    setFormError('')
  }

  async function submit(event) {
    event.preventDefault()
    if (saving) return
    const nombre = form.nombre_categoria.trim()
    if (!nombre) { setFormError('El nombre de la categoría es obligatorio.'); return }
    setSaving(true)
    setFormError('')
    try {
      const payload = { nombre_categoria: nombre, descripcion: form.descripcion.trim() || null }
      const { data } = editing === 'new'
        ? await api.post('/categorias', payload)
        : await api.patch(`/categorias/${editing.id_categoria}`, payload)
      setEditing(null)
      setNotice(data.message || 'Categoría guardada correctamente.')
      await load()
    } catch (err) { setFormError(errorMessage(err)) }
    finally { setSaving(false) }
  }

  async function changeStatus() {
    if (!pending || changing) return
    setChanging(true)
    setStatusError('')
    try {
      const { data } = await api.patch(`/categorias/${pending.id_categoria}/estado`, { estado: !pending.estado })
      setPending(null)
      setNotice(data.message || 'Estado actualizado correctamente.')
      await load()
    } catch (err) { setStatusError(errorMessage(err)) }
    finally { setChanging(false) }
  }

  return <section className={styles.page}>
    <header className={styles.header}>
      <div><p className={styles.eyebrow}>GESTIÓN DE MERCADERÍA</p><h1>Categorías</h1><p className={styles.muted}>Organizá los productos de tu comercio.</p></div>
      <button type="button" className={styles.primary} onClick={() => openForm()}>+ Nueva categoría</button>
    </header>
    <div className={styles.metrics}>
      <article><span>Total de categorías</span><strong>{categorias.length}</strong></article>
      <article><span>Activas</span><strong>{categorias.filter((c) => c.estado === true).length}</strong></article>
      <article><span>Inactivas</span><strong>{categorias.filter((c) => c.estado === false).length}</strong></article>
    </div>
    {notice && <Alert type="success">{notice}</Alert>}
    {error && <Alert type="error">{error}</Alert>}
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <label>Buscar categoría<input type="search" placeholder="Nombre, descripción o ID" value={query} onChange={(e) => { setQuery(e.target.value); setPage(1) }} /></label>
        <label>Estado<select value={filter} onChange={(e) => { setFilter(e.target.value); setPage(1) }}><option value="todos">Todas</option><option value="activos">Activas</option><option value="inactivos">Inactivas</option></select></label>
        <label>Mostrar<select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}>{PAGE_SIZES.map((n) => <option key={n} value={n}>{n} registros</option>)}</select></label>
        <button type="button" className={styles.secondary} disabled={loading} onClick={() => void load()}>Actualizar</button>
      </div>
      <p className={styles.muted}>{filtered.length} categorías encontradas</p>
      {loading ? <p role="status">Cargando categorías…</p> : error && categorias.length === 0 ? <p>No se pudo cargar el listado.</p> : filtered.length === 0 ? <p>No hay categorías para mostrar.</p> : <div className={styles.scroll}>
        <table><thead><tr>
          <th><button type="button" onClick={() => changeSort('id_categoria')}>ID{sortMark('id_categoria')}</button></th>
          <th><button type="button" onClick={() => changeSort('nombre_categoria')}>Categoría{sortMark('nombre_categoria')}</button></th>
          <th>Descripción</th><th>Estado</th><th>Acciones</th>
        </tr></thead><tbody>{rows.map((c) => <tr key={c.id_categoria}>
          <td>#{c.id_categoria}</td><td><strong>{c.nombre_categoria}</strong></td><td>{c.descripcion || '—'}</td>
          <td><span className={c.estado === true ? styles.active : styles.inactive}>{c.estado === true ? 'Activa' : 'Inactiva'}</span></td>
          <td><div className={styles.actions}>
            <button type="button" className={styles.secondary} onClick={() => setDetails(c)}>Ver detalle</button>
            <button type="button" className={styles.secondary} onClick={() => openForm(c)}>Editar</button>
            <button type="button" className={styles.secondary} onClick={() => { setPending(c); setStatusError('') }}>{c.estado === true ? 'Desactivar' : 'Activar'}</button>
          </div></td>
        </tr>)}</tbody></table>
      </div>}
      {!loading && filtered.length > 0 && <div className={styles.pagination}>
        <span>Mostrando {(currentPage - 1) * pageSize + 1}–{Math.min(currentPage * pageSize, filtered.length)} de {filtered.length}</span>
        <div className={styles.actions}><button type="button" className={styles.secondary} disabled={currentPage === 1} onClick={() => setPage((n) => n - 1)}>Anterior</button><span>Página {currentPage} de {pages}</span><button type="button" className={styles.secondary} disabled={currentPage === pages} onClick={() => setPage((n) => n + 1)}>Siguiente</button></div>
      </div>}
    </div>
    <Modal open={editing !== null} onClose={() => { if (!saving) setEditing(null) }} busy={saving} title={editing === 'new' ? 'Nueva categoría' : 'Editar categoría'} description="Completá los datos de la categoría." size="medium">
      <form className={styles.form} onSubmit={(event) => void submit(event)}>
        <label>Nombre de categoría<input required maxLength={150} value={form.nombre_categoria} onChange={(e) => setForm((f) => ({ ...f, nombre_categoria: e.target.value }))} /></label>
        <label>Descripción (opcional)<textarea className={styles.textarea} rows={3} value={form.descripcion} onChange={(e) => setForm((f) => ({ ...f, descripcion: e.target.value }))} /></label>
        {formError && <Alert type="error">{formError}</Alert>}
        <div className={styles.actions}><button type="button" className={styles.secondary} disabled={saving} onClick={() => setEditing(null)}>Cancelar</button><button type="submit" className={styles.primary} disabled={saving}>{saving ? 'Guardando…' : 'Guardar categoría'}</button></div>
      </form>
    </Modal>
    <ConfirmDialog open={Boolean(pending)} onClose={() => { if (!changing) { setPending(null); setStatusError('') } }} onConfirm={() => void changeStatus()} title={pending?.estado === true ? 'Desactivar categoría' : 'Activar categoría'} description="No se puede desactivar una categoría con productos activos asociados." details={pending ? [{ label: 'Categoría', value: pending.nombre_categoria }] : []} error={statusError} busy={changing} destructive={pending?.estado === true} confirmLabel={pending?.estado === true ? 'Desactivar' : 'Activar'} />
    <Modal open={details !== null} onClose={() => setDetails(null)} title={details?.nombre_categoria || 'Categoría'} description="Información de la categoría." size="medium">
      {details && <dl className={styles.detailList}>
        <div><dt>ID</dt><dd>#{details.id_categoria}</dd></div>
        <div><dt>Descripción</dt><dd>{details.descripcion || '—'}</dd></div>
        <div><dt>Estado</dt><dd>{details.estado === true ? 'Activa' : 'Inactiva'}</dd></div>
      </dl>}
    </Modal>
  </section>
}
