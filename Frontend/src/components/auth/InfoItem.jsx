export default function InfoItem({ Icon, title, description, active, onClick }) {
  return <article className="aionix-info-item">
    <button type="button" className="aionix-info-icon aionix-info-button" onClick={onClick}
      aria-label={`Ver información: ${title}`} aria-pressed={active} title={`Conocer más: ${title}`}>
      <Icon size={32} strokeWidth={2} aria-hidden="true" />
    </button>
    <div><h2>{title}</h2><p>{description}</p></div>
  </article>
}
