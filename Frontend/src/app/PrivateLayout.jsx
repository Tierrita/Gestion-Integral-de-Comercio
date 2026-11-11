import { NavLink, Outlet } from 'react-router-dom'
import styles from './PrivateLayout.module.css'

export default function PrivateLayout({ profile, onLogout }) {  const { usuario, comercio } = profile

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <strong>Gestión Integral de Comercio</strong>
        <nav aria-label="Navegación principal">
          <NavLink to="/inicio" end>Inicio</NavLink>
          <NavLink to="/perfil" end>Mi perfil</NavLink>
        </nav>
      </aside>

      <div className={styles.workspace}>
        <header className={styles.header}>
          <strong>{comercio.nombre_comercio}</strong>
          <span>{usuario.nombre_completo || usuario.email}</span>
        <button className={styles.logout} type="button" onClick={onLogout}>
        Cerrar sesión
        </button>
        </header>

        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}