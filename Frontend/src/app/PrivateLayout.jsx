import { NavLink, Outlet } from 'react-router-dom'
import { tienePermiso } from '../shared/auth/permisos.js'
import styles from './PrivateLayout.module.css'

export default function PrivateLayout({ profile, onLogout }) {
  const { usuario, comercio } = profile

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <strong>Gestión Integral de Comercio</strong>
        <nav aria-label="Navegación principal">
          <NavLink to="/inicio" end>Inicio</NavLink>
          {(tienePermiso(profile, 'productos.ver') || tienePermiso(profile, 'stock.ver')) && (
            <div className={styles.grupoStock} role="group" aria-labelledby="menu-stock">
              <span id="menu-stock" className={styles.grupo}>Stock</span>
              {tienePermiso(profile, 'productos.ver') && <NavLink to="/stock/productos">Productos</NavLink>}
              {tienePermiso(profile, 'stock.ver') && <>
                <NavLink to="/stock/existencias">Existencias</NavLink>
                <NavLink to="/stock/alertas">Alertas</NavLink>
                <NavLink to="/stock/historial">Historial</NavLink>
              </>}
            </div>
          )}
          {(tienePermiso(profile, 'compras.ver') || tienePermiso(profile, 'compras.registrar')) &&
            <NavLink to={tienePermiso(profile, 'compras.ver') ? '/compras' : '/compras/nueva'}>Compras</NavLink>}
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