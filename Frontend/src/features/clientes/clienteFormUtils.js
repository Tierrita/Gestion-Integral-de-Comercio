export const EMPTY_CLIENT = {
  nombre_completo: '', telefono: '', tipo_cliente: 'PARTICULAR', nombre_comercial: '',
  tipo_documento: '', numero_documento: '', condicion_iva: '', email: '', whatsapp: '',
  direccion: '', localidad: '', provincia: '', codigo_postal: '',
  referencia_entrega: '', observaciones: '',
}

export function clientToForm(client) {
  return Object.fromEntries(Object.entries(EMPTY_CLIENT).map(([key, fallback]) => [key, client?.[key] ?? fallback]))
}

export function clientPayload(form, isGeneral = false) {
  return Object.fromEntries(Object.entries(form)
    .filter(([key]) => !(isGeneral && key === 'nombre_completo'))
    .map(([key, value]) => [key, typeof value === 'string' ? value.trim() || (key === 'tipo_cliente' ? 'PARTICULAR' : null) : value]))
}
