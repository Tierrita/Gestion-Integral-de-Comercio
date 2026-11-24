import AboutSection from './sections/AboutSection.jsx'
import GoalSection from './sections/GoalSection.jsx'
import ManagementSection from './sections/ManagementSection.jsx'
import ContactSection from './sections/ContactSection.jsx'

const sections = {
  'quienes-somos': { title: 'Quiénes somos', Component: AboutSection },
  'nuestro-objetivo': { title: 'Nuestro objetivo', Component: GoalSection },
  'que-gestionamos': { title: 'Qué gestionamos', Component: ManagementSection },
  contacto: { title: 'Contacto', Component: ContactSection },
}

export default function SectionView({ section, onBack }) {
  const entry = sections[section]
  if (!entry) return null
  const { title, Component } = entry
  return <section className="aionix-section-card" aria-labelledby="aionix-section-title">
    <button type="button" className="aionix-back-button" onClick={onBack}><span aria-hidden="true">←</span> Volver al inicio de sesión</button>
    <h1 id="aionix-section-title">{title}</h1>
    <Component />
  </section>
}
