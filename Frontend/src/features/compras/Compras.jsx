import ActionButton from '../../shared/components/ActionButton.jsx'
import { formatoMoneda } from '../../shared/utils/formatters.js'

import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import styles from '../ventas/Ventas.module.css'
import Alert from '../../shared/components/Alert.jsx'
import Modal from '../../shared/components/Modal.jsx'
import ConfirmDialog from '../../shared/components/ConfirmDialog.jsx'

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

export default function Compras({ esPropietario = false }) {
  const navigate = useNavigate()

  const [compras, setCompras] = useState([])
  const [proveedores, setProveedores] = useState([])
  const [productos, setProductos] = useState([])
  const [usuarios, setUsuarios] = useState([])
  const [busqueda, setBusqueda] = useState('')
  const [estado, setEstado] = useState('TODOS')
  const [desde, setDesde] = useState('')
  const [hasta, setHasta] = useState('')
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [errorProveedores, setErrorProveedores] = useState('')

  const [detalle, setDetalle] = useState(null)
  const [detalleId, setDetalleId] = useState(null)
  const [cargandoDetalle, setCargandoDetalle] = useState(false)
  const [errorDetalle, setErrorDetalle] = useState('')
  const [anulando, setAnulando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [confirmando, setConfirmando] = useState(false)
  const [errorAnulacion, setErrorAnulacion] = useState('')
  const detalleRequest = useRef(0)

  async function cargarCompras(signal) {
    setCargando(true)
    setError('')

    try {
      const { data } = await api.get('/compras', { signal })

      if (!Array.isArray(data)) {
        throw new Error('Respuesta de compras inválida')
      }

      if (!signal?.aborted) setCompras(data)
    } catch (err) {
      if (signal?.aborted) return
      setError(
        err.response?.data?.error ||
        'No se pudieron cargar las compras.',
      )
    } finally {
      if (!signal?.aborted) setCargando(false)
    }
  }

  useEffect(() => {
    const controller = new AbortController()

    const timer = setTimeout(() => {
      void cargarCompras(controller.signal)
    }, 0)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    async function cargarProveedores() {
      try {
        const { data } = await api.get('/proveedores', {
          signal: controller.signal,
        })

        const lista = Array.isArray(data)
          ? data
          : data?.proveedores

        if (!Array.isArray(lista)) {
          throw new Error('Respuesta de proveedores inválida')
        }

        if (!controller.signal.aborted) setProveedores(lista)
      } catch (err) {
        if (controller.signal.aborted) return

        setErrorProveedores(
          err.response?.status === 403
            ? 'Sin permiso para consultar proveedores. Se mostrarán sus identificadores.'
            : 'No se pudieron cargar los nombres de proveedores.',
        )
      }
    }

    void cargarProveedores()
    async function cargarNombres() {
      const respuestas = await Promise.allSettled([
        api.get('/productos', { signal: controller.signal }),
        api.get('/usuarios', { signal: controller.signal }),
      ])
      if (controller.signal.aborted) return
      const [rProductos, rUsuarios] = respuestas
      if (rProductos.status === 'fulfilled') {
        const datos = rProductos.value.data
        setProductos(Array.isArray(datos) ? datos : Array.isArray(datos?.productos) ? datos.productos : [])
      }
      if (rUsuarios.status === 'fulfilled') {
        const datos = rUsuarios.value.data
        setUsuarios(Array.isArray(datos) ? datos : Array.isArray(datos?.usuarios) ? datos.usuarios : [])
      }
    }
    void cargarNombres()
    return () => controller.abort()
  }, [])

  const nombreProveedor = (id) =>
    proveedores.find(
      (item) => String(item.id_proveedor) === String(id),
    )?.nombre_proveedor || `Proveedor #${id}`

  const nombreProducto = (id) => productos.find((item) => String(item.id_producto) === String(id))?.nombre_producto || `Producto #${id}`
  const nombreUsuario = (id) => usuarios.find((item) => String(item.id_usuario) === String(id))?.nombre_completo || `Usuario #${id}`

  const filtradas = useMemo(() => {
    const texto = busqueda.trim().toLowerCase()

    return compras.filter((compra) => {
      const nombre = proveedores.find(
        (item) =>
          String(item.id_proveedor) === String(compra.id_proveedor),
      )?.nombre_proveedor

      const coincideBusqueda = [
        compra.numero_compra,
        compra.id_proveedor,
        nombre,
        compra.observaciones,
      ].some((valor) =>
        String(valor ?? '').toLowerCase().includes(texto),
      )

      const fecha = fechaFiltro(compra.fecha_compra)

      return (
        coincideBusqueda &&
        (estado === 'TODOS' || normalizar(compra.estado) === estado) &&
        (!desde || fecha >= desde) &&
        (!hasta || fecha <= hasta)
      )
    })
  }, [compras, proveedores, busqueda, estado, desde, hasta])

  const completadas = filtradas.filter(
    (compra) => normalizar(compra.estado) === 'COMPLETADA',
  )

  const anuladas = filtradas.filter(
    (compra) => normalizar(compra.estado) === 'ANULADA',
  )

  const totalComprado = completadas.reduce(
    (suma, compra) => suma + Number(compra.total_compra || 0),
    0,
  )

  async function verDetalle(id) {
    const request = ++detalleRequest.current
    setConfirmando(false)
    setErrorAnulacion('')
    setDetalleId(id)
    setDetalle(null)
    setErrorDetalle('')
    setCargandoDetalle(true)

    try {
      const { data } = await api.get(`/compras/${id}`)

      if (!data?.compra || !Array.isArray(data.detalles)) {
        throw new Error('Respuesta de detalle inválida')
      }

      if (request === detalleRequest.current) setDetalle(data)
    } catch (err) {
      if (request !== detalleRequest.current) return
      setErrorDetalle(
        err.response?.data?.error ||
        'No se pudo cargar el detalle de la compra.',
      )
    } finally {
      if (request === detalleRequest.current) setCargandoDetalle(false)
    }
  }

  function abrirConfirmacion() {
    if (!esPropietario || !detalle?.compra || anulando || normalizar(detalle.compra.estado) !== 'COMPLETADA') return
    setErrorAnulacion('')
    setConfirmando(true)
  }

  async function anularCompra() {
    if (!esPropietario || !detalle || anulando || normalizar(detalle.compra.estado) !== 'COMPLETADA') return
    const id = detalle.compra.id_compra
    setAnulando(true)
    setErrorAnulacion('')
    setMensaje('')
    try {
      await api.patch(`/compras/${id}/anular`)
      detalleRequest.current += 1
      setConfirmando(false)
      setDetalle(null)
      setDetalleId(null)
      setMensaje('Compra anulada correctamente. El stock fue actualizado.')
      await cargarCompras()
    } catch (err) {
      setErrorAnulacion(err.response?.data?.error || 'No se pudo anular la compra. Verificá su estado y el stock.')
    } finally {
      setAnulando(false)
    }
  }

  function cerrarDetalle() {
    if (anulando || confirmando) return
    detalleRequest.current += 1
    setCargandoDetalle(false)
    setDetalleId(null)
    setDetalle(null)
    setErrorDetalle('')
    setErrorAnulacion('')
  }

  return (
    <section className={styles.pagina}>
      <header className={styles.encabezado}>
        <div>
          <p className={styles.etiqueta}>GESTIÓN COMERCIAL</p>
          <h1>Compras</h1>
          <p className={styles.descripcion}>
            Consultá las compras registradas en tu comercio.
          </p>
        </div>

        <ActionButton
          type="button"
          variant="primary"
          onClick={() => navigate('/compras/nueva')}
        >
          + Nueva compra
        </ActionButton>
      </header>

      <div className={styles.indicadores}>
        <article>
          <span>Compras completadas</span>
          <strong>{completadas.length}</strong>
        </article>
        <article>
          <span>Total comprado</span>
          <strong>{formatoMoneda(totalComprado)}</strong>
        </article>
        <article>
          <span>Compras anuladas</span>
          <strong>{anuladas.length}</strong>
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
                placeholder="N.º, proveedor u observación"
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

            <ActionButton
              type="button"
              variant="secondary"
              onClick={() => cargarCompras()}
              disabled={cargando}
            >
              Actualizar
            </ActionButton>
          </div>
        </div>

        {mensaje && <Alert type="success" title="Compra anulada">{mensaje}</Alert>}

        {errorProveedores && (
          <Alert type="warning" title="Información de proveedores">{errorProveedores}</Alert>
        )}

        {error && (
          <Alert type="error">{error}</Alert>
        )}

        {!cargando && (
          <p className={styles.conteo}>
            Mostrando {filtradas.length} de {compras.length} compras
          </p>
        )}

        {cargando ? (
          <p className={styles.vacio}>Cargando compras…</p>
        ) : filtradas.length === 0 ? (
          <p className={styles.vacio}>
            No hay compras para mostrar.
          </p>
        ) : (
          <div className={`${styles.tablaScroll} ${styles.tablaListado}`}>
            <table>
              <thead>
                <tr>
                  <th>N.º</th>
                  <th>Fecha</th>
                  <th>Proveedor</th>
                  <th>Estado</th>
                  <th>Total</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {filtradas.map((compra) => (
                  <tr key={compra.id_compra}>
                    <td>
                      <strong>
                        #{compra.numero_compra ?? compra.id_compra}
                      </strong>
                    </td>
                    <td>{fechaLocal(compra.fecha_compra)}</td>
                    <td>{nombreProveedor(compra.id_proveedor)}</td>
                    <td>
                      <span
                        className={
                          normalizar(compra.estado) === 'ANULADA'
                            ? styles.anulada
                            : styles.completada
                        }
                      >
                        {normalizar(compra.estado)}
                      </span>
                    </td>
                    <td className={styles.importe}>
                      <strong>{formatoMoneda(compra.total_compra)}</strong>
                    </td>
                    <td>
                      <button
                        type="button"
                        className={`${styles.secundario} ${styles.botonTabla}`}
                        onClick={() => verDetalle(compra.id_compra)}
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

      <Modal open={detalleId !== null && !confirmando} onClose={cerrarDetalle}
        title={`Compra #${detalle?.compra?.numero_compra ?? detalleId}`}
        description="Detalle de operación" busy={anulando} size="large">
            {cargandoDetalle && (
              <p className={styles.vacio}>Cargando detalle…</p>
            )}

            {errorDetalle && (
              <Alert type="error">{errorDetalle}</Alert>
            )}

            {detalle && (
              <div className={styles.modalBody}>
                <div className={styles.modalSummary}>
                  <div>
                    <span>Estado</span>
                    <strong>
                      {normalizar(detalle.compra.estado)}
                    </strong>
                  </div>
                  <div>
                    <span>Fecha</span>
                    <strong>
                      {fechaLocal(detalle.compra.fecha_compra)}
                    </strong>
                  </div>
                  <div>
                    <span>Proveedor</span>
                    <strong>
                      {nombreProveedor(detalle.compra.id_proveedor)}
                    </strong>
                  </div>
                  <div>
                    <span>Registrada por</span>
                    <strong>
                      {nombreUsuario(detalle.compra.id_usuario)}
                    </strong>
                  </div>
                </div>

                <h3>Productos de la compra</h3>

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
                        <tr key={item.id_detalle_compra}>
                          <td>{nombreProducto(item.id_producto)}</td>
                          <td>{item.cantidad}</td>
                          <td>{formatoMoneda(item.precio_unitario)}</td>
                          <td>{formatoMoneda(item.subtotal)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className={styles.modalTotal}>
                  <span>Total de la compra</span>
                  <strong>
                    {formatoMoneda(detalle.compra.total_compra)}
                  </strong>
                </div>

                {esPropietario && normalizar(detalle.compra.estado) === 'COMPLETADA' && (
                  <div className={styles.modalTotal}>
                    <span>La anulación revierte el stock de esta compra.</span>
                    <button type="button" className={styles.secundario} disabled={anulando}
                      onClick={abrirConfirmacion}>
                      {anulando ? 'Anulando…' : 'Anular compra'}
                    </button>
                  </div>
                )}

                <div className={styles.observaciones}>
                  <strong>Observaciones</strong>
                  <p>
                    {detalle.compra.observaciones ||
                      'Sin observaciones'}
                  </p>
                </div>
              </div>
            )}
      </Modal>
      <ConfirmDialog
        open={confirmando && Boolean(detalle?.compra)}
        onClose={() => { if (!anulando) { setConfirmando(false); setErrorAnulacion('') } }}
        onConfirm={anularCompra}
        title={`¿Anular la compra #${detalle?.compra?.numero_compra ?? detalleId}?`}
        description="Revisá los datos antes de confirmar la anulación."
        details={[
          { label: 'Proveedor', value: detalle ? nombreProveedor(detalle.compra.id_proveedor) : '—' },
          { label: 'Importe', value: formatoMoneda(detalle?.compra?.total_compra) },
        ]}
        warning="Se descontará del stock la mercadería registrada en esta compra. Esta acción no se puede deshacer."
        error={errorAnulacion}
        busy={anulando}
        destructive
        confirmLabel="Confirmar anulación"
      />

    </section>
  )
}
