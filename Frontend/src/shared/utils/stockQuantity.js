export const formatStockQuantity = (value, unit) => new Intl.NumberFormat('es-AR', { maximumFractionDigits: unit === 'KG' ? 3 : 0 }).format(Number(value ?? 0))

export function parseStockQuantity(value) {
  const normalized = String(value ?? '').trim().replace(',', '.')
  if (!/^[0-9]+([.][0-9]+)?$/.test(normalized)) return null
  const number = Number(normalized)
  return Number.isFinite(number) ? number : null
}

export function validStockQuantity(value, unit) {
  const number = parseStockQuantity(value)
  if (number === null || number <= 0) return false
  if (unit === 'KG') return Number.isSafeInteger(Math.round(number * 1000)) && Math.abs(number * 1000 - Math.round(number * 1000)) < 1e-7
  return unit === 'UNIDAD' && Number.isSafeInteger(number)
}

