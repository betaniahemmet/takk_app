// src/VersionDisplay.jsx
import { useEffect, useState } from 'react';

export function VersionDisplay() {
  const [version, setVersion] = useState('');
  
  useEffect(() => {
    fetch('/api/version')
      .then(r => r.json())
      .then(data => setVersion(data.version))
      .catch(() => setVersion('unknown'));
  }, []);
  
  if (!version) return null;
  
  return (
    <div className="text-xs text-muted-foreground/60 text-center py-2">
      v{version}
    </div>
  );
}