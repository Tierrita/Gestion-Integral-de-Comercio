
import { useEffect, useMemo, useState } from 'react'
import tableStyles from '../../shared/components/CommerceTable.module.css'
import StockAdjustmentFields, { validStockQuantity } from '../../shared/components/StockAdjustmentFields.jsx'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import MercaderiaNav from '../productos/MercaderiaNav.jsx'
import ActionButton from '../../shared/components/ActionButton.jsx'
import Modal from '../../shared/components/Modal.jsx'
import Alert from '../../shared/components/Alert.jsx'
import styles from './Inventario.module.css'

const errorText = (error) =>
  error.response?.data?.error ||
  (error.response?.status === 403
    ? 'Tu usuario no tiene permiso para realizar esta operación.'
    : 'No se pudo conectar con el servidor Flask.')

const classify = (product) => {
  if (product.estado === false) return 'inactivo'

  return Number(product.stock) <= Number(product.stock_minimo)
    ? 'alerta'
    : 'normal'
}

const isKg = (product) => product.unidad_de_medida === 'KG'

const formatQuantity = (value, unit = 'UNIDAD') => {
  const number = Number(value)

  if (!Number.isFinite(number)) return '—'

  return new Intl.NumberFormat('es-AR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: unit === 'KG' ? 3 : 0,
  }).format(number)
}

const unitLabel = (unit) => unit === 'KG' ? 'kg' : 'un.'


export default function Inventario() {
  const [searchParams] = useSearchParams()
  const selectedProductId = searchParams.get('producto')
  const [items, setItems] = useState([])
  const [alerts, setAlerts] = useState([])
  const [categories, setCategories] = useState([])

  const [category, setCategory] = useState('todas')
  const [categoryError, setCategoryError] = useState('')
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('todos')

  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [notice, setNotice] = useState('')

  const [selected, setSelected] = useState(null)
  const [adjustType, setAdjustType] = useState('AUMENTAR')
  const [amount, setAmount] = useState('')
  const [adjustError, setAdjustError] = useState('')
  const [saving, setSaving] = useState(false)

  async function reload() {
    setLoading(true)
    setLoadError('')

    try {
      const [stockResult, alertResult, categoryResult] =
        await Promise.allSettled([
          api.get('/stock'),
          api.get('/stock/alertas'),
          api.get('/categorias'),
        ])

      if (
        stockResult.status === 'fulfilled' &&
        Array.isArray(stockResult.value.data)
      ) {
        setItems(stockResult.value.data)
      } else {
        setItems([])
        setLoadError(
          stockResult.status === 'rejected'
            ? errorText(stockResult.reason)
            : 'Flask devolvió un listado de stock inválido.'
        )
      }

      if (
        alertResult.status === 'fulfilled' &&
        Array.isArray(alertResult.value.data)
      ) {
        setAlerts(alertResult.value.data)
      } else {
        setAlerts([])
        setLoadError((previous) =>
          [
            previous,
            'No se pudieron consultar las alertas de stock.',
          ].filter(Boolean).join(' ')
        )
      }

      if (
        categoryResult.status === 'fulfilled' &&
        Array.isArray(categoryResult.value.data)
      ) {
        setCategories(categoryResult.value.data)
        setCategoryError('')
      } else {
        setCategories([])
        setCategory('todas')
        setCategoryError(
          'No se pudieron consultar las categorías. El filtro por categoría no está disponible.'
        )
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      void reload()
    }, 0)

    return () => clearTimeout(timer)
  }, [])

  const visible = useMemo(() => {
    const query = search.trim().toLocaleLowerCase('es-AR')

    return items.filter((product) => {
      const matchesSelectedProduct = !selectedProductId || String(product.id_producto) === selectedProductId
      const matchesSearch = [
        product.nombre_producto,
        product.numero_producto,
        product.id_producto,
      ].some((value) =>
        String(value ?? '')
          .toLocaleLowerCase('es-AR')
          .includes(query)
      )

      const matchesCategory =
        category === 'todas' ||
        String(product.id_categoria) === category

      const matchesSituation =
        filter === 'todos' ||
        classify(product) === filter

      return matchesSelectedProduct && matchesSearch && matchesCategory && matchesSituation
    })
  }, [items, search, category, filter, selectedProductId])

  const activeCount = items.filter(
    (product) => product.estado !== false
  ).length

  const zeroCount = items.filter(
    (product) =>
      product.estado !== false &&
      Number(product.stock) === 0
  ).length

  function openAdjustment(product) {
    setSelected(product)
    setAdjustType('AUMENTAR')
    setAmount('')
    setAdjustError('')
    setNotice('')
  }

  function closeAdjustment() {
    if (saving) return

    setSelected(null)
    setAmount('')
    setAdjustError('')
  }

  const quantity = Number(amount)

  async function submit(event) {
    event.preventDefault()

    if (!selected || saving) return

    if (!validQuantity(amount, selected.unidad_de_medida)) {
      setAdjustError(
        isKg(selected)
          ? 'Ingresá una cantidad mayor a cero, con un máximo de 3 decimales.'
          : 'Ingresá una cantidad entera mayor a cero.'
      )
      return
    }

    if (
      adjustType === 'DISMINUIR' &&
      quantity > Number(selected.stock)
    ) {
      setAdjustError(
        'No podés retirar más stock del disponible.'
      )
      return
    }

    setSaving(true)
    setAdjustError('')

    try {
      const { data } = await api.patch(
        `/stock/${selected.id_producto}/ajustar`,
        {
          cantidad: quantity,
          tipo_ajuste: adjustType,
        }
      )

      const productName = selected.nombre_producto
      const unit = selected.unidad_de_medida

      const previousStock = data.data?.stock_anterior
      const newStock = data.data?.stock_nuevo

      setSelected(null)

      const detail =
        previousStock != null && newStock != null
          ? ` ${productName}: ${formatQuantity(previousStock, unit)} → ${formatQuantity(newStock, unit)} ${unitLabel(unit)}`
          : ` ${productName}.`

      setNotice(
        `${data.message || 'Stock actualizado correctamente.'}${detail}`
      )

      await reload()
    } catch (error) {
      setAdjustError(errorText(error))
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className={styles.page}>
      <MercaderiaNav />

      <header className={styles.heading}>
        <div>
          <p className={styles.eyebrow}>
            CONTROL DE EXISTENCIAS
          </p>

          <h1>Inventario</h1>

          <p className={styles.muted}>
            Consultá existencias, detectá faltantes y registrá ajustes manuales.
          </p>
        </div>

        <div className={styles.headingActions}>
          <ActionButton as={Link} to="/inventario/historial">
            Ver historial
          </ActionButton>

          <ActionButton
            variant="secondary"
            type="button"
            disabled={loading}
            onClick={() => void reload()}
          >
            ↻ Actualizar
          </ActionButton>
        </div>
      </header>

      <div className={styles.metrics}>
        <div>
          <span>Productos registrados</span>
          <strong>{items.length}</strong>
        </div>

        <div>
          <span>Productos activos</span>
          <strong>{activeCount}</strong>
        </div>

        <div>
          <span>Alertas de stock</span>
          <strong>{alerts.length}</strong>
        </div>

        <div>
          <span>Activos sin stock</span>
          <strong>{zeroCount}</strong>
        </div>
      </div>

      {notice && (
        <p className={styles.success} role="status">
          {notice}
        </p>
      )}

      {loadError && (
        <p className={styles.error} role="alert">
          {loadError}
        </p>
      )}

      {categoryError && (
        <p className={styles.error} role="alert">
          {categoryError}
        </p>
      )}

      <section className={styles.panel}>
        <div className={styles.toolbar}>
          <label>
            Buscar producto
            <input
              type="search"
              placeholder="Nombre o número"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
            />
          </label>

          <label>
            Categoría
            <select
              value={category}
              disabled={Boolean(categoryError)}
              onChange={(event) =>
                setCategory(event.target.value)
              }
            >
              <option value="todas">
                Todas las categorías
              </option>

              {categories.map((item) => (
                <option
                  key={item.id_categoria}
                  value={String(item.id_categoria)}
                >
                  {item.nombre_categoria}
                </option>
              ))}
            </select>
          </label>

          <label>
            Situación
            <select
              value={filter}
              onChange={(event) =>
                setFilter(event.target.value)
              }
            >
              <option value="todos">Todos</option>
              <option value="normal">Stock normal</option>
              <option value="alerta">Stock bajo / mínimo</option>
              <option value="inactivo">Inactivos</option>
            </select>
          </label>
        </div>

        {selectedProductId && (
          <p className={styles.muted}>
            Mostrando el inventario del producto seleccionado.{' '}
            <Link to="/inventario">Ver todos los productos</Link>
          </p>
        )}

        <div className={styles.tableInfo}>
          <span>
            {loading
              ? 'Actualizando inventario…'
              : `${visible.length} de ${items.length} productos`}
          </span>
        </div>

        {loading ? (
          <p className={styles.empty}>
            Cargando inventario…
          </p>
        ) : loadError && !items.length ? (
          <p className={styles.empty}>
            No se pudo cargar el inventario.
          </p>
        ) : !visible.length ? (
          <p className={styles.empty}>
            No hay productos que coincidan con los filtros.
          </p>
        ) : (
          <div className={`${styles.scroll} ${tableStyles.scroll}`}>
            <table className={tableStyles.table}>
              <thead>
                <tr>
                  <th>N.º</th>
                  <th>Producto</th>
                  <th className={styles.numeric}>Existencias</th>
                  <th className={styles.numeric}>Mínimo</th>
                  <th>Situación</th>
                  <th>Acción</th>
                </tr>
              </thead>

              <tbody>
                {visible.map((product) => {
                  const situation = classify(product)
                  const unit = product.unidad_de_medida

                  return (
                    <tr key={product.id_producto}>
                      <td className={styles.productNumber}>
                        #{product.numero_producto ?? product.id_producto}
                      </td>

                      <td className={styles.productCell}>
                        <strong>
                          {product.nombre_producto}
                        </strong>
                        <small>{unitLabel(unit)}</small>
                      </td>

                      <td className={styles.numeric}>
                        <span
                          className={
                            situation === 'alerta'
                              ? styles.quantityAlert
                              : styles.quantity
                          }
                        >
                          {formatQuantity(product.stock, unit)}
                        </span>
                      </td>

                      <td className={styles.numeric}>
                        {formatQuantity(product.stock_minimo, unit)}
                      </td>

                      <td>
                        <span
                          className={
                            situation === 'alerta'
                              ? styles.alert
                              : situation === 'inactivo'
                                ? tableStyles.inactive
                                : styles.ok
                          }
                        >
                          {situation === 'alerta'
                            ? 'Stock bajo'
                            : situation === 'inactivo'
                              ? 'Inactivo'
                              : 'Normal'}
                        </span>
                      </td>

                      <td>
                        <ActionButton
                          size="compact"
                          type="button"
                          disabled={product.estado === false}
                          onClick={() => openAdjustment(product)}
                        >
                          Ajustar stock
                        </ActionButton>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <Modal
        open={Boolean(selected)}
        onClose={closeAdjustment}
        title="Ajustar stock"
        description="Movimiento manual"
        busy={saving}
        size="medium"
      >
        {selected && (
          <>
            <p>
              <strong>{selected.nombre_producto}</strong>
            </p>

            <StockAdjustmentFields unit={selected.unidad_de_medida} currentStock={selected.stock} type={adjustType} onTypeChange={(value) => { setAdjustType(value); setAdjustError('') }} amount={amount} onAmountChange={(value) => { setAmount(value); setAdjustError('') }} onSubmit={submit} onCancel={closeAdjustment} saving={saving} error={adjustError} />
          </>
        )}
      </Modal>
    </section>
  )
}
