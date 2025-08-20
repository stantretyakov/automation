import React, { useState } from 'react';
import CameraViewport from './components/CameraViewport';

const App: React.FC = () => {
  const [lastCode, setLastCode] = useState<string | null>(null);

  return (
    <div style={{ padding: '16px', textAlign: 'center' }}>
      <h1>Kiosk</h1>
      <p>Place your QR code inside the square to check in.</p>
      <div style={{ margin: '16px auto' }}>
        <CameraViewport size={300} onDetect={setLastCode} />
      </div>
      {lastCode && (
        <div style={{ marginTop: '16px' }}>
          <strong>Last scan:</strong> {lastCode}
        </div>
      )}
      <p style={{ marginTop: '32px' }}>
        <a href="https://example.com/help" target="_blank" rel="noopener noreferrer">
          Need help?
        </a>
      </p>
    </div>
  );
};

export default App;
