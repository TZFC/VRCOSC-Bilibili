import axios from 'axios';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export default function Sidebar({ rules, onSelect, selectedId, onRefresh }: any) {
  const addRule = async () => {
    await axios.post('/api/rules', { name: 'New Rule', event_type: 'Danmaku' });
    onRefresh();
  };

  const deleteRule = async (id: number) => {
    await axios.delete(`/api/rules/${id}`);
    if (selectedId === id) onSelect(null);
    onRefresh();
  };

  const exportRules = async () => {
    const res = await axios.get('/api/rules/export');
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vrcosc_rules.json';
    a.click();
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const importRules = async (e: any) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        await axios.post('/api/rules/import', json);
        onRefresh();
      } catch {
        alert('Invalid JSON');
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="unity-sidebar">
      {/* Unity Toolbar */}
      <div className="flex justify-between items-center p-2 bg-[var(--bg-dark)] border-b border-[var(--border-color)]">
        <span className="font-bold text-xs uppercase tracking-wider text-[var(--text-muted)] select-none">Hierarchy</span>
        <div className="flex gap-1">
          <button onClick={addRule} className="text-xs px-2 py-0.5 font-bold" title="Add New Rule">+</button>
          <button onClick={exportRules} className="text-xs px-1.5 py-0.5" title="Export Rules">Export</button>
          <label className="text-[13px] px-1.5 py-0.5 bg-[var(--bg-panel)] hover:bg-[var(--bg-hover)] text-[var(--text-active)] border border-[var(--border-color)] rounded cursor-pointer transition-colors duration-150 inline-block font-medium">
            Import
            <input type="file" className="hidden" accept=".json" onChange={importRules} />
          </label>
        </div>
      </div>
      
      {/* Hierarchy View list */}
      <div className="flex-1 overflow-y-auto bg-[var(--bg-darker)]">
        {rules.length === 0 ? (
          <div className="p-4 text-xs text-[var(--text-muted)] italic text-center select-none">
            No rules. Click '+' to create one.
          </div>
        ) : (
          rules.map((r: any) => (
            <div 
              key={r.id} 
              className={`unity-list-item group text-xs justify-between ${selectedId === r.id ? 'selected' : ''}`}
              onClick={() => onSelect(r.id)}
            >
              <div className="flex items-center gap-2 truncate">
                <span className="w-1.5 h-1.5 rounded-full bg-gray-400 opacity-60"></span>
                <span className="truncate font-medium">{r.name}</span>
              </div>
              <button 
                onClick={(e) => { e.stopPropagation(); deleteRule(r.id); }} 
                className="opacity-0 group-hover:opacity-100 hover:opacity-100 px-1 py-0.5 bg-transparent hover:bg-red-900/30 text-red-400 hover:text-red-300 border-none rounded text-[10px] font-bold transition-all"
                style={{ background: 'transparent', border: 'none' }}
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
