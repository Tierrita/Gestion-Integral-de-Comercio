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

function GraficoVentas({ puntos, agrupacion }) {
  const datos = puntos.map((p) => ({ etiqueta: String(p.periodo), valor: Number(p.facturacion) }))
    .filter((p) => Number.isFinite(p.valor) && p.valor >= 0)
  if (!datos.length) return <p className={styles.detalle}>No hay ventas registradas para este período.</p>

  const ancho = 760
  const alto = 240
  const izquierda = 72
  const derecha = 18
  const arriba = 16
  const abajo = 45
  const maximo = Math.max(1, ...datos.map((p) => p.valor))
  const rangoX = ancho - izquierda - derecha
  const rangoY = alto - arriba - abajo
  const x = (i) => izquierda + (datos.length === 1 ? rangoX / 2 : (i / (datos.length - 1)) * rangoX)
  const y = (valor) => arriba + rangoY * (1 - valor / maximo)
  const linea = datos.map((p, i) => `${i === 0 ? 'M' : 'L'} ${x(i).toFixed(1)} ${y(p.valor).toFixed(1)}`).join(' ')
  const marcas = [...new Set([0, Math.floor((datos.length - 1) / 2), datos.length - 1])]
  return (
    <div className={styles.graficoContenedor}>
      <svg className={styles.grafico} viewBox={`0 0 ${ancho} ${alto}`} role="img"
        aria-label={`Evolución de facturación por ${agrupacion || 'período'}: ${datos.length} puntos`}>
        {[0, 0.5, 1].map((nivel) => (
          <g key={nivel}>
            <line x1={izquierda} x2={ancho - derecha} y1={y(maximo * nivel)} y2={y(maximo * nivel)} className={styles.lineaGuia} />
            <text x={izquierda - 10} y={y(maximo * nivel) + 4} textAnchor="end" className={styles.etiquetaEje}>
              {numero.format(Math.round(maximo * nivel))}
            </text>
          </g>
        ))}
        <path d={linea} className={styles.lineaVentas} />
        {datos.map((p, i) => (
          <circle key={`${p.etiqueta}-${i}`} cx={x(i)} cy={y(p.valor)} r="3.5" className={styles.puntoVentas}>
            <title>{`${p.etiqueta}: ${valorMoneda(p.valor)}`}</title>
          </circle>
        ))}
        {marcas.map((i) => (
          <text key={i} x={x(i)} y={alto - 14} textAnchor="middle" className={styles.etiquetaEje}>{datos[i].etiqueta}</text>
        ))}
      </svg>
      <p className={styles.detalle}>Facturación en ARS · {datos.length} intervalos con ventas. Los intervalos sin ventas no se representan.</p>
    </div>
  )
}

export default function OwnerDashboard() {
  const [periodo, setPeriodo] = useState('mes')
  const [intento, setIntento] = useState(0)
  const [resumen, setResumen] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [evolucion, setEvolucion] = useState(null)
  const [errorEvolucion, setErrorEvolucion] = useState('')
  const [cargandoEvolucion, setCargandoEvolucion] = useState(true)

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

  useEffect(() => {
    const controller = new AbortController()
    async function cargarEvolucion() {
      setCargandoEvolucion(true)
      setErrorEvolucion('')
      setEvolucion(null)
      try {
        const { data } = await api.get('/finanzas/ventas/evolucion', {
          params: { periodo },
          signal: controller.signal,
          timeout: 30000,
        })
        if (!Array.isArray(data?.ventas?.evolucion)) throw new Error('Respuesta de evolución inválida')
        if (!controller.signal.aborted) setEvolucion(data.ventas)
      } catch (err) {
        if (!controller.signal.aborted) setErrorEvolucion(mensajeError(err))
      } finally {
        if (!controller.signal.aborted) setCargandoEvolucion(false)
      }
    }
    cargarEvolucion()
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

          <section className={styles.panel} aria-labelledby="titulo-evolucion">
            <h2 id="titulo-evolucion">Evolución de ventas</h2>
            {cargandoEvolucion && <p role="status">Cargando evolución de ventas…</p>}
            {!cargandoEvolucion && errorEvolucion && (
              <div role="alert">
                <p>{errorEvolucion}</p>
                <button type="button" className={styles.actualizar} onClick={() => setIntento((n) => n + 1)}>Reintentar</button>
              </div>
            )}
            {!cargandoEvolucion && evolucion && (
              <GraficoVentas puntos={evolucion.evolucion} agrupacion={evolucion.agrupacion} />
            )}
          </section>

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
