import BrandPanel from '../components/auth/BrandPanel.jsx'
import AuthCard from '../components/auth/AuthCard.jsx'
import '../styles/auth.css'

export default function AuthPage({ notice, onLogin }) {
  return <main className="aionix-auth-page">
    <BrandPanel />
    <div className="aionix-auth-side"><AuthCard notice={notice} onLogin={onLogin} /></div>
  </main>
}
