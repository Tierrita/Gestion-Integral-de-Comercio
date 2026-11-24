import ActionButton from '../../shared/components/ActionButton.jsx'
import { formatoMoneda } from '../../shared/utils/formatters.js'

import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import styles from './Ventas.module.css'
import Alert from '../../shared/components/Alert.jsx'
import Modal from '../../shared/components/Modal.jsx'
import ConfirmDialog from '../../shared/components/ConfirmDialog.jsx'

const cantidadFormato = (valor) =>
  new Intl.NumberFormat('es-AR', {
    maximumFractionDigits: 3,
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
  const local = new Date(
    fecha.getTime() - fecha.getTimezoneOffset() * 60000,
  )
  return local.toISOString().slice(0, 10)
}

export default function Ventas({ esPropietario = false }) {
  const navigate = useNavigate()
  const [ventas, setVentas] = useState([])
  const [clientes, setClientes] = useState([])
  const [productos, setProductos] = useState([])
  const [usuarios, setUsuarios] = useState([])
  const [erroresReferencias, setErroresReferencias] = useState([])
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
  const [anulando, setAnulando] = useState(false)
  const [errorAnulacion, setErrorAnulacion] = useState('')
  const [mostrarConfirmacion, setMostrarConfirmacion] = useState(false)
  const [mensajeExito, setMensajeExito] = useState('')


  const detalleRequest = useRef(0)

  function cerrarDetalle() {
    if (anulando) return
    setMostrarConfirmacion(false)
    detalleRequest.current += 1
    setSeleccionada(null)
    setDetalle(null)
    setErrorDetalle('')
    setErrorAnulacion('')
    setCargandoDetalle(false)
  }

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

  useEffect(() => {
    const controller = new AbortController()

    async function cargarReferencias() {
      const endpoints = ['/clientes', '/productos', '/usuarios']
      const respuestas = await Promise.allSettled(
        endpoints.map((ruta) => api.get(ruta, { signal: controller.signal })),
      )
      if (controller.signal.aborted) return

      const errores = []
      const [rClientes, rProductos, rUsuarios] = respuestas

      function extraer(resultado, clave, ruta) {
        if (resultado.status === 'rejected') {
          const status = resultado.reason?.response?.status
          errores.push(`${ruta}: ${status ? `HTTP ${status}` : 'error de conexión'}`)
          return []
        }
        const datos = resultado.value.data
        const lista = Array.isArray(datos) ? datos : datos?.[clave]
        if (!Array.isArray(lista)) {
          errores.push(`${ruta}: formato de respuesta inesperado`)
          return []
        }
        return lista
      }

      setClientes(extraer(rClientes, 'clientes', '/clientes'))
      setProductos(extraer(rProductos, 'productos', '/productos'))
      setUsuarios(extraer(rUsuarios, 'usuarios', '/usuarios'))
      setErroresReferencias(errores)
    }

    void cargarReferencias()
    return () => controller.abort()
  }, [])

  const nombreCliente = (id) =>
    clientes.find((item) => String(item.id_cliente) === String(id))
      ?.nombre_completo || `Cliente #${id}`

  const nombreProducto = (id) =>
    productos.find((item) => String(item.id_producto) === String(id))
      ?.nombre_producto || `Producto #${id}`

  const nombreUsuario = (id) =>
    usuarios.find((item) => String(item.id_usuario) === String(id))
      ?.nombre_completo || `Usuario #${id}`

  const filtradas = useMemo(() => {
    return ventas.filter((venta) => {
      const texto = busqueda.trim().toLowerCase()
      const fecha = fechaFiltro(venta.fecha_venta)

      const coincideBusqueda = [
        venta.numero_venta,
        venta.id_cliente,
        clientes.find(
        (item) => String(item.id_cliente) === String(venta.id_cliente),
        )?.nombre_completo,
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
  }, [ventas, clientes, busqueda, estado, metodo, desde, hasta])
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
    setErrorAnulacion('')
    setMensajeExito('')
    setMostrarConfirmacion(false)
    setCargandoDetalle(true)

    try {
      const { data } = await api.get(`/ventas/${id}`)

      if (!data?.venta || !Array.isArray(data.detalles)) {
        throw new Error('Detalle inválido')
      }

      if (request === detalleRequest.current) {
        setDetalle(data)
      }
    } catch (err) {
      if (request !== detalleRequest.current) return

      setErrorDetalle(
        err.response?.data?.error ||
        'No se pudo cargar el detalle.',
      )
    } finally {
      if (request === detalleRequest.current) {
        setCargandoDetalle(false)
      }
    }
  }

  function abrirConfirmacion() {
    if (!esPropietario || !detalle?.venta || anulando) return
    if (normalizar(detalle.venta.estado) !== 'COMPLETADA') return
    setErrorAnulacion('')
    setMostrarConfirmacion(true)
  }

  async function confirmarAnulacion() {
    if (!esPropietario || !detalle?.venta || anulando) return

    const venta = detalle.venta

    if (normalizar(venta.estado) !== 'COMPLETADA') return

    setAnulando(true)
    setErrorAnulacion('')

    try {
      await api.patch(`/ventas/${venta.id_venta}/anular`)

      setMostrarConfirmacion(false)
      cerrarDetalle()
      setMensajeExito(`La venta #${venta.numero_venta ?? venta.id_venta} se anuló correctamente.`)
      await cargarVentas()
    } catch (err) {
      setErrorAnulacion(
        err.response?.data?.error ||
        'No se pudo anular la venta. Intentá nuevamente.',
      )
    } finally {
      setAnulando(false)
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

        <ActionButton
          type="button"
          variant="primary"
          onClick={() => navigate('/ventas/nueva')}
        >
          + Nueva venta
        </ActionButton>
      </header>

      <div className={styles.indicadores}>
        <article>
          <span>Ventas completadas</span>
          <strong>{activas.length}</strong>
        </article>

        <article>
          <span>Total vendido</span>
          <strong>{formatoMoneda(total)}</strong>
        </article>

        <article>
          <span>Ventas anuladas</span>
          <strong>
            {
              filtradas.filter(
                (v) => normalizar(v.estado) === 'ANULADA',
              ).length
            }
          </strong>
        </article>

        <article>
          <span>Registros encontrados</span>
          <strong>{filtradas.length}</strong>
        </article>
      </div>

      {mensajeExito && (
        <Alert type="success" title="Venta anulada">{mensajeExito}</Alert>
      )}

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
              <select
                value={estado}
                onChange={(e) => setEstado(e.target.value)}
              >
                <option value="TODOS">Todos</option>
                <option value="COMPLETADA">Completadas</option>
                <option value="ANULADA">Anuladas</option>
              </select>
            </label>

            <label>
              Método de pago
              <select
                value={metodo}
                onChange={(e) => setMetodo(e.target.value)}
              >
                <option value="TODOS">Todos</option>
                <option value="EFECTIVO">Efectivo</option>
                <option value="TRANSFERENCIA">Transferencia</option>
                <option value="CUENTA_CORRIENTE">
                  Cuenta corriente
                </option>
              </select>
            </label>

            <ActionButton
              type="button"
              variant="secondary"
              onClick={cargarVentas}
              disabled={cargando}
            >
              Actualizar
            </ActionButton>
          </div>
        </div>

        {erroresReferencias.length > 0 && (
          <p role="alert" className={styles.error}>
            No se pudieron cargar algunos nombres: {erroresReferencias.join('; ')}.
            Las ventas siguen disponibles.
          </p>
        )}

        {error && (
          <p role="alert" className={styles.error}>
            {error}
          </p>
        )}

        {!cargando && (
          <p className={styles.conteo}>
            Mostrando {filtradas.length} de {ventas.length} ventas
          </p>
        )}

        {cargando ? (
          <p role="status" className={styles.vacio}>
            Cargando ventas…
          </p>
        ) : filtradas.length === 0 ? (
          <p className={styles.vacio}>
            No hay ventas para mostrar.
          </p>
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
                    <td>
                      <strong>
                        #{venta.numero_venta ?? venta.id_venta}
                      </strong>
                    </td>

                    <td>{fechaLocal(venta.fecha_venta)}</td>

                    <td>{nombreCliente(venta.id_cliente)}</td>

                    <td className={styles.metodoPago}>
                      {normalizar(venta.metodo_pago).replaceAll('_', ' ')}
                    </td>

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

                    <td className={styles.importe}>
                      <strong>{formatoMoneda(venta.total)}</strong>
                    </td>

                    <td>
                      <button
                        type="button"
                        className={`${styles.secundario} ${styles.botonTabla}`}
                        onClick={() => verDetalle(venta.id_venta)}
                      >
                        Ver detalle
                      </button>
                      <button
                        type="button"
                        className={`${styles.secundario} ${styles.botonTabla}`}
                        onClick={() => navigate(`/ventas/${venta.id_venta}/comprobante`)}
                      >
                        Comprobante X
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal open={seleccionada !== null && !mostrarConfirmacion} onClose={cerrarDetalle}
        title={`Venta #${detalle?.venta?.numero_venta ?? ventas.find((venta) => venta.id_venta === seleccionada)?.numero_venta ?? seleccionada}`}
        description="Detalle de operación" busy={anulando} size="large">
            {cargandoDetalle && (
              <p role="status" className={styles.vacio}>
                Cargando detalle…
              </p>
            )}

            {errorDetalle && (
              <p role="alert" className={styles.error}>
                {errorDetalle}
              </p>
            )}

            {detalle && (
              <div className={styles.modalBody}>
                <div className={styles.modalSummary}>
                  <div>
                    <span>Estado</span>
                    <strong
                      className={
                        normalizar(detalle.venta.estado) === 'ANULADA'
                          ? styles.anulada
                          : styles.completada
                      }
                    >
                      {normalizar(detalle.venta.estado)}
                    </strong>
                  </div>

                  <div>
                    <span>Fecha</span>
                    <strong>
                      {fechaLocal(detalle.venta.fecha_venta)}
                    </strong>
                  </div>

                  <div>
                    <span>Cliente</span>
                    <strong>
                      {nombreCliente(detalle.venta.id_cliente)}
                    </strong>
                  </div>

                  <div>
                    <span>Registrada por</span>
                    <strong>
                      {nombreUsuario(detalle.venta.id_usuario)}
                    </strong>
                  </div>

                  <div>
                    <span>Método de pago</span>
                    <strong>
                      {normalizar(detalle.venta.metodo_pago)
                        .replaceAll('_', ' ')}
                    </strong>
                  </div>
                </div>

                <button
                  type="button"
                  className={styles.secundario}
                  onClick={() => navigate(`/ventas/${detalle.venta.id_venta}/comprobante`)}
                >
                  Ver / imprimir comprobante X
                </button>

                <h3>Productos de la venta</h3>

                <div className={styles.tablaScroll}>
                  <table>
                    <thead>
                      <tr>
                        <th>Producto</th>
                        <th>Cantidad</th>
                        <th>Precio unitario</th>
                        <th>Subtotal</th>
                      </tr>
                    </thead>

                    <tbody>
                      {detalle.detalles.map((item) => (
                        <tr key={item.id_detalle_venta}>
                          <td>
                            {nombreProducto(item.id_producto)}
                          </td>
                          <td>{cantidadFormato(item.cantidad)}</td>
                          <td>
                            {formatoMoneda(item.precio_unitario)}
                          </td>
                          <td>
                            {formatoMoneda(item.subtotal)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className={styles.modalTotal}>
                  <span>Total de la venta</span>
                  <strong>
                    {formatoMoneda(detalle.venta.total)}
                  </strong>
                </div>

                <div className={styles.observaciones}>
                  <strong>Observaciones</strong>
                  <p>
                    {detalle.venta.observaciones ||
                      'Sin observaciones'}
                  </p>
                </div>

                {esPropietario &&
                  normalizar(detalle.venta.estado) === 'COMPLETADA' && (
                    <>
                      <button
                        type="button"
                        className={styles.secundario}
                        onClick={abrirConfirmacion}
                        disabled={anulando}
                      >
                        {anulando ? 'Anulando venta...' : 'Anular venta'}
                      </button>

                      {errorAnulacion && (
                        <p role="alert" className={styles.error}>
                          {errorAnulacion}
                        </p>
                      )}
                    </>
                  )}
              </div>
            )}
      </Modal>

      <ConfirmDialog
        open={mostrarConfirmacion && Boolean(detalle?.venta)}
        onClose={() => { if (!anulando) { setMostrarConfirmacion(false); setErrorAnulacion('') } }}
        onConfirm={confirmarAnulacion}
        title={`¿Anular la venta #${detalle?.venta?.numero_venta ?? seleccionada}?`}
        description="Revisá los datos antes de confirmar la operación."
        details={[
          { label: 'Venta', value: `#${detalle?.venta?.numero_venta ?? seleccionada}` },
          { label: 'Importe', value: formatoMoneda(detalle?.venta?.total) },
          { label: 'Método de pago', value: normalizar(detalle?.venta?.metodo_pago).replaceAll('_', ' ') },
          { label: 'Estado', value: normalizar(detalle?.venta?.estado) },
        ]}
        warning="Los productos volverán al stock. En ventas en efectivo o transferencia, se revertirá el ingreso financiero correspondiente. La operación quedará registrada en el historial."
        error={errorAnulacion} busy={anulando} destructive confirmLabel="Confirmar anulación"
      />
    </section>
  )
}
