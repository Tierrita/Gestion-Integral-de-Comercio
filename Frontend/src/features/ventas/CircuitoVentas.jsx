import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import styles from '../compras/Operaciones.module.css'

const moneda = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })
const consultaClientes = ['/clientes']
const consultaVentas = ['/ventas', '/clientes', '/productos']

function useDatos(rutas) {
  const [intento, setIntento] = useState(0)
  const [resultado, setResultado] = useState(null)

  useEffect(() => {
    const controller = new AbortController()
    Promise.all(rutas.map((ruta) => api.get(ruta, { signal: controller.signal })))
      .then((respuestas) => {
        if (!controller.signal.aborted) setResultado({ intento, data: respuestas.map(({ data }) => data) })
      })
      .catch(() => {
        if (!controller.signal.aborted) setResultado({ intento, error: 'No pudimos cargar los datos.' })
      })
    return () => controller.abort()
  }, [rutas, intento])

  return { ...(resultado?.intento === intento ? resultado : null), recargar: () => setIntento((n) => n + 1) }
}

function Estado({ error, recargar }) {
  if (!error) return <p role="status">Cargando…</p>
  return <><p role="alert">{error}</p><button type="button" onClick={recargar}>Reintentar consulta</button></>
}

function useRegistro(ruta, avisoIncierto) {
  const activo = useRef(false)
  const [estado, setEstado] = useState({})

  async function registrar(datos, confirmar) {
    if (activo.current || estado.incierto) return
    activo.current = true
    setEstado({ enviando: true })
    try {
      await api.post(ruta, datos)
      setEstado({ exito: true })
      confirmar()
    } catch (error) {
      const status = error.response?.status
      const incierto = !status || status >= 500
      setEstado({
        incierto,
        error: incierto ? avisoIncierto : error.response?.data?.error || 'No pudimos registrar la operación.',
      })
    } finally {
      activo.current = false
    }
  }

  return { ...estado, registrar }
}

export function Ventas() {
  const consulta = useDatos(consultaVentas)
  const registro = useRegistro('/ventas', 'No se pudo confirmar la venta. Revisá el historial, el stock y el saldo del cliente antes de volver a registrarla.')
  const [lineas, setLineas] = useState([0])
  const siguiente = useRef(1)
  const [error, setError] = useState('')

  function registrar(event) {
    event.preventDefault()
    const form = event.currentTarget
    const datos = new FormData(form)
    const productos = lineas.map((id) => ({
      id_producto: Number(datos.get('producto-' + id)),
      cantidad: Number(datos.get('cantidad-' + id)),
    }))

    if (new Set(productos.map(({ id_producto }) => id_producto)).size !== productos.length) {
      setError('Elegí cada producto una sola vez.')
      return
    }

    setError('')
    registro.registrar({ id_cliente: Number(datos.get('cliente')), metodo_pago: 'CUENTA_CORRIENTE', productos }, () => {
      form.reset()
      setLineas([siguiente.current++])
      consulta.recargar()
    })
  }

  const [ventas, clientes, catalogo] = consulta.data || []
  const activos = clientes?.filter((cliente) => cliente.estado === true && cliente.numero_cliente !== 1)
  const disponibles = catalogo?.filter((producto) => producto.estado === true && Number(producto.stock) > 0)

  return (
    <section className={styles.pagina}>
      <h1>Ventas</h1>
      <div className={styles.acciones}><Link to="/clientes">Consultar saldo de clientes</Link><Link to="/stock">Consultar stock</Link></div>
      {registro.exito && <p role="status">Venta registrada.</p>}
      {(error || registro.error) && <p role="alert">{error || registro.error}</p>}
      {!consulta.data ? <Estado {...consulta} /> : (
        <>
          <form className={styles.panel} onSubmit={registrar}>
            <h2>Nueva venta en cuenta corriente</h2>
            {(!activos.length || !disponibles.length) && <p>Necesitás un cliente activo y un producto con stock. <Link to="/clientes">Ir a Clientes</Link></p>}
            <fieldset disabled={registro.enviando || registro.incierto || !activos.length || !disponibles.length}>
              <label>Cliente<select name="cliente" required defaultValue=""><option value="">Elegir cliente</option>
                {activos.map((cliente) => <option key={cliente.id_cliente} value={cliente.id_cliente}>{cliente.nombre_completo}</option>)}
              </select></label>
              {lineas.map((id, indice) => (
                <div className={styles.linea} key={id}>
                  <label>Producto {indice + 1}<select name={'producto-' + id} required defaultValue=""><option value="">Elegir producto</option>
                    {disponibles.map((producto) => <option key={producto.id_producto} value={producto.id_producto}>{producto.nombre_producto} · Stock {producto.stock}</option>)}
                  </select></label>
                  <label>Cantidad<input name={'cantidad-' + id} type="number" min="1" step="1" defaultValue="1" required /></label>
                  {lineas.length > 1 && <button type="button" onClick={() => setLineas((actuales) => actuales.filter((linea) => linea !== id))}>Quitar producto {indice + 1}</button>}
                </div>
              ))}
              <div className={styles.acciones}>
                <button type="button" onClick={() => { const id = siguiente.current++; setLineas((actuales) => [...actuales, id]) }}>Agregar producto</button>
                <button className={styles.principal} type="submit">{registro.enviando ? 'Registrando…' : 'Registrar venta'}</button>
              </div>
            </fieldset>
          </form>
          <h2>Historial de ventas</h2>
          {registro.incierto && <button type="button" onClick={consulta.recargar}>Actualizar historial</button>}
          {ventas.length ? <div className={styles.tabla}><table>
            <thead><tr><th>Venta</th><th>Cliente</th><th>Fecha</th><th>Estado</th><th>Total</th></tr></thead>
            <tbody>{ventas.map((venta) => <tr key={venta.id_venta}>
              <td>#{venta.numero_venta ?? venta.id_venta}</td>
              <td><Link to={'/clientes/' + venta.id_cliente}>{clientes.find((cliente) => cliente.id_cliente === venta.id_cliente)?.nombre_completo || 'Ver cliente'}</Link></td>
              <td>{new Date(venta.fecha_venta).toLocaleString('es-AR')}</td><td>{venta.estado}</td><td>{moneda.format(venta.total)}</td>
            </tr>)}</tbody>
          </table></div> : <p>Todavía no hay ventas registradas.</p>}
        </>
      )}
    </section>
  )
}

export function Clientes() {
  const consulta = useDatos(consultaClientes)
  const registro = useRegistro('/clientes', 'No se pudo confirmar el alta. Actualizá la lista y verificá si el cliente figura antes de volver a crearlo.')

  function crearCliente(event) {
    event.preventDefault()
    const formulario = event.currentTarget
    const datos = new FormData(formulario)
    registro.registrar({
      nombre_completo: datos.get('nombre').trim(),
      telefono: datos.get('telefono').trim(),
    }, () => {
      formulario.reset()
      consulta.recargar()
    })
  }

  return (
    <section className={styles.pagina}>
      <h1>Clientes</h1>
      <form className={styles.panel} onSubmit={crearCliente}>
        <h2>Nuevo cliente</h2>
        <fieldset disabled={registro.enviando || registro.incierto}>
          <div className={styles.linea}>
            <label>Nombre completo<input name="nombre" required minLength={2} /></label>
            <label>Teléfono (opcional)<input name="telefono" type="tel" /></label>
          </div>
          <div className={styles.acciones}>
            <button className={styles.principal} type="submit">{registro.enviando ? 'Guardando…' : 'Crear cliente'}</button>
          </div>
        </fieldset>
      </form>
      {registro.exito && <p role="status">Cliente creado. <Link to="/ventas">Ir a Ventas</Link></p>}
      {registro.error && <p role="alert">{registro.error}</p>}
      {registro.incierto && <button type="button" onClick={consulta.recargar}>Actualizar lista</button>}
      {!consulta.data ? <Estado {...consulta} /> : consulta.data[0].length ? (
        <div className={styles.tabla}><table>
          <thead><tr><th>Cliente</th><th>Estado</th><th>Cuenta corriente</th></tr></thead>
          <tbody>{consulta.data[0].map((cliente) => <tr key={cliente.id_cliente}>
            <td>{cliente.nombre_completo}</td><td>{cliente.estado ? 'Activo' : 'Inactivo'}</td>
            <td><Link to={'/clientes/' + cliente.id_cliente}>Ver saldo de {cliente.nombre_completo}</Link></td>
          </tr>)}</tbody>
        </table></div>
      ) : <p>Todavía no hay clientes registrados.</p>}
    </section>
  )
}

export function CuentaCliente() {
  const { id } = useParams()
  return <DetalleCliente key={id} id={id} />
}

function DetalleCliente({ id }) {
  const [rutas] = useState(() => ['/clientes/' + id + '/saldo', '/cuentas', '/clientes/' + id + '/cobros'])
  const consulta = useDatos(rutas)
  const registro = useRegistro('/cobros', 'No se pudo confirmar el cobro. Actualizá el historial y revisá el saldo antes de volver a registrarlo.')

  function cobrar(event) {
    event.preventDefault()
    const form = event.currentTarget
    const datos = new FormData(form)
    registro.registrar({
      id_cliente: Number(id),
      id_cuenta: Number(datos.get('cuenta')),
      monto: Number(datos.get('monto')),
    }, () => {
      form.reset()
      consulta.recargar()
    })
  }

  const [saldo, cuentas, historial] = consulta.data || []
  const activas = cuentas?.cuentas.filter((cuenta) => cuenta.estado === true)
  const cobros = historial?.cobros

  return (
    <section className={styles.pagina}>
      <h1>{saldo?.cliente.nombre_completo || 'Cuenta corriente del cliente'}</h1>
      <Link to="/clientes">Volver a clientes</Link>
      {registro.exito && <p role="status">Cobro registrado.</p>}
      {registro.error && <p role="alert">{registro.error}</p>}
      {!consulta.data ? <Estado {...consulta} /> : (
        <>
          <p>Saldo actual <strong>{moneda.format(saldo.saldo)}</strong> · {saldo.situacion.replaceAll('_', ' ').toLowerCase()}</p>
          {saldo.cliente.estado && saldo.saldo > 0 && (
            <form className={styles.panel} onSubmit={cobrar}>
              <h2>Registrar cobro</h2>
              {!activas.length && <p>Necesitás una cuenta financiera activa.</p>}
              <fieldset disabled={registro.enviando || registro.incierto || !activas.length}>
                <div className={styles.linea}>
                  <label>Cuenta de destino<select name="cuenta" required defaultValue=""><option value="">Elegir cuenta</option>
                    {activas.map((cuenta) => <option key={cuenta.id_cuenta} value={cuenta.id_cuenta}>{cuenta.nombre_cuenta}</option>)}
                  </select></label>
                  <label>Importe<input name="monto" type="number" min="0.01" step="0.01" max={Number(saldo.saldo).toFixed(2)} required /></label>
                </div>
                <div className={styles.acciones}><button className={styles.principal} type="submit">{registro.enviando ? 'Registrando…' : 'Registrar cobro'}</button></div>
              </fieldset>
            </form>
          )}
          <h2>Historial de cobros</h2>
          {registro.incierto && <button type="button" onClick={consulta.recargar}>Actualizar saldo e historial</button>}
          {cobros.length ? <div className={styles.tabla}><table>
            <thead><tr><th>Cobro</th><th>Estado</th><th>Importe</th></tr></thead>
            <tbody>{cobros.map((cobro) => <tr key={cobro.id_cobro}><td>#{cobro.numero_cobro ?? cobro.id_cobro}</td><td>{cobro.estado}</td><td>{moneda.format(cobro.monto)}</td></tr>)}</tbody>
          </table></div> : <p>Todavía no hay cobros para este cliente.</p>}
        </>
      )}
    </section>
  )
}
