import { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import Inspector from './components/Inspector';
import Console from './components/Console';
import AuthPanel from './components/AuthPanel';

axios.defaults.baseURL = 'http://localhost:8000';

function App() {
// eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [config, setConfig] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [authActive, setAuthActive] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [rules, setRules] = useState<any[]>([]);
  const [selectedRuleId, setSelectedRuleId] = useState<number | null>(null);
  const [lang, setLang] = useState<'zh' | 'en'>('zh');

  async function fetchConfig() {
    try {
      const res = await axios.get('/api/config');
      setConfig(res.data);
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchRules() {
    try {
      const res = await axios.get('/api/rules');
      setRules(res.data);
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchAuth() {
    try {
      const res = await axios.get('/api/auth/active');
      setAuthActive(res.data);
    } catch (e) {
      console.error(e);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchConfig();
    fetchRules();
    fetchAuth();
  }, []);

  return (
    <div className="unity-window font-sans text-[var(--text-main)]">
      <Sidebar 
        rules={rules} 
        onSelect={setSelectedRuleId} 
        selectedId={selectedRuleId} 
        onRefresh={fetchRules}
        lang={lang}
        onLangChange={setLang}
      />
      <div className="unity-main-content border-l border-[var(--border-color)]">
        <div className="flex flex-1 h-[60%] overflow-hidden">
          {selectedRuleId ? (
            <Inspector 
              rule={rules.find(r => r.id === selectedRuleId)} 
              onUpdate={fetchRules}
              lang={lang}
            />
          ) : (
            <div className="flex-1 overflow-auto bg-[var(--bg-dark)]">
              <AuthPanel 
                authActive={authActive} 
                onAuthUpdate={fetchAuth} 
                config={config} 
                onConfigUpdate={fetchConfig}
                lang={lang}
              />
            </div>
          )}
        </div>
        <div className="h-[40%] border-t border-[var(--border-color)] overflow-hidden">
          <Console lang={lang} />
        </div>
      </div>
    </div>
  );
}
export default App;
