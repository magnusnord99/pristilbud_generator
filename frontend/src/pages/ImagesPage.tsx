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
        justifyContent: 'center'
      }}>
        <h1 style={{
          margin: '0 0 20px 0',
          color: '#2c3e50',
          fontSize: '2rem',
          fontWeight: '600'
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


