import { useCallback, useEffect, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'
import { api } from '../../shared/api/client.js'
import Alert from '../../shared/components/Alert.jsx'
import Modal from '../../shared/components/Modal.jsx'
import ConfirmDialog from '../../shared/components/ConfirmDialog.jsx'
import styles from './Clientes.module.css'
import CuentaCorrienteCliente from './CuentaCorrienteCliente.jsx'

const messageOf = (error) => error.response?.data?.error || (error.response?.status === 403 ? 'No tenés permisos para esta operación.' : 'No se pudo completar la operación. Verificá la conexión con Flask.')
const money = (value) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(Number(value || 0))
const PAGE_SIZES = [10, 25, 50]

export default function Clientes({ esPropietario = false }) {
  const [clientes, setClientes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('todos')
  const [pageSize, setPageSize] = useState(10)
  const [page, setPage] = useState(1)
  const [sort, setSort] = useState({ key: 'numero_cliente', asc: true })
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ nombre_completo: '', telefono: '' })
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)
  const [pending, setPending] = useState(null)
  const [statusError, setStatusError] = useState('')
  const [changing, setChanging] = useState(false)
  const [accountClient, setAccountClient] = useState(null)
  const [cobroClient, setCobroClient] = useState(null)
  const [saldos, setSaldos] = useState({})
  const [saldosError, setSaldosError] = useState('')
  const [menu, setMenu] = useState(null)

  const loadSaldos = useCallback(async () => {
    try {
      const { data } = await api.get('/clientes/saldos')
      if (!Array.isArray(data?.saldos)) throw new Error('Formato de saldos inválido')
      setSaldos(Object.fromEntries(data.saldos.map((item) => [item.id_cliente, item])))
      setSaldosError('')
    } catch (err) {
      setSaldos({})
      setSaldosError(messageOf(err))
    }
  }, [])

  const load = useCallback(async (signal) => {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get('/clientes', { signal })
      if (!Array.isArray(data)) throw new Error('Formato inválido')
      if (!signal?.aborted) { setClientes(data); void loadSaldos() }
    } catch (err) {
      if (!signal?.aborted) setError(messageOf(err))
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [loadSaldos])

  useEffect(() => {
    const controller = new AbortController()
    const timer = setTimeout(() => { void load(controller.signal) }, 0)
    return () => { clearTimeout(timer); controller.abort() }
  }, [load])

  const totalDeuda = Object.values(saldos).reduce((sum, item) => sum + Math.max(0, item.saldo), 0)
  const totalFavor = Object.values(saldos).reduce((sum, item) => sum + Math.max(0, -item.saldo), 0)
  const filtered = useMemo(() => clientes.filter((c) => {
    const active = c.estado !== false
    return (filter === 'todos' || (filter === 'activos' ? active : !active)) &&
      [c.nombre_completo, c.numero_cliente, c.telefono].some((v) => String(v ?? '').toLowerCase().includes(query.trim().toLowerCase()))
  }).sort((a, b) => {
    const av = a[sort.key] ?? ''
    const bv = b[sort.key] ?? ''
    const result = sort.key === 'numero_cliente' ? Number(av) - Number(bv) : String(av).localeCompare(String(bv), 'es-AR', { numeric: true })
    return sort.asc ? result : -result
  }), [clientes, filter, query, sort])
  const pages = Math.max(1, Math.ceil(filtered.length / pageSize))
  const currentPage = Math.min(page, pages)
  const rows = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize)
  const changeSort = (key) => { setSort((old) => ({ key, asc: old.key === key ? !old.asc : true })); setPage(1) }
  const sortMark = (key) => sort.key === key ? (sort.asc ? ' ↑' : ' ↓') : ' ↕'

  function openForm(client = null) {
    setEditing(client || 'new')
    setForm({ nombre_completo: client?.nombre_completo || '', telefono: client?.telefono || '' })
    setFormError('')
  }

  async function submit(event) {
    event.preventDefault()
    if (saving) return
    const nombre = form.nombre_completo.trim()
    if (nombre.length < 2) { setFormError('El nombre debe tener al menos 2 caracteres.'); return }
    setSaving(true)
    setFormError('')
    try {
      const payload = editing !== 'new' && Number(editing.numero_cliente) === 1
        ? { telefono: form.telefono.trim() || null }
        : { nombre_completo: nombre, telefono: form.telefono.trim() || null }
      const { data } = editing === 'new' ? await api.post('/clientes', payload) : await api.patch(`/clientes/${editing.id_cliente}`, payload)
      setEditing(null)
      setNotice(data.message || 'Cliente guardado correctamente.')
      await load()
    } catch (err) { setFormError(messageOf(err)) }
    finally { setSaving(false) }
  }

  async function changeStatus() {
    if (!pending || changing) return
    setChanging(true)
    setStatusError('')
    try {
      const { data } = await api.patch(`/clientes/${pending.id_cliente}/estado`, { estado: pending.estado === false })
      setPending(null)
      setNotice(data.message || 'Estado actualizado.')
      await load()
    } catch (err) { setStatusError(messageOf(err)) }
    finally { setChanging(false) }
  }


  return <section className={styles.page}>
    <header className={styles.header}>
      <div><p className={styles.eyebrow}>GESTIÓN COMERCIAL</p><h1>Clientes</h1><p className={styles.muted}>Administrá tus clientes y consultá sus operaciones.</p></div>
      <button className={styles.primary} type="button" onClick={() => openForm()}>+ Nuevo cliente</button>
    </header>
    <div className={styles.metrics}>
      <article><span>Total de clientes</span><strong>{clientes.length}</strong></article>
      <article><span>Total por cobrar</span><strong>{saldosError ? '—' : money(totalDeuda)}</strong></article>
      <article><span>Saldos a favor</span><strong>{saldosError ? '—' : money(totalFavor)}</strong></article>
    </div>
    {notice && <Alert type="success">{notice}</Alert>}
    {error && <Alert type="error">{error}</Alert>}
    {saldosError && <Alert type="warning">No se pudieron cargar los saldos: {saldosError}</Alert>}
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <label>Buscar cliente<input type="search" placeholder="Nombre, número o teléfono" value={query} onChange={(e) => { setQuery(e.target.value); setPage(1) }} /></label>
        <label>Estado<select value={filter} onChange={(e) => { setFilter(e.target.value); setPage(1) }}><option value="todos">Todos</option><option value="activos">Activos</option><option value="inactivos">Inactivos</option></select></label>
        <label>Mostrar<select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1) }}>{PAGE_SIZES.map((n) => <option key={n} value={n}>{n} registros</option>)}</select></label>
        <button className={styles.secondary} type="button" disabled={loading} onClick={() => void load()}>Actualizar</button>
      </div>
      <p className={styles.muted}>{filtered.length} clientes encontrados</p>
      {loading ? <p role="status">Cargando clientes…</p> : error && clientes.length === 0 ? <p>No se pudo cargar el listado.</p> : filtered.length === 0 ? <p>No hay clientes para mostrar.</p> : <div className={styles.scroll}><table><thead><tr>
        <th><button type="button" onClick={() => changeSort('numero_cliente')}>N.º{sortMark('numero_cliente')}</button></th>
        <th><button type="button" onClick={() => changeSort('nombre_completo')}>Cliente{sortMark('nombre_completo')}</button></th>
        <th>Teléfono</th><th>Estado</th><th>Saldo</th><th>Acciones</th>
      </tr></thead><tbody>{rows.map((c) => <tr key={c.id_cliente}>
        <td>#{c.numero_cliente}</td><td><strong>{c.nombre_completo}</strong></td><td>{c.telefono || '—'}</td>
        <td><span className={c.estado === false ? styles.inactive : styles.active}>{c.estado === false ? 'Inactivo' : 'Activo'}</span></td>
        <td>{saldos[c.id_cliente] ? <span className={saldos[c.id_cliente].saldo > 0 ? styles.deuda : saldos[c.id_cliente].saldo < 0 ? styles.favor : styles.neutro}>{money(Math.abs(saldos[c.id_cliente].saldo))} · {saldos[c.id_cliente].saldo > 0 ? 'Debe' : saldos[c.id_cliente].saldo < 0 ? 'A favor' : 'Al día'}</span> : '—'}</td>
        <td><div className={styles.actions}>
          {Number(c.numero_cliente) !== 1 && c.estado !== false && <button className={styles.primary} type="button" onClick={() => setCobroClient(c)}>Cobrar</button>}
          <button className={styles.secondary} type="button" onClick={() => setAccountClient(c)}>Ver detalle</button>
          <button className={styles.menuTrigger} type="button" aria-label={`Más opciones para ${c.nombre_completo}`} aria-expanded={menu?.cliente.id_cliente === c.id_cliente} onClick={(event) => {
            if (menu?.cliente.id_cliente === c.id_cliente) { setMenu(null); return }
            const rect = event.currentTarget.getBoundingClientRect()
            const width = 190
            const height = 110
            setMenu({ cliente: c, top: rect.bottom + height > window.innerHeight ? Math.max(8, rect.top - height) : rect.bottom + 4, left: Math.max(8, Math.min(rect.right - width, window.innerWidth - width - 8)) })
          }}>···</button></div></td>
      </tr>)}</tbody></table></div>}
      {!loading && filtered.length > 0 && <div className={styles.pagination}><span>Mostrando {(currentPage - 1) * pageSize + 1}–{Math.min(currentPage * pageSize, filtered.length)} de {filtered.length}</span><div className={styles.actions}><button className={styles.secondary} type="button" disabled={currentPage === 1} onClick={() => setPage((n) => n - 1)}>Anterior</button><span>Página {currentPage} de {pages}</span><button className={styles.secondary} type="button" disabled={currentPage === pages} onClick={() => setPage((n) => n + 1)}>Siguiente</button></div></div>}
    </div>
    {menu && createPortal(<>
      <button type="button" className={styles.menuBackdrop} aria-label="Cerrar opciones" onClick={() => setMenu(null)} />
      <div className={styles.floatingMenu} role="group" aria-label={`Opciones de ${menu.cliente.nombre_completo}`} style={{ top: menu.top, left: menu.left }}>
        <button type="button" onClick={() => { openForm(menu.cliente); setMenu(null) }}>Editar cliente</button>
        {Number(menu.cliente.numero_cliente) !== 1 && <button type="button" onClick={() => { setPending(menu.cliente); setStatusError(''); setMenu(null) }}>{menu.cliente.estado === false ? 'Activar cliente' : 'Desactivar cliente'}</button>}
      </div>
    </>, document.body)}
    <Modal open={editing !== null} onClose={() => { if (!saving) setEditing(null) }} title={editing === 'new' ? 'Nuevo cliente' : 'Editar cliente'} description="Completá los datos del cliente." busy={saving} size="small">
      <form className={styles.form} onSubmit={(event) => void submit(event)}>
        <label>Nombre completo<input required minLength={2} maxLength={150} disabled={editing !== 'new' && Number(editing?.numero_cliente) === 1} value={form.nombre_completo} onChange={(e) => setForm((f) => ({ ...f, nombre_completo: e.target.value }))} /></label>
        <label>Teléfono (opcional)<input type="tel" maxLength={50} value={form.telefono} onChange={(e) => setForm((f) => ({ ...f, telefono: e.target.value }))} /></label>
        {editing !== 'new' && Number(editing?.numero_cliente) === 1 && <Alert type="warning">El nombre de CLIENTE GENERAL está protegido.</Alert>}
        {formError && <Alert type="error">{formError}</Alert>}
        <div className={styles.actions}><button className={styles.secondary} type="button" disabled={saving} onClick={() => setEditing(null)}>Cancelar</button><button className={styles.primary} type="submit" disabled={saving}>{saving ? 'Guardando…' : 'Guardar cliente'}</button></div>
      </form>
    </Modal>
    <ConfirmDialog open={Boolean(pending)} onClose={() => { if (!changing) { setPending(null); setStatusError('') } }} onConfirm={() => void changeStatus()} title={pending?.estado === false ? 'Activar cliente' : 'Desactivar cliente'} description="Confirmá el cambio de estado del cliente." details={pending ? [{ label: 'Cliente', value: pending.nombre_completo }] : []} error={statusError} busy={changing} destructive={pending?.estado !== false} confirmLabel={pending?.estado === false ? 'Activar' : 'Desactivar'} />
    <CuentaCorrienteCliente cliente={accountClient} esPropietario={esPropietario} onClose={() => setAccountClient(null)} onCobroRegistrado={() => void loadSaldos()} />
    <CuentaCorrienteCliente cliente={cobroClient} modo="cobro" onClose={() => setCobroClient(null)} onCobroRegistrado={() => void loadSaldos()} />

  </section>
}
