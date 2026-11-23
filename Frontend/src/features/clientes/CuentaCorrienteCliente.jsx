import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import Alert from '../../shared/components/Alert.jsx'
import Modal from '../../shared/components/Modal.jsx'
import styles from './CuentaCorrienteCliente.module.css'

const dinero = (n) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(Number(n || 0))
const fecha = (v) => v ? new Date(v).toLocaleString('es-AR') : '—'
const totalVenta = (venta) => venta.total ?? venta.total_venta
const errorDe = (e) => e.response?.data?.error || (e.response?.status === 403 ? 'No tenés permiso para consultar esta información.' : 'No se pudo consultar la cuenta corriente.')
const etiquetas = { DEUDA: 'Con deuda', AL_DIA: 'Al día', SALDO_A_FAVOR: 'Saldo a favor' }

export default function CuentaCorrienteCliente({ cliente, onClose, modo = 'detalle', onCobroRegistrado }) {
  const [saldo, setSaldo] = useState(null)
  const [ventas, setVentas] = useState(null)
  const [cobros, setCobros] = useState(null)
  const [errores, setErrores] = useState({})
  const [cargando, setCargando] = useState(false)
  const [revision, setRevision] = useState(0)
  const [cuentas, setCuentas] = useState([])
  const mostrarCobro = modo === 'cobro' && cuentas.length > 0
  const [monto, setMonto] = useState('')
  const [cuenta, setCuenta] = useState('')
  const [observaciones, setObservaciones] = useState('')
  const [guardando, setGuardando] = useState(false)
  const [errorCobro, setErrorCobro] = useState('')
  const [exitoCobro, setExitoCobro] = useState('')


  async function registrarCobro(event) {
    event.preventDefault()
    if (guardando || !cliente) return
    const limpio = monto.trim().replace(',', '.')
    const importe = Number(limpio)
    if (!/^\d+(?:\.\d{1,2})?$/.test(limpio) || !Number.isFinite(importe) || importe <= 0) {
      setErrorCobro('Ingresá un importe positivo con hasta dos decimales.')
      return
    }
    if (!cuentas.some((item) => item.id_cuenta === Number(cuenta))) {
      setErrorCobro('Seleccioná una cuenta válida.')
      return
    }
    setGuardando(true)
    setErrorCobro('')
    try {
      await api.post('/cobros', {
        id_cliente: cliente.id_cliente,
        id_cuenta: Number(cuenta),
        monto: importe,
        observaciones: observaciones.trim() || null,
      })
      setMonto('')
      setObservaciones('')
      setExitoCobro('Cobro registrado correctamente.')
      onCobroRegistrado?.()
      if (modo === 'cobro') onClose?.()
      setRevision((valor) => valor + 1)
    } catch (error) {
      setErrorCobro(error.response?.data?.error || errorDe(error))
    } finally {
      setGuardando(false)
    }
  }


  useEffect(() => {
    if (!cliente || modo !== 'cobro') return
    const controller = new AbortController()
    api.get('/cuentas', { signal: controller.signal })
      .then(({ data }) => {
        if (controller.signal.aborted) return
        const activas = (data?.cuentas || []).filter((item) => item.estado === true)
        if (!activas.length) {
          setErrorCobro('No hay cuentas financieras activas.')
          return
        }
        setCuentas(activas)
        setCuenta(String(activas[0].id_cuenta))
      })
      .catch((error) => {
        if (!controller.signal.aborted) {
          setErrorCobro(error.response?.data?.error || error.message || 'No se pudieron cargar las cuentas.')
        }
      })
    return () => controller.abort()
  }, [cliente, modo])

  useEffect(() => {
    if (!cliente) return
    const controller = new AbortController()
    const timer = setTimeout(async () => {
      setCargando(true)
      setSaldo(null)
      setVentas(null)
      setCobros(null)
      setErrores({})
      const id = cliente.id_cliente
      const peticiones = [
        ['saldo', `/clientes/${id}/saldo`],
        ['ventas', `/clientes/${id}/ventas`],
        ['cobros', `/clientes/${id}/cobros`],
      ]
      const resultados = await Promise.allSettled(peticiones.map(([, ruta]) => api.get(ruta, { signal: controller.signal })))
      if (controller.signal.aborted) return
      const fallas = {}
      resultados.forEach((resultado, index) => {
        const tipo = peticiones[index][0]
        if (resultado.status === 'rejected') {
          fallas[tipo] = errorDe(resultado.reason)
        } else {
          const data = resultado.value.data
          if (tipo === 'saldo') {
            if (typeof data?.saldo === 'number' && typeof data?.situacion === 'string') setSaldo(data)
            else fallas[tipo] = 'Formato de saldo inválido.'
          }
          if (tipo === 'ventas') {
            if (Array.isArray(data?.ventas)) setVentas(data.ventas)
            else fallas[tipo] = 'Formato de ventas inválido.'
          }
          if (tipo === 'cobros') {
            if (Array.isArray(data?.cobros)) setCobros(data.cobros)
            else fallas[tipo] = 'Formato de cobros inválido.'
          }
        }
      })
      setErrores(fallas)
      setCargando(false)
    }, 0)
    return () => { clearTimeout(timer); controller.abort() }
  }, [cliente, revision])

  return <Modal open={Boolean(cliente)} onClose={onClose} title={`${modo === 'cobro' ? 'Registrar cobro' : 'Detalle del cliente'} · ${cliente?.nombre_completo || ''}`} description={modo === "cobro" ? "Registrá el importe recibido y elegí la cuenta de destino." : "Saldo actual, ventas y cobros registrados."} size="large">
    <div className={styles.contenido}>
      {modo !== "cobro" && <div className={styles.barra}>
        <span>Cliente #{cliente?.numero_cliente}</span>
        <div className={styles.acciones}>
          <button type="button" className={styles.boton} disabled={cargando || guardando} onClick={() => setRevision((v) => v + 1)}>Actualizar cuenta</button>

        </div>
      </div>}
      {exitoCobro && <Alert type="success">{exitoCobro}</Alert>}
      {errorCobro && <Alert type="error">{errorCobro}</Alert>}
      {mostrarCobro && <form className={styles.formulario} onSubmit={(event) => void registrarCobro(event)}>
        <h3>Registrar cobro</h3>
        <p className={styles.aclaracion}>Se permiten cobros parciales y anticipos con saldo a favor.</p>
        <label>Importe recibido (ARS)<input required inputMode="decimal" value={monto} onChange={(event) => setMonto(event.target.value)} placeholder="15000,50" disabled={guardando} /></label>
        <label>Cuenta de destino<select required value={cuenta} onChange={(event) => setCuenta(event.target.value)} disabled={guardando}>
          {cuentas.map((item) => <option key={item.id_cuenta} value={item.id_cuenta}>{item.nombre_cuenta}</option>)}
        </select></label>
        <label>Observaciones (opcional)<textarea rows={2} maxLength={500} value={observaciones} onChange={(event) => setObservaciones(event.target.value)} disabled={guardando} /></label>
        <button className={styles.principal} type="submit" disabled={guardando}>{guardando ? 'Registrando…' : 'Confirmar cobro'}</button>
      </form>}
      {modo !== "cobro" && cargando && <p role="status">Consultando movimientos…</p>}
      {modo !== "cobro" && errores.saldo && <Alert type="error">Saldo: {errores.saldo}</Alert>}
      {saldo && <div className={styles.resumen}>
        <article><span>Saldo actual</span><strong className={saldo.situacion === 'DEUDA' ? styles.deuda : styles.saldo}>{dinero(Math.abs(saldo.saldo))}</strong><small>{etiquetas[saldo.situacion] || saldo.situacion}</small></article>
        <article><span>Ventas vigentes</span><strong>{dinero(saldo.total_ventas)}</strong></article>
        <article><span>Cobros completados</span><strong>{dinero(saldo.total_cobros)}</strong></article>
      </div>}
      {modo !== "cobro" && <p className={styles.aclaracion}>El saldo se calcula con ventas vigentes a cuenta corriente menos cobros completados. Un saldo a favor no es una deuda.</p>}
      {modo !== "cobro" && <><h3>Ventas del cliente</h3>
      {errores.ventas && <Alert type="error">Ventas: {errores.ventas}</Alert>}
      {ventas && (ventas.length ? <div className={styles.scroll}><table><thead><tr><th>Venta</th><th>Fecha</th><th>Estado</th><th>Total</th><th>Comprobante</th></tr></thead><tbody>
        {ventas.map(({ venta }) => <tr key={venta.id_venta}><td>{venta.numero_venta != null ? `#${venta.numero_venta}` : "—"}</td><td>{fecha(venta.fecha_venta)}</td><td>{venta.estado}</td><td>{totalVenta(venta) == null ? "—" : dinero(totalVenta(venta))}</td><td><Link to={`/ventas/${venta.id_venta}/comprobante`} onClick={onClose}>Ver comprobante</Link></td></tr>)}
      </tbody></table></div> : <p className={styles.vacio}>Este cliente todavía no tiene ventas.</p>)}
      <h3>Cobros registrados</h3>
      {errores.cobros && <Alert type="error">Cobros: {errores.cobros}</Alert>}
      {cobros && (cobros.length ? <div className={styles.scroll}><table><thead><tr><th>N.º</th><th>Fecha</th><th>Estado</th><th>Importe</th></tr></thead><tbody>
        {cobros.map((c) => <tr key={c.id_cobro}><td>{c.numero_cobro != null ? `#${c.numero_cobro}` : "—"}</td><td>{fecha(c.fecha_cobro)}</td><td>{c.estado}</td><td>{dinero(c.monto)}</td></tr>)}
      </tbody></table></div> : <p className={styles.vacio}>Este cliente todavía no tiene cobros registrados.</p>)}
      <p className={styles.aclaracion}>Los cobros se acreditan en la cuenta financiera seleccionada. La anulación está reservada al propietario.</p></>}
    </div>
  </Modal>
}
