import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import './App.css'

function AppContent() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuth()
  const path = location.pathname

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // If not authenticated and not on login page, redirect to login
  if (!isAuthenticated && path !== '/login') {
    return (
      <div style={{ 
        maxWidth: '900px', 
        margin: '24px auto', 
        padding: '16px',
        textAlign: 'center'
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '32px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          border: '1px solid #e1e5e9'
        }}>
          <h2>🔐 Innlogging kreves</h2>
          <p>Du må logge inn for å bruke tjenesten.</p>
          <button
            onClick={() => navigate('/login')}
            style={{
              padding: '12px 24px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            Gå til login
          </button>
        </div>
      </div>
    )
  }

  // If on login page, don't show navigation
  if (path === '/login') {
    return <Outlet />
  }

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
        border: '1px solid #e1e5e9',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', gap: '8px' }}>
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
        </div>
        
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ color: '#6b7280', fontSize: '0.9rem' }}>
              Logget inn som: {user.name}
            </span>
            <button
              onClick={handleLogout}
              style={{
                padding: '8px 16px',
                backgroundColor: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.9rem',
                cursor: 'pointer'
              }}
            >
              Logg ut
            </button>
          </div>
        )}
      </nav>
      <Outlet />
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
