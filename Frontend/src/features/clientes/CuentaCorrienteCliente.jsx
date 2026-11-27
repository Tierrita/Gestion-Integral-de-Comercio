import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import Alert from '../../shared/components/Alert.jsx'
import Modal from '../../shared/components/Modal.jsx'
import ActionButton from '../../shared/components/ActionButton.jsx'
import styles from './CuentaCorrienteCliente.module.css'

const dinero = (n) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(Number(n || 0))
const fecha = (v) => v ? new Date(v).toLocaleString('es-AR') : '—'
const totalVenta = (venta) => venta.total ?? venta.total_venta
const errorDe = (e) => e.response?.data?.error || (e.response?.status === 403 ? 'No tenés permiso para consultar esta información.' : 'No se pudo consultar la cuenta corriente.')
const etiquetas = { DEUDA: 'Con deuda', AL_DIA: 'Al día', SALDO_A_FAVOR: 'Saldo a favor' }

export default function CuentaCorrienteCliente({ cliente, onClose, modo = 'detalle', onCobroRegistrado, esPropietario = false }) {
  const [saldo, setSaldo] = useState(null)
  const [ventas, setVentas] = useState(null)
  const [cobros, setCobros] = useState(null)
  const [movimientos, setMovimientos] = useState(null)
  const [errores, setErrores] = useState({})
  const [filtro, setFiltro] = useState('TODOS')
  const [busqueda, setBusqueda] = useState('')
  const [expandido, setExpandido] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [revision, setRevision] = useState(0)
  const [cuentas, setCuentas] = useState([])
  const mostrarCobro = modo === 'cobro' && cuentas.length > 0
  const [monto, setMonto] = useState('')
  const [cuenta, setCuenta] = useState('')
  const [observaciones, setObservaciones] = useState('')
  const [guardando, setGuardando] = useState(false)
  const [revisandoCobro, setRevisandoCobro] = useState(false)
  const [errorCobro, setErrorCobro] = useState('')
  const [exitoCobro, setExitoCobro] = useState('')
  const [cobroAnular, setCobroAnular] = useState(null)
  const formularioAnulacionRef = useRef(null)
  const [motivoAnulacion, setMotivoAnulacion] = useState('')
  const [anulando, setAnulando] = useState(false)
  const [errorAnulacion, setErrorAnulacion] = useState('')
  const [exitoAnulacion, setExitoAnulacion] = useState('')


  const movimientosFiltrados = useMemo(() => {
    const termino = busqueda.trim().toLocaleLowerCase('es-AR')
    return (movimientos || []).filter((m) => {
      const esReversion = m.tipo.startsWith('ANULACION_')
      const clase = esReversion ? 'ANULACIONES' : m.origen === 'VENTA' ? 'VENTAS' : 'COBROS'
      if (filtro !== 'TODOS' && clase !== filtro) return false
      if (!termino) return true
      return [m.numero_venta, m.cuenta, m.metodo_pago, m.tipo, m.origen, m.monto, m.id_operacion]
        .some((dato) => String(dato ?? '').toLocaleLowerCase('es-AR').includes(termino))
    })
  }, [movimientos, filtro, busqueda])

  const cobrosPorId = useMemo(() => new Map((cobros || []).map((c) => [Number(c.id_cobro), c])), [cobros])
  const ventasPorId = useMemo(() => new Map((ventas || []).map(({ venta }) => [Number(venta.id_venta), venta])), [ventas])

  const importeCobro = Number(monto.trim().replace(',', '.'))
  const importeValido = /^\d+(?:[.,]\d{1,2})?$/.test(monto.trim()) && Number.isFinite(importeCobro) && importeCobro > 0
  const saldoActual = typeof saldo?.saldo === 'number' ? saldo.saldo : null
  const saldoPosterior = saldoActual === null || !importeValido ? null : Math.round((saldoActual - importeCobro) * 100) / 100
  const cuentaSeleccionada = cuentas.find((item) => item.id_cuenta === Number(cuenta))

  function revisarCobro(event) {
    event.preventDefault()
    if (guardando || !cliente || cargando) return
    if (!importeValido) {
      setErrorCobro('Ingresá un importe positivo con hasta dos decimales.')
      return
    }
    if (!cuentaSeleccionada) {
      setErrorCobro('Seleccioná una cuenta válida.')
      return
    }
    if (saldoActual === null) {
      setErrorCobro('No se pudo consultar el saldo actualizado. Reintentá antes de registrar el cobro.')
      return
    }
    setErrorCobro('')
    setRevisandoCobro(true)
  }

  async function registrarCobro() {
    if (guardando || !cliente || !revisandoCobro || !importeValido || !cuentaSeleccionada || saldoActual === null) return
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
        monto: limpio,
        observaciones: observaciones.trim() || null,
      })
      setMonto('')
      setObservaciones('')
      setRevisandoCobro(false)
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


  async function confirmarAnulacion(event) {
    event.preventDefault()
    if (!esPropietario || !cobroAnular || anulando) return
    const motivo = motivoAnulacion.trim()
    if (motivo.length < 5) {
      setErrorAnulacion('El motivo debe tener al menos 5 caracteres.')
      return
    }
    setAnulando(true)
    setErrorAnulacion('')
    try {
      await api.patch('/cobros/' + cobroAnular.id_cobro + '/anular', { motivo_anulacion: motivo })
      setCobroAnular(null)
      setMotivoAnulacion('')
      setExitoAnulacion('Cobro anulado correctamente. Revisá el saldo y la caja.')
      setRevision((valor) => valor + 1)
      onCobroRegistrado?.()
    } catch (error) {
      setErrorAnulacion(error.response?.data?.error || 'No se pudo anular el cobro.')
    } finally {
      setAnulando(false)
    }
  }

  useEffect(() => {
    if (!cobroAnular) return
    const timer = setTimeout(() => formularioAnulacionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 0)
    return () => clearTimeout(timer)
  }, [cobroAnular])

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
      setMovimientos(null)
      setErrores({})
      const id = cliente.id_cliente
      const peticiones = [
        ['saldo', `/clientes/${id}/saldo`],
        ['ventas', `/clientes/${id}/ventas`],
        ['cobros', `/clientes/${id}/cobros`],
        ['movimientos', `/clientes/${id}/movimientos-financieros`],
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
          if (tipo === 'movimientos') {
            if (Array.isArray(data?.movimientos)) setMovimientos(data.movimientos)
            else fallas[tipo] = 'Formato de movimientos inválido.'
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
      {exitoAnulacion && <Alert type="success">{exitoAnulacion}</Alert>}
      {errorCobro && <Alert type="error">{errorCobro}</Alert>}
      {cobroAnular && esPropietario && <form ref={formularioAnulacionRef} className={styles.formulario} onSubmit={(event) => void confirmarAnulacion(event)}>
        <h3>Anular cobro</h3>
        <p className={styles.aclaracion}>Cobro seleccionado: <strong>{dinero(cobroAnular.monto)}</strong>. Esta operación revierte el ingreso financiero y modifica el saldo del cliente.</p>
        <label>Motivo de anulación (mínimo 5 caracteres)
          <textarea required minLength={5} maxLength={500} rows={3} value={motivoAnulacion} onChange={(event) => setMotivoAnulacion(event.target.value)} disabled={anulando} placeholder="Ej.: Cobro registrado por error" />
        </label>
        {errorAnulacion && <Alert type="error">{errorAnulacion}</Alert>}
        <div className={styles.acciones}>
          <button type="button" className={styles.boton} disabled={anulando} onClick={() => setCobroAnular(null)}>Cancelar</button>
          <button type="submit" className={styles.anularConfirmar} disabled={anulando || motivoAnulacion.trim().length < 5}>{anulando ? 'Anulando…' : 'Confirmar anulación'}</button>
        </div>
      </form>}
      {modo === 'cobro' && errores.saldo && <Alert type="error">Saldo: {errores.saldo}</Alert>}
      {modo === 'cobro' && cargando && <p role="status">Consultando saldo actualizado…</p>}
      {mostrarCobro && <form className={styles.formulario} onSubmit={revisarCobro}>
        <div className={styles.cobroEncabezado}>
          <div><span className={styles.cobroEyebrow}>AIOnix · Gestión financiera</span><h3>Registrar cobro</h3></div>
          <span className={styles.cobroEstado}>Cobro manual</span>
        </div>
        <div className={styles.cobroSaldos}>
          <div><span>Saldo actual</span><strong className={saldoActual > 0 ? styles.deuda : saldoActual < 0 ? styles.favor : styles.neutro}>{saldoActual === null ? 'Consultando…' : dinero(Math.abs(saldoActual))}</strong><small>{saldoActual === null ? 'Pendiente de consulta' : saldoActual > 0 ? 'Deuda pendiente' : saldoActual < 0 ? 'Saldo a favor' : 'Al día'}</small></div>
          <div><span>Saldo después del cobro</span><strong className={saldoPosterior > 0 ? styles.deuda : saldoPosterior < 0 ? styles.favor : styles.neutro}>{saldoPosterior === null ? '—' : dinero(Math.abs(saldoPosterior))}</strong><small>{saldoPosterior === null ? 'Ingresá un importe válido' : saldoPosterior > 0 ? 'Deuda pendiente' : saldoPosterior < 0 ? 'Saldo a favor' : 'Al día'}</small></div>
        </div>
        <p className={styles.aclaracion}>Se permiten cobros parciales y anticipos con saldo a favor.</p>
        <label>Importe recibido (ARS)<input required inputMode="decimal" value={monto} onChange={(event) => { setMonto(event.target.value); setRevisandoCobro(false) }} placeholder="15000,50" disabled={guardando || revisandoCobro} /></label>
        <label>Cuenta de destino<select required value={cuenta} onChange={(event) => { setCuenta(event.target.value); setRevisandoCobro(false) }} disabled={guardando || revisandoCobro}>
          {cuentas.map((item) => <option key={item.id_cuenta} value={item.id_cuenta}>{item.nombre_cuenta}</option>)}
        </select></label>
        <label>Observaciones (opcional)<textarea rows={2} maxLength={500} value={observaciones} onChange={(event) => { setObservaciones(event.target.value); setRevisandoCobro(false) }} disabled={guardando || revisandoCobro} /></label>
        {revisandoCobro && <div className={styles.cobroRevision} role="status">
          <strong>Revisá antes de confirmar</strong>
          <span>Cliente: {cliente?.nombre_completo}</span>
          <span>Importe: {dinero(importeCobro)}</span>
          <span>Cuenta: {cuentaSeleccionada?.nombre_cuenta}</span>
          <span>Saldo posterior: {saldoPosterior === null ? '—' : dinero(Math.abs(saldoPosterior))} · {saldoPosterior > 0 ? 'Deuda' : saldoPosterior < 0 ? 'A favor' : 'Al día'}</span>
        </div>}
        <div className={styles.cobroAcciones}>
          <ActionButton variant="secondary" type="button" disabled={guardando} onClick={() => revisandoCobro ? setRevisandoCobro(false) : onClose?.()}>{revisandoCobro ? 'Modificar datos' : 'Cancelar'}</ActionButton>
          {revisandoCobro
            ? <ActionButton variant="primary" type="button" disabled={guardando} onClick={() => void registrarCobro()}>{guardando ? 'Registrando…' : 'Confirmar cobro'}</ActionButton>
            : <ActionButton variant="primary" type="submit" disabled={guardando || cargando || saldoActual === null || !importeValido || !cuentaSeleccionada}>Revisar cobro</ActionButton>}
        </div>
      </form>}
      {modo !== "cobro" && cargando && <p role="status">Consultando movimientos…</p>}
      {modo !== "cobro" && errores.saldo && <Alert type="error">Saldo: {errores.saldo}</Alert>}
      {modo !== 'cobro' && saldo && <div className={styles.resumen}>
        <article><span>Saldo actual</span><strong className={saldo.situacion === 'DEUDA' ? styles.deuda : styles.saldo}>{dinero(Math.abs(saldo.saldo))}</strong><small>{etiquetas[saldo.situacion] || saldo.situacion}</small></article>
        <article><span>Ventas vigentes</span><strong>{dinero(saldo.total_ventas)}</strong></article>
        <article><span>Cobros completados</span><strong>{dinero(saldo.total_cobros)}</strong></article>
      </div>}
      {modo !== "cobro" && <p className={styles.aclaracion}>El saldo se calcula con ventas vigentes a cuenta corriente menos cobros completados. Un saldo a favor no es una deuda.</p>}
      {modo !== "cobro" && <>
      <div className={styles.historialEncabezado}>
        <div>
          <h3>Movimientos del cliente</h3>
          <p className={styles.aclaracion}>Ventas cobradas, cobros de deuda y anulaciones. Las ventas a crédito figuran en «Todas las ventas».</p>
        </div>
        <span className={styles.contador}>{movimientosFiltrados.length} movimientos</span>
      </div>
      {errores.movimientos && <Alert type="error">Movimientos: {errores.movimientos}</Alert>}
      {errores.cobros && <Alert type="error">Cobros: {errores.cobros}</Alert>}
      <div className={styles.filtros}>
        <div className={styles.pestanas} role="group" aria-label="Filtrar movimientos">
          {['TODOS', 'VENTAS', 'COBROS', 'ANULACIONES'].map((opcion) => <button key={opcion} type="button" aria-pressed={filtro === opcion} className={filtro === opcion ? styles.pestanaActiva : styles.pestana} onClick={() => setFiltro(opcion)}>{opcion === 'TODOS' ? 'Todos' : opcion === 'VENTAS' ? 'Ventas' : opcion === 'COBROS' ? 'Cobros' : 'Anulaciones'}</button>)}
        </div>
        <input className={styles.buscar} type="search" aria-label="Buscar movimientos" placeholder="Buscar por venta, cuenta o importe" value={busqueda} onChange={(event) => setBusqueda(event.target.value)} />
      </div>
      {movimientos && (movimientosFiltrados.length ? <div className={styles.movimientos}>
        {movimientosFiltrados.map((m) => {
          const esVenta = m.origen === 'VENTA'
          const reversion = m.tipo.startsWith('ANULACION_')
          const venta = esVenta ? ventasPorId.get(Number(m.id_operacion)) : null
          const cobro = !esVenta ? cobrosPorId.get(Number(m.id_operacion)) : null
          const vigente = esVenta ? String(venta?.estado ?? m.estado_operacion).toUpperCase() === 'COMPLETADA' : String(cobro?.estado ?? m.estado_operacion).toUpperCase() === 'COMPLETADO'
          const titulo = reversion ? (esVenta ? 'Anulación de venta' : 'Anulación de cobro') : esVenta ? 'Venta cobrada' : 'Cobro de cliente'
          const numero = esVenta && m.numero_venta != null ? `#${m.numero_venta}` : ''
          const metodo = esVenta ? String(m.metodo_pago || 'Pago').replaceAll('_', ' ') : 'Cobro de deuda'
          const abierto = expandido === m.id_movimiento
          return <article key={m.id_movimiento} className={styles.movimiento}>
            <div className={styles.movimientoFila}>
              <div className={styles.movimientoInfo}>
                <div className={styles.movimientoTitulo}><strong>{titulo} {numero}</strong><span className={reversion ? styles.etiquetaAnulada : vigente ? styles.etiquetaVigente : styles.etiquetaAnulada}>{reversion ? 'Reversión' : vigente ? 'Registrado' : 'Anulado'}</span></div>
                <span className={styles.aclaracion}>{metodo} · {m.cuenta}</span>
                <span className={styles.aclaracion}>{fecha(m.fecha)}</span>
              </div>
              <div className={styles.movimientoDerecha}>
                <strong className={reversion ? styles.importeNegativo : styles.importePositivo}>{reversion ? '−' : '+'}{dinero(m.monto)}</strong>
                <button type="button" className={styles.boton} aria-expanded={abierto} onClick={() => setExpandido(abierto ? null : m.id_movimiento)}>{abierto ? 'Ocultar' : 'Ver detalle'}</button>
              </div>
            </div>
            {abierto && <div className={styles.movimientoDetalle}>
              <p><strong>Origen:</strong> {esVenta ? 'Venta' : 'Cobro posterior'} · <strong>Estado:</strong> {String(m.estado_operacion).replaceAll('_', ' ')}</p>
              <p><strong>Cuenta:</strong> {m.cuenta} · <strong>Fecha:</strong> {fecha(m.fecha)}</p>
              <div className={styles.acciones}>
                {esVenta && <Link to={`/ventas/${m.id_operacion}/comprobante`} onClick={onClose}>Ver comprobante</Link>}
                {esVenta && <Link to="/ventas" onClick={onClose}>Gestionar venta</Link>}
                {!esVenta && !reversion && vigente && esPropietario && cobro && <button type="button" className={styles.anular} onClick={() => { setCobroAnular(cobro); setMotivoAnulacion(''); setErrorAnulacion(''); setExitoAnulacion('') }}>Anular cobro</button>}
                {esVenta && !reversion && vigente && esPropietario && <span className={styles.aclaracion}>Para anular la venta completa, ingresá a Ventas → Ver detalle. Esto también devuelve el stock.</span>}
              </div>
            </div>}
          </article>
        })}
      </div> : <p className={styles.vacio}>No hay movimientos para este filtro.</p>)}
      <details className={styles.ventasAdicionales}>
        <summary>Todas las ventas del cliente (incluidas las ventas a crédito)</summary>
        {errores.ventas && <Alert type="error">Ventas: {errores.ventas}</Alert>}
        {ventas && (ventas.length ? <div className={styles.scroll}><table><thead><tr><th>Venta</th><th>Fecha</th><th>Estado</th><th>Total</th><th>Comprobante</th></tr></thead><tbody>
          {ventas.map(({ venta }) => <tr key={venta.id_venta}><td>{venta.numero_venta != null ? `#${venta.numero_venta}` : '—'}</td><td>{fecha(venta.fecha_venta)}</td><td>{venta.estado}</td><td>{totalVenta(venta) == null ? '—' : dinero(totalVenta(venta))}</td><td><Link to={`/ventas/${venta.id_venta}/comprobante`} onClick={onClose}>Ver comprobante</Link></td></tr>)}
        </tbody></table></div> : <p className={styles.vacio}>Este cliente todavía no tiene ventas.</p>)}
      </details>
      <p className={styles.aclaracion}>Anular un cobro no devuelve mercadería. Anular una venta completa sí revierte el stock y su ingreso. La anulación independiente de un pago de venta aún no está disponible.</p>

</>}
    </div>
  </Modal>
}
