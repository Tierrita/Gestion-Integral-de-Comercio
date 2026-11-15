import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import { tienePermiso } from '../../shared/auth/permisos.js'
import styles from '../productos/Productos.module.css'

const etiquetas = { cero: 'Sin stock', bajo: 'Stock bajo', todos: 'Todos' }
const estado = (p) => p.estado && p.stock === 0 ? 'cero'
  : p.estado && p.stock > 0 && p.stock <= p.stock_minimo ? 'bajo' : 'todos'
const normalizar = (s) => s.trim().toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '')

function useDatos(ruta) {
  const [version, actualizar] = useState(0)
  const [resultado, setResultado] = useState(null)
  useEffect(() => {
    const controller = new AbortController()
    api.get(ruta, { signal: controller.signal }).then(({ data }) => {
      if (!controller.signal.aborted) setResultado({ ruta, version, data })
    }).catch(() => {
      if (!controller.signal.aborted) setResultado({ ruta, version, error: true })
    })
    return () => controller.abort()
  }, [ruta, version])
  return {
    ...(resultado?.ruta === ruta && resultado.version === version ? resultado : null),
    recargar: () => actualizar((n) => n + 1),
  }
}

function Espera({ consulta }) {
  return consulta.error
    ? <p role="alert">No pudimos cargar los datos. <button onClick={consulta.recargar}>Reintentar</button></p>
    : <p role="status">Cargando…</p>
}

export default function Stock({ profile, vista }) {
  const consulta = useDatos(vista === 'alertas' ? '/stock/alertas' : '/stock')
  const [busqueda, setBusqueda] = useState('')
  const [categoria, setCategoria] = useState('')
  const [filtro, setFiltro] = useState('todos')
  const [panel, setPanel] = useState(null)
  const [aviso, setAviso] = useState('')
  const filas = consulta.data || []
  const categorias = [...new Set(filas.map((p) => p.categoria).filter(Boolean))].sort()
  const termino = normalizar(busqueda)
  const visibles = filas.filter((p) =>
    (!termino || normalizar(p.nombre_producto).includes(termino) || String(p.numero_producto) === termino)
    && (!categoria || p.categoria === categoria)
    && (filtro === 'todos' || estado(p) === filtro),
  )

  return <section className={styles.pagina}>
    <h1>{vista === 'alertas' ? 'Alertas de stock' : 'Existencias'}</h1>
    {aviso && <p role="status">{aviso}</p>}
    <div className={styles.filtros}>
      <label>Buscar<input type="search" placeholder="Nombre o número" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} /></label>
      <label>Categoría<select value={categoria} onChange={(e) => setCategoria(e.target.value)}>
        <option value="">Todas</option>{categorias.map((c) => <option key={c}>{c}</option>)}
      </select></label>
      <label>Disponibilidad<select value={filtro} onChange={(e) => setFiltro(e.target.value)}>
        {['todos', 'cero', 'bajo'].map((clave) => <option key={clave} value={clave}>{etiquetas[clave]}</option>)}
      </select></label>
    </div>
    {!consulta.data ? <Espera consulta={consulta} /> : visibles.length === 0 ? <p>No hay productos para estos filtros.</p> :
      <div className={styles.tabla}><table>
        <thead><tr><th>N.º de producto</th><th>Nombre</th><th>Categoría</th><th>Stock actual</th><th>Stock mínimo</th><th>Estado</th><th>Acciones</th></tr></thead>
        <tbody>{visibles.map((p) => <tr key={p.id_producto}>
          <td>{p.numero_producto}</td><td>{p.nombre_producto}</td><td>{p.categoria || '—'}</td>
          <td>{p.stock} {p.unidad_de_medida}</td><td>{p.stock_minimo}</td>
          <td>{!p.estado ? 'Inactivo' : estado(p) === 'todos' ? 'Disponible' : etiquetas[estado(p)]}</td>
          <td><button onClick={() => setPanel({ producto: p, modo: 'historial' })}>Historial</button>{' '}
            {p.estado && tienePermiso(profile, 'stock.ajustar') && <button onClick={() => setPanel({ producto: p, modo: 'ajuste' })}>Ajustar stock</button>}
          </td>
        </tr>)}</tbody>
      </table></div>}
    {panel && <Panel titulo={panel.producto.nombre_producto} cerrar={() => setPanel(null)}>
      {panel.modo === 'historial' ? <HistorialStock producto={panel.producto} /> :
        <Ajuste producto={panel.producto} completar={(data) => {
          setAviso('Stock actualizado a ' + data.stock_nuevo + '.')
          setPanel(null)
          consulta.recargar()
        }} revisar={() => {
          setPanel(null)
          consulta.recargar()
        }} />}
    </Panel>}
  </section>
}

function Panel({ titulo, cerrar, children }) {
  const ref = useRef(null)
  useEffect(() => {
    const dialogo = ref.current
    dialogo.showModal()
    return () => dialogo.close()
  }, [])
  return <dialog ref={ref} className={styles.panel} aria-labelledby="titulo-stock"
    onCancel={(e) => { e.preventDefault(); cerrar() }}>
    <header className={styles.barra}><h2 id="titulo-stock">{titulo}</h2><button onClick={cerrar}>Cerrar</button></header>
    {children}
  </dialog>
}

function Ajuste({ producto, completar, revisar }) {
  const [tipo, setTipo] = useState('AUMENTAR')
  const [cantidad, setCantidad] = useState('')
  const [motivo, setMotivo] = useState('')
  const [estadoEnvio, setEstadoEnvio] = useState({})
  const activo = useRef(false)
  const nuevo = producto.stock + Number(cantidad) * (tipo === 'AUMENTAR' ? 1 : -1)
  const valido = Number.isSafeInteger(Number(cantidad)) && Number(cantidad) > 0 && nuevo >= 0 && motivo.trim().length >= 5

  async function confirmar(e) {
    e.preventDefault()
    if (activo.current || estadoEnvio.incierto || !valido) return
    activo.current = true
    setEstadoEnvio({ guardando: true })
    try {
      const { data } = await api.patch('/stock/' + producto.id_producto + '/ajustar', {
        tipo_ajuste: tipo,
        cantidad: Number(cantidad),
        observaciones: motivo.trim(),
        stock_esperado: producto.stock,
      })
      completar(data.data)
    } catch (error) {
      const status = error.response?.status
      const incierto = !status || status >= 500
      setEstadoEnvio({
        incierto,
        revisar: incierto || status === 409,
        mensaje: incierto ? 'No se pudo confirmar el ajuste. Revisá las existencias y el historial.'
          : error.response?.data?.error || 'No se pudo ajustar el stock.',
      })
    } finally {
      activo.current = false
    }
  }

  return <form onSubmit={confirmar}>
    <fieldset disabled={estadoEnvio.guardando || estadoEnvio.revisar}>
      <legend>Ajustar stock</legend>
      <label>Movimiento<select value={tipo} onChange={(e) => setTipo(e.target.value)}>
        <option value="AUMENTAR">Entrada</option><option value="DISMINUIR">Salida</option>
      </select></label>
      <label>Cantidad<input type="number" min="1" step="1" required value={cantidad} onChange={(e) => setCantidad(e.target.value)} /></label>
      <label>Motivo (mínimo 5 caracteres)<input required minLength={5} value={motivo} onChange={(e) => setMotivo(e.target.value)} /></label>
      <p>Stock actual {producto.stock} · Stock resultante {nuevo}</p>
      {nuevo < 0 && <p role="alert">La salida supera el stock disponible.</p>}
      <button className={styles.principal} disabled={!valido}>{estadoEnvio.guardando ? 'Guardando…' : 'Confirmar ajuste'}</button>
    </fieldset>
    {estadoEnvio.mensaje && <p role="alert">{estadoEnvio.mensaje}</p>}
    {estadoEnvio.revisar && <button type="button" onClick={revisar}>Actualizar existencias</button>}
  </form>
}

export function HistorialStock({ producto }) {
  const [pagina, setPagina] = useState(1)
  const consulta = useDatos('/stock/historial?pagina=' + pagina + (producto ? '&id_producto=' + producto.id_producto : ''))
  return <section className={styles.pagina}>
    <div className={styles.barra}><h2>Historial de stock</h2>{!producto && <Link to="/stock/existencias">Volver a existencias</Link>}</div>
    {!consulta.data ? <Espera consulta={consulta} /> : consulta.data.movimientos.length ? (
      <div className={styles.tabla}><table>
        <thead><tr><th>Fecha</th>{!producto && <th>Producto</th>}<th>Usuario</th><th>Movimiento</th><th>Motivo</th><th>Cantidad</th><th>Antes</th><th>Después</th></tr></thead>
        <tbody>{consulta.data.movimientos.map((m) => <tr key={m.id_movimiento}>
          <td>{new Date(m.fecha_movimiento).toLocaleString('es-AR')}</td>
          {!producto && <td>{m.productos.numero_producto} · {m.productos.nombre_producto}</td>}
          <td>{m.usuarios?.nombre_completo || '—'}</td><td>{m.tipo_movimiento.replaceAll('_', ' ')}</td>
          <td>{m.observaciones || '—'}</td><td>{m.cantidad}</td><td>{m.stock_anterior}</td><td>{m.stock_nuevo}</td>
        </tr>)}</tbody>
      </table></div>
    ) : <p>Todavía no hay movimientos.</p>}
    {consulta.data && (pagina > 1 || consulta.data.hay_mas) && <div className={styles.filtros}>
      <button disabled={pagina === 1} onClick={() => setPagina(pagina - 1)}>Anterior</button>
      <span>Página {pagina}</span>
      <button disabled={!consulta.data.hay_mas} onClick={() => setPagina(pagina + 1)}>Siguiente</button>
    </div>}
  </section>
}
