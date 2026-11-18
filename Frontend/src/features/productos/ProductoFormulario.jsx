
import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import styles from './ProductoFormulario.module.css'

const initial = {
  nombre_producto: '',
  precio_costo: '',
  precio_venta: '',
  id_categoria: '',
  id_proveedor: '',
  unidad_de_medida: 'UNIDAD',
  stock: '0',
  stock_minimo: '0',
}

const errorMessage = (error) =>
  error.response?.data?.error ||
  (error.response?.status === 403
    ? 'No tenés permiso para realizar esta operación.'
    : 'No se pudo conectar con Flask.')

const list = (data) => (Array.isArray(data) ? data : [])

const isValidQuantity = (value, unit) => {
  if (value === '' || value === null || value === undefined) {
    return false
  }

  const number = Number(value)

  if (!Number.isFinite(number) || number < 0) {
    return false
  }

  if (unit === 'UNIDAD') {
    return Number.isSafeInteger(number)
  }

  if (unit === 'KG') {
    return Number.isSafeInteger(Math.round(number * 1000)) &&
      Math.abs(number * 1000 - Math.round(number * 1000)) < 1e-7
  }

  return false
}

function Field({ label, children, hint }) {
  return (
    <label className={styles.field}>
      <span>{label}</span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  )
}

function Section({ number, title, description, children }) {
  return (
    <section className={styles.section}>
      <header className={styles.sectionHeader}>
        <span className={styles.number}>{number}</span>

        <div>
          <h2>{title}</h2>
          {description && <p>{description}</p>}
        </div>
      </header>

      {children}
    </section>
  )
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
      setLoading(true)
      setError('')
      setCatalogError('')

      const results = await Promise.allSettled([
        api.get('/categorias', {
          signal: controller.signal,
        }),
        api.get('/proveedores', {
          signal: controller.signal,
        }),
        ...(editing
          ? [
              api.get(`/productos/${id}`, {
                signal: controller.signal,
              }),
            ]
          : []),
      ])

      if (controller.signal.aborted) return

      const [categoryResult, supplierResult, detailResult] = results

      if (categoryResult.status === 'fulfilled') {
        setCategories(list(categoryResult.value.data))
      } else {
        setCategories([])
      }

      if (supplierResult.status === 'fulfilled') {
        setSuppliers(list(supplierResult.value.data))
      } else {
        setSuppliers([])
      }

      if (
        categoryResult.status === 'rejected' ||
        supplierResult.status === 'rejected'
      ) {
        setCatalogError(
          'No pudimos cargar categorías o proveedores. Revisá tus permisos y la conexión con Flask.'
        )
      }

      if (editing) {
        if (detailResult.status === 'rejected') {
          setError(errorMessage(detailResult.reason))
          setOriginal(null)
        } else {
          const product = detailResult.value.data

          setOriginal(product)

          setForm({
            nombre_producto: product.nombre_producto ?? '',
            precio_costo:
              product.precio_costo == null
                ? ''
                : String(product.precio_costo),
            precio_venta: String(product.precio_venta ?? ''),
            id_categoria: String(product.id_categoria ?? ''),
            id_proveedor: String(product.id_proveedor ?? ''),
            unidad_de_medida:
              product.unidad_de_medida ?? 'UNIDAD',
            stock: String(product.stock ?? 0),
            stock_minimo: String(product.stock_minimo ?? 0),
          })
        }
      } else {
        setOriginal(null)
        setForm(initial)
      }

      setLoading(false)
    }

    void load()

    return () => controller.abort()
  }, [editing, id])

  const categoryOptions = categories.filter(
    (category) =>
      category.estado !== false ||
      String(category.id_categoria) === form.id_categoria
  )

  const supplierOptions = suppliers.filter(
    (supplier) =>
      supplier.estado !== false ||
      String(supplier.id_proveedor) === form.id_proveedor
  )

  const canSave =
    !loading &&
    !saving &&
    !catalogError &&
    (!editing || Boolean(original)) &&
    categoryOptions.length > 0 &&
    supplierOptions.length > 0

  const isKg = form.unidad_de_medida === 'KG'
  const quantityStep = isKg ? '0.001' : '1'

  function change(event) {
    const { name, value } = event.target

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }))

    if (error) setError('')
  }

  function changeUnit(event) {
    const unit = event.target.value

    setForm((previous) => ({
      ...previous,
      unidad_de_medida: unit,
      stock: '0',
      stock_minimo: '0',
    }))

    setError('')
  }

  async function submit(event) {
    event.preventDefault()

    if (!canSave) return

    setError('')

    const name = form.nombre_producto.trim()
    const unit = form.unidad_de_medida

    if (name.length < 2) {
      setError('El nombre del producto debe tener al menos 2 caracteres.')
      return
    }

    if (!['UNIDAD', 'KG'].includes(unit)) {
      setError('Seleccioná una unidad de medida válida.')
      return
    }

    if (
      !categoryOptions.some(
        (category) =>
          String(category.id_categoria) === form.id_categoria
      )
    ) {
      setError('Seleccioná una categoría válida.')
      return
    }

    if (
      !supplierOptions.some(
        (supplier) =>
          String(supplier.id_proveedor) === form.id_proveedor
      )
    ) {
      setError('Seleccioná un proveedor válido.')
      return
    }

    if (!isValidQuantity(form.stock_minimo, unit)) {
      setError(
        unit === 'KG'
          ? 'El stock mínimo debe ser mayor o igual a cero y tener como máximo 3 decimales.'
          : 'El stock mínimo debe ser un número entero mayor o igual a cero.'
      )
      return
    }

    if (!editing && !isValidQuantity(form.stock, unit)) {
      setError(
        unit === 'KG'
          ? 'El stock inicial debe ser mayor o igual a cero y tener como máximo 3 decimales.'
          : 'El stock inicial debe ser un número entero mayor o igual a cero.'
      )
      return
    }

    if (
      form.precio_venta.trim() === '' ||
      !Number.isFinite(Number(form.precio_venta)) ||
      Number(form.precio_venta) < 0
    ) {
      setError('Ingresá un precio de venta válido.')
      return
    }

    if (
      (!editing || original?.precio_costo != null) &&
      (
        form.precio_costo.trim() === '' ||
        !Number.isFinite(Number(form.precio_costo)) ||
        Number(form.precio_costo) < 0
      )
    ) {
      setError('Ingresá un precio de costo válido.')
      return
    }

    const payload = {
      nombre_producto: name,
      precio_venta: Number(form.precio_venta),
      id_categoria: Number(form.id_categoria),
      id_proveedor: Number(form.id_proveedor),
      unidad_de_medida: unit,
      stock_minimo: Number(form.stock_minimo),
    }

    if (!editing) {
      payload.precio_costo = Number(form.precio_costo)
      payload.stock = Number(form.stock)
    } else if (
      original.precio_costo != null &&
      Number(form.precio_costo) !== Number(original.precio_costo)
    ) {
      payload.precio_costo = Number(form.precio_costo)
    }

    setSaving(true)

    try {
      const { data } = editing
        ? await api.patch(`/productos/${id}`, payload)
        : await api.post('/productos', payload)

      navigate('/productos', {
        replace: true,
        state: {
          notice:
            data.message ||
            'Producto guardado correctamente.',
        },
      })
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.top}>
        <div>
          <p className={styles.breadcrumb}>
            <Link to="/productos">Mercadería</Link>
            {' / '}
            {editing ? 'Editar producto' : 'Nuevo producto'}
          </p>

          <h1>
            {editing
              ? 'Editar producto'
              : 'Agregar nuevo producto'}
          </h1>

          <p className={styles.muted}>
            Completá la información comercial del producto.
          </p>
        </div>

        <Link className={styles.back} to="/productos">
          ← Volver al catálogo
        </Link>
      </div>

      {loading ? (
        <p role="status">Cargando formulario…</p>
      ) : (
        <form onSubmit={submit} className={styles.form}>
          {catalogError && (
            <p className={styles.error} role="alert">
              {catalogError}
            </p>
          )}

          {error && (
            <p className={styles.error} role="alert">
              {error}
            </p>
          )}

          <Section
            number="1"
            title="Información del producto"
            description="Datos generales y clasificación"
          >
            <div className={styles.grid}>
              <Field label="Nombre del producto *">
                <input
                  name="nombre_producto"
                  required
                  minLength={2}
                  value={form.nombre_producto}
                  onChange={change}
                  placeholder="Ej. Coca-Cola 500 ml"
                />
              </Field>

              <Field label="Categoría *">
                <select
                  name="id_categoria"
                  required
                  value={form.id_categoria}
                  onChange={change}
                >
                  <option value="">
                    Seleccionar categoría
                  </option>

                  {categoryOptions.map((category) => (
                    <option
                      key={category.id_categoria}
                      value={category.id_categoria}
                    >
                      {category.nombre_categoria}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Proveedor *">
                <select
                  name="id_proveedor"
                  required
                  value={form.id_proveedor}
                  onChange={change}
                >
                  <option value="">
                    Seleccionar proveedor
                  </option>

                  {supplierOptions.map((supplier) => (
                    <option
                      key={supplier.id_proveedor}
                      value={supplier.id_proveedor}
                    >
                      {supplier.nombre_proveedor}
                    </option>
                  ))}
                </select>
              </Field>

              <Field
                label="Unidad de medida *"
                hint={
                  editing
                    ? 'La unidad no puede modificarse después de crear el producto.'
                    : 'Seleccioná cómo se contabilizará el stock.'
                }
              >
                <select
                  name="unidad_de_medida"
                  required
                  value={form.unidad_de_medida}
                  onChange={changeUnit}
                  disabled={editing}
                >
                  <option value="UNIDAD">Unidad</option>
                  <option value="KG">Kilogramo (kg)</option>
                </select>
              </Field>
            </div>
          </Section>

          <Section
            number="2"
            title="Stock"
            description={
              editing
                ? 'El stock actual se modifica desde Inventario.'
                : 'Cantidad inicial y umbral para alertas'
            }
          >
            <div className={styles.grid}>
              {!editing && (
                <Field
                  label="Stock inicial *"
                  hint={
                    isKg
                      ? 'Permitidos hasta 3 decimales. Ej. 22.500'
                      : 'Ingresá unidades enteras.'
                  }
                >
                  <input
                    type="number"
                    name="stock"
                    min="0"
                    step={quantityStep}
                    required
                    value={form.stock}
                    onChange={change}
                  />
                </Field>
              )}

              <Field
                label="Stock mínimo *"
                hint={
                  isKg
                    ? 'Umbral de alerta en kilogramos.'
                    : 'Umbral de alerta en unidades.'
                }
              >
                <input
                  type="number"
                  name="stock_minimo"
                  min="0"
                  step={quantityStep}
                  required
                  value={form.stock_minimo}
                  onChange={change}
                />
              </Field>

              {editing && (
                <div className={styles.readonly}>
                  <span>Stock actual</span>

                  <strong>
                    {original?.stock ?? '—'}{' '}
                    {original?.unidad_de_medida === 'KG'
                      ? 'kg'
                      : 'unidades'}
                  </strong>

                  <small>
                    Solo lectura. Utilizá el módulo
                    Inventario para ajustarlo.
                  </small>
                </div>
              )}
            </div>
          </Section>

          <Section
            number="3"
            title="Precios"
            description="Importes expresados en pesos argentinos (ARS)"
          >
            <div className={styles.grid}>
              {(!editing ||
                original?.precio_costo != null) && (
                <Field label="Precio de costo *">
                  <input
                    type="number"
                    name="precio_costo"
                    min="0"
                    step="0.01"
                    required={!editing}
                    value={form.precio_costo}
                    onChange={change}
                  />
                </Field>
              )}

              <Field label="Precio de venta *">
                <input
                  type="number"
                  name="precio_venta"
                  min="0"
                  step="0.01"
                  required
                  value={form.precio_venta}
                  onChange={change}
                />
              </Field>
            </div>

            {editing &&
              original?.precio_costo == null && (
                <p className={styles.muted}>
                  Tu usuario no tiene acceso al
                  precio de costo.
                </p>
              )}
          </Section>

          <div className={styles.footer}>
            <Link
              to="/productos"
              className={styles.back}
            >
              Cancelar
            </Link>

            <button
              type="submit"
              disabled={!canSave}
            >
              {saving
                ? 'Guardando…'
                : editing
                  ? 'Guardar cambios'
                  : 'Crear producto'}
            </button>
          </div>
        </form>
      )}
    </div>
  )
}
