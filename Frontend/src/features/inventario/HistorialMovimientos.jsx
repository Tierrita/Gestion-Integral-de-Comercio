
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import styles from './Inventario.module.css'
import h from './HistorialMovimientos.module.css'
import MercaderiaNav from '../productos/MercaderiaNav.jsx'
import ActionButton from '../../shared/components/ActionButton.jsx'
import Modal from '../../shared/components/Modal.jsx'

const TIME_ZONE = 'America/Argentina/Buenos_Aires'

const dateFormatter = new Intl.DateTimeFormat('es-AR', {
  timeZone: TIME_ZONE,
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
})

const dayFormatter = new Intl.DateTimeFormat('en-CA', {
  timeZone: TIME_ZONE,
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
})

const quantityFormatter = new Intl.NumberFormat('es-AR', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 3,
})

const stamp = (row) =>
  row.fecha_movimiento ?? row.fecha ?? row.created_at ?? ''

function formatDate(value) {
  if (!value) return '—'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return String(value)

  return dateFormatter.format(date).replace(',', ' ·')
}

function localDay(value) {
  if (!value) return ''

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return ''

  const parts = dayFormatter.formatToParts(date)

  const year = parts.find((part) => part.type === 'year')?.value
  const month = parts.find((part) => part.type === 'month')?.value
  const day = parts.find((part) => part.type === 'day')?.value

  return year && month && day ? `${year}-${month}-${day}` : ''
}

function signedChange(row) {
  if (row.stock_anterior == null || row.stock_nuevo == null) {
    return null
  }

  const before = Number(row.stock_anterior)
  const after = Number(row.stock_nuevo)

  if (!Number.isFinite(before) || !Number.isFinite(after)) {
    return null
  }

  return Math.round((after - before) * 1000) / 1000
}

function formatQuantity(value) {
  if (value == null || value === '') return '—'

  const number = Number(value)

  return Number.isFinite(number)
    ? quantityFormatter.format(number)
    : String(value)
}

function formatChange(value) {
  if (value == null) return '—'

  return `${value > 0 ? '+' : ''}${formatQuantity(value)}`
}

function responsibleLabel(row) {
  return row.nombre_responsable ||
    (row.id_usuario == null
      ? 'Sin identificar'
      : 'Usuario sin nombre disponible')
}

function commercialNotes(value) {
  if (value == null || String(value).trim() === '') return 'Sin observaciones'
  // El ID global se conserva en la base de datos para auditoría interna.
  return String(value)
    .replace(/\s*\(\s*ID\s+global\s*#?\s*\d+\s*\)/gi, '')
    .trim()
}

function movementLabel(value) {
  return String(value ?? 'SIN TIPO').replaceAll('_', ' ')
}

function exportCell(value) {
  const text = String(value ?? '')

  // Evita que Excel interprete contenido externo como una fórmula.
  const safe = /^[\s]*[=+\-@\t\r]/.test(text)
    ? `'${text}`
    : text

  return `"${safe.replaceAll('"', '""')}"`
}

export default function HistorialMovimientos() {
  const [rows, setRows] = useState([])
  const [products, setProducts] = useState([])

  const [productId, setProductId] = useState('')
  const [type, setType] = useState('')
  const [direction, setDirection] = useState('')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [userId, setUserId] = useState('')

  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [refresh, setRefresh] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function load() {
      try {
        const [history, stock] = await Promise.all([
          api.get('/stock/historial', {
            signal: controller.signal,
          }),
          api.get('/stock', {
            signal: controller.signal,
          }),
        ])

        if (
          !Array.isArray(history.data) ||
          !Array.isArray(stock.data)
        ) {
          throw new Error('Formato inesperado')
        }

        if (controller.signal.aborted) return

        setRows(history.data)
        setProducts(stock.data)
        setError('')
      } catch (err) {
        if (controller.signal.aborted) return

        setError(
          err.response?.data?.error ||
          'No se pudo consultar el historial. Revisá la conexión con Flask.'
        )
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    void load()

    return () => controller.abort()
  }, [refresh])

  const filtered = useMemo(() => {
    return rows
      .filter((row) => {
        const day = localDay(stamp(row))
        const change = signedChange(row)

        return (
          (!productId || String(row.id_producto) === productId) &&
          (!type || row.tipo_movimiento === type) &&
          (!userId || String(row.id_usuario ?? '') === userId) &&
          (!from || (day && day >= from)) &&
          (!to || (day && day <= to)) &&
          (!direction ||
            (direction === 'entrada'
              ? change !== null && change > 0
              : change !== null && change < 0))
        )
      })
      .sort(
        (a, b) =>
          (Date.parse(stamp(b)) || 0) -
          (Date.parse(stamp(a)) || 0)
      )
  }, [rows, productId, type, direction, from, to, userId])

  const types = useMemo(
    () =>
      [...new Set(
        rows.map((row) => row.tipo_movimiento).filter(Boolean)
      )].sort(),
    [rows]
  )

  const users = useMemo(
    () =>
      [...new Set(
        rows.map((row) => row.id_usuario).filter((id) => id != null)
      )].sort((a, b) => Number(a) - Number(b)),
    [rows]
  )

  const entries = filtered.filter((row) => signedChange(row) > 0).length
  const exits = filtered.filter((row) => signedChange(row) < 0).length

  const hasFilters = Boolean(
    productId || type || direction || from || to || userId
  )

  function clearFilters() {
    setProductId('')
    setType('')
    setDirection('')
    setFrom('')
    setTo('')
    setUserId('')
  }

  function reload() {
    setLoading(true)
    setRefresh((current) => current + 1)
  }

  function exportCsv() {
    const header = [
      'Fecha',
      'Producto',
      'Tipo',
      'Variación',
      'Cantidad registrada',
      'Stock anterior',
      'Stock nuevo',
      'Responsable',
      'Observaciones',
    ]

    const data = filtered.map((row) => [
      formatDate(stamp(row)),
      row.nombre_producto,
      movementLabel(row.tipo_movimiento),
      signedChange(row),
      row.cantidad,
      row.stock_anterior,
      row.stock_nuevo,
      responsibleLabel(row),
      commercialNotes(row.observaciones),
    ])

    const csv =
      '\uFEFF' +
      [header, ...data]
        .map((line) => line.map(exportCell).join(';'))
        .join('\r\n')

    const url = URL.createObjectURL(
      new Blob([csv], { type: 'text/csv;charset=utf-8' })
    )

    const anchor = document.createElement('a')

    anchor.href = url
    anchor.download = 'historial-inventario.csv'

    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()

    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  return (
    <section className={styles.page}>
      <MercaderiaNav />

      <header className={styles.heading}>
        <div>
          <p className={styles.eyebrow}>INVENTARIO / AUDITORÍA</p>
          <h1>Historial de movimientos</h1>
          <p className={styles.muted}>
            Trazabilidad de compras, ventas, anulaciones y ajustes de stock.
          </p>
        </div>

        <div className={h.headerActions}>
          <ActionButton as={Link} to="/inventario">
            ← Volver a inventario
          </ActionButton>

          <ActionButton
            type="button"
            variant="secondary"
            disabled={loading}
            onClick={reload}
          >
            ↻ Actualizar
          </ActionButton>

          <ActionButton
            type="button"
            variant="primary"
            disabled={loading || !filtered.length || Boolean(error)}
            onClick={exportCsv}
          >
            Exportar CSV
          </ActionButton>
        </div>
      </header>

      <div className={h.metrics}>
        <div>
          <span>Movimientos encontrados</span>
          <strong>{loading ? '—' : filtered.length}</strong>
        </div>

        <div>
          <span>Entradas de stock</span>
          <strong className={h.positive}>
            {loading ? '—' : entries}
          </strong>
        </div>

        <div>
          <span>Salidas de stock</span>
          <strong className={h.negative}>
            {loading ? '—' : exits}
          </strong>
        </div>
      </div>

      <section className={styles.panel}>
        <div className={h.filters}>
          <label>
            Producto
            <select
              value={productId}
              onChange={(event) => setProductId(event.target.value)}
            >
              <option value="">Todos los productos</option>
              {products.map((product) => (
                <option
                  key={product.id_producto}
                  value={String(product.id_producto)}
                >
                  {product.nombre_producto}
                </option>
              ))}
            </select>
          </label>

          <label>
            Tipo
            <select
              value={type}
              onChange={(event) => setType(event.target.value)}
            >
              <option value="">Todos los tipos</option>
              {types.map((item) => (
                <option key={item} value={item}>
                  {movementLabel(item)}
                </option>
              ))}
            </select>
          </label>

          <label>
            Dirección
            <select
              value={direction}
              onChange={(event) => setDirection(event.target.value)}
            >
              <option value="">Entradas y salidas</option>
              <option value="entrada">Solo entradas (+)</option>
              <option value="salida">Solo salidas (−)</option>
            </select>
          </label>

          <label>
            Desde
            <input
              type="date"
              value={from}
              max={to || undefined}
              onChange={(event) => setFrom(event.target.value)}
            />
          </label>

          <label>
            Hasta
            <input
              type="date"
              value={to}
              min={from || undefined}
              onChange={(event) => setTo(event.target.value)}
            />
          </label>

          <label>
            Usuario
            <select
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
            >
              <option value="">Todos los usuarios</option>
              {users.map((id) => (
                <option key={id} value={String(id)}>
                  {responsibleLabel(
                    rows.find((row) => row.id_usuario === id) ||
                    { id_usuario: id }
                  )}
                </option>
              ))}
            </select>
          </label>

          {hasFilters && (
            <ActionButton
              type="button"
              variant="secondary"
              onClick={clearFilters}
            >
              Limpiar filtros
            </ActionButton>
          )}
        </div>

        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}

        {loading ? (
          <p className={styles.empty}>Consultando movimientos…</p>
        ) : error ? (
          <p className={styles.empty}>
            No se pudo actualizar el historial.
          </p>
        ) : !filtered.length ? (
          <p className={styles.empty}>
            No hay movimientos que coincidan con los filtros.
          </p>
        ) : (
          <div className={styles.scroll}>
            <table className={h.table}>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Producto</th>
                  <th>Movimiento</th>
                  <th className={h.numeric}>Cambio</th>
                  <th className={h.numeric}>Stock anterior</th>
                  <th className={h.numeric}>Stock nuevo</th>
                  <th>Responsable</th>
                  <th>Detalle</th>
                </tr>
              </thead>

              <tbody>
                {filtered.map((row, index) => {
                  const change = signedChange(row)

                  const tone =
                    change > 0
                      ? h.positive
                      : change < 0
                        ? h.negative
                        : ''

                  const badge =
                    change > 0
                      ? h.entryBadge
                      : change < 0
                        ? h.exitBadge
                        : h.neutralBadge

                  return (
                    <tr key={row.id_movimiento ?? index}>
                      <td className={h.dateCell}>
                        {formatDate(stamp(row))}
                      </td>

                      <td className={h.productCell}>
                        <strong>
                          {row.nombre_producto ?? 'Producto sin nombre'}
                        </strong>
                        <small>
                          {row.numero_producto != null ? `N.º ${row.numero_producto}` : ''}
                        </small>
                      </td>

                      <td>
                        <span className={badge}>
                          {movementLabel(row.tipo_movimiento)}
                        </span>
                      </td>

                      <td className={`${h.numeric} ${tone}`}>
                        <strong>
                          {change === null
                            ? formatQuantity(row.cantidad)
                            : formatChange(change)}
                        </strong>
                      </td>

                      <td className={h.numeric}>
                        {formatQuantity(row.stock_anterior)}
                      </td>

                      <td className={h.numeric}>
                        {formatQuantity(row.stock_nuevo)}
                      </td>

                      <td className={h.responsibleCell}>
                        {responsibleLabel(row)}
                      </td>

                      <td>
                        <ActionButton
                          type="button"
                          size="compact"
                          onClick={() => setSelected(row)}
                        >
                          Ver detalle
                        </ActionButton>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        {!loading && !error && (
          <p className={h.footer}>
            Mostrando {filtered.length} de {rows.length} movimientos.
            Los filtros también se aplican al archivo CSV.
          </p>
        )}
      </section>

      <Modal
        open={Boolean(selected)}
        onClose={() => setSelected(null)}
        title="Detalle del movimiento"
        size="large"
      >
        {selected && (
            <dl className={h.detailGrid}>
              <div>
                <dt>Producto</dt>
                <dd>
                  {selected.nombre_producto ?? 'Producto sin nombre'}
                </dd>
              </div>

              <div>
                <dt>Fecha</dt>
                <dd>{formatDate(stamp(selected))}</dd>
              </div>

              <div>
                <dt>Operación</dt>
                <dd>{movementLabel(selected.tipo_movimiento)}</dd>
              </div>

              <div>
                <dt>Responsable</dt>
                <dd>
                  {responsibleLabel(selected)}
                </dd>
              </div>

              <div>
                <dt>Cantidad registrada</dt>
                <dd>{formatQuantity(selected.cantidad)}</dd>
              </div>

              <div>
                <dt>Variación real</dt>
                <dd>{formatChange(signedChange(selected))}</dd>
              </div>

              <div>
                <dt>Stock anterior</dt>
                <dd>{formatQuantity(selected.stock_anterior)}</dd>
              </div>

              <div>
                <dt>Stock nuevo</dt>
                <dd>{formatQuantity(selected.stock_nuevo)}</dd>
              </div>

              <div className={h.fullWidth}>
                <dt>Observaciones</dt>
                <dd className={h.notes}>
                  {commercialNotes(selected.observaciones)}
                </dd>
              </div>
            </dl>
        )}
      </Modal>
    </section>
  )
}
