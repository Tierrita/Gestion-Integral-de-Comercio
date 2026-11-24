import styles from './Clientes.module.css'

const TYPES = [['PARTICULAR', 'Particular'], ['COMERCIO', 'Comercio'], ['EMPRESA', 'Empresa'], ['INSTITUCION', 'Institución']]
const DOCUMENTS = [['', 'Sin especificar'], ['DNI', 'DNI'], ['CUIT', 'CUIT'], ['CUIL', 'CUIL'], ['PASAPORTE', 'Pasaporte'], ['OTRO', 'Otro']]

export default function ClienteForm({ form, setForm, isGeneral }) {
  const update = (key) => (event) => setForm((prev) => ({ ...prev, [key]: event.target.value }))
  const field = (key, label, props = {}) => <label key={key}>{label}<input value={form[key]} onChange={update(key)} {...props} /></label>
  return <div className={styles.formSections}>
    <fieldset className={styles.formSection}>
      <legend>Identificación</legend>
      <div className={styles.formGrid}>
        <label>Tipo de cliente<select value={form.tipo_cliente} onChange={update('tipo_cliente')}>{TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        {field('nombre_completo', 'Nombre o razón social *', { required: true, minLength: 2, maxLength: 150, disabled: isGeneral, autoComplete: 'name' })}
        {form.tipo_cliente !== 'PARTICULAR' && field('nombre_comercial', 'Nombre comercial', { maxLength: 150 })}
      </div>
    </fieldset>
    <fieldset className={styles.formSection}>
      <legend>Información fiscal</legend>
      <div className={styles.formGrid}>
        <label>Tipo de documento<select value={form.tipo_documento} onChange={update('tipo_documento')}>{DOCUMENTS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
        {field('numero_documento', 'Número de documento', { maxLength: 30 })}
        {field('condicion_iva', 'Condición frente al IVA', { maxLength: 50, placeholder: 'Ej.: Responsable inscripto' })}
      </div>
    </fieldset>
    <fieldset className={styles.formSection}>
      <legend>Contacto</legend>
      <div className={styles.formGrid}>
        {field('telefono', 'Teléfono', { type: 'tel', maxLength: 50, autoComplete: 'tel' })}
        {field('whatsapp', 'WhatsApp', { type: 'tel', maxLength: 50 })}
        {field('email', 'Correo electrónico', { type: 'email', maxLength: 254, autoComplete: 'email' })}
      </div>
    </fieldset>
    <fieldset className={styles.formSection}>
      <legend>Domicilio y entrega</legend>
      <div className={styles.formGrid}>
        {field('direccion', 'Dirección', { maxLength: 200, autoComplete: 'street-address' })}
        {field('localidad', 'Localidad', { maxLength: 100, autoComplete: 'address-level2' })}
        {field('provincia', 'Provincia', { maxLength: 100, autoComplete: 'address-level1' })}
        {field('codigo_postal', 'Código postal', { maxLength: 20, autoComplete: 'postal-code' })}
        <label className={styles.fullWidth}>Referencias de entrega<textarea value={form.referencia_entrega} onChange={update('referencia_entrega')} maxLength={2000} rows={2} /></label>
      </div>
    </fieldset>
    <fieldset className={styles.formSection}>
      <legend>Información adicional</legend>
      <label>Observaciones<textarea value={form.observaciones} onChange={update('observaciones')} maxLength={2000} rows={3} /></label>
    </fieldset>
  </div>
}
