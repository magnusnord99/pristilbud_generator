import { Link, Outlet, useLocation } from 'react-router-dom'
import './App.css'

function App() {
  const location = useLocation()
  const path = location.pathname
  return (
    <div style={{ 
      maxWidth: '900px', 
      margin: '24px auto', 
      padding: '16px' 
    }}>
      <nav style={{ 
        display: 'flex', 
        gap: '8px', 
        marginBottom: '32px',
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '16px',
        boxShadow: '0 2px 12px rgba(0, 0, 0, 0.08)',
        border: '1px solid #e1e5e9'
      }}>
        <Link 
          to="/" 
          style={{ 
            fontWeight: path === '/' ? '600' : '400',
            color: path === '/' ? '#3b82f6' : '#6b7280',
            textDecoration: 'none',
            padding: '12px 20px',
            borderRadius: '8px',
            backgroundColor: path === '/' ? '#eff6ff' : 'transparent',
            transition: 'all 0.2s',
            fontSize: '1rem',
            flex: '1',
            textAlign: 'center',
            minWidth: '0'
          }}
        >
          Pristilbud
        </Link>
        <Link 
          to="/project" 
          style={{ 
            fontWeight: path === '/project' ? '600' : '400',
            color: path === '/project' ? '#3b82f6' : '#6b7280',
            textDecoration: 'none',
            padding: '12px 20px',
            borderRadius: '8px',
            backgroundColor: path === '/project' ? '#eff6ff' : 'transparent',
            transition: 'all 0.2s',
            fontSize: '1rem',
            flex: '1',
            textAlign: 'center',
            minWidth: '0'
          }}
        >
          Prosjektbeskrivelse
        </Link>
        <Link 
          to="/images" 
          style={{ 
            fontWeight: path === '/images' ? '600' : '400',
            color: path === '/images' ? '#3b82f6' : '#6b7280',
            textDecoration: 'none',
            padding: '12px 20px',
            borderRadius: '8px',
            backgroundColor: path === '/images' ? '#eff6ff' : 'transparent',
            transition: 'all 0.2s',
            fontSize: '1rem',
            flex: '1',
            textAlign: 'center',
            minWidth: '0'
          }}
        >
          Bilder
        </Link>
      </nav>
      <Outlet />
    </div>
  )
}

export default App
