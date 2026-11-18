
import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import styles from './PrivateLayout.module.css'

const THEME_KEY = 'gestion-integral.theme'

function initialTheme() {
  try {
    return localStorage.getItem(THEME_KEY) === 'light' ? 'light' : 'dark'
  } catch {
    return 'dark'
  }
}

export default function PrivateLayout({ profile, onLogout }) {
  const { usuario, comercio } = profile
  const location = useLocation()
  const [theme, setTheme] = useState(initialTheme)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    document.documentElement.dataset.theme = theme

    try {
      localStorage.setItem(THEME_KEY, theme)
    } catch {
      // El tema sigue funcionando si el navegador bloquea el almacenamiento.
    }
  }, [theme])

  const closeMenu = () => setMenuOpen(false)

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar} data-open={menuOpen}>
        <div className={styles.brand}>
          <span className={styles.brandMark} aria-hidden="true">G</span>
          <div>
            <strong>Gestión Integral</strong>
            <small>COMERCIO · V2</small>
          </div>
        </div>

        <div className={styles.navCaption}>ESPACIO DE TRABAJO</div>

        <nav
          className={styles.navigation}
          aria-label="Navegación principal"
        >
          <NavLink
            to="/inicio"
            end
            onClick={closeMenu}
            className={({ isActive }) => isActive ? styles.active : ''}
          >
            <span aria-hidden="true">◫</span> Panel principal
          </NavLink>

          <NavLink
            to="/productos"
            onClick={closeMenu}
            className={({ isActive }) =>
              isActive || location.pathname.startsWith('/inventario')
                ? styles.active
                : ''
            }
          >
            <span aria-hidden="true">▦</span> Productos e inventario
          </NavLink>

          {/* MÓDULO DE VENTAS */}
          <NavLink
            to="/ventas"
            onClick={closeMenu}
            className={({ isActive }) => isActive ? styles.active : ''}
          >
            <span aria-hidden="true">▤</span> Ventas
          </NavLink>

          <NavLink
            to="/perfil"
            end
            onClick={closeMenu}
            className={({ isActive }) => isActive ? styles.active : ''}
          >
            <span aria-hidden="true">◉</span> Mi perfil
          </NavLink>
        </nav>

        <div className={styles.sidebarFooter}>
          <span className={styles.statusDot} aria-hidden="true" />
          Sesión activa
        </div>
      </aside>

      {menuOpen && (
        <button
          className={styles.backdrop}
          aria-label="Cerrar menú"
          type="button"
          onClick={closeMenu}
        />
      )}

      <div className={styles.workspace}>
        <header className={styles.header}>
          <div className={styles.heading}>
            <button
              className={styles.menuToggle}
              type="button"
              onClick={() => setMenuOpen((open) => !open)}
              aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
              aria-expanded={menuOpen}
            >
              ☰
            </button>

            <div>
              <span className={styles.eyebrow}>MI COMERCIO</span>
              <strong>{comercio.nombre_comercio}</strong>
            </div>
          </div>

          <div className={styles.headerActions}>
            <button
              className={styles.themeButton}
              type="button"
              onClick={() =>
                setTheme((current) => current === 'dark' ? 'light' : 'dark')
              }
              aria-label={
                theme === 'dark'
                  ? 'Activar modo claro'
                  : 'Activar modo oscuro'
              }
            >
              {theme === 'dark' ? '☀ Modo claro' : '☾ Modo oscuro'}
            </button>

            <div className={styles.identity}>
              <strong>{usuario.nombre_completo || usuario.email}</strong>
              <span>
                {usuario.es_propietario ? 'Propietario' : 'Colaborador'}
              </span>
            </div>

            <button
              className={styles.logout}
              type="button"
              onClick={onLogout}
            >
              Salir
            </button>
          </div>
        </header>

        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
