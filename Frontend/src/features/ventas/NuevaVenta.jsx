
import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import ConfirmDialog from '../../shared/components/ConfirmDialog.jsx'
import BackButton from '../../shared/components/BackButton.jsx'
import Alert from '../../shared/components/Alert.jsx'
import styles from './NuevaVenta.module.css'
import { formatoMoneda, formatoFechaHora } from '../../shared/utils/formatters.js'

const cantidadValida = (valor, unidad, stock) => {
  const texto = String(valor).trim()
  const formato = unidad === 'KG'
    ? /^\d+(\.\d{1,3})?$/
    : /^\d+$/

  if (!formato.test(texto)) return false

  const numero = Number(texto)
  return numero > 0 && numero <= Number(stock)
}

export default function NuevaVenta() {
  const navigate = useNavigate()
  const enviandoRef = useRef(false)
  const [enviando, setEnviando] = useState(false)
  const [errorVenta, setErrorVenta] = useState('')
  const [confirmando, setConfirmando] = useState(false)

  const [fechaActual] = useState(() => formatoFechaHora(new Date()))

  const [cliente, setCliente] = useState('')
  const [clientes, setClientes] = useState([])
  const [errorClientes, setErrorClientes] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [metodoPago, setMetodoPago] = useState('EFECTIVO')
  const [observaciones, setObservaciones] = useState('')

  const [cuentas, setCuentas] = useState([])
  const [cuentaSeleccionada, setCuentaSeleccionada] = useState('')
  const [errorCuentas, setErrorCuentas] = useState('')
  const [cargandoCuentas, setCargandoCuentas] = useState(true)



  const [productos, setProductos] = useState([])
  const [carrito, setCarrito] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    async function cargarProductos() {
      try {
        const { data } = await api.get('/productos', {
          signal: controller.signal,
        })

        if (!Array.isArray(data)) {
          throw new Error('Respuesta de productos inválida.')
        }

        if (!controller.signal.aborted) {
          setProductos(data)
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(
            err.response?.data?.error ||
            'No se pudieron cargar los productos.',
          )
        }
      } finally {
        if (!controller.signal.aborted) {
          setCargando(false)
        }
      }
    }

    const timer = setTimeout(() => {
      void cargarProductos()
    }, 0)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [])


  useEffect(() => {
  const controller = new AbortController()

  async function cargarClientes() {
    try {
      const { data } = await api.get('/clientes', {
        signal: controller.signal,
      })

      if (!Array.isArray(data)) {
        throw new Error('Respuesta inválida de clientes')
      }

      setClientes(data.filter((item) => item.estado === true))
    } catch (error) {
      if (!controller.signal.aborted) {
        setErrorClientes(
          error.response?.data?.error ||
          'No se pudieron cargar los clientes.',
        )
      }
    }
  }

  void cargarClientes()

  return () => controller.abort()
}, [])



useEffect(() => {
  const controller = new AbortController()

  async function cargarCuentas() {
    try {
      const { data } = await api.get('/cuentas', {
        signal: controller.signal,
      })

      if (!Array.isArray(data?.cuentas)) {
        throw new Error('Respuesta inválida de cuentas')
      }

      if (controller.signal.aborted) return
      const activas = data.cuentas.filter((cuenta) => cuenta.estado === true)
      setCuentas(activas)
      const principal = activas.find((cuenta) => String(cuenta.nombre_cuenta ?? '').trim().toUpperCase() === 'CAJA PRINCIPAL')
      setCuentaSeleccionada((actual) => actual || String(principal?.id_cuenta ?? ''))
    } catch (error) {
      if (!controller.signal.aborted) {
        setErrorCuentas(
          error.response?.data?.error ||
          'No se pudieron cargar las cuentas.',
        )
      }
    } finally {
      if (!controller.signal.aborted) setCargandoCuentas(false)
    }
  }

  void cargarCuentas()

  return () => controller.abort()
}, [])


  const resultados = useMemo(() => {
    const texto = busqueda.trim().toLowerCase()

    if (!texto) return []

    return productos
      .filter((producto) =>
        producto.estado !== false &&
        Number(producto.stock) > 0 &&
        [
          producto.nombre_producto,
          producto.numero_producto,
          producto.id_producto,
        ].some((valor) =>
          String(valor ?? '').toLowerCase().includes(texto),
        ),
      )
      .slice(0, 10)
  }, [productos, busqueda])

  function agregarProducto(producto) {
    setCarrito((actual) => {
      if (actual.some((item) =>
        item.id_producto === producto.id_producto
      )) {
        return actual
      }

      return [
        ...actual,
        {
          ...producto,
          cantidad: '1',
        },
      ]
    })

    setBusqueda('')
  }

  function cambiarCantidad(id, valor) {
    setCarrito((actual) =>
      actual.map((item) =>
        item.id_producto === id
          ? { ...item, cantidad: valor }
          : item,
      ),
    )
  }

  function quitarProducto(id) {
    setCarrito((actual) =>
      actual.filter((item) => item.id_producto !== id),
    )
  }

  const total = carrito.reduce((acumulado, item) => {
    if (!cantidadValida(
      item.cantidad,
      item.unidad_de_medida,
      item.stock,
    )) {
      return acumulado
    }

    return acumulado +
      Number(item.cantidad) * Number(item.precio_venta)
  }, 0)

  const carritoValido = carrito.length > 0 &&
    carrito.every((item) =>
      cantidadValida(
        item.cantidad,
        item.unidad_de_medida,
        item.stock,
      ),
    )

  const puedeConfirmar = Boolean(cliente) && !errorClientes && carritoValido &&
    (metodoPago === 'CUENTA_CORRIENTE' || (Boolean(cuentaSeleccionada) && !cargandoCuentas && !errorCuentas)) &&
    !enviando && !cargando && !error

  function solicitarConfirmacion() {
    if (!puedeConfirmar || enviandoRef.current) return
    setErrorVenta('')
    setConfirmando(true)
  }

  async function confirmarVenta() {
    if (enviandoRef.current) return

    if (!cliente || !carritoValido ||
      (metodoPago !== 'CUENTA_CORRIENTE' && !cuentaSeleccionada)) {
      setErrorVenta('Seleccioná un cliente, agregá productos válidos y elegí una cuenta de destino cuando corresponda.')
      return
    }

    enviandoRef.current = true
    setEnviando(true)
    setErrorVenta('')

    const payload = {
      id_cliente: Number(cliente),
      metodo_pago: metodoPago,
      productos: carrito.map((item) => ({
        id_producto: Number(item.id_producto),
        cantidad: Number(item.cantidad),
      })),
      observaciones: observaciones.trim(),
    }

    if (metodoPago !== 'CUENTA_CORRIENTE') {
      payload.id_cuenta = Number(cuentaSeleccionada)
    }

    try {
      await api.post('/ventas', payload)
      setConfirmando(false)
      navigate('/ventas', { replace: true })
    } catch (err) {
      const respuesta = err.response?.data
      const mensaje = respuesta?.error || respuesta?.message
      setErrorVenta(
        typeof mensaje === 'string' ? mensaje :
          'No se pudo confirmar la venta. Revisá la conexión y el listado antes de reintentar.',
      )
    } finally {
      enviandoRef.current = false
      setEnviando(false)
    }
  }

  return (
    <section className={styles.pagina}>
      <header className={styles.encabezado}>
        <div>
          <p className={styles.etiqueta}>GESTIÓN COMERCIAL</p>
          <h1>Crear venta</h1>
          <p className={styles.descripcion}>
            Registrá una nueva operación comercial.
          </p>
        </div>

        <BackButton to="/ventas" label="Volver a ventas" />
      </header>

      <section className={styles.panel}>
        <div className={styles.datosGrid}>
          <label className={styles.campo}>
            Vendedor
            <input value="Usuario autenticado" readOnly />
          </label>

          <label className={styles.campo}>
            Fecha de emisión
            <input value={fechaActual} readOnly />
          </label>

          
<label className={styles.campo}>
  Cliente
  <select
    value={cliente}
    onChange={(e) => setCliente(e.target.value)}
  >
    <option value="">Seleccionar cliente</option>

    {clientes.map((item) => (
      <option key={item.id_cliente} value={item.id_cliente}>
        {item.nombre_completo} (N.º {item.numero_cliente})
      </option>
    ))}
  </select>

  {errorClientes && (
    <span role="alert" className={styles.error}>{errorClientes}</span>
  )}
</label>

        </div>

        <div className={styles.productos}>
          <h2>Productos</h2>

          <div className={styles.buscador}>
            <label className={styles.campo}>
              Buscar producto
              <input
                type="search"
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                placeholder="Buscar por nombre o número..."
                disabled={cargando || Boolean(error)}
              />
            </label>

            {cargando && (
              <p role="status">Cargando productos…</p>
            )}

            {error && <Alert type="error">{error}</Alert>}

            {busqueda.trim() && !cargando && !error && (
              <div className={styles.resultados}>
                {resultados.length === 0 ? (
                  <p className={styles.sinResultados}>
                    No se encontraron productos disponibles.
                  </p>
                ) : (
                  resultados.map((producto) => {
                    const agregado = carrito.some(
                      (item) =>
                        item.id_producto === producto.id_producto,
                    )

                    return (
                      <button
                        key={producto.id_producto}
                        type="button"
                        className={styles.resultado}
                        onClick={() => agregarProducto(producto)}
                        disabled={agregado}
                      >
                        <span>
                          <strong>{producto.nombre_producto}</strong>
                          <small>
                            N.º {producto.numero_producto} ·
                            Stock: {producto.stock}{' '}
                            {producto.unidad_de_medida}
                          </small>
                        </span>

                        <strong>
                          {agregado
                            ? 'Agregado'
                            : formatoMoneda(producto.precio_venta)}
                        </strong>
                      </button>
                    )
                  })
                )}
              </div>
            )}
          </div>

          <div className={styles.tablaScroll}>
            <table>
              <thead>
                <tr>
                  <th>Producto</th>
                  <th>Cantidad</th>
                  <th>Precio</th>
                  <th>Subtotal</th>
                  <th>Acción</th>
                </tr>
              </thead>

              <tbody>
                {carrito.length === 0 ? (
                  <tr>
                    <td colSpan={5} className={styles.vacio}>
                      Todavía no agregaste productos.
                    </td>
                  </tr>
                ) : (
                  carrito.map((item) => {
                    const valido = cantidadValida(
                      item.cantidad,
                      item.unidad_de_medida,
                      item.stock,
                    )

                    return (
                      <tr key={item.id_producto}>
                        <td>
                          <strong>{item.nombre_producto}</strong>
                          <div className={styles.datoExtra}>
                            Stock disponible: {item.stock}{' '}
                            {item.unidad_de_medida}
                          </div>
                        </td>

                        <td>
                          <input
                            className={styles.cantidadInput}
                            type="number"
                            min={item.unidad_de_medida === 'KG'
                              ? '0.001'
                              : '1'}
                            max={item.stock}
                            step={item.unidad_de_medida === 'KG'
                              ? '0.001'
                              : '1'}
                            value={item.cantidad}
                            aria-label={`Cantidad de ${item.nombre_producto}`}
                            aria-invalid={!valido}
                            onChange={(e) =>
                              cambiarCantidad(
                                item.id_producto,
                                e.target.value,
                              )
                            }
                          />

                          {!valido && (
                            <small className={styles.errorCantidad}>
                              Cantidad inválida
                            </small>
                          )}
                        </td>

                        <td>{formatoMoneda(item.precio_venta)}</td>

                        <td>
                          {valido
                            ? formatoMoneda(
                                Number(item.cantidad) *
                                Number(item.precio_venta),
                              )
                            : '—'}
                        </td>

                        <td>
                          <button
                            type="button"
                            className={styles.quitar}
                            onClick={() =>
                              quitarProducto(item.id_producto)
                            }
                          >
                            Quitar
                          </button>
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>

              <tfoot>
                <tr>
                  <td colSpan={3}>Productos agregados</td>
                  <td colSpan={2}>{carrito.length}</td>
                </tr>

                <tr className={styles.filaTotal}>
                  <td colSpan={3}>Total a pagar</td>
                  <td colSpan={2}>
                    {carritoValido ? formatoMoneda(total) : '—'}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </section>

      <section className={styles.panel}>
        <h2>Agregar pago</h2>

        <div className={styles.pagoGrid}>
          <label className={styles.campo}>
            Importe
            <input
              value={carritoValido ? formatoMoneda(total) : '—'}
              readOnly
            />
          </label>

          <label className={styles.campo}>
            Método de pago
            <select
              value={metodoPago}
              onChange={(e) => setMetodoPago(e.target.value)}
            >
              <option value="EFECTIVO">Efectivo</option>
              <option value="TRANSFERENCIA">Transferencia</option>
              <option value="CUENTA_CORRIENTE">
                Cuenta corriente
              </option>
            </select>
          </label>

          {metodoPago !== 'CUENTA_CORRIENTE' && (
            <label className={styles.campo}>
              Cuenta de destino
              <select
                value={cuentaSeleccionada}
                onChange={(e) => setCuentaSeleccionada(e.target.value)}
                disabled={cargandoCuentas || Boolean(errorCuentas)}
              >
                <option value="">{cargandoCuentas ? 'Cargando cuentas…' : 'Seleccionar cuenta'}</option>
                {cuentas.map((cuenta) => (
                  <option key={cuenta.id_cuenta} value={cuenta.id_cuenta}>
                    {cuenta.nombre_cuenta}
                  </option>
                ))}
              </select>
              {errorCuentas && <span role="alert" className={styles.error}>{errorCuentas}</span>}
              {!cargandoCuentas && !errorCuentas && cuentas.length === 0 && <small className={styles.ayudaCampo}>No hay cuentas activas disponibles.</small>}
            </label>
          )}
        </div>
      </section>

      <section className={styles.panel}>
        <h2>Observaciones</h2>

        <textarea
          value={observaciones}
          onChange={(e) => setObservaciones(e.target.value)}
          placeholder="Observaciones opcionales..."
          rows={3}
        />
      </section>

      <footer className={styles.acciones}>
        <button
          type="button"
          className={styles.secundario}
          onClick={() => navigate('/ventas')}
        >
          Cancelar
        </button>

        {errorVenta && !confirmando && <Alert type="error">{errorVenta}</Alert>}

        <button
          type="button"
          className={styles.confirmar}
          disabled={!puedeConfirmar}
          onClick={solicitarConfirmacion}
        >
          {enviando ? 'Registrando venta…' : 'Confirmar venta'}
        </button>
      </footer>
      <ConfirmDialog open={confirmando} onClose={() => { if (!enviando) setConfirmando(false) }}
        onConfirm={confirmarVenta} title="¿Registrar esta venta?"
        description="Confirmá los datos antes de registrar la venta."
        details={[
          { label: 'Cliente', value: clientes.find((item) => String(item.id_cliente) === String(cliente))?.nombre_completo || `Cliente #${cliente}` },
          { label: 'Total estimado', value: formatoMoneda(total) },
          { label: 'Método de pago', value: metodoPago.replaceAll('_', ' ') },
          ...(metodoPago !== 'CUENTA_CORRIENTE' ? [{ label: 'Cuenta de destino', value: cuentas.find((item) => String(item.id_cuenta) === String(cuentaSeleccionada))?.nombre_cuenta || '—' }] : []),
        ]}
        warning="Se descontará el stock y se registrará la operación comercial."
        error={errorVenta} busy={enviando} confirmLabel="Registrar venta" />
    </section>
  )
}
