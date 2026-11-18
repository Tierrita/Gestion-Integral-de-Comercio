
import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../../shared/api/client.js'
import styles from './Ventas.module.css'

const dinero = (valor) =>
  new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
  }).format(Number(valor) || 0)

const normalizar = (valor) =>
  String(valor ?? '').trim().toUpperCase()

const fechaLocal = (valor) =>
  valor
    ? new Date(valor).toLocaleString('es-AR', {
        dateStyle: 'short',
        timeStyle: 'short',
      })
    : '—'

const fechaFiltro = (valor) => {
  if (!valor) return ''
  const fecha = new Date(valor)
  if (Number.isNaN(fecha.getTime())) return ''
  const local = new Date(fecha.getTime() - fecha.getTimezoneOffset() * 60000)
  return local.toISOString().slice(0, 10)
}

export default function Ventas() {
  const [ventas, setVentas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [estado, setEstado] = useState('TODOS')
  const [metodo, setMetodo] = useState('TODOS')
  const [desde, setDesde] = useState('')
  const [hasta, setHasta] = useState('')
  const [seleccionada, setSeleccionada] = useState(null)
  const [detalle, setDetalle] = useState(null)
  const [errorDetalle, setErrorDetalle] = useState('')
  const [cargandoDetalle, setCargandoDetalle] = useState(false)
  const detalleRequest = useRef(0)

  function cerrarDetalle() {
    detalleRequest.current += 1
    setSeleccionada(null)
    setDetalle(null)
    setErrorDetalle('')
    setCargandoDetalle(false)
  }

  useEffect(() => {
    if (seleccionada === null) return undefined
    const onKeyDown = (event) => {
      if (event.key === 'Escape') cerrarDetalle()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [seleccionada])

  async function cargarVentas() {
    setCargando(true)
    setError('')

    try {
      const { data } = await api.get('/ventas')
      if (!Array.isArray(data)) {
        throw new Error('Respuesta inválida del servidor')
      }
      setVentas(data)
    } catch (err) {
      setError(
        err.response?.data?.error ||
        'No se pudieron cargar las ventas. Verificá la conexión con Flask.',
      )
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      void cargarVentas()
    }, 0)
    return () => clearTimeout(timer)
  }, [])

  const filtradas = useMemo(() => {
    return ventas.filter((venta) => {
      const texto = busqueda.trim().toLowerCase()
      const fecha = fechaFiltro(venta.fecha_venta)

      const coincideBusqueda = [
        venta.numero_venta,
        venta.id_cliente,
        venta.observaciones,
      ].some((valor) =>
        String(valor ?? '').toLowerCase().includes(texto),
      )

      return (
        coincideBusqueda &&
        (estado === 'TODOS' || normalizar(venta.estado) === estado) &&
        (metodo === 'TODOS' || normalizar(venta.metodo_pago) === metodo) &&
        (!desde || fecha >= desde) &&
        (!hasta || fecha <= hasta)
      )
    })
  }, [ventas, busqueda, estado, metodo, desde, hasta])

  const activas = filtradas.filter(
    (venta) => normalizar(venta.estado) === 'COMPLETADA',
  )

  const total = activas.reduce(
    (acumulado, venta) => acumulado + Number(venta.total || 0),
    0,
  )

  async function verDetalle(id) {
    const request = ++detalleRequest.current
    setSeleccionada(id)
    setDetalle(null)
    setErrorDetalle('')
    setCargandoDetalle(true)

    try {
      const { data } = await api.get(`/ventas/${id}`)
      if (!data?.venta || !Array.isArray(data.detalles)) {
        throw new Error('Detalle inválido')
      }
      if (request === detalleRequest.current) setDetalle(data)
    } catch (err) {
      if (request !== detalleRequest.current) return
      setErrorDetalle(
        err.response?.data?.error || 'No se pudo cargar el detalle.',
      )
    } finally {
      if (request === detalleRequest.current) setCargandoDetalle(false)
    }
  }

  return (
    <section className={styles.pagina}>
      <header className={styles.encabezado}>
        <div>
          <p className={styles.etiqueta}>GESTIÓN COMERCIAL</p>
          <h1>Ventas</h1>
          <p className={styles.descripcion}>
            Consultá las operaciones registradas en tu comercio.
          </p>
        </div>
        <button
          type="button"
          className={styles.principal}
          disabled
          title="Disponible en la próxima etapa"
        >
          + Nueva venta
        </button>
      </header>

      <div className={styles.indicadores}>
        <article>
          <span>Ventas completadas</span>
          <strong>{activas.length}</strong>
        </article>
        <article>
          <span>Total vendido</span>
          <strong>{dinero(total)}</strong>
        </article>
        <article>
          <span>Ventas anuladas</span>
          <strong>
            {filtradas.filter((v) => normalizar(v.estado) === 'ANULADA').length}
          </strong>
        </article>
        <article>
          <span>Registros encontrados</span>
          <strong>{filtradas.length}</strong>
        </article>
      </div>

      <div className={styles.panel}>
        <div className={styles.panelContenido}>
        <div className={styles.filtros}>
          <label>
            Buscar
            <input
              type="search"
              placeholder="N.º, ID cliente u observación"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </label>

          <label>
            Desde
            <input
              type="date"
              value={desde}
              onChange={(e) => setDesde(e.target.value)}
            />
          </label>

          <label>
            Hasta
            <input
              type="date"
              value={hasta}
              onChange={(e) => setHasta(e.target.value)}
            />
          </label>

          <label>
            Estado
            <select value={estado} onChange={(e) => setEstado(e.target.value)}>
              <option value="TODOS">Todos</option>
              <option value="COMPLETADA">Completadas</option>
              <option value="ANULADA">Anuladas</option>
            </select>
          </label>

          <label>
            Método de pago
            <select value={metodo} onChange={(e) => setMetodo(e.target.value)}>
              <option value="TODOS">Todos</option>
              <option value="EFECTIVO">Efectivo</option>
              <option value="TRANSFERENCIA">Transferencia</option>
              <option value="CUENTA_CORRIENTE">Cuenta corriente</option>
            </select>
          </label>

          <button
            type="button"
            className={styles.secundario}
            onClick={cargarVentas}
            disabled={cargando}
          >
            Actualizar
          </button>
        </div>

        </div>

        {error && <p role="alert" className={styles.error}>{error}</p>}
        {!cargando && <p className={styles.conteo}>Mostrando {filtradas.length} de {ventas.length} ventas</p>}

        {cargando ? (
          <p role="status" className={styles.vacio}>Cargando ventas…</p>
        ) : filtradas.length === 0 ? (
          <p className={styles.vacio}>No hay ventas para mostrar.</p>
        ) : (
          <div className={`${styles.tablaScroll} ${styles.tablaListado}`}>
            <table>
              <thead>
                <tr>
                  <th>N.º</th>
                  <th>Fecha</th>
                  <th>Cliente</th>
                  <th>Pago</th>
                  <th>Estado</th>
                  <th>Total</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtradas.map((venta) => (
                  <tr key={venta.id_venta}>
                    <td><strong>#{venta.numero_venta ?? venta.id_venta}</strong></td>
                    <td>{fechaLocal(venta.fecha_venta)}</td>
                    <td>Cliente #{venta.id_cliente}</td>
                    <td className={styles.metodoPago}>{normalizar(venta.metodo_pago).replaceAll('_', ' ')}</td>
                    <td>
                      <span
                        className={
                          normalizar(venta.estado) === 'ANULADA'
                            ? styles.anulada
                            : styles.completada
                        }
                      >
                        {normalizar(venta.estado)}
                      </span>
                    </td>
                    <td className={styles.importe}><strong>{dinero(venta.total)}</strong></td>
                    <td>
                      <button
                        type="button"
                        className={`${styles.secundario} ${styles.botonTabla}`}
                        onClick={() => verDetalle(venta.id_venta)}
                      >
                        Ver detalle
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {seleccionada !== null && (
        <div className={styles.modalBackdrop} onMouseDown={(event) => {
          if (event.target === event.currentTarget) cerrarDetalle()
        }}>
          <section className={styles.modal} role="dialog" aria-modal="true" aria-labelledby="venta-detalle-titulo">
            <header className={styles.modalHeader}>
              <div>
                <p className={styles.etiqueta}>DETALLE DE OPERACIÓN</p>
                <h2 id="venta-detalle-titulo">Venta #{detalle?.venta?.numero_venta ?? seleccionada}</h2>
              </div>
              <button type="button" className={styles.secundario} onClick={cerrarDetalle} autoFocus>
                Cerrar ×
              </button>
            </header>

            {cargandoDetalle && <p role="status" className={styles.vacio}>Cargando detalle…</p>}
            {errorDetalle && <p role="alert" className={styles.error}>{errorDetalle}</p>}

            {detalle && (
              <div className={styles.modalBody}>
                <div className={styles.modalSummary}>
                  <div><span>Estado</span><strong className={normalizar(detalle.venta.estado) === 'ANULADA' ? styles.anulada : styles.completada}>{normalizar(detalle.venta.estado)}</strong></div>
                  <div><span>Fecha</span><strong>{fechaLocal(detalle.venta.fecha_venta)}</strong></div>
                  <div><span>Cliente</span><strong>Cliente #{detalle.venta.id_cliente}</strong></div>
                  <div><span>Registrada por</span><strong>Usuario #{detalle.venta.id_usuario}</strong></div>
                  <div><span>Método de pago</span><strong>{normalizar(detalle.venta.metodo_pago).replaceAll('_', ' ')}</strong></div>
                </div>
                <h3>Productos de la venta</h3>
                <div className={styles.tablaScroll}>
                  <table>
                    <thead><tr><th>Producto</th><th>Cantidad</th><th>Precio unitario</th><th>Subtotal</th></tr></thead>
                    <tbody>
                      {detalle.detalles.map((item) => (
                        <tr key={item.id_detalle_venta}>
                          <td>Producto #{item.id_producto}</td>
                          <td>{item.cantidad}</td>
                          <td>{dinero(item.precio_unitario)}</td>
                          <td>{dinero(item.subtotal)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className={styles.modalTotal}><span>Total de la venta</span><strong>{dinero(detalle.venta.total)}</strong></div>
                <div className={styles.observaciones}><strong>Observaciones</strong><p>{detalle.venta.observaciones || 'Sin observaciones'}</p></div>
              </div>
            )}
          </section>
        </div>
      )}
    </section>
  )
}
