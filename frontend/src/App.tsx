import { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import Inspector from './components/Inspector';
import Console from './components/Console';
import AuthPanel from './components/AuthPanel';

axios.defaults.baseURL = 'http://localhost:8000';

function App() {
  const [config, setConfig] = useState<any>(null);
  const [authActive, setAuthActive] = useState<any>(null);
  const [rules, setRules] = useState<any[]>([]);
  const [selectedRuleId, setSelectedRuleId] = useState<number | null>(null);

  useEffect(() => {
    fetchConfig();
    fetchRules();
    fetchAuth();
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await axios.get('/api/config');
      setConfig(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchRules = async () => {
    try {
      const res = await axios.get('/api/rules');
      setRules(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchAuth = async () => {
    try {
      const res = await axios.get('/api/auth/active');
      setAuthActive(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#282828] text-[#d4d4d4] overflow-hidden font-sans">
      <Sidebar rules={rules} onSelect={setSelectedRuleId} selectedId={selectedRuleId} onRefresh={fetchRules} />
      <div className="flex flex-col flex-1 border-l border-[#383838]">
        <div className="flex flex-1 h-[60%]">
          {selectedRuleId ? (
            <Inspector rule={rules.find(r => r.id === selectedRuleId)} onUpdate={fetchRules} />
          ) : (
            <div className="flex-1 overflow-auto bg-[#3e3e42]">
              <AuthPanel authActive={authActive} onAuthUpdate={fetchAuth} config={config} onConfigUpdate={fetchConfig} />
            </div>
          )}
        </div>
        <div className="h-[40%] border-t border-[#383838]">
          <Console />
        </div>
      </div>
    </div>
  );
}
export default App;
