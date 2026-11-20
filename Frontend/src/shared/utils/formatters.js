// Formatos compartidos de presentación. No alteran valores enviados al backend.
const monedaARS = new Intl.NumberFormat('es-AR', {
  style: 'currency',
  currency: 'ARS',
})

const fechaHoraAR = new Intl.DateTimeFormat('es-AR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
})

export function formatoMoneda(valor) {
  const numero = Number(valor)
  return monedaARS.format(Number.isFinite(numero) ? numero : 0)
}

export function formatoFechaHora(valor) {
  if (valor === null || valor === undefined || valor === '') return '—'
  const fecha = valor instanceof Date ? valor : new Date(valor)
  return Number.isNaN(fecha.getTime()) ? '—' : fechaHoraAR.format(fecha)
}
