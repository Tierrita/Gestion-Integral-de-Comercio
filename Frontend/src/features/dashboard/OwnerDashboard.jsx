import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../shared/api/client.js'
import styles from './OwnerDashboard.module.css'

const moneda = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 })
const numero = new Intl.NumberFormat('es-AR')
const periodos = [
  { value: 'hoy', label: 'Hoy' },
  { value: 'semana', label: 'Semana' },
  { value: 'mes', label: 'Mes' },
  { value: 'anio', label: 'Año' },
]

function valorMoneda(value) {
  return Number.isFinite(value) ? moneda.format(value) : 'No disponible'
}

function valorNumero(value) {
  return Number.isFinite(value) ? numero.format(value) : 'No disponible'
}

function Tarjeta({ titulo, valor, detalle, acento = false }) {
  return (
    <article className={`${styles.tarjeta} ${acento ? styles.destacada : ''}`}>
      <p className={styles.etiqueta}>{titulo}</p>
      <strong className={styles.valor}>{valor}</strong>
      <p className={styles.detalle}>{detalle}</p>
    </article>
  )
}

function Ranking({ titulo, dato, campo }) {
  const nombre = dato?.nombre_producto ?? dato?.nombre_completo ?? dato?.nombre_cliente ?? dato?.nombre_proveedor ?? dato?.nombre ?? null
  return (
    <article className={styles.ranking}>
      <span className={styles.etiqueta}>{titulo}</span>
      <strong>{nombre || 'Sin datos para este período'}</strong>
      {nombre && Number.isFinite(dato?.[campo]) && <small>{valorMoneda(dato[campo])}</small>}
    </article>
  )
}

function mensajeError(error) {
  if (error.response?.status === 401) return 'Tu sesión venció. Cerrá sesión y volvé a ingresar.'
  if (error.response?.status === 403) return 'No tenés permisos para consultar las estadísticas.'
  if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') return 'La consulta tardó demasiado en responder.'
  if (error.response?.status === 400) return 'El período seleccionado no es válido.'
  return 'No pudimos cargar las estadísticas. Comprobá la conexión con el servidor.'
}

export default function OwnerDashboard() {
  const [periodo, setPeriodo] = useState('mes')
  const [intento, setIntento] = useState(0)
  const [resumen, setResumen] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    async function cargar() {
      setCargando(true)
      setError('')
      setResumen(null)
      try {
        const { data } = await api.get('/finanzas/dashboard', {
          params: { periodo },
          signal: controller.signal,
          timeout: 30000,
        })
        if (!data || typeof data !== 'object' || !data.ventas || !data.caja || !data.clientes) {
          throw new Error('Respuesta financiera incompleta')
        }
        if (!controller.signal.aborted) setResumen(data)
      } catch (err) {
        if (!controller.signal.aborted) setError(mensajeError(err))
      } finally {
        if (!controller.signal.aborted) setCargando(false)
      }
    }
    cargar()
    return () => controller.abort()
  }, [periodo, intento])

  const ventas = resumen?.ventas
  const rentabilidad = resumen?.rentabilidad
  const caja = resumen?.caja
  const clientes = resumen?.clientes
  const proveedores = resumen?.proveedores
  const stock = resumen?.stock
  const rankings = resumen?.rankings

  return (
    <section className={styles.pagina} aria-labelledby="titulo-dashboard">
      <header className={styles.cabecera}>
        <div>
          <span className={styles.sobretitulo}>CENTRO DE OPERACIONES</span>
          <h1 id="titulo-dashboard">Panel de control</h1>
          <p>Una visión integral de la actividad de tu comercio.</p>
        </div>
        <button type="button" className={styles.actualizar} onClick={() => setIntento((n) => n + 1)} disabled={cargando}>
          ↻ Actualizar datos
        </button>
      </header>

      <div className={styles.barraPeriodos} aria-label="Filtrar estadísticas por período">
        {periodos.map((item) => (
          <button
            type="button"
            key={item.value}
            className={`${styles.periodo} ${periodo === item.value ? styles.periodoActivo : ''}`}
            onClick={() => setPeriodo(item.value)}
            aria-pressed={periodo === item.value}
          >
            {item.label}
          </button>
        ))}
      </div>

      {cargando && <div className={styles.estado} role="status">Cargando indicadores del comercio…</div>}
      {!cargando && error && (
        <div className={styles.estado} role="alert">
          <p>{error}</p>
          <button type="button" className={styles.actualizar} onClick={() => setIntento((n) => n + 1)}>Reintentar</button>
        </div>
      )}

      {!cargando && resumen && (
        <>
          <div className={styles.grilla}>
            <Tarjeta titulo="Facturación" valor={valorMoneda(ventas?.facturacion)} detalle={`${valorNumero(ventas?.cantidad_ventas)} ventas en el período`} acento />
            <Tarjeta titulo="Ganancia bruta" valor={rentabilidad?.rentabilidad_calculable === true ? valorMoneda(rentabilidad.ganancia_bruta) : 'No disponible'} detalle={rentabilidad?.rentabilidad_calculable === true ? 'Ventas menos costo de mercadería vendida' : 'Faltan costos históricos para calcularla'} />
            <Tarjeta titulo="Flujo neto de caja" valor={valorMoneda(caja?.saldo_neto)} detalle="Entradas menos salidas del período; no es el saldo disponible" />
            <Tarjeta titulo="Cuentas por cobrar" valor={valorMoneda(clientes?.total_por_cobrar)} detalle={`${valorNumero(clientes?.cantidad_clientes_con_deuda)} clientes con deuda · saldo actual`} />
            <Tarjeta titulo="Ticket promedio" valor={valorMoneda(ventas?.ticket_promedio)} detalle={`${valorNumero(ventas?.unidades_vendidas)} unidades vendidas`} />
            <Tarjeta titulo="Margen bruto" valor={rentabilidad?.rentabilidad_calculable === true && Number.isFinite(rentabilidad?.margen_bruto) ? `${numero.format(rentabilidad.margen_bruto)} %` : 'No disponible'} detalle="Margen sobre ventas; no equivale a utilidad neta" />
          </div>

          <div className={styles.columnas}>
            <section className={styles.panel} aria-labelledby="titulo-caja">
              <h2 id="titulo-caja">Movimiento financiero</h2>
              <div className={styles.fila}><span>Entradas del período</span><strong>{valorMoneda(caja?.total_entradas)}</strong></div>
              <div className={styles.fila}><span>Salidas del período</span><strong>{valorMoneda(caja?.total_salidas)}</strong></div>
              <div className={styles.fila}><span>Compras del período</span><strong>{valorMoneda(proveedores?.total_comprado)}</strong></div>
              <div className={styles.fila}><span>Deuda con proveedores (actual)</span><strong>{valorMoneda(proveedores?.deuda_total_proveedores)}</strong></div>
            </section>
            <section className={styles.panel} aria-labelledby="titulo-stock">
              <h2 id="titulo-stock">Inventario valorizado</h2>
              <div className={styles.fila}><span>Unidades en stock</span><strong>{valorNumero(stock?.unidades_en_stock)}</strong></div>
              <div className={styles.fila}><span>Valor a costo</span><strong>{valorMoneda(stock?.valor_stock_costo)}</strong></div>
              <div className={styles.fila}><span>Valor a precio de venta</span><strong>{valorMoneda(stock?.valor_stock_venta)}</strong></div>
              <div className={styles.fila}><span>Ganancia potencial estimada</span><strong>{valorMoneda(stock?.ganancia_potencial)}</strong></div>
            </section>
          </div>

          <section className={styles.panel} aria-labelledby="titulo-rankings">
            <h2 id="titulo-rankings">Destacados del período</h2>
            <div className={styles.rankingGrid}>
              <Ranking titulo="Producto más vendido" dato={rankings?.producto_mas_vendido} campo="facturacion" />
              <Ranking titulo="Mejor cliente" dato={rankings?.mejor_cliente} campo="facturacion" />
              <Ranking titulo="Principal proveedor" dato={rankings?.principal_proveedor} campo="total_comprado" />
            </div>
          </section>

          <section className={styles.panel} aria-labelledby="titulo-accesos">
            <h2 id="titulo-accesos">Accesos rápidos</h2>
            <nav className={styles.accesos} aria-label="Accesos rápidos">
              <Link to="/ventas">Ventas <span aria-hidden="true">↗</span></Link>
              <Link to="/compras">Compras <span aria-hidden="true">↗</span></Link>
              <Link to="/productos">Mercadería <span aria-hidden="true">↗</span></Link>
              <Link to="/clientes">Clientes <span aria-hidden="true">↗</span></Link>
            </nav>
          </section>
        </>
      )}
    </section>
  )
}
