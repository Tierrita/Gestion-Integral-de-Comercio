import { useEffect, useRef, useState } from 'react'
import { api } from '../../shared/api/client.js'
import { tienePermiso } from '../../shared/auth/permisos.js'
import { HistorialStock } from '../stock/Stock.jsx'
import styles from './Productos.module.css'

const pesos = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })
const normalizar = (texto) => texto.trim().toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '')
const nombreCategoria = (producto, categorias) => categorias.find((c) => c.id_categoria === producto.id_categoria)?.nombre_categoria
  ?? (producto.id_categoria ? 'Categoría #' + producto.id_categoria : 'Sin categoría')

function mensaje(error) {
  const status = error.response?.status
  return status >= 400 && status < 500
    ? error.response.data?.error || 'Flask rechazó la operación.'
    : 'No se pudo confirmar la operación. Actualizá los datos antes de reintentar.'
}

function useConsulta(ruta) {
  const [version, setVersion] = useState(0)
  const [resultado, setResultado] = useState(null)
  useEffect(() => {
    if (!ruta) return
    const controller = new AbortController()
    api.get(ruta, { signal: controller.signal }).then(({ data }) => {
      if (!controller.signal.aborted) setResultado({ ruta, version, data })
    }).catch((error) => {
      if (!controller.signal.aborted) setResultado({ ruta, version, error: mensaje(error) })
    })
    return () => controller.abort()
  }, [ruta, version])

  return {
    ...(resultado?.ruta === ruta && resultado.version === version ? resultado : null),
    actualizar: () => setVersion((actual) => actual + 1),
  }
}

function Estado({ consulta }) {
  return consulta.error
    ? <div role="alert">{consulta.error} <button onClick={consulta.actualizar}>Reintentar consulta</button></div>
    : <p role="status">Cargando…</p>
}

function Panel({ titulo, cerrar, children }) {
  const dialogo = useRef(null)
  useEffect(() => {
    const elemento = dialogo.current
    elemento.showModal()
    return () => elemento.close()
  }, [])

  return <dialog ref={dialogo} className={styles.panel} aria-labelledby="titulo-producto"
    onCancel={(event) => { event.preventDefault(); cerrar() }}>
    <header className={styles.barra}><h2 id="titulo-producto">{titulo}</h2><button onClick={cerrar}>Cerrar</button></header>
    {children}
  </dialog>
}

export default function Productos({ profile }) {
  const permite = (permiso) => tienePermiso(profile, permiso)
  const productos = useConsulta('/productos')
  const categorias = useConsulta(permite('categorias.ver') ? '/categorias' : null)
  const [busqueda, setBusqueda] = useState('')
  const [activos, setActivos] = useState(true)
  const [panel, setPanel] = useState(null)
  const [aviso, setAviso] = useState('')
  const termino = normalizar(busqueda)
  const visibles = productos.data?.filter((producto) => producto.estado === activos && (
    /^\d+$/.test(termino) ? Number(termino) === producto.numero_producto : normalizar(producto.nombre_producto).includes(termino)
  ))
  const verCosto = permite('productos.ver_costos')
  const verCatalogos = permite('categorias.ver') && permite('proveedores.ver')

  function finalizar(texto) {
    setPanel(null)
    setAviso(texto)
    productos.actualizar()
  }

  return <section className={styles.pagina}>
    <div className={styles.barra}>
      <h1>Productos</h1>
      {permite('productos.crear') && verCatalogos && <button className={styles.principal} onClick={() => setPanel({ modo: 'crear' })}>Nuevo producto</button>}
    </div>
    {aviso && <p role="status">{aviso}</p>}
    <div className={styles.filtros}>
      <label>Buscar producto<input type="search" placeholder="Nombre o número" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} /></label>
      <label>Estado<select value={activos ? 'activos' : 'inactivos'} onChange={(e) => setActivos(e.target.value === 'activos')}>
        <option value="activos">Activos</option><option value="inactivos">Inactivos</option>
      </select></label>
    </div>
    {categorias.error && <Estado consulta={categorias} />}
    {!productos.data ? <Estado consulta={productos} /> : visibles.length ? (
      <div className={styles.tabla}><table>
        <thead><tr><th>N.º de producto</th><th>Nombre</th><th>Categoría</th><th>Precio de venta</th>{verCosto && <th>Precio de costo</th>}</tr></thead>
        <tbody>{visibles.map((p) => <tr key={p.id_producto}>
          <td>{p.numero_producto}</td><td><button className={styles.enlace} onClick={() => setPanel({ modo: 'ver', id: p.id_producto })}>{p.nombre_producto}</button></td>
          <td>{nombreCategoria(p, categorias.data || [])}</td><td>{pesos.format(p.precio_venta)}</td>
          {verCosto && <td>{p.precio_costo == null ? '—' : pesos.format(p.precio_costo)}</td>}
        </tr>)}</tbody>
      </table></div>
    ) : <p>No hay productos {activos ? 'activos' : 'inactivos'} para mostrar.</p>}
    {panel && <Panel titulo={panel.modo === 'crear' ? 'Nuevo producto' : 'Detalle de producto'} cerrar={() => setPanel(null)}>
      {panel.modo === 'crear' ? <Editor categorias={categorias} crearCategoria={permite('categorias.gestionar')} finalizar={finalizar} />
        : <Ficha key={panel.id} id={panel.id} categorias={categorias} editar={permite('productos.modificar') && verCatalogos}
          verHistorial={permite('stock.ver')} cambiarEstado={permite('productos.estado')} finalizar={finalizar} />}
    </Panel>}
  </section>
}

function Ficha({ id, categorias, editar, verHistorial, cambiarEstado, finalizar }) {
  const consulta = useConsulta('/productos/' + id)
  const [edita, setEdita] = useState(false)
  const [historial, setHistorial] = useState(false)
  const [confirma, setConfirma] = useState(false)
  const guardado = useGuardado()
  const p = consulta.data

  if (!p) return <Estado consulta={consulta} />
  if (edita) return <Editor producto={p} categorias={categorias} finalizar={finalizar} cancelar={() => setEdita(false)} />

  function cambiar() {
    guardado.enviar(
      () => api.patch('/productos/' + id + '/estado', { estado: !p.estado }),
      () => finalizar(p.estado ? 'Producto desactivado.' : 'Producto reactivado.'),
    )
  }

  return <>
    <h3>{p.nombre_producto}</h3>
    <dl>
      <dt>N.º de producto</dt><dd>{p.numero_producto}</dd>
      <dt>Categoría</dt><dd>{nombreCategoria(p, categorias.data || [])}</dd>
      <dt>Precio de venta</dt><dd>{pesos.format(p.precio_venta)}</dd>
      {p.precio_costo != null && <><dt>Precio de costo</dt><dd>{pesos.format(p.precio_costo)}</dd></>}
      <dt>Stock</dt><dd>{p.stock} {p.unidad_de_medida}</dd>
      <dt>Stock mínimo</dt><dd>{p.stock_minimo}</dd>
      <dt>Estado</dt><dd>{p.estado ? 'Activo' : 'Inactivo'}</dd>
    </dl>
    <div className={styles.barra}>
      {editar && !confirma && <button disabled={guardado.ocupado || guardado.incierto} onClick={() => setEdita(true)}>Editar</button>}
      {cambiarEstado && !confirma && <button disabled={guardado.ocupado || guardado.incierto}
        onClick={() => p.estado ? setConfirma(true) : cambiar()}>{p.estado ? 'Desactivar' : 'Reactivar'}</button>}
    </div>
    {confirma && <div>
      <p>¿Desactivar {p.nombre_producto}?</p>
      <button disabled={guardado.ocupado || guardado.incierto} onClick={cambiar}>Confirmar desactivación</button>{' '}
      <button disabled={guardado.ocupado} onClick={() => setConfirma(false)}>Cancelar</button>
    </div>}
    {guardado.error && <p role="alert">{guardado.error}</p>}
    {verHistorial && <button onClick={() => setHistorial(!historial)}>{historial ? 'Ocultar historial' : 'Ver historial'}</button>}
    {verHistorial && historial && <HistorialStock producto={p} />}
  </>
}

function useGuardado() {
  const activo = useRef(false)
  const [estado, setEstado] = useState({})
  async function enviar(peticion, completar) {
    if (activo.current || estado.incierto) return
    activo.current = true
    setEstado({ ocupado: true })
    try {
      const { data } = await peticion()
      completar(data)
      setEstado({})
    } catch (error) {
      const status = error.response?.status
      setEstado({ error: mensaje(error), incierto: !status || status >= 500 })
    } finally {
      activo.current = false
    }
  }

  return { ...estado, enviar }
}

function Editor({ producto, categorias, crearCategoria, finalizar, cancelar }) {
  const proveedores = useConsulta('/proveedores')
  const guardado = useGuardado()
  const altaCategoria = useGuardado()
  const [nueva, setNueva] = useState(null)
  const [categoria, setCategoria] = useState(String(producto?.id_categoria ?? ''))
  const [proveedor, setProveedor] = useState(String(producto?.id_proveedor ?? ''))
  const [nombre, setNombre] = useState('')
  const bloqueado = guardado.ocupado || guardado.incierto || altaCategoria.ocupado
  const lista = categorias.data || []
  const opciones = nueva && !lista.some((c) => c.id_categoria === nueva.id_categoria) ? [...lista, nueva] : lista

  function agregarCategoria() {
    altaCategoria.enviar(() => api.post('/categorias', { nombre_categoria: nombre.trim() }), (data) => {
      setNueva(data.categoria)
      setCategoria(String(data.categoria.id_categoria))
      setNombre('')
      categorias.actualizar()
    })
  }

  function guardar(event) {
    event.preventDefault()
    const datos = Object.fromEntries(new FormData(event.currentTarget))
    for (const campo of ['id_categoria', 'id_proveedor', 'precio_costo', 'precio_venta', 'stock', 'stock_minimo']) {
      if (campo in datos) datos[campo] = Number(datos[campo])
    }
    if (producto && datos.id_categoria === producto.id_categoria) delete datos.id_categoria
    if (producto && datos.id_proveedor === producto.id_proveedor) delete datos.id_proveedor
    datos.nombre_producto = datos.nombre_producto.trim()
    datos.unidad_de_medida = datos.unidad_de_medida.trim()
    guardado.enviar(
      () => producto ? api.patch('/productos/' + producto.id_producto, datos) : api.post('/productos', datos),
      () => finalizar(producto ? 'Producto actualizado.' : 'Producto creado.'),
    )
  }

  return <>
    {!proveedores.data && <Estado consulta={proveedores} />}
    {!categorias.data && <Estado consulta={categorias} />}
    <form onSubmit={guardar}>
      <fieldset disabled={bloqueado}>
        <label>Nombre<input name="nombre_producto" minLength="2" required defaultValue={producto?.nombre_producto} /></label>
        <label>Categoría<select name="id_categoria" required value={categoria} onChange={(e) => setCategoria(e.target.value)}>
          <option value="">Elegí una categoría</option>
          {opciones.filter((c) => c.estado || c.id_categoria === producto?.id_categoria).map((c) => <option key={c.id_categoria} value={c.id_categoria}>{c.nombre_categoria}</option>)}
        </select></label>
        <label>Proveedor<select name="id_proveedor" required value={proveedor} onChange={(e) => setProveedor(e.target.value)}>
          <option value="">Elegí un proveedor</option>
          {proveedores.data?.filter((p) => p.estado || p.id_proveedor === producto?.id_proveedor).map((p) => <option key={p.id_proveedor} value={p.id_proveedor}>{p.nombre_proveedor}</option>)}
        </select></label>
        <label>Unidad de medida<input name="unidad_de_medida" placeholder="Ej. unidad" required defaultValue={producto?.unidad_de_medida} /></label>
        <label>Precio de venta<input name="precio_venta" type="number" min="0" step="0.01" required defaultValue={producto?.precio_venta} /></label>
        {(!producto || producto.precio_costo != null) && <label>Precio de costo<input name="precio_costo" type="number" min="0" step="0.01" required defaultValue={producto?.precio_costo} /></label>}
        {!producto && <label>Stock inicial<input name="stock" type="number" min="0" step="1" required defaultValue="0" /></label>}
        <label>Stock mínimo<input name="stock_minimo" type="number" min="0" step="1" required defaultValue={producto?.stock_minimo ?? 0} /></label>
        <div className={styles.barra}>
          <button className={styles.principal} disabled={!proveedores.data || !categorias.data}>{guardado.ocupado ? 'Guardando…' : 'Guardar producto'}</button>
          {cancelar && <button type="button" onClick={cancelar}>Cancelar edición</button>}
        </div>
      </fieldset>
    </form>
    {guardado.error && <p role="alert">{guardado.error}</p>}
    {crearCategoria && <form className={styles.categoria} onSubmit={(e) => { e.preventDefault(); agregarCategoria() }}>
      <label>Nueva categoría<input required value={nombre} onChange={(e) => setNombre(e.target.value)} /></label>
      <button disabled={!nombre.trim() || bloqueado || altaCategoria.incierto}>{altaCategoria.ocupado ? 'Creando…' : 'Crear categoría'}</button>
      {altaCategoria.error && <p role="alert">{altaCategoria.error}</p>}
      {altaCategoria.incierto && <button type="button" onClick={categorias.actualizar}>Actualizar categorías</button>}
    </form>}
  </>
}
