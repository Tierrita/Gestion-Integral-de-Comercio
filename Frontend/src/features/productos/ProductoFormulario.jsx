import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import styles from './ProductoFormulario.module.css'

const initial = { nombre_producto: '', precio_costo: '', precio_venta: '', id_categoria: '', id_proveedor: '', unidad_de_medida: 'UNIDAD', stock: '0', stock_minimo: '0' }
const errorMessage = (error) => error.response?.data?.error || (error.response?.status === 403 ? 'No tenés permiso para realizar esta operación.' : 'No se pudo conectar con Flask.')
const list = (data) => Array.isArray(data) ? data : []

function Field({ label, children, hint }) {
  return <label className={styles.field}><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>
}

function Section({ number, title, description, children }) {
  return <section className={styles.section}><header className={styles.sectionHeader}><span className={styles.number}>{number}</span><div><h2>{title}</h2>{description && <p>{description}</p>}</div></header>{children}</section>
}

export default function ProductoFormulario() {
  const { id } = useParams()
  const editing = Boolean(id)
  const navigate = useNavigate()
  const [form, setForm] = useState(initial)
  const [original, setOriginal] = useState(null)
  const [categories, setCategories] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [catalogError, setCatalogError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    async function load() {
      const results = await Promise.allSettled([
        api.get('/categorias', { signal: controller.signal }),
        api.get('/proveedores', { signal: controller.signal }),
        ...(editing ? [api.get('/productos/' + id, { signal: controller.signal })] : []),
      ])
      if (controller.signal.aborted) return
      const [c, p, detail] = results
      if (c.status === 'fulfilled') setCategories(list(c.value.data))
      if (p.status === 'fulfilled') setSuppliers(list(p.value.data))
      if (c.status === 'rejected' || p.status === 'rejected') setCatalogError('No pudimos cargar categorías o proveedores. Revisá tus permisos y la conexión con Flask.')
      if (editing) {
        if (detail.status === 'rejected') setError(errorMessage(detail.reason))
        else {
          const product = detail.value.data
          setOriginal(product)
          setForm({
            nombre_producto: product.nombre_producto ?? '',
            precio_costo: product.precio_costo == null ? '' : String(product.precio_costo),
            precio_venta: String(product.precio_venta ?? ''),
            id_categoria: String(product.id_categoria ?? ''),
            id_proveedor: String(product.id_proveedor ?? ''),
            unidad_de_medida: product.unidad_de_medida ?? 'UNIDAD',
            stock: String(product.stock ?? 0),
            stock_minimo: String(product.stock_minimo ?? 0),
          })
        }
      }
      setLoading(false)
    }
    load()
    return () => controller.abort()
  }, [editing, id])

  const categoryOptions = categories.filter((c) => c.estado !== false || String(c.id_categoria) === form.id_categoria)
  const supplierOptions = suppliers.filter((p) => p.estado !== false || String(p.id_proveedor) === form.id_proveedor)
  const canSave = !loading && !saving && !catalogError && (!editing || original) && categoryOptions.length > 0 && supplierOptions.length > 0

  function change(event) {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  async function submit(event) {
    event.preventDefault()
    if (!canSave) return
    setError('')
    if (!form.nombre_producto.trim() || !form.unidad_de_medida.trim()) {
      setError('Completá el nombre y la unidad de medida.')
      return
    }
    const payload = {
      nombre_producto: form.nombre_producto.trim(),
      precio_venta: Number(form.precio_venta),
      id_categoria: Number(form.id_categoria),
      id_proveedor: Number(form.id_proveedor),
      unidad_de_medida: form.unidad_de_medida.trim(),
      stock_minimo: Number(form.stock_minimo),
    }
    if (!editing) {
      payload.precio_costo = Number(form.precio_costo)
      payload.stock = Number(form.stock)
    } else if (original.precio_costo != null && form.precio_costo !== '' && Number(form.precio_costo) !== Number(original.precio_costo)) {
      payload.precio_costo = Number(form.precio_costo)
    }
    setSaving(true)
    try {
      const { data } = editing ? await api.patch('/productos/' + id, payload) : await api.post('/productos', payload)
      navigate('/productos', { replace: true, state: { notice: data.message || 'Producto guardado correctamente.' } })
    } catch (err) { setError(errorMessage(err)) }
    finally { setSaving(false) }
  }

  return <div className={styles.page}>
    <div className={styles.top}>
      <div><p className={styles.breadcrumb}><Link to="/productos">Productos</Link> / {editing ? 'Editar' : 'Nuevo producto'}</p><h1>{editing ? 'Editar producto' : 'Agregar nuevo producto'}</h1><p className={styles.muted}>Completá la información comercial del producto.</p></div>
      <Link className={styles.back} to="/productos">← Volver al catálogo</Link>
    </div>
    {loading ? <p role="status">Cargando formulario…</p> : <form onSubmit={submit} className={styles.form}>
      {catalogError && <p className={styles.error} role="alert">{catalogError}</p>}
      {error && <p className={styles.error} role="alert">{error}</p>}
      <Section number="1" title="Información del producto" description="Datos generales y clasificación">
        <div className={styles.grid}>
          <Field label="Nombre del producto *"><input name="nombre_producto" required minLength="2" value={form.nombre_producto} onChange={change} placeholder="Ej. Coca-Cola 500 ml" /></Field>
          <Field label="Categoría *"><select name="id_categoria" required value={form.id_categoria} onChange={change}><option value="">Seleccionar categoría</option>{categoryOptions.map((c) => <option key={c.id_categoria} value={c.id_categoria}>{c.nombre_categoria}</option>)}</select></Field>
          <Field label="Proveedor *"><select name="id_proveedor" required value={form.id_proveedor} onChange={change}><option value="">Seleccionar proveedor</option>{supplierOptions.map((p) => <option key={p.id_proveedor} value={p.id_proveedor}>{p.nombre_proveedor}</option>)}</select></Field>
          <Field label="Unidad de medida *" hint="Ej. UNIDAD, KG o LITRO"><input name="unidad_de_medida" required value={form.unidad_de_medida} onChange={change} /></Field>
        </div>
      </Section>
      <Section number="2" title="Stock" description={editing ? 'El stock actual se modifica desde Inventario.' : 'Cantidad inicial y umbral para alertas'}>
        <div className={styles.grid}>
          {!editing && <Field label="Stock inicial *"><input type="number" name="stock" min="0" step="1" required value={form.stock} onChange={change} /></Field>}
          <Field label="Stock mínimo *" hint="Se utiliza para identificar productos con existencias bajas"><input type="number" name="stock_minimo" min="0" step="1" required value={form.stock_minimo} onChange={change} /></Field>
          {editing && <div className={styles.readonly}><span>Stock actual</span><strong>{original?.stock ?? '—'}</strong><small>Solo lectura. Utilizá el módulo Inventario para ajustarlo.</small></div>}
        </div>
      </Section>
      <Section number="3" title="Precios" description="Importes expresados en pesos argentinos (ARS)">
        <div className={styles.grid}>
          {(!editing || original?.precio_costo != null) && <Field label="Precio de costo *"><input type="number" name="precio_costo" min="0" step="0.01" required={!editing} value={form.precio_costo} onChange={change} /></Field>}
          <Field label="Precio de venta *"><input type="number" name="precio_venta" min="0" step="0.01" required value={form.precio_venta} onChange={change} /></Field>
        </div>
        {editing && original?.precio_costo == null && <p className={styles.muted}>Tu usuario no tiene acceso al precio de costo.</p>}
      </Section>
      <div className={styles.footer}><Link to="/productos" className={styles.back}>Cancelar</Link><button type="submit" disabled={!canSave}>{saving ? 'Guardando…' : editing ? 'Guardar cambios' : 'Crear producto'}</button></div>
    </form>}
  </div>
}
