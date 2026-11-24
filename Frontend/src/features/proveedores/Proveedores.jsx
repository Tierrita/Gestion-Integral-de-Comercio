import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from '../../shared/api/client.js'
import Alert from '../../shared/components/Alert.jsx'
import Modal from '../../shared/components/Modal.jsx'
import ConfirmDialog from '../../shared/components/ConfirmDialog.jsx'
import styles from './Proveedores.module.css'

const money = (value) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(Number(value || 0))
const PAGE_SIZES = [10, 25, 50]
const EMPTY = { nombre_proveedor: '', telefono: '', email: '', direccion: '', descripcion: '' }
const errorMessage = (error) => error.response?.data?.error || (error.response?.status === 403
  ? 'No tenés permisos para esta operación.'
  : 'No se pudo completar la operación. Verificá la conexión con Flask.')

export default function Proveedores() {
  const [proveedores, setProveedores] = useState([])
  const [saldos, setSaldos] = useState({})
  const [saldosError, setSaldosError] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('todos')
  const [pageSize, setPageSize] = useState(10)
  const [page, setPage] = useState(1)
  const [sort, setSort] = useState({ key: 'numero_proveedor', asc: true })
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(EMPTY)
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
      const [proveedoresResponse, saldosResponse] = await Promise.allSettled([
        api.get('/proveedores', { signal }),
        api.get('/proveedores/saldos', { signal }),
      ])
      if (proveedoresResponse.status !== 'fulfilled' || !Array.isArray(proveedoresResponse.value.data)) throw new Error('No se pudieron cargar los proveedores')
      if (!signal?.aborted) setProveedores(proveedoresResponse.value.data)
      if (saldosResponse.status === 'fulfilled' && Array.isArray(saldosResponse.value.data?.saldos)) {
        if (!signal?.aborted) {
          setSaldos(Object.fromEntries(saldosResponse.value.data.saldos.map((item) => [item.id_proveedor, item])))
          setSaldosError('')
        }
      } else if (!signal?.aborted) {
        setSaldos({})
        setSaldosError('No se pudieron cargar las deudas de proveedores.')
      }
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

  const filtered = useMemo(() => proveedores.filter((p) => {
    const active = p.estado === true
    return (filter === 'todos' || (filter === 'activos' ? active : !active)) &&
      [p.numero_proveedor, p.nombre_proveedor, p.telefono, p.email, p.direccion, p.descripcion]
        .some((v) => String(v ?? '').toLocaleLowerCase('es-AR').includes(query.trim().toLocaleLowerCase('es-AR')))
  }).sort((a, b) => {
    const av = a[sort.key] ?? ''
    const bv = b[sort.key] ?? ''
    const comparison = sort.key === 'numero_proveedor'
      ? Number(av) - Number(bv)
      : String(av).localeCompare(String(bv), 'es-AR', { numeric: true })
    return sort.asc ? comparison : -comparison
  }), [proveedores, filter, query, sort])
  const pages = Math.max(1, Math.ceil(filtered.length / pageSize))
  const currentPage = Math.min(page, pages)
  const rows = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize)
  const changeSort = (key) => { setSort((old) => ({ key, asc: old.key === key ? !old.asc : true })); setPage(1) }
  const sortMark = (key) => sort.key === key ? (sort.asc ? ' ↑' : ' ↓') : ' ↕'

  function openForm(proveedor = null) {
    setEditing(proveedor || 'new')
    setForm(proveedor ? Object.fromEntries(Object.keys(EMPTY).map((key) => [key, proveedor[key] ?? ''])) : { ...EMPTY })
    setFormError('')
  }

  async function submit(event) {
    event.preventDefault()
    if (saving) return
    const nombre = form.nombre_proveedor.trim()
    if (!nombre) { setFormError('El nombre del proveedor es obligatorio.'); return }
    setSaving(true)
    setFormError('')
    try {
      const payload = Object.fromEntries(Object.entries(form).map(([key, value]) => [key, value.trim() || null]))
      payload.nombre_proveedor = nombre
      const { data } = editing === 'new'
        ? await api.post('/proveedores', payload)
        : await api.patch(`/proveedores/${editing.id_proveedor}`, payload)
      setEditing(null)
      setNotice(data.message || 'Proveedor guardado correctamente.')
      await load()
    } catch (err) { setFormError(errorMessage(err)) }
    finally { setSaving(false) }
  }

  async function changeStatus() {
    if (!pending || changing) return
    setChanging(true)
    setStatusError('')
    try {
      const { data } = await api.patch(`/proveedores/${pending.id_proveedor}/estado`, { estado: !pending.estado })
      setPending(null)
      setNotice(data.message || 'Estado actualizado correctamente.')
      await load()
    } catch (err) { setStatusError(errorMessage(err)) }
    finally { setChanging(false) }
  }

  return <section className={styles.page}>
    <header className={styles.header}>
      <div><p className={styles.eyebrow}>GESTIÓN COMERCIAL</p><h1>Proveedores</h1><p className={styles.muted}>Administrá los proveedores de tu comercio.</p></div>
      <button type="button" className={styles.primary} onClick={() => openForm()}>+ Nuevo proveedor</button>
    </header>
    <div className={styles.metrics}>
      <article><span>Total de proveedores</span><strong>{proveedores.length}</strong></article>
      <article><span>Activos</span><strong>{proveedores.filter((p) => p.estado === true).length}</strong></article>
      <article><span>Inactivos</span><strong>{proveedores.filter((p) => p.estado === false).length}</strong></article>
    </div>
    {notice && <Alert type="success">{notice}</Alert>}
    {error && <Alert type="error">{error}</Alert>}
    {saldosError && <Alert type="warning">{saldosError}</Alert>}
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <label>Buscar proveedor<input type="search" placeholder="Nombre, número, teléfono, email..." value={query} onChange={(e) => { setQuery(e.target.value); setPage(1) }} /></label>
        <label>Estado<select value={filter} onChange={(e) => { setFilter(e.target.value); setPage(1) }}><option value="todos">Todos</option><option value="activos">Activos</option><option value="inactivos">Inactivos</option></select></label>
        <label>Mostrar<select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}>{PAGE_SIZES.map((n) => <option key={n} value={n}>{n} registros</option>)}</select></label>
        <button type="button" className={styles.secondary} disabled={loading} onClick={() => void load()}>Actualizar</button>
      </div>
      <p className={styles.muted}>{filtered.length} proveedores encontrados</p>
      {loading ? <p role="status">Cargando proveedores…</p> : error && proveedores.length === 0 ? <p>No se pudo cargar el listado.</p> : filtered.length === 0 ? <p>No hay proveedores para mostrar.</p> : <div className={styles.scroll}>
        <table><thead><tr>
          <th><button type="button" onClick={() => changeSort('numero_proveedor')}>N.º{sortMark('numero_proveedor')}</button></th>
          <th><button type="button" onClick={() => changeSort('nombre_proveedor')}>Proveedor{sortMark('nombre_proveedor')}</button></th>
          <th>Teléfono</th><th>Email</th><th>Estado</th><th>Saldo</th><th>Acciones</th>
        </tr></thead><tbody>{rows.map((p) => <tr key={p.id_proveedor}>
          <td>#{p.numero_proveedor}</td><td><strong>{p.nombre_proveedor}</strong></td><td>{p.telefono || '—'}</td><td>{p.email || '—'}</td>
          <td><span className={p.estado === true ? styles.active : styles.inactive}>{p.estado === true ? 'Activo' : 'Inactivo'}</span></td>
          <td>{saldos[p.id_proveedor] ? <span className={saldos[p.id_proveedor].saldo > 0 ? styles.deuda : saldos[p.id_proveedor].saldo < 0 ? styles.favor : styles.neutro}>{money(Math.abs(saldos[p.id_proveedor].saldo))} · {saldos[p.id_proveedor].saldo > 0 ? 'Deuda' : saldos[p.id_proveedor].saldo < 0 ? 'A favor' : 'Al día'}</span> : '—'}</td>
          <td><div className={styles.actions}>
            <button type="button" className={styles.secondary} onClick={() => setDetails(p)}>Ver detalle</button>
            <button type="button" className={styles.secondary} onClick={() => openForm(p)}>Editar</button>
            <button type="button" className={styles.secondary} onClick={() => { setPending(p); setStatusError('') }}>{p.estado === true ? 'Desactivar' : 'Activar'}</button>
          </div></td>
        </tr>)}</tbody></table>
      </div>}
      {!loading && filtered.length > 0 && <div className={styles.pagination}>
        <span>Mostrando {(currentPage - 1) * pageSize + 1}–{Math.min(currentPage * pageSize, filtered.length)} de {filtered.length}</span>
        <div className={styles.actions}><button type="button" className={styles.secondary} disabled={currentPage === 1} onClick={() => setPage((n) => n - 1)}>Anterior</button><span>Página {currentPage} de {pages}</span><button type="button" className={styles.secondary} disabled={currentPage === pages} onClick={() => setPage((n) => n + 1)}>Siguiente</button></div>
      </div>}
    </div>
    <Modal open={editing !== null} onClose={() => { if (!saving) setEditing(null) }} busy={saving} title={editing === 'new' ? 'Nuevo proveedor' : 'Editar proveedor'} description="Completá los datos del proveedor." size="medium">
      <form className={styles.form} onSubmit={(event) => void submit(event)}>
        <label>Nombre del proveedor<input required maxLength={150} value={form.nombre_proveedor} onChange={(e) => setForm((f) => ({ ...f, nombre_proveedor: e.target.value }))} /></label>
        <label>Teléfono (opcional)<input type="tel" maxLength={50} value={form.telefono} onChange={(e) => setForm((f) => ({ ...f, telefono: e.target.value }))} /></label>
        <label>Email (opcional)<input type="email" maxLength={150} value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} /></label>
        <label>Dirección (opcional)<input maxLength={250} value={form.direccion} onChange={(e) => setForm((f) => ({ ...f, direccion: e.target.value }))} /></label>
        <label>Descripción (opcional)<textarea className={styles.textarea} rows={3} value={form.descripcion} onChange={(e) => setForm((f) => ({ ...f, descripcion: e.target.value }))} /></label>
        {formError && <Alert type="error">{formError}</Alert>}
        <div className={styles.actions}><button type="button" className={styles.secondary} disabled={saving} onClick={() => setEditing(null)}>Cancelar</button><button type="submit" className={styles.primary} disabled={saving}>{saving ? 'Guardando…' : 'Guardar proveedor'}</button></div>
      </form>
    </Modal>
    <ConfirmDialog open={Boolean(pending)} onClose={() => { if (!changing) { setPending(null); setStatusError('') } }} onConfirm={() => void changeStatus()} title={pending?.estado === true ? 'Desactivar proveedor' : 'Activar proveedor'} description="Confirmá el cambio de estado del proveedor." details={pending ? [{ label: 'Proveedor', value: pending.nombre_proveedor }] : []} error={statusError} busy={changing} destructive={pending?.estado === true} confirmLabel={pending?.estado === true ? 'Desactivar' : 'Activar'} />
    <Modal open={details !== null} onClose={() => setDetails(null)} title={details?.nombre_proveedor || 'Proveedor'} description="Información del proveedor." size="medium">
      {details && <dl className={styles.detailList}>
        <div><dt>Número</dt><dd>#{details.numero_proveedor}</dd></div>
        <div><dt>Teléfono</dt><dd>{details.telefono || '—'}</dd></div>
        <div><dt>Email</dt><dd>{details.email || '—'}</dd></div>
        <div><dt>Dirección</dt><dd>{details.direccion || '—'}</dd></div>
        <div><dt>Descripción</dt><dd>{details.descripcion || '—'}</dd></div>
        <div><dt>Estado</dt><dd>{details.estado === true ? 'Activo' : 'Inactivo'}</dd></div>
      </dl>}
    </Modal>
  </section>
}
