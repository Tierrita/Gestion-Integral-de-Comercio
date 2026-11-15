import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import { tienePermiso } from '../../shared/auth/permisos.js'
import styles from './Operaciones.module.css'

const moneda = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })
const nuevaLinea = (id) => ({ id, id_producto: '', cantidad: '1', precio_unitario: '' })

function useConsulta(cargar) {
  const [resultado, setResultado] = useState(null)
  const [intento, setIntento] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    cargar(controller.signal).then((data) => {
      if (!controller.signal.aborted) setResultado({ intento, data })
    }).catch((error) => {
      if (!controller.signal.aborted) {
        setResultado({ intento, error: error.response?.data?.error || 'No se pudo cargar la información.' })
      }
    })
    return () => controller.abort()
  }, [cargar, intento])

  return {
    ...(resultado?.intento === intento ? resultado : null),
    recargar: () => setIntento((actual) => actual + 1),
  }
}

function Estado({ error, recargar }) {
  return error ? (
    <div><p role="alert">{error}</p><button type="button" onClick={recargar}>Reintentar</button></div>
  ) : <p role="status">Cargando…</p>
}

const cargarCompras = (signal) => api.get('/compras', { signal }).then(({ data }) => data)
const cargarCatalogo = async (signal) => {
  const [proveedores, productos] = await Promise.all([
    api.get('/proveedores', { signal }),
    api.get('/productos', { signal }),
  ])
  return {
    proveedores: proveedores.data.filter((proveedor) => proveedor.estado),
    productos: productos.data.filter((producto) => producto.estado),
  }
}

export function NuevaCompra({ profile }) {
  const catalogo = useConsulta(cargarCatalogo)
  const [proveedor, setProveedor] = useState('')
  const [lineas, setLineas] = useState([nuevaLinea(0)])
  const [mensaje, setMensaje] = useState('')
  const [compra, setCompra] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [incierta, setIncierta] = useState(false)
  const siguiente = useRef(1)
  const envioActivo = useRef(false)

  function cambiar(id, campo, valor) {
    setLineas((actuales) => actuales.map((linea) => linea.id === id ? { ...linea, [campo]: valor } : linea))
  }

  async function registrar(event) {
    event.preventDefault()
    if (envioActivo.current || incierta) return
    const productos = lineas.map(({ id_producto, cantidad, precio_unitario }) => ({
      id_producto: Number(id_producto),
      cantidad: Number(cantidad),
      precio_unitario: Number(precio_unitario),
    }))
    if (new Set(productos.map((producto) => producto.id_producto)).size !== productos.length) {
      setMensaje('Elegí cada producto una sola vez.')
      return
    }

    envioActivo.current = true
    setEnviando(true)
    setMensaje('')
    try {
      const { data } = await api.post('/compras', { id_proveedor: Number(proveedor), productos })
      const registrada = data?.compra?.compra
      if (!registrada?.id_compra) throw new Error('Compra sin identificador')
      setCompra(registrada)
    } catch (error) {
      const status = error.response?.status
      if (!status || status >= 500) {
        setIncierta(true)
        setMensaje('No se pudo confirmar el resultado. Revisá el historial y el stock antes de volver a registrar la compra.')
      } else {
        setMensaje(error.response?.data?.error || 'No se pudo registrar la compra.')
      }
    } finally {
      envioActivo.current = false
      setEnviando(false)
    }
  }

  if (!catalogo.data) return <section className={styles.pagina}><h1>Nueva compra</h1><Estado {...catalogo} /></section>

  const { proveedores, productos } = catalogo.data
  return (
    <section className={styles.pagina}>
      <h1>Nueva compra</h1>
      {tienePermiso(profile, 'compras.ver') && <Link to="/compras">Volver al historial</Link>}
      {compra ? (
        <div className={styles.panel}>
          <p role="status">Compra #{compra.numero_compra ?? compra.id_compra} registrada.</p>
          {tienePermiso(profile, 'compras.ver') && <Link to={`/compras/${compra.id_compra}`}>Ver detalle</Link>}
          {tienePermiso(profile, 'stock.ver') && <Link to="/stock/existencias">Consultar stock</Link>}
        </div>
      ) : proveedores.length === 0 || productos.length === 0 ? (
        <p>Necesitás al menos un proveedor y un producto activos para registrar una compra.</p>
      ) : (
        <form className={styles.panel} onSubmit={registrar}>
          <fieldset disabled={enviando || incierta}>
            <label>Proveedor
              <select required value={proveedor} onChange={(event) => setProveedor(event.target.value)}>
                <option value="">Seleccioná un proveedor</option>
                {proveedores.map((item) => <option key={item.id_proveedor} value={item.id_proveedor}>{item.nombre_proveedor}</option>)}
              </select>
            </label>
            {lineas.map((linea, indice) => (
              <div className={styles.linea} key={linea.id}>
                <label>Producto {indice + 1}
                  <select required value={linea.id_producto} onChange={(event) => cambiar(linea.id, 'id_producto', event.target.value)}>
                    <option value="">Seleccioná un producto</option>
                    {productos.map((item) => <option key={item.id_producto} value={item.id_producto}>{item.numero_producto != null ? `#${item.numero_producto} · ` : ''}{item.nombre_producto}</option>)}
                  </select>
                </label>
                <label>Cantidad
                  <input required type="number" min="1" step="1" value={linea.cantidad} onChange={(event) => cambiar(linea.id, 'cantidad', event.target.value)} />
                </label>
                <label>Precio unitario
                  <input required type="number" min="0.01" step="0.01" value={linea.precio_unitario} onChange={(event) => cambiar(linea.id, 'precio_unitario', event.target.value)} />
                </label>
                <button type="button" disabled={lineas.length === 1} onClick={() => setLineas((actuales) => actuales.filter(({ id }) => id !== linea.id))}>Quitar</button>
              </div>
            ))}
            <p>Total estimado <strong>{moneda.format(lineas.reduce((total, linea) => total + Number(linea.cantidad) * Number(linea.precio_unitario), 0))}</strong></p>
            <div className={styles.acciones}>
              <button type="button" onClick={() => {
                const linea = nuevaLinea(siguiente.current++)
                setLineas((actuales) => [...actuales, linea])
              }}>Agregar producto</button>
              <button className={styles.principal} type="submit">{enviando ? 'Registrando…' : 'Registrar compra'}</button>
            </div>
          </fieldset>
          {mensaje && <p role="alert">{mensaje}</p>}
        </form>
      )}
    </section>
  )
}

export function HistorialCompras({ profile }) {
  const consulta = useConsulta(cargarCompras)
  return (
    <section className={styles.pagina}>
      <h1>Compras</h1>
      {tienePermiso(profile, 'compras.registrar') && <Link className={styles.principal} to="/compras/nueva">Nueva compra</Link>}
      {!consulta.data ? <Estado {...consulta} /> : consulta.data.length === 0 ? <p>No hay compras registradas.</p> : (
        <div className={styles.tabla}><table>
          <thead><tr><th>Número</th><th>Fecha</th><th>Estado</th><th>Total</th><th>Detalle</th></tr></thead>
          <tbody>{consulta.data.map((compra) => (
            <tr key={compra.id_compra}>
              <td>{compra.numero_compra ?? compra.id_compra}</td><td>{compra.fecha_compra?.slice(0, 10) ?? '—'}</td>
              <td>{compra.estado}</td><td>{moneda.format(compra.total_compra)}</td>
              <td><Link to={`/compras/${compra.id_compra}`}>Ver compra</Link></td>
            </tr>
          ))}</tbody>
        </table></div>
      )}
    </section>
  )
}

export function DetalleCompra({ profile }) {
  const { id } = useParams()
  return <CompraPorId key={id} id={id} profile={profile} />
}

function CompraPorId({ id, profile }) {
  const cargar = useCallback((signal) => api.get(`/compras/${encodeURIComponent(id)}`, { signal }).then(({ data }) => data), [id])
  const consulta = useConsulta(cargar)
  const data = consulta.data
  return (
    <section className={styles.pagina}>
      <h1>{data ? `Compra #${data.compra.numero_compra ?? id}` : 'Detalle de compra'}</h1>
      <Link to="/compras">Volver al historial</Link>
      {!data ? <Estado {...consulta} /> : (
        <>
          <p>{data.compra.estado} · Total {moneda.format(data.compra.total_compra)}</p>
          <div className={styles.tabla}><table>
            <thead><tr><th>ID de producto</th><th>Cantidad</th><th>Precio unitario</th><th>Subtotal</th></tr></thead>
            <tbody>{data.detalles.map((detalle) => (
              <tr key={detalle.id_detalle_compra}>
                <td>{detalle.id_producto}</td><td>{detalle.cantidad}</td>
                <td>{moneda.format(detalle.precio_unitario)}</td><td>{moneda.format(detalle.subtotal)}</td>
              </tr>
            ))}</tbody>
          </table></div>
          {tienePermiso(profile, 'stock.ver') && <Link to="/stock/existencias">Consultar stock</Link>}
        </>
      )}
    </section>
  )
}
