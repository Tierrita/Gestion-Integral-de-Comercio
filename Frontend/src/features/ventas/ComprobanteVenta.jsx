import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import BackButton from '../../shared/components/BackButton.jsx'
import ActionButton from '../../shared/components/ActionButton.jsx'
import { api } from '../../shared/api/client.js'
import { formatoFechaHora, formatoMoneda } from '../../shared/utils/formatters.js'
import styles from './ComprobanteVenta.module.css'

const cantidad = (valor) => new Intl.NumberFormat('es-AR', { maximumFractionDigits: 3 }).format(Number(valor))
const normalizar = (valor) => String(valor ?? '').toUpperCase()

export default function ComprobanteVenta() {
  const { id } = useParams()
  const [datos, setDatos] = useState(null)
  const [comercio, setComercio] = useState(null)
  const [cliente, setCliente] = useState(null)
  const [productos, setProductos] = useState({})
  const [avisos, setAvisos] = useState([])
  const [saldoCliente, setSaldoCliente] = useState(null)
  const [fechaConsultaSaldo, setFechaConsultaSaldo] = useState(null)
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    const controller = new AbortController()
    async function cargar() {
      setCargando(true)
      setError('')
      setAvisos([])
      setSaldoCliente(null)
      setFechaConsultaSaldo(null)
      try {
        // La venta se consulta por el JWT: Flask valida el comercio y el permiso ventas.ver.
        const { data } = await api.get(`/ventas/${id}`, { signal: controller.signal })
        if (!data?.venta || !Array.isArray(data.detalles)) throw new Error('El servidor devolvió una venta incompleta.')
        if (controller.signal.aborted) return
        setDatos(data)
        // Datos auxiliares: un error de permisos no debe impedir ver el comprobante.
        const [perfil, ficha, catalogo, saldo] = await Promise.allSettled([
          api.get('/auth/me', { signal: controller.signal }),
          api.get(`/clientes/${data.venta.id_cliente}`, { signal: controller.signal }),
          api.get('/productos', { signal: controller.signal }),
          api.get(`/clientes/${data.venta.id_cliente}/saldo`, { signal: controller.signal }),
        ])
        if (controller.signal.aborted) return
        if (saldo.status === 'fulfilled' && saldo.value.data?.saldo != null && Number.isFinite(Number(saldo.value.data.saldo))) {
          setSaldoCliente(Number(saldo.value.data.saldo))
          setFechaConsultaSaldo(new Date())
        }
        if (perfil.status === 'fulfilled') setComercio(perfil.value.data?.comercio ?? null)
        if (ficha.status === 'fulfilled') setCliente(ficha.value.data?.cliente ?? ficha.value.data ?? null)
        if (catalogo.status === 'fulfilled') {
          const lista = Array.isArray(catalogo.value.data) ? catalogo.value.data : catalogo.value.data?.productos
          if (Array.isArray(lista)) setProductos(Object.fromEntries(lista.map((p) => [p.id_producto, p.nombre_producto])))
        }
        const advertencias = []
        if (ficha.status !== 'fulfilled') advertencias.push('No se pudo consultar la ficha del cliente.')
        if (catalogo.status !== 'fulfilled') advertencias.push('No se pudo consultar el catálogo de productos.')
        if (saldo.status !== 'fulfilled' || saldo.value.data?.saldo == null || !Number.isFinite(Number(saldo.value.data.saldo))) advertencias.push('No se pudo obtener el saldo actual del cliente.')
        setAvisos(advertencias)
      } catch (err) {
        if (!controller.signal.aborted) setError(err.response?.data?.error || err.message || 'No se pudo consultar la venta.')
      } finally {
        if (!controller.signal.aborted) setCargando(false)
      }
    }
    void cargar()
    return () => controller.abort()
  }, [id])

  const venta = datos?.venta
  const anulada = normalizar(venta?.estado) === 'ANULADA'
  const numero = venta?.numero_venta != null ? String(venta.numero_venta).padStart(6, '0') : null
  const nombreCliente = cliente?.nombre_comercial || cliente?.nombre_completo || 'Cliente no identificado'
  const datosCliente = [
    cliente?.nombre_comercial && cliente?.nombre_completo && ['Razón social / titular', cliente.nombre_completo],
    cliente?.tipo_documento && cliente?.numero_documento && [cliente.tipo_documento, cliente.numero_documento],
    cliente?.condicion_iva && ['Condición IVA', cliente.condicion_iva],
    cliente?.telefono && ['Teléfono', cliente.telefono],
    cliente?.email && ['Email', cliente.email],
    [cliente?.direccion, cliente?.localidad, cliente?.provincia, cliente?.codigo_postal].filter(Boolean).length > 0 &&
      ['Domicilio', [cliente?.direccion, cliente?.localidad, cliente?.provincia, cliente?.codigo_postal].filter(Boolean).join(', ')],
  ].filter(Boolean)
  const datosComercio = [
    comercio?.razon_social && ['Razón social', comercio.razon_social],
    comercio?.cuit && ['CUIT', comercio.cuit],
    comercio?.direccion && ['Dirección', [comercio.direccion, comercio.localidad, comercio.provincia].filter(Boolean).join(', ')],
    comercio?.telefono && ['Teléfono', comercio.telefono],
  ].filter(Boolean)

  return <section className={styles.pagina}>
    <header className={styles.acciones}>
      <div><BackButton to="/ventas" label="Volver a ventas" /><h1>Comprobante de venta</h1></div>
      <ActionButton variant="primary" onClick={() => window.print()} disabled={!venta || cargando}>Imprimir / Guardar PDF</ActionButton>
    </header>
    {cargando && <p role="status">Cargando comprobante…</p>}
    {error && <p role="alert" className={styles.error}>{error}</p>}
    {avisos.length > 0 && <p role="status" className={styles.aviso}>{avisos.join(' ')} Revisá los permisos o la conexión antes de imprimir.</p>}
    {venta && <article className={styles.hoja}>
      <div className={styles.encabezado}>
        <div className={styles.identidad}>
          <span className={styles.marcaSistema}>AIONIX</span>
          <strong className={styles.marca}>{comercio?.nombre_comercio || 'Comercio'}</strong>
          <span className={styles.subtitulo}>Gestión comercial</span>
        </div>
        <div className={styles.numero}>
          <span>ORDEN DE VENTA</span>
          <strong>{numero || 'SIN NUMERACIÓN'}</strong>
          <span>Fecha de emisión: {formatoFechaHora(venta.fecha_venta)}</span>
        </div>
      </div>
      {datosComercio.length > 0 && <div className={styles.datosComercio}>
        {datosComercio.map(([etiqueta, valor]) => <span key={etiqueta}><b>{etiqueta}:</b> {valor}</span>)}
      </div>}
      {anulada && <div className={styles.anulada}>VENTA ANULADA · SIN VALIDEZ COMO COMPROBANTE DE OPERACIÓN VIGENTE</div>}
      <div className={styles.cliente}>
        <span>Apellido y nombre / Razón social</span><strong>{nombreCliente}</strong>
        {datosCliente.map(([etiqueta, valor]) => <div className={styles.datoCliente} key={etiqueta}><span>{etiqueta}</span><strong>{valor}</strong></div>)}
        <span>Forma de pago</span><strong>{normalizar(venta.metodo_pago).replaceAll('_', ' ')}</strong>
      </div>
      <table className={styles.tabla}>
        <thead><tr><th>Producto</th><th>Cantidad</th><th>Precio unitario</th><th>Subtotal</th></tr></thead>
        <tbody>{datos.detalles.map((item) => <tr key={item.id_detalle_venta ?? item.id_producto}>
          <td>{item.nombre_producto || productos[item.id_producto] || 'Producto sin descripción disponible'}</td>
          <td>{cantidad(item.cantidad)}</td>
          <td>{formatoMoneda(item.precio_unitario)}</td>
          <td>{formatoMoneda(item.subtotal)}</td>
        </tr>)}</tbody>
      </table>
      <div className={styles.cierre}><div className={styles.agradecimiento}><strong>¡Gracias por su compra!</strong><span>Comprobante emitido por AIOnix</span></div><div className={styles.total}><span>TOTAL</span><strong>{formatoMoneda(venta.total)}</strong></div></div>
      <section className={styles.estadoCuenta}>
        <h2>ESTADO ACTUAL DE CUENTA</h2>
        <div className={styles.resumenSaldo}>
          <span>Importe de esta compra</span>
          <strong>{formatoMoneda(venta.total)}</strong>
        </div>
        <div className={styles.resumenSaldo}>
          <span>{saldoCliente === null ? 'Saldo total del cliente' : saldoCliente > 0 ? 'TOTAL QUE DEBE EL CLIENTE' : saldoCliente < 0 ? 'SALDO A FAVOR DEL CLIENTE' : 'ESTADO DE CUENTA'}</span>
          <strong>{saldoCliente === null ? 'No disponible' : saldoCliente === 0 ? 'AL DÍA · ' + formatoMoneda(0) : formatoMoneda(Math.abs(saldoCliente))}</strong>
        </div>
        <p>{fechaConsultaSaldo ? `Saldo actualizado al ${fechaConsultaSaldo.toLocaleString('es-AR')}. Incluye esta venta si fue a cuenta corriente y sigue pendiente, así como otras operaciones y pagos registrados. El importe de la compra se informa por separado y no se suma otra vez al saldo.` : 'No se pudo consultar la deuda actual. El importe de la compra no representa necesariamente la deuda del cliente.'}</p>
      </section>
      {venta.observaciones && <p className={styles.observaciones}><strong>Observaciones:</strong> {venta.observaciones}</p>}
      <footer className={styles.pie}>Documento comercial interno · No constituye factura fiscal.</footer>
    </article>}
  </section>
}
