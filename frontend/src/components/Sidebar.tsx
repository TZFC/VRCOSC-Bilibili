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
    <div className="w-64 bg-[#383838] flex flex-col h-full border-r border-[#282828]">
      <div className="flex justify-between items-center p-2 bg-[#424242] border-b border-[#282828]">
        <span className="font-bold text-sm">Hierarchy</span>
        <div className="flex gap-2">
          <button onClick={addRule} className="text-xs bg-[#007acc] px-2 py-1 rounded">+</button>
          <button onClick={exportRules} className="text-xs bg-gray-600 px-2 py-1 rounded">Exp</button>
          <label className="text-xs bg-gray-600 px-2 py-1 rounded cursor-pointer">
            Imp
            <input type="file" className="hidden" accept=".json" onChange={importRules} />
          </label>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
        {rules.map((r: any) => (
          <div 
            key={r.id} 
            className={`p-2 flex justify-between cursor-pointer text-sm hover:bg-[#007acc] ${selectedId === r.id ? 'bg-[#007acc]' : ''}`}
            onClick={() => onSelect(r.id)}
          >
            <span>{r.name}</span>
            <button onClick={(e) => { e.stopPropagation(); deleteRule(r.id); }} className="text-red-400 hover:text-red-200">x</button>
          </div>
        ))}
      </div>
    </div>
  );
}
