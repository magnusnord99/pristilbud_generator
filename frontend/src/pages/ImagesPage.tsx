export default function ImagesPage() {
  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px',
      minHeight: '600px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
        border: '1px solid #e1e5e9',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        position: 'relative'
      }}>
        {/* Leafilms Logo */}
        <div style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <div style={{
            width: '32px',
            height: '32px',
            backgroundColor: '#10b981',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            fontSize: '18px'
          }}>
            🍃
          </div>
          <span style={{
            color: '#10b981',
            fontWeight: '700',
            fontSize: '1.2rem',
            letterSpacing: '0.5px'
          }}>
            Leafilms
          </span>
        </div>

        <h1 style={{
          margin: '0 0 20px 0',
          color: '#2c3e50',
          fontSize: '2rem',
          fontWeight: '600',
          marginTop: '20px'
        }}>Bilder</h1>
        <p style={{
          margin: '0 0 16px 0',
          color: '#5a6c7d',
          fontSize: '1.1rem',
          lineHeight: '1.6'
        }}>Her vil du kunne laste opp og administrere bilder relatert til prosjektene.</p>
        <p style={{
          margin: '0',
          color: '#7f8c8d',
          fontSize: '1rem'
        }}>Kommer snart! 📸</p>
      </div>
    </div>
  )
}


