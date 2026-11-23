import { useLocation, useNavigate } from 'react-router-dom'
import BrandPanel from '../components/auth/BrandPanel.jsx'
import AuthCard from '../components/auth/AuthCard.jsx'
import SectionView, { sectionSlugs } from '../components/auth/SectionView.jsx'
import '../styles/auth.css'

export default function AuthPage({ notice, onLogin }) {
  const navigate = useNavigate()
  const location = useLocation()
  const slug = location.pathname.split('/')[2]
  const activeSection = sectionSlugs.includes(slug) ? slug : null

  return <main className="aionix-auth-page">
    <BrandPanel activeSection={activeSection} onSelectSection={section => navigate(`/login/${section}`)} />
    <div className="aionix-auth-side">
      {activeSection
        ? <SectionView section={activeSection} onBack={() => navigate('/login')} />
        : <AuthCard notice={notice} onLogin={onLogin} />}
    </div>
  </main>
}
