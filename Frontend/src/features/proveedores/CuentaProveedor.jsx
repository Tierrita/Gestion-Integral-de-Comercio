import { useEffect, useMemo, useState } from 'react'
import { api } from '../../shared/api/client.js'
import Alert from '../../shared/components/Alert.jsx'
import Modal from '../../shared/components/Modal.jsx'
import styles from './CuentaProveedor.module.css'

const money = (value) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(Number(value || 0))
const date = (value) => value ? new Date(value).toLocaleString('es-AR') : '—'
const message = (error) => error.response?.data?.error || (error.response?.status === 403 ? 'No tenés permiso para esta operación.' : 'No se pudo completar la operación.')
const validAmount = (value) => /^\d+(?:[.,]\d{1,2})?$/.test(value.trim()) && Number(value.trim().replace(',', '.')) > 0

export default function CuentaProveedor({ proveedor, modo = 'detalle', esPropietario = false, onClose, onChange }) {
  const [saldo, setSaldo] = useState(null)
  const [pagos, setPagos] = useState([])
  const [compras, setCompras] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [revision, setRevision] = useState(0)
  const [monto, setMonto] = useState('')
  const [observaciones, setObservaciones] = useState('')
  const [saving, setSaving] = useState(false)
  const [anular, setAnular] = useState(null)
  const [motivo, setMotivo] = useState('')
  const [filter, setFilter] = useState('TODOS')
  const [search, setSearch] = useState('')

  useEffect(() => {
    if (!proveedor) return
    const controller = new AbortController()
    const timer = setTimeout(async () => {
      setLoading(true)
      setError('')
      const id = proveedor.id_proveedor
      try {
        const results = await Promise.all([
          api.get(`/proveedores/${id}/saldo`, { signal: controller.signal }),
          api.get(`/proveedores/${id}/pagos`, { signal: controller.signal }),
          api.get('/compras', { signal: controller.signal }),
        ])
        if (controller.signal.aborted) return
        const [saldoData, pagosData, comprasData] = results.map((r) => r.data)
        if (!Array.isArray(pagosData) || !Array.isArray(comprasData)) throw new Error('Respuesta de cuenta corriente inválida.')
        setSaldo(saldoData)
        setPagos(pagosData)
        setCompras(comprasData.filter((c) => Number(c.id_proveedor) === Number(id)))
      } catch (err) {
        if (!controller.signal.aborted) setError(message(err))
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }, 0)
    return () => { clearTimeout(timer); controller.abort() }
  }, [proveedor, revision])

  const movimientos = useMemo(() => [
    ...compras.map((c) => ({
      key: `compra-${c.id_compra}`, tipo: 'COMPRA', fecha: c.fecha_compra,
      numero: c.numero_compra, monto: c.total_compra, estado: c.estado, observaciones: c.observaciones,
    })),
    ...pagos.map((p) => ({
      key: `pago-${p.id_pago}`, tipo: 'PAGO', fecha: p.fecha_pago,
      monto: p.monto, estado: p.estado, observaciones: p.observaciones, pago: p,
    })),
  ].filter((m) => (filter === 'TODOS' || (filter === 'ANULADOS' ? ['ANULADA', 'ANULADO'].includes(String(m.estado).toUpperCase()) : m.tipo === filter)) &&
    [m.numero, m.tipo, m.estado, m.monto, m.observaciones].some((v) => String(v ?? '').toLowerCase().includes(search.toLowerCase())))
    .sort((a, b) => new Date(b.fecha || 0) - new Date(a.fecha || 0)), [compras, pagos, filter, search])

  async function registrar(event) {
    event.preventDefault()
    if (saving || !proveedor || proveedor.estado === false) return
    if (!validAmount(monto)) { setError('Ingresá un importe positivo de hasta dos decimales.'); return }
    setSaving(true)
    setError('')
    setNotice('')
    try {
      await api.post('/pagos-proveedor', {
        id_proveedor: proveedor.id_proveedor,
        monto: Number(monto.trim().replace(',', '.')),
        observaciones: observaciones.trim() || null,
      })
      setMonto('')
      setObservaciones('')
      setNotice('Pago registrado correctamente. No se modificó ninguna caja.')
      setRevision((v) => v + 1)
      onChange?.()
    } catch (err) { setError(message(err)) }
    finally { setSaving(false) }
  }

  async function confirmarAnulacion(event) {
    event.preventDefault()
    if (!esPropietario || !anular || saving) return
    if (motivo.trim().length < 5) { setError('El motivo debe tener al menos 5 caracteres.'); return }
    setSaving(true)
    setError('')
    setNotice('')
    try {
      await api.patch(`/pagos-proveedor/${anular.id_pago}/anular`, { motivo_anulacion: motivo.trim() })
      setAnular(null)
      setMotivo('')
      setNotice('Pago anulado. Se actualizó la deuda sin afectar cajas.')
      setRevision((v) => v + 1)
      onChange?.()
    } catch (err) { setError(message(err)) }
    finally { setSaving(false) }
  }

  return <Modal open={Boolean(proveedor)} onClose={() => { if (!saving) onClose?.() }} busy={saving}
    title={`${modo === 'pago' ? 'Registrar pago' : 'Cuenta corriente'} · ${proveedor?.nombre_proveedor || ''}`}
    description="Compras y pagos del proveedor. No se descuentan fondos de ninguna caja." size="large">
    <div className={styles.content}>
      {error && <Alert type="error">{error}</Alert>}
      {notice && <Alert type="success">{notice}</Alert>}
      {loading && <p role="status">Actualizando cuenta corriente…</p>}
      {saldo && <div className={styles.summary}>
        <article><span>Saldo actual</span><strong>{money(Math.abs(saldo.saldo))}</strong><small>{saldo.situacion === 'DEUDA' ? 'Deuda pendiente' : saldo.situacion === 'SALDO_A_FAVOR' ? 'Saldo a favor' : 'Al día'}</small></article>
        <article><span>Compras vigentes</span><strong>{money(saldo.total_compras)}</strong></article>
        <article><span>Pagos completados</span><strong>{money(saldo.total_pagos)}</strong></article>
      </div>}
      {modo === 'pago' && proveedor?.estado === false && <Alert type="warning">El proveedor está inactivo. Para registrar pagos, primero activalo.</Alert>}
      {modo === 'pago' && proveedor?.estado !== false && <form className={styles.form} onSubmit={(e) => void registrar(e)}>
        <h3>Registrar pago</h3>
        <p>Podés registrar pagos parciales o anticipos. El importe solo modifica el saldo del proveedor.</p>
        <label>Importe (ARS)<input required inputMode="decimal" value={monto} onChange={(e) => setMonto(e.target.value)} placeholder="15000,50" disabled={saving} /></label>
        <label>Observaciones (opcional)<textarea maxLength={500} rows={2} value={observaciones} onChange={(e) => setObservaciones(e.target.value)} disabled={saving} /></label>
        <button className={styles.primary} disabled={saving || !validAmount(monto)} type="submit">{saving ? 'Registrando…' : 'Confirmar pago'}</button>
      </form>}
      {modo === 'detalle' && <>
        <div className={styles.heading}><h3>Historial de compras y pagos</h3><button type="button" className={styles.secondary} disabled={loading} onClick={() => setRevision((v) => v + 1)}>Actualizar</button></div>
        <div className={styles.filters}>
          <label>Movimiento<select value={filter} onChange={(e) => setFilter(e.target.value)}><option value="TODOS">Todos</option><option value="COMPRA">Compras</option><option value="PAGO">Pagos</option><option value="ANULADOS">Anulados</option></select></label>
          <label>Buscar<input type="search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Número, importe o estado" /></label>
        </div>
        {movimientos.length ? <div className={styles.history}>{movimientos.map((m) => <article key={m.key} className={styles.item}>
          <div><strong>{m.tipo === 'COMPRA' ? `Compra #${m.numero ?? '—'}` : 'Pago registrado'}</strong><small>{date(m.fecha)} · {m.estado}</small>{m.observaciones && <small>{m.observaciones}</small>}</div>
          <div className={styles.right}><strong>{m.tipo === 'COMPRA' ? '+' : '−'}{money(m.monto)}</strong>{m.tipo === 'PAGO' && m.estado === 'COMPLETADO' && esPropietario && <button type="button" className={styles.secondary} onClick={() => { setAnular(m.pago); setMotivo(''); setError('') }}>Anular pago</button>}</div>
        </article>)}</div> : <p>No hay movimientos para mostrar.</p>}
        {anular && esPropietario && <form className={styles.form} onSubmit={(e) => void confirmarAnulacion(e)}>
          <h3>Anular pago de {money(anular.monto)}</h3>
          <p>El pago quedará registrado como anulado y dejará de descontarse de la deuda.</p>
          <label>Motivo de anulación<textarea required minLength={5} maxLength={500} rows={3} value={motivo} onChange={(e) => setMotivo(e.target.value)} disabled={saving} /></label>
          <div className={styles.buttons}><button type="button" className={styles.secondary} disabled={saving} onClick={() => setAnular(null)}>Cancelar</button><button type="submit" className={styles.danger} disabled={saving || motivo.trim().length < 5}>Confirmar anulación</button></div>
        </form>}
      </>}
    </div>
  </Modal>
}
