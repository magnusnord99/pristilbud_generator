import { Link, Outlet, useLocation } from 'react-router-dom'
import './App.css'

function App() {
  const location = useLocation()
  const path = location.pathname
  return (
    <div style={{ maxWidth: 900, margin: '24px auto', padding: 16 }}>
      <nav style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
        <Link to="/" style={{ fontWeight: path === '/' ? 700 : 400 }}>Pristilbud</Link>
        <Link to="/project" style={{ fontWeight: path === '/project' ? 700 : 400 }}>Prosjektbeskrivelse</Link>
        <Link to="/images" style={{ fontWeight: path === '/images' ? 700 : 400 }}>Bilder</Link>
      </nav>
      <Outlet />
    </div>
  )
}

export default App
