import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import styles from './PrivateLayout.module.css'

const THEME_KEY = 'gestion-integral.theme'
const SIDEBAR_KEY = 'aionix.sidebar.pinned'

function storedPreference(key, expected) {
  try { return localStorage.getItem(key) === expected } catch { return false }
}

const navItems = [
  { to: '/inicio', label: 'Panel principal', icon: 'dashboard', end: true },
  { to: '/productos', label: 'Mercadería', icon: 'package', includes: '/inventario' },
  { to: '/ventas', label: 'Ventas', icon: 'sales' },
  { to: '/compras', label: 'Compras', icon: 'purchases' },
  { to: '/clientes', label: 'Clientes', icon: 'clients' },
  { to: '/proveedores', label: 'Proveedores', icon: 'suppliers' },
  { to: '/categorias', label: 'Categorías', icon: 'categories' },
]

function NavIcon({ name }) {
  const paths = {
    dashboard: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    package: <><path d="m12 2 9 5-9 5-9-5 9-5Z"/><path d="M3 7v10l9 5 9-5V7M12 12v10"/></>,
    sales: <><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h4"/></>,
    purchases: <><path d="M3 5h2l2 11h12l2-8H6M9 21h.01M18 21h.01"/></>,
    clients: <><circle cx="9" cy="8" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2M17 5a3 3 0 0 1 0 6M18 14a5 5 0 0 1 3 5"/></>,
    suppliers: <><path d="M3 21V7l9-4 9 4v14M3 11h18M9 21v-6h6v6"/></>,
    categories: <><rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/></>,
    profile: <><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></>,
    pin: <><path d="m16 3 5 5-4 1-3 5-4-4-5 3 3-5-1-4 9-1ZM12 14l-7 7"/></>,
    menu: <path d="M4 7h16M4 12h16M4 17h16"/>,
    sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></>,
    moon: <path d="M20 15.5A8.5 8.5 0 0 1 8.5 4 8.5 8.5 0 1 0 20 15.5Z"/>,
    logout: <><path d="M10 17l5-5-5-5m5 5H3M12 3h6a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3h-6"/></>,
  }
  return <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>
}

export default function PrivateLayout({ profile, onLogout }) {
  const { usuario, comercio } = profile
  const location = useLocation()
  const [theme, setTheme] = useState(() => storedPreference(THEME_KEY, 'light') ? 'light' : 'dark')
  const [pinned, setPinned] = useState(() => storedPreference(SIDEBAR_KEY, 'true'))
  const [menuOpen, setMenuOpen] = useState(false)
  const [accountOpen, setAccountOpen] = useState(false)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    try { localStorage.setItem(THEME_KEY, theme) } catch { /* Storage may be unavailable. */ }
  }, [theme])

  useEffect(() => {
    try { localStorage.setItem(SIDEBAR_KEY, String(pinned)) } catch { /* Storage may be unavailable. */ }
  }, [pinned])

  // El menú se cierra al seleccionar una acción; no requiere efecto de sincronización.

  useEffect(() => {
    if (!menuOpen) return undefined
    function onEscape(event) { if (event.key === 'Escape') setMenuOpen(false) }
    document.addEventListener('keydown', onEscape)
    return () => document.removeEventListener('keydown', onEscape)
  }, [menuOpen])

  const closeMenu = () => setMenuOpen(false)
  const displayName = usuario.nombre_completo || usuario.email

  return (
    <div className={styles.layout} data-pinned={pinned}>
      <aside className={styles.sidebar} data-open={menuOpen} aria-label="Menú lateral">
        <div className={styles.brand}>
          <span className={styles.brandMark} aria-hidden="true">A</span>
          <div className={styles.brandText}><strong>AIOnix</strong><small>COMMERCE OS</small></div>
          <button type="button" className={styles.pinButton} onClick={() => setPinned(value => !value)}
            aria-label={pinned ? 'Desfijar menú lateral' : 'Fijar menú lateral expandido'}
            aria-pressed={pinned} title={pinned ? 'Contraer menú' : 'Fijar menú abierto'}>
            <NavIcon name="pin" />
          </button>
        </div>
        <div className={styles.navCaption}>ESPACIO DE TRABAJO</div>
        <nav className={styles.navigation} aria-label="Navegación principal">
          {navItems.map(item => (
            <NavLink key={item.to} to={item.to} end={item.end} onClick={closeMenu}
              title={item.label} aria-label={item.label}
              className={({ isActive }) => isActive || (item.includes && location.pathname.startsWith(item.includes)) ? styles.active : ''}>
              <NavIcon name={item.icon} /><span className={styles.navLabel}>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className={styles.sidebarFooter}>
          <span className={styles.statusDot} aria-hidden="true" />
          <span className={styles.footerText}>Sesión activa</span>
        </div>
      </aside>

      {menuOpen && <button className={styles.backdrop} aria-label="Cerrar menú" type="button" onClick={closeMenu} />}
      <div className={styles.workspace}>
        <header className={styles.header}>
          <div className={styles.heading}>
            <button className={styles.menuToggle} type="button" onClick={() => setMenuOpen(open => !open)}
              aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'} aria-expanded={menuOpen}>
              <NavIcon name="menu" />
            </button>
            <div className={styles.commerce}><span className={styles.eyebrow}>COMERCIO ACTIVO</span><strong>{comercio.nombre_comercio}</strong></div>
          </div>
          <div className={styles.headerActions}>
            <button className={styles.themeButton} type="button"
              onClick={() => setTheme(current => current === 'dark' ? 'light' : 'dark')}
              aria-label={theme === 'dark' ? 'Activar modo claro' : 'Activar modo oscuro'}
              title={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}>
              <NavIcon name={theme === 'dark' ? 'sun' : 'moon'} />
            </button>
            <div className={styles.account}>
              <button type="button" className={styles.accountButton} onClick={() => setAccountOpen(open => !open)}
                aria-expanded={accountOpen} aria-haspopup="true" aria-label="Opciones de usuario">
                <span className={styles.avatar} aria-hidden="true">{displayName.charAt(0).toUpperCase()}</span>
                <span className={styles.identity}><strong>{displayName}</strong><small>{usuario.es_propietario ? 'Propietario' : 'Colaborador'}</small></span>
                <span aria-hidden="true">⌄</span>
              </button>
              {accountOpen && <div className={styles.accountMenu}>
                <NavLink to="/perfil" onClick={() => setAccountOpen(false)}><NavIcon name="profile" /> Mi perfil</NavLink>
                <button type="button" onClick={onLogout}><NavIcon name="logout" /> Cerrar sesión</button>
              </div>}
            </div>
          </div>
        </header>
        <main className={styles.content}><Outlet /></main>
      </div>
    </div>
  )
}
