import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
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
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    const controller = new AbortController()
    async function cargar() {
      setCargando(true)
      setError('')
      try {
        // La venta se consulta por el JWT: Flask valida el comercio y el permiso ventas.ver.
        const { data } = await api.get(`/ventas/${id}`, { signal: controller.signal })
        if (!data?.venta || !Array.isArray(data.detalles)) throw new Error('El servidor devolvió una venta incompleta.')
        if (controller.signal.aborted) return
        setDatos(data)
        // Datos auxiliares: un error de permisos no debe impedir ver el comprobante.
        const [perfil, ficha, catalogo] = await Promise.allSettled([
          api.get('/auth/me', { signal: controller.signal }),
          api.get(`/clientes/${data.venta.id_cliente}`, { signal: controller.signal }),
          api.get('/productos', { signal: controller.signal }),
        ])
        if (controller.signal.aborted) return
        if (perfil.status === 'fulfilled') setComercio(perfil.value.data?.comercio ?? null)
        if (ficha.status === 'fulfilled') setCliente(ficha.value.data ?? null)
        if (catalogo.status === 'fulfilled' && Array.isArray(catalogo.value.data)) {
          setProductos(Object.fromEntries(catalogo.value.data.map((p) => [p.id_producto, p.nombre_producto])))
        }
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
  const numero = venta?.numero_venta ?? venta?.id_venta

  return <section className={styles.pagina}>
    <header className={styles.acciones}>
      <div><Link to="/ventas">← Volver a ventas</Link><h1>Comprobante de venta</h1></div>
      <button type="button" onClick={() => window.print()} disabled={!venta || !comercio}>Imprimir / Guardar PDF</button>
    </header>
    {cargando && <p role="status">Cargando comprobante…</p>}
    {error && <p role="alert" className={styles.error}>{error}</p>}
    {venta && <article className={styles.hoja}>
      <div className={styles.encabezado}>
        <div><strong className={styles.marca}>{comercio?.nombre_comercio || 'Comercio'}</strong><p>Comprobante interno de operación</p></div>
        <div className={styles.tipo}><strong>X</strong><span>NO FISCAL</span></div>
        <div className={styles.numero}><strong>ORDEN DE VENTA #{numero}</strong><span>Fecha: {formatoFechaHora(venta.fecha_venta)}</span></div>
      </div>
      <div className={styles.advertencia}>DOCUMENTO INTERNO · NO VÁLIDO COMO FACTURA FISCAL</div>
      {anulada && <div className={styles.anulada}>VENTA ANULADA · SIN VALIDEZ COMO COMPROBANTE DE OPERACIÓN VIGENTE</div>}
      <div className={styles.cliente}>
        <span>Cliente</span><strong>{cliente?.nombre_completo || `Cliente #${venta.id_cliente}`}</strong>
        <span>Forma de pago</span><strong>{normalizar(venta.metodo_pago).replaceAll('_', ' ')}</strong>
      </div>
      <table className={styles.tabla}>
        <thead><tr><th>Producto</th><th>Cantidad</th><th>Precio unitario</th><th>Subtotal</th></tr></thead>
        <tbody>{datos.detalles.map((item) => <tr key={item.id_detalle_venta ?? item.id_producto}>
          <td>{item.nombre_producto || productos[item.id_producto] || `Producto #${item.id_producto}`}</td>
          <td>{cantidad(item.cantidad)}</td>
          <td>{formatoMoneda(item.precio_unitario)}</td>
          <td>{formatoMoneda(item.subtotal)}</td>
        </tr>)}</tbody>
      </table>
      <div className={styles.total}><span>Total de la venta</span><strong>{formatoMoneda(venta.total)}</strong></div>
      {venta.observaciones && <p className={styles.observaciones}><strong>Observaciones:</strong> {venta.observaciones}</p>}
      <footer className={styles.pie}>Gracias por su compra · Comprobante emitido a partir de la venta registrada en el sistema. No reemplaza una factura autorizada por ARCA.</footer>
    </article>}
  </section>
}
