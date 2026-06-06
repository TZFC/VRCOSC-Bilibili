import { useState, useEffect } from 'react';
import axios from 'axios';

export default function AuthPanel({ authActive, onAuthUpdate, config, onConfigUpdate }: any) {
  const [profiles, setProfiles] = useState<any[]>([]);
  const [localConfig, setLocalConfig] = useState(config || { bili_room_id: 0, osc_client_ip: '127.0.0.1', osc_client_port: 9000, osc_server_ip: '127.0.0.1', osc_server_port: 9001 });

  useEffect(() => {
    if (config) setLocalConfig(config);
  }, [config]);

  const scan = async () => {
    const res = await axios.get('/api/auth/scan');
    setProfiles(res.data);
  };

  const selectProfile = async (profile: any) => {
    await axios.post('/api/auth/select', profile);
    onAuthUpdate();
  };

  const saveConfig = async () => {
    await axios.post('/api/config', localConfig);
    onConfigUpdate();
    alert('Config Saved & Applied!');
  };

  const handleConfigChange = (e: any) => {
    setLocalConfig({ ...localConfig, [e.target.name]: e.target.value });
  };

  return (
    <div className="p-8 h-full overflow-y-auto">
      <h2 className="text-2xl font-bold mb-6">VRCOSC-Bilibili Setup</h2>
      
      <div className="bg-[#282828] p-4 rounded mb-6">
        <h3 className="text-lg font-bold mb-4">1. Connection Config</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <label className="block mb-1">Bilibili Room ID</label>
            <input name="bili_room_id" value={localConfig.bili_room_id} onChange={handleConfigChange} className="bg-[#3e3e42] p-2 w-full rounded" />
          </div>
          <div></div>
          <div>
            <label className="block mb-1">OSC Client IP</label>
            <input name="osc_client_ip" value={localConfig.osc_client_ip} onChange={handleConfigChange} className="bg-[#3e3e42] p-2 w-full rounded" />
          </div>
          <div>
            <label className="block mb-1">OSC Client Port (VRC In)</label>
            <input name="osc_client_port" value={localConfig.osc_client_port} onChange={handleConfigChange} className="bg-[#3e3e42] p-2 w-full rounded" />
          </div>
          <div>
            <label className="block mb-1">OSC Server IP</label>
            <input name="osc_server_ip" value={localConfig.osc_server_ip} onChange={handleConfigChange} className="bg-[#3e3e42] p-2 w-full rounded" />
          </div>
          <div>
            <label className="block mb-1">OSC Server Port (VRC Out)</label>
            <input name="osc_server_port" value={localConfig.osc_server_port} onChange={handleConfigChange} className="bg-[#3e3e42] p-2 w-full rounded" />
          </div>
        </div>
        <button onClick={saveConfig} className="mt-4 bg-[#007acc] px-4 py-2 rounded font-bold hover:bg-blue-600">Save & Apply Config</button>
      </div>

      <div className="bg-[#282828] p-4 rounded mb-6">
        <h3 className="text-lg font-bold mb-4">2. Authentication</h3>
        {authActive ? (
          <div className="flex items-center gap-4 bg-[#3e3e42] p-4 rounded mb-4">
            <img src={authActive.face_url} className="w-12 h-12 rounded-full" />
            <div>
              <div className="font-bold">{authActive.name}</div>
              <div className="text-sm text-gray-400">UID: {authActive.uid}</div>
            </div>
            <div className="ml-auto text-green-400 font-bold">Active</div>
          </div>
        ) : (
          <div className="text-yellow-400 mb-4">No active authentication.</div>
        )}

        <button onClick={scan} className="bg-[#007acc] px-4 py-2 rounded font-bold hover:bg-blue-600 mb-4">Auto-Scan Browsers for Login</button>
        
        {profiles.length > 0 && (
          <div className="grid grid-cols-2 gap-4 mb-4">
            {profiles.map(p => (
              <div key={p.uid} onClick={() => selectProfile(p)} className="flex items-center gap-4 bg-[#3e3e42] p-4 rounded cursor-pointer hover:bg-gray-600 border border-transparent hover:border-[#007acc]">
                <img src={p.face_url} className="w-10 h-10 rounded-full" />
                <div>
                  <div className="font-bold">{p.name}</div>
                  <div className="text-xs text-gray-400">UID: {p.uid}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
