import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import Alert from '../../shared/components/Alert.jsx'
import Modal from '../../shared/components/Modal.jsx'
import styles from './CuentaCorrienteCliente.module.css'

const dinero = (n) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(Number(n || 0))
const fecha = (v) => v ? new Date(v).toLocaleString('es-AR') : '—'
const errorDe = (e) => e.response?.data?.error || (e.response?.status === 403 ? 'No tenés permiso para consultar esta información.' : 'No se pudo consultar la cuenta corriente.')
const etiquetas = { DEUDA: 'Con deuda', AL_DIA: 'Al día', SALDO_A_FAVOR: 'Saldo a favor' }

export default function CuentaCorrienteCliente({ cliente, onClose }) {
  const [saldo, setSaldo] = useState(null)
  const [ventas, setVentas] = useState(null)
  const [cobros, setCobros] = useState(null)
  const [errores, setErrores] = useState({})
  const [cargando, setCargando] = useState(false)
  const [revision, setRevision] = useState(0)

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

  return <Modal open={Boolean(cliente)} onClose={onClose} title={`Cuenta corriente · ${cliente?.nombre_completo || ''}`} description="Saldo actual, ventas y cobros registrados." size="large">
    <div className={styles.contenido}>
      <div className={styles.barra}>
        <span>Cliente #{cliente?.numero_cliente}</span>
        <button type="button" className={styles.boton} disabled={cargando} onClick={() => setRevision((v) => v + 1)}>Actualizar cuenta</button>
      </div>
      {cargando && <p role="status">Consultando movimientos…</p>}
      {errores.saldo && <Alert type="error">Saldo: {errores.saldo}</Alert>}
      {saldo && <div className={styles.resumen}>
        <article><span>Saldo actual</span><strong className={saldo.situacion === 'DEUDA' ? styles.deuda : styles.saldo}>{dinero(Math.abs(saldo.saldo))}</strong><small>{etiquetas[saldo.situacion] || saldo.situacion}</small></article>
        <article><span>Ventas vigentes</span><strong>{dinero(saldo.total_ventas)}</strong></article>
        <article><span>Cobros completados</span><strong>{dinero(saldo.total_cobros)}</strong></article>
      </div>}
      <p className={styles.aclaracion}>El saldo se calcula con ventas no anuladas menos cobros completados. Un saldo a favor no es una deuda.</p>
      <h3>Ventas del cliente</h3>
      {errores.ventas && <Alert type="error">Ventas: {errores.ventas}</Alert>}
      {ventas && (ventas.length ? <div className={styles.scroll}><table><thead><tr><th>Venta</th><th>Fecha</th><th>Estado</th><th>Total</th><th>Comprobante</th></tr></thead><tbody>
        {ventas.map(({ venta }) => <tr key={venta.id_venta}><td>#{venta.numero_venta ?? venta.id_venta}</td><td>{fecha(venta.fecha_venta)}</td><td>{venta.estado}</td><td>{dinero(venta.total_venta ?? venta.total)}</td><td><Link to={`/ventas/${venta.id_venta}/comprobante`} onClick={onClose}>Ver X</Link></td></tr>)}
      </tbody></table></div> : <p className={styles.vacio}>Este cliente todavía no tiene ventas.</p>)}
      <h3>Cobros registrados</h3>
      {errores.cobros && <Alert type="error">Cobros: {errores.cobros}</Alert>}
      {cobros && (cobros.length ? <div className={styles.scroll}><table><thead><tr><th>N.º</th><th>Fecha</th><th>Estado</th><th>Importe</th></tr></thead><tbody>
        {cobros.map((c) => <tr key={c.id_cobro}><td>#{c.id_cobro}</td><td>{fecha(c.fecha_cobro)}</td><td>{c.estado}</td><td>{dinero(c.monto)}</td></tr>)}
      </tbody></table></div> : <p className={styles.vacio}>Este cliente todavía no tiene cobros registrados.</p>)}
      <p className={styles.aclaracion}>El registro y la anulación de cobros se incorporarán en Cobros V1. Esta pantalla es de consulta.</p>
    </div>
  </Modal>
}
