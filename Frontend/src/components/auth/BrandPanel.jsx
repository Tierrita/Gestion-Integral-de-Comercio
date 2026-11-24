import InfoItem from './InfoItem.jsx'

function LineIcon({ kind }) {
  const paths = {
    about: <><rect x="4" y="4" width="16" height="16" rx="3" /><path d="M8 9h8M8 13h8M8 17h5" /></>,
    goal: <><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5" /><circle cx="12" cy="12" r="1" /></>,
    management: <><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /></>,
    contact: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m4 7 8 6 8-6" /></>,
  }
  return <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[kind]}</svg>
}

const items = [
  { slug: 'quienes-somos', kind: 'about', title: 'Quiénes somos', description: 'AIOnix es una plataforma de gestión integral para kioscos y comercios minoristas.' },
  { slug: 'nuestro-objetivo', kind: 'goal', title: 'Nuestro objetivo', description: 'Simplificar tus operaciones, registrar ventas y compras y ayudarte a tomar mejores decisiones.' },
  { slug: 'que-gestionamos', kind: 'management', title: 'Qué gestionamos', description: 'Productos, inventario, movimientos de stock, proveedores y resultados del comercio.' },
  { slug: 'contacto', kind: 'contact', title: 'Contacto', description: 'Un espacio pensado para acompañar la administración diaria de tu negocio.' },
]

export default function BrandPanel({ activeSection, onSelectSection }) {
  return <section className="aionix-brand" aria-label="Presentación de AIOnix">
    <div className="aionix-brand-inner">
      <div className="aionix-brand-header">
        <div className="aionix-brand-logo"><span className="aionix-brand-mark">ai</span><span>AIOnix</span></div>
        <p className="aionix-brand-tagline">Gestión inteligente para tu comercio</p>
      </div>
      <div className="aionix-brand-items">{items.map(({ slug, kind, title, description }) =>
        <InfoItem key={slug} Icon={() => <LineIcon kind={kind} />} title={title} description={description}
          active={activeSection === slug} onClick={() => onSelectSection(slug)} />
      )}</div>
    </div>
  </section>
}
