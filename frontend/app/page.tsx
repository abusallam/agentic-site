export default function HomePage() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#2563eb', marginBottom: '1rem' }}>
        🚀 Development Environment - dev.consulting.sa
      </h1>
      <p style={{ marginBottom: '1rem' }}>
        Welcome to the development version of Consulting.sa
      </p>
      <p style={{ marginBottom: '1rem' }}>
        This is a minimal version for testing the deployment infrastructure.
      </p>
      <div style={{ 
        background: '#f3f4f6', 
        padding: '1rem', 
        borderRadius: '8px', 
        marginTop: '2rem' 
      }}>
        <h2 style={{ color: '#374151', marginBottom: '0.5rem' }}>
          ✅ Development Features:
        </h2>
        <ul style={{ color: '#6b7280' }}>
          <li>• Separate development database tables</li>
          <li>• Debug logging enabled</li>
          <li>• Test API keys for safe testing</li>
          <li>• Isolated from production environment</li>
          <li>• SSL-enabled subdomain: dev.consulting.sa</li>
        </ul>
      </div>
    </div>
  )
}