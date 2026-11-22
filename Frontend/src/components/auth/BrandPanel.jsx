import { Store, ChartNoAxesCombined, Boxes, Headset } from 'lucide-react'

const items = [
  { Icon: Store, title: 'Quiénes somos', description: 'AIOnix es una plataforma de gestión integral para kioscos y comercios minoristas.' },
  { Icon: ChartNoAxesCombined, title: 'Nuestro objetivo', description: 'Simplificar tus operaciones, registrar ventas y compras y ayudarte a tomar mejores decisiones.' },
  { Icon: Boxes, title: 'Qué gestionamos', description: 'Productos, inventario, movimientos de stock, proveedores y resultados del comercio.' },
  { Icon: Headset, title: 'Contacto', description: 'Un espacio pensado para acompañar la administración diaria de tu negocio.' },
]

function InfoItem({ Icon, title, description }) {
  return <article className="aionix-info-item">
    <span className="aionix-info-icon" aria-hidden="true"><Icon size={32} strokeWidth={2} /></span>
    <div><h2>{title}</h2><p>{description}</p></div>
  </article>
}

export default function BrandPanel() {
  return <section className="aionix-brand" aria-label="Presentación de AIOnix">
    <div className="aionix-brand-inner">
      <div className="aionix-brand-logo"><span className="aionix-brand-mark">ai</span><span>AIOnix</span></div>
      <div className="aionix-brand-items">{items.map(({ Icon, title, description }) =>
        <InfoItem key={title} Icon={Icon} title={title} description={description} />
      )}</div>
    </div>
  </section>
}
