import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import ConfirmDialog from '../../shared/components/ConfirmDialog.jsx'
import Alert from '../../shared/components/Alert.jsx'
import styles from '../ventas/NuevaVenta.module.css'
import { formatoMoneda } from '../../shared/utils/formatters.js'

const cantidadValida = (valor, unidad) => {
  const texto = String(valor).trim()
  const formato = String(unidad).toUpperCase() === 'KG'
    ? /^\d+(\.\d{1,3})?$/
    : /^\d+$/
  return formato.test(texto) && Number(texto) > 0
}

const costoValido = (valor) => {
  const texto = String(valor).trim()
  return /^\d+(\.\d{1,2})?$/.test(texto) && Number(texto) > 0
}

export default function NuevaCompra() {
  const navigate = useNavigate()
  const enviandoRef = useRef(false)
  const [proveedores, setProveedores] = useState([])
  const [productos, setProductos] = useState([])
  const [proveedor, setProveedor] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [carrito, setCarrito] = useState([])
  const [observaciones, setObservaciones] = useState('')
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [errorCompra, setErrorCompra] = useState('')
  const [confirmando, setConfirmando] = useState(false)
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    async function cargar() {
      try {
        const [respuestaProductos, respuestaProveedores] = await Promise.all([
          api.get('/productos', { signal: controller.signal }),
          api.get('/proveedores', { signal: controller.signal }),
        ])
        const listaProductos = respuestaProductos.data
        const listaProveedores = Array.isArray(respuestaProveedores.data)
          ? respuestaProveedores.data
          : respuestaProveedores.data?.proveedores
        if (!Array.isArray(listaProductos) || !Array.isArray(listaProveedores)) {
          throw new Error('Respuesta de productos o proveedores inválida.')
        }
        if (!controller.signal.aborted) {
          setProductos(listaProductos.filter((item) => item.estado === true))
          setProveedores(listaProveedores.filter((item) => item.estado === true))
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err.response?.data?.error || err.message || 'No se pudieron cargar los datos.')
        }
      } finally {
        if (!controller.signal.aborted) setCargando(false)
      }
    }
    void cargar()
    return () => controller.abort()
  }, [])

  const resultados = useMemo(() => {
    const texto = busqueda.trim().toLowerCase()
    if (!texto) return []
    return productos.filter((item) => [
      item.nombre_producto, item.numero_producto, item.id_producto,
    ].some((valor) => String(valor ?? '').toLowerCase().includes(texto)))
      .slice(0, 10)
  }, [productos, busqueda])

  function agregarProducto(producto) {
    setCarrito((actual) => actual.some((item) => item.id_producto === producto.id_producto)
      ? actual
      : [...actual, { ...producto, cantidad: '1', precio_unitario: String(producto.precio_costo ?? '') }])
    setBusqueda('')
  }

  function cambiarItem(id, campo, valor) {
    setCarrito((actual) => actual.map((item) =>
      item.id_producto === id ? { ...item, [campo]: valor } : item))
  }

  const carritoValido = carrito.length > 0 && carrito.every((item) =>
    cantidadValida(item.cantidad, item.unidad_de_medida) &&
    costoValido(item.precio_unitario))
  const total = carrito.reduce((suma, item) => (
    cantidadValida(item.cantidad, item.unidad_de_medida) && costoValido(item.precio_unitario)
      ? suma + Number(item.cantidad) * Number(item.precio_unitario)
      : suma
  ), 0)

  function solicitarConfirmacion() {
    if (!proveedor || !carritoValido || enviandoRef.current || cargando || error) return
    setErrorCompra('')
    setConfirmando(true)
  }

  async function confirmarCompra() {
    if (enviandoRef.current) return
    if (!proveedor || !carritoValido) {
      setErrorCompra('Seleccioná un proveedor y cargá productos con cantidades y costos válidos.')
      return
    }
    enviandoRef.current = true
    setEnviando(true)
    setErrorCompra('')
    try {
      await api.post('/compras', {
        id_proveedor: Number(proveedor),
        productos: carrito.map((item) => ({
          id_producto: Number(item.id_producto),
          cantidad: Number(item.cantidad),
          precio_unitario: Number(item.precio_unitario),
        })),
        observaciones: observaciones.trim(),
      })
      setConfirmando(false)
      navigate('/compras', { replace: true })
    } catch (err) {
      setErrorCompra(err.response?.data?.error ||
        'No se pudo registrar la compra. Verificá el listado antes de reintentar.')
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
          <h1>Crear compra</h1>
          <p className={styles.descripcion}>Registrá mercadería recibida y actualizá su costo.</p>
        </div>
        <button type="button" className={styles.secundario} onClick={() => navigate('/compras')}>Volver a compras</button>
      </header>

      <section className={styles.panel}>
        <div className={styles.datosGrid}>
          <label className={styles.campo}>
            Proveedor
            <select value={proveedor} onChange={(e) => setProveedor(e.target.value)} disabled={cargando || Boolean(error)}>
              <option value="">Seleccionar proveedor</option>
              {proveedores.map((item) => (
                <option key={item.id_proveedor} value={item.id_proveedor}>{item.nombre_proveedor}</option>
              ))}
            </select>
          </label>
        </div>

        <div className={styles.productos}>
          <h2>Productos recibidos</h2>
          {cargando && <p role="status">Cargando productos y proveedores…</p>}
          {error && <Alert type="error">{error}</Alert>}
          {!cargando && !error && proveedores.length === 0 && (
            <p role="status">No hay proveedores activos disponibles.</p>
          )}
          <div className={styles.buscador}>
            <label className={styles.campo}>
              Buscar producto
              <input type="search" value={busqueda} onChange={(e) => setBusqueda(e.target.value)}
                placeholder="Nombre, número o ID…" disabled={cargando || Boolean(error)} />
            </label>
            {busqueda.trim() && !cargando && !error && (
              <div className={styles.resultados}>
                {resultados.length === 0 ? (
                  <p className={styles.sinResultados}>No se encontraron productos activos.</p>
                ) : resultados.map((item) => {
                  const agregado = carrito.some((producto) => producto.id_producto === item.id_producto)
                  return (
                    <button type="button" className={styles.resultado} key={item.id_producto}
                      onClick={() => agregarProducto(item)} disabled={agregado}>
                      <span><strong>{item.nombre_producto}</strong><small>N.º {item.numero_producto} · Stock: {item.stock} {item.unidad_de_medida}</small></span>
                      <strong>{agregado ? 'Agregado' : formatoMoneda(item.precio_costo)}</strong>
                    </button>
                  )
                })}
              </div>
            )}
          </div>

          <div className={styles.tablaScroll}>
            <table>
              <thead><tr><th>Producto</th><th>Cantidad</th><th>Costo unitario</th><th>Subtotal</th><th>Acción</th></tr></thead>
              <tbody>
                {carrito.length === 0 ? (
                  <tr><td colSpan={5} className={styles.vacio}>Todavía no agregaste productos.</td></tr>
                ) : carrito.map((item) => {
                  const cantidadOk = cantidadValida(item.cantidad, item.unidad_de_medida)
                  const costoOk = costoValido(item.precio_unitario)
                  return (
                    <tr key={item.id_producto}>
                      <td><strong>{item.nombre_producto}</strong><div className={styles.datoExtra}>Stock actual: {item.stock} {item.unidad_de_medida}</div></td>
                      <td>
                        <input className={styles.cantidadInput} type="number" min={item.unidad_de_medida === 'KG' ? '0.001' : '1'}
                          step={item.unidad_de_medida === 'KG' ? '0.001' : '1'} value={item.cantidad}
                          aria-label={`Cantidad de ${item.nombre_producto}`} aria-invalid={!cantidadOk}
                          onChange={(e) => cambiarItem(item.id_producto, 'cantidad', e.target.value)} />
                        {!cantidadOk && <small className={styles.errorCantidad}>Cantidad inválida</small>}
                      </td>
                      <td>
                        <input className={styles.cantidadInput} type="number" min="0.01" step="0.01"
                          value={item.precio_unitario} aria-label={`Costo de ${item.nombre_producto}`}
                          aria-invalid={!costoOk} onChange={(e) => cambiarItem(item.id_producto, 'precio_unitario', e.target.value)} />
                        {!costoOk && <small className={styles.errorCantidad}>Costo inválido (máx. 2 decimales)</small>}
                      </td>
                      <td>{cantidadOk && costoOk ? formatoMoneda(Number(item.cantidad) * Number(item.precio_unitario)) : '—'}</td>
                      <td><button type="button" className={styles.quitar}
                        onClick={() => setCarrito((actual) => actual.filter((producto) => producto.id_producto !== item.id_producto))}>Quitar</button></td>
                    </tr>
                  )
                })}
              </tbody>
              <tfoot><tr><td colSpan={3}>Productos agregados</td><td colSpan={2}>{carrito.length}</td></tr><tr className={styles.filaTotal}><td colSpan={3}>Total estimado</td><td colSpan={2}>{carritoValido ? formatoMoneda(total) : '—'}</td></tr></tfoot>
            </table>
          </div>
        </div>
      </section>

      <section className={styles.panel}>
        <h2>Observaciones</h2>
        <textarea rows={3} value={observaciones} onChange={(e) => setObservaciones(e.target.value)}
          placeholder="Observaciones opcionales…" />
      </section>

      <footer className={styles.acciones}>
        <button type="button" className={styles.secundario} onClick={() => navigate('/compras')}>Cancelar</button>
        {errorCompra && !confirmando && <Alert type="error">{errorCompra}</Alert>}
        <button type="button" className={styles.confirmar} disabled={!proveedor || !carritoValido || enviando || cargando || Boolean(error)}
          onClick={solicitarConfirmacion}>{enviando ? 'Registrando compra…' : 'Confirmar compra'}</button>
      </footer>
      <ConfirmDialog open={confirmando} onClose={() => { if (!enviando) setConfirmando(false) }}
        onConfirm={confirmarCompra} title="¿Registrar esta compra?"
        description="Confirmá los datos antes de registrar la compra."
        details={[
          { label: 'Proveedor', value: proveedores.find((item) => String(item.id_proveedor) === String(proveedor))?.nombre_proveedor || `Proveedor #${proveedor}` },
          { label: 'Productos', value: carrito.length },
          { label: 'Total estimado', value: formatoMoneda(total) },
        ]}
        warning="Se actualizarán el stock y los costos de los productos."
        error={errorCompra} busy={enviando} confirmLabel="Registrar compra" />
    </section>
  )
}
