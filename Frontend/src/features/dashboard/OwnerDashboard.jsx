import { useEffect, useState } from 'react'
import { api } from '../../shared/api/client.js'
import styles from './OwnerDashboard.module.css'

import SalesEvolution from './SalesEvolution.jsx'

const periodos = [
  ['hoy', 'Hoy'],
  ['semana', 'Semana'],
  ['mes', 'Mes'],
  ['anio', 'Año'],
]

const moneda = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
})

function Indicador({ titulo, monto, detalle }) {
  return (
    <article className={styles.tarjeta}>
      <h2>{titulo}</h2>
      <strong>{moneda.format(monto)}</strong>
      <p>{detalle}</p>
    </article>
  )
}

export default function OwnerDashboard() {
  const [periodo, setPeriodo] = useState('mes')

  return (
    <section>
      <h1>Resumen financiero</h1>
      <label className={styles.periodo}>
        Período
        <select value={periodo} onChange={(event) => setPeriodo(event.target.value)}>
          {periodos.map(([valor, etiqueta]) => (
            <option key={valor} value={valor}>{etiqueta}</option>
          ))}
        </select>
      </label>
      <ResumenFinanciero periodo={periodo} />
      <SalesEvolution key={periodo} periodo={periodo} />
    </section>
  )
}

function ResumenFinanciero({ periodo }) {
  const [resultado, setResultado] = useState(null)
  const [intento, setIntento] = useState(0)

  const actual = resultado?.periodo === periodo && resultado.intento === intento ? resultado : null
  const resumen = actual?.resumen
  const error = actual?.error

  useEffect(() => {
    const controller = new AbortController()

    async function cargarResumen() {
      try {
        const { data } = await api.get('/finanzas/dashboard', {
          params: { periodo },
          timeout: 30000,
          signal: controller.signal,
        })
        const montos = [
          data?.ventas?.facturacion,
          data?.caja?.saldo_neto,
          data?.caja?.total_entradas,
          data?.caja?.total_salidas,
          data?.clientes?.total_por_cobrar,
        ]

        if (!montos.every(Number.isFinite) || !Number.isInteger(data?.ventas?.cantidad_ventas)) {
          throw new Error('Resumen financiero incompleto')
        }

        if (!controller.signal.aborted) setResultado({ periodo, intento, resumen: data })
      } catch (error) {
        if (controller.signal.aborted) return

        const status = error.response?.status
        if (status === 401) {
          setResultado({ periodo, intento, error: 'Tu sesión ya no es válida. Cerrá sesión y volvé a ingresar.' })
        } else if (status === 403) {
          setResultado({ periodo, intento, error: 'Tu cuenta no tiene acceso al resumen financiero.' })
        } else if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
          setResultado({ periodo, intento, error: 'El resumen financiero tardó demasiado en responder.' })
        } else {
          setResultado({ periodo, intento, error: 'No pudimos cargar el resumen financiero.' })
        }
      }
    }

    cargarResumen()
    return () => controller.abort()
  }, [periodo, intento])

  function reintentar() {
    setResultado(null)
    setIntento((anterior) => anterior + 1)
  }

  return (
    <div aria-busy={!actual}>
      <p role="status" hidden={Boolean(actual)} translate="no">
        <span>Cargando resumen financiero…</span>
      </p>
      {error ? (
        <>
          <p role="alert">{error}</p>
          <button className={styles.reintentar} type="button" onClick={reintentar}>
            Reintentar
          </button>
        </>
      ) : resumen ? (
        <div className={styles.grilla}>
          <Indicador
            titulo="Ventas del período"
            monto={resumen.ventas.facturacion}
            detalle={`Operaciones: ${resumen.ventas.cantidad_ventas}`}
          />
          <Indicador
            titulo="Flujo neto de caja"
            monto={resumen.caja.saldo_neto}
            detalle={`Entradas ${moneda.format(resumen.caja.total_entradas)} · Salidas ${moneda.format(resumen.caja.total_salidas)}`}
          />
          <Indicador
            titulo="Pendiente de cobrar"
            monto={resumen.clientes.total_por_cobrar}
            detalle="Saldo actual de clientes con compras en el período seleccionado."
          />
        </div>
      ) : null}
    </div>
  )
}
