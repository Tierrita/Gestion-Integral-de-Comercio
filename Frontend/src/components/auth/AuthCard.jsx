import { useState } from 'react'
import LoginForm from './LoginForm.jsx'

export default function AuthCard({ notice, onLogin }) {
  const [view, setView] = useState('login')
  return <section className="aionix-auth-card" aria-label="Acceso a AIOnix">
    <div className="aionix-auth-tabs" role="tablist" aria-label="Acceso">
      <button type="button" role="tab" id="aionix-tab-login" aria-selected={view === 'login'}
        aria-controls="aionix-auth-content" className={view === 'login' ? 'is-active' : ''}
        onClick={() => setView('login')}>Iniciar sesión</button>
      <button type="button" role="tab" id="aionix-tab-register" aria-selected={view === 'register'}
        aria-controls="aionix-auth-content" className={view === 'register' ? 'is-active' : ''}
        onClick={() => setView('register')}>Registrarse</button>
    </div>
    <div id="aionix-auth-content" role="tabpanel" aria-labelledby={view === 'login' ? 'aionix-tab-login' : 'aionix-tab-register'} className="aionix-auth-body">
      {view === 'login' ? <LoginForm notice={notice} onLogin={onLogin} /> :
        <div className="aionix-register-preview">
          <h2>Gestioná tu comercio con AIOnix</h2>
          <p>Próximamente podrás registrar tu comercio y configurar tu cuenta desde aquí.</p>
          <p>El formulario de registro se habilitará cuando validemos el endpoint y las reglas de alta del backend.</p>
          <button type="button" className="aionix-primary-button" onClick={() => setView('login')}>Volver a iniciar sesión</button>
        </div>}
    </div>
  </section>
}
