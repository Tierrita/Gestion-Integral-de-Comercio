import InfoItem from './InfoItem.jsx'

const items = [
  { slug: 'quienes-somos', Icon: () => <span aria-hidden="true">▣</span>, title: 'Quiénes somos', description: 'AIOnix es una plataforma de gestión integral para kioscos y comercios minoristas.' },
  { slug: 'nuestro-objetivo', Icon: () => <span aria-hidden="true">◈</span>, title: 'Nuestro objetivo', description: 'Simplificar tus operaciones, registrar ventas y compras y ayudarte a tomar mejores decisiones.' },
  { slug: 'que-gestionamos', Icon: () => <span aria-hidden="true">▤</span>, title: 'Qué gestionamos', description: 'Productos, inventario, movimientos de stock, proveedores y resultados del comercio.' },
  { slug: 'contacto', Icon: () => <span aria-hidden="true">✉</span>, title: 'Contacto', description: 'Un espacio pensado para acompañar la administración diaria de tu negocio.' },
]

export default function BrandPanel({ activeSection, onSelectSection }) {
  return <section className="aionix-brand" aria-label="Presentación de AIOnix">
    <div className="aionix-brand-inner">
      <div className="aionix-brand-logo"><span className="aionix-brand-mark">ai</span><span>AIOnix</span></div>
      <div className="aionix-brand-items">{items.map(({ slug, Icon, title, description }) =>
        <InfoItem key={slug} Icon={Icon} title={title} description={description}
          active={activeSection === slug} onClick={() => onSelectSection(slug)} />
      )}</div>
    </div>
  </section>
}
