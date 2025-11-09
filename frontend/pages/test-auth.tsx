export default function TestAuth() {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: '#fcfcfc'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        backgroundColor: 'white',
        padding: '24px',
        borderRadius: '12px',
        border: '1px solid #e5e7eb',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px', textAlign: 'center' }}>
          TEST VERSION - 400px CARD
        </h1>
        <p style={{ fontSize: '14px', color: '#6b7280', textAlign: 'center' }}>
          This is a test card that should be 400px wide
        </p>
      </div>
    </div>
  );
}
