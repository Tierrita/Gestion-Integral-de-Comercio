import { useEffect, useState } from 'react'
import { api } from '../../shared/api/client.js'
import styles from './OwnerDashboard.module.css'

const moneda = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
})

const agrupaciones = { hora: 'Hora', dia: 'Día', mes: 'Mes' }

export default function SalesEvolution({ periodo }) {
  const [serie, setSerie] = useState(null)
  const [error, setError] = useState(false)
  const [intento, setIntento] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function cargarEvolucion() {
      try {
        const { data: respuesta } = await api.get('/finanzas/ventas/evolucion', {
          params: { periodo },
          signal: controller.signal,
        })

        if (controller.signal.aborted) return

        const data = respuesta?.ventas

        if (!Array.isArray(data?.evolucion) || !data.evolucion.every(
          (punto) => typeof punto?.periodo === 'string' && Number.isFinite(punto.facturacion),
        )) {
          throw new Error('Serie de ventas incompleta')
        }

        setSerie(data)
      } catch {
        if (!controller.signal.aborted) setError(true)
      }
    }

    cargarEvolucion()
    return () => controller.abort()
  }, [periodo, intento])

  const maximo = Math.max(1, ...(serie?.evolucion ?? []).map(
    ({ facturacion }) => Math.abs(facturacion),
  ))

  return (
    <section className={styles.evolucion}>
      <h2>Evolución de ventas</h2>
      {error && (
        <>
          <p role="alert">No pudimos cargar la evolución de ventas.</p>
          <button className={styles.reintentar} type="button" onClick={() => {
            setError(false)
            setIntento((anterior) => anterior + 1)
          }}>
            Reintentar
          </button>
        </>
      )}
      {!error && !serie && <p role="status">Cargando evolución de ventas…</p>}
      {serie?.evolucion.length === 0 && <p>No hay ventas registradas para este período.</p>}
      {serie?.evolucion.length > 0 && (
        <>
          <p>{agrupaciones[serie.agrupacion] ?? 'Período'} · Facturación en pesos</p>
          <ul className={styles.barras}>
            {serie.evolucion.map(({ periodo: etiqueta, facturacion }) => (
              <li key={etiqueta}>
                <div className={styles.etiquetaBarra}>
                  <span>{etiqueta}</span>
                  <strong>{moneda.format(facturacion)}</strong>
                </div>
                <div className={styles.pista} aria-hidden="true">
                  <div
                    className={facturacion < 0 ? styles.barraNegativa : styles.barra}
                    style={{ width: `${Math.abs(facturacion) / maximo * 100}%` }}
                  />
                </div>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}
