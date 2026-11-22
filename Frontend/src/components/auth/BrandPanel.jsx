import { Store, ChartNoAxesCombined, Boxes, Headset } from 'lucide-react'
import InfoItem from './InfoItem.jsx'

const items = [
  { slug: 'quienes-somos', Icon: Store, title: 'Quiénes somos', description: 'AIOnix es una plataforma de gestión integral para kioscos y comercios minoristas.' },
  { slug: 'nuestro-objetivo', Icon: ChartNoAxesCombined, title: 'Nuestro objetivo', description: 'Simplificar tus operaciones, registrar ventas y compras y ayudarte a tomar mejores decisiones.' },
  { slug: 'que-gestionamos', Icon: Boxes, title: 'Qué gestionamos', description: 'Productos, inventario, movimientos de stock, proveedores y resultados del comercio.' },
  { slug: 'contacto', Icon: Headset, title: 'Contacto', description: 'Un espacio pensado para acompañar la administración diaria de tu negocio.' },
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
