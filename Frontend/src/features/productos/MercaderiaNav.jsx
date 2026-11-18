import { NavLink } from 'react-router-dom'
import styles from './MercaderiaNav.module.css'

const tabs = [
  { to: '/productos', label: 'Catálogo', end: true },
  { to: '/inventario', label: 'Existencias y ajustes', end: true },
  { to: '/inventario/historial', label: 'Historial de movimientos', end: true },
]

export default function MercaderiaNav() {
  return <nav className={styles.tabs} aria-label="Secciones de productos e inventario">
    {tabs.map(({ to, label, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => isActive ? styles.active : styles.tab}>{label}</NavLink>)}
  </nav>
}
