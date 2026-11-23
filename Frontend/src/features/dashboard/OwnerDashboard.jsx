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

// Los períodos del backend usan fechas de Argentina y un límite superior inclusivo en la respuesta.
function completarIntervalos(puntos, agrupacion, rango) {
  const mapa = new Map(puntos.map((p) => [String(p.periodo), Number(p.facturacion)]))
  const desde = rango?.desde
  const hasta = rango?.hasta
  if (!desde || !hasta) return puntos.map((p) => ({ etiqueta: String(p.periodo), valor: Number(p.facturacion) }))
  const fechas = []
  if (agrupacion === 'hora') {
    for (let h = 0; h < 24; h += 1) fechas.push(`${String(h).padStart(2, '0')}:00`)
  } else if (agrupacion === 'mes') {
    const inicio = Number(desde.slice(0, 4))
    const fin = Number(hasta.slice(0, 4))
    for (let anio = inicio; anio <= fin && fechas.length < 24; anio += 1) {
      const primerMes = anio === inicio ? Number(desde.slice(5, 7)) : 1
      const ultimoMes = anio === fin ? Number(hasta.slice(5, 7)) : 12
      for (let mes = primerMes; mes <= ultimoMes; mes += 1) fechas.push(`${anio}-${String(mes).padStart(2, '0')}`)
    }
  } else {
    const inicio = new Date(`${desde}T12:00:00Z`)
    const fin = new Date(`${hasta}T12:00:00Z`)
    for (let dia = new Date(inicio); dia <= fin && fechas.length < 366; dia.setUTCDate(dia.getUTCDate() + 1)) {
      fechas.push(dia.toISOString().slice(0, 10))
    }
  }
  return fechas.map((etiqueta) => ({ etiqueta, valor: mapa.get(etiqueta) ?? 0 }))
}

function GraficoVentas({ puntos, agrupacion, rango }) {
  const datos = completarIntervalos(puntos, agrupacion, rango)
    .filter((p) => Number.isFinite(p.valor) && p.valor >= 0)
  if (!datos.length) return <p className={styles.detalle}>No hay intervalos para este período.</p>

  const [seleccion, setSeleccion] = useState(null)
  const ancho = 760
  const alto = 238
  const izquierda = 78
  const derecha = 20
  const arriba = 22
  const abajo = 42
  const maximo = Math.max(1, ...datos.map((p) => p.valor))
  const rangoX = ancho - izquierda - derecha
  const rangoY = alto - arriba - abajo
  const x = (i) => izquierda + (datos.length === 1 ? rangoX / 2 : (i / (datos.length - 1)) * rangoX)
  const y = (valor) => arriba + rangoY * (1 - valor / maximo)
  const linea = datos.map((p, i) => `${i === 0 ? 'M' : 'L'} ${x(i).toFixed(1)} ${y(p.valor).toFixed(1)}`).join(' ')
  const area = `${linea} L ${x(datos.length - 1)} ${y(0)} L ${x(0)} ${y(0)} Z`
  const marcas = [...new Set([0, Math.floor((datos.length - 1) / 2), datos.length - 1])] 
  const abreviar = (etiqueta) => {
    if (agrupacion === 'hora') return etiqueta
    if (agrupacion === 'mes') return new Intl.DateTimeFormat('es-AR', { month: 'short', timeZone: 'UTC' }).format(new Date(`${etiqueta}-01T12:00:00Z`))
    return new Intl.DateTimeFormat('es-AR', { day: '2-digit', month: 'short', timeZone: 'UTC' }).format(new Date(`${etiqueta}T12:00:00Z`))
  }
  const total = datos.reduce((s, p) => s + p.valor, 0)
  const activos = datos.filter((p) => p.valor > 0).length
  const mayor = Math.max(...datos.map((p) => p.valor))
  return (
    <div className={styles.graficoContenedor}>
      <div className={styles.resumenGrafico}>
        <div><span className={styles.etiqueta}>Facturación del período</span><strong>{valorMoneda(total)}</strong></div>
        <div><span className={styles.etiqueta}>Intervalos con ventas</span><strong>{activos} de {datos.length}</strong></div>
        <div><span className={styles.etiqueta}>Pico de facturación</span><strong>{valorMoneda(mayor)}</strong></div>
      </div>
      <div className={styles.detalleInteractivo} role="status" aria-live="polite">{seleccion === null ? 'Seleccioná un punto para ver el detalle' : `${abreviar(datos[seleccion].etiqueta)} · ${valorMoneda(datos[seleccion].valor)}`}</div>
      <svg className={styles.grafico} viewBox={`0 0 ${ancho} ${alto}`} role="img"
        aria-label={`Evolución de facturación por ${agrupacion || 'período'}: ${datos.length} intervalos, ${activos} con ventas`}>
        <defs>
          <linearGradient id="dashboard-area-ventas" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--color-primary)" stopOpacity="0.3" />
            <stop offset="100%" stopColor="var(--color-primary)" stopOpacity="0.01" />
          </linearGradient>
        </defs>
        {[0, 0.5, 1].map((nivel) => (
          <g key={nivel}>
            <line x1={izquierda} x2={ancho - derecha} y1={y(maximo * nivel)} y2={y(maximo * nivel)} className={styles.lineaGuia} />
            <text x={izquierda - 10} y={y(maximo * nivel) + 4} textAnchor="end" className={styles.etiquetaEje}>
              {numero.format(Math.round(maximo * nivel))}
            </text>
          </g>
        ))}
        <path d={area} fill="url(#dashboard-area-ventas)" />
        <path d={linea} className={styles.lineaVentas} />
        {datos.map((p, i) => (
          <circle key={p.etiqueta} cx={x(i)} cy={y(p.valor)} r={seleccion === i ? 6 : p.valor > 0 ? 4 : 2.5} className={styles.puntoVentas} onMouseEnter={() => setSeleccion(i)} onFocus={() => setSeleccion(i)} onClick={() => setSeleccion(i)} tabIndex={0} role="button" aria-label={`${abreviar(p.etiqueta)}: ${valorMoneda(p.valor)}`}>
            <title>{`${p.etiqueta}: ${valorMoneda(p.valor)}`}</title>
          </circle>
        ))}
        {marcas.map((i) => (
          <text key={i} x={x(i)} y={alto - 14} textAnchor="middle" className={styles.etiquetaEje}>{abreviar(datos[i].etiqueta)}</text>
        ))}
      </svg>
      <p className={styles.detalle}>Facturación en ARS · Se muestran también los intervalos sin ventas, con valor cero. Pasá el cursor o seleccioná un punto para consultar su importe.</p>
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

          <div className={styles.zonaAnalitica}>
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
              <GraficoVentas puntos={evolucion.evolucion} agrupacion={evolucion.agrupacion} rango={evolucion.periodo} />
            )}
          </section>

            <aside className={styles.panel} aria-labelledby="titulo-pulso">
              <span className={styles.sobretitulo}>ANÁLISIS COMERCIAL</span>
              <h2 id="titulo-pulso">Pulso del negocio</h2>
              <p className={styles.detalle}>Indicadores actuales para tomar decisiones.</p>
              <div className={styles.pulsoFila}><span>Ticket promedio</span><strong>{valorMoneda(ventas?.ticket_promedio)}</strong></div>
              <div className={styles.pulsoFila}><span>Unidades vendidas</span><strong>{valorNumero(ventas?.unidades_vendidas)}</strong></div>
              <div className={styles.pulsoFila}><span>Clientes con deuda</span><strong>{valorNumero(clientes?.cantidad_clientes_con_deuda)}</strong></div>
              <div className={styles.pulsoFila}><span>Deuda a cobrar</span><strong>{valorMoneda(clientes?.total_por_cobrar)}</strong></div>
              <Link className={styles.pulsoAcceso} to="/clientes">Ver clientes ↗</Link>
            </aside>
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
