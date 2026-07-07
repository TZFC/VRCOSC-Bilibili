import { useState, useEffect } from 'react';
import axios from 'axios';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export default function AuthPanel({ authActive, onAuthUpdate, config, onConfigUpdate }: any) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [profiles, setProfiles] = useState<any[]>([]);
  const [localConfig, setLocalConfig] = useState(config || { bili_room_id: 0, osc_client_ip: '127.0.0.1', osc_client_port: 9000, osc_server_ip: '127.0.0.1', osc_server_port: 9001 });

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (config) setLocalConfig(config);
  }, [config]);

  const scan = async () => {
    try {
      const res = await axios.get('/api/auth/scan');
      setProfiles(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    scan();
  }, []);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const selectProfile = async (profile: any) => {
    await axios.post('/api/auth/select', profile);
    onAuthUpdate();
  };

  const saveConfig = async () => {
    await axios.post('/api/config', localConfig);
    onConfigUpdate();
    alert('Config Saved & Applied!');
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleConfigChange = (e: any) => {
    setLocalConfig({ ...localConfig, [e.target.name]: e.target.value });
  };

  return (
    <div className="p-6 h-full overflow-y-auto max-w-4xl mx-auto">
      {/* Title */}
      <div className="flex items-center justify-between mb-6 border-b border-[var(--border-color)] pb-3 select-none">
        <span className="font-bold text-sm uppercase tracking-wider text-[var(--text-main)]">VRCOSC-Bilibili Project Settings</span>
        <span className="text-[10px] text-[var(--text-muted)] font-mono">v3.0.0</span>
      </div>
      
      {/* Connection Config Panel */}
      <div className="unity-panel">
        <div className="unity-panel-header">1. Connection Config</div>
        <div className="space-y-2">
          <div className="unity-inspector-row">
            <span className="unity-inspector-label">Bilibili Room ID</span>
            <div className="unity-inspector-value">
              <input name="bili_room_id" type="number" value={localConfig.bili_room_id} onChange={handleConfigChange} className="w-full" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">OSC Client IP</span>
            <div className="unity-inspector-value">
              <input name="osc_client_ip" value={localConfig.osc_client_ip} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">OSC Client Port (VRC In)</span>
            <div className="unity-inspector-value">
              <input name="osc_client_port" type="number" value={localConfig.osc_client_port} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">OSC Server IP</span>
            <div className="unity-inspector-value">
              <input name="osc_server_ip" value={localConfig.osc_server_ip} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">OSC Server Port (VRC Out)</span>
            <div className="unity-inspector-value">
              <input name="osc_server_port" type="number" value={localConfig.osc_server_port} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>
        </div>
        <button onClick={saveConfig} className="mt-4 w-full py-2 bg-[var(--accent-blue)] hover:bg-[var(--accent-blue-hover)] text-white border-none rounded font-bold text-xs">Save & Apply Config</button>
      </div>

      {/* Authentication Config Panel */}
      <div className="unity-panel">
        <div className="unity-panel-header">2. Authentication</div>
        
        {authActive ? (
          <div className="flex items-center gap-4 bg-[var(--bg-darker)] p-3 border border-[var(--border-color)] rounded mb-4">
            <img src={authActive.face_url} className="w-12 h-12 rounded-full border border-[var(--border-color)]" alt={authActive.name} />
            <div>
              <div className="font-bold text-xs text-[var(--text-active)]">{authActive.name}</div>
              <div className="text-[10px] text-[var(--text-muted)] font-mono">UID: {authActive.uid}</div>
            </div>
            <div className="ml-auto flex items-center gap-1.5 bg-[var(--bg-dark)] px-2.5 py-1 border border-[var(--border-color)] rounded">
              <span className="w-2 h-2 rounded-full bg-[var(--accent-green)] animate-pulse"></span>
              <span className="text-[10px] font-bold text-[var(--accent-green)] uppercase tracking-wider">Active</span>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 bg-[var(--bg-darker)]/40 p-3 border border-dashed border-[var(--border-color)] rounded mb-4 text-xs text-[var(--accent-yellow)] font-medium">
            <span className="w-2 h-2 rounded-full bg-[var(--accent-yellow)] animate-pulse"></span>
            No active authentication profile. Scanning local browsers...
          </div>
        )}

        {profiles.length > 0 && (
          <div className="mt-4">
            <div className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-2 select-none">Available Browser Sessions:</div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {profiles.map(p => (
                <div 
                  key={p.uid} 
                  onClick={() => selectProfile(p)} 
                  className="flex items-center gap-3 bg-[var(--bg-darker)] p-3 rounded cursor-pointer border border-[var(--border-color)] hover:border-[var(--accent-blue)] hover:bg-[var(--bg-hover)] transition-all duration-150 group"
                >
                  <img src={p.face_url} className="w-9 h-9 rounded-full border border-[var(--border-color)]" alt={p.name} />
                  <div className="truncate">
                    <div className="font-bold text-xs text-[var(--text-active)] group-hover:text-[var(--accent-blue-hover)] transition-colors duration-150 truncate">{p.name}</div>
                    <div className="text-[10px] text-[var(--text-muted)] font-mono truncate">UID: {p.uid}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
