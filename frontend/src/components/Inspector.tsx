import { useState, useEffect } from 'react';
import axios from 'axios';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export default function Inspector({ rule, onUpdate }: any) {
  const [localRule, setLocalRule] = useState(rule);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLocalRule(rule);
  }, [rule]);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleChange = (e: any) => {
    const { name, value, type, checked } = e.target;
    setLocalRule({ ...localRule, [name]: type === 'checkbox' ? checked : value });
  };

  const save = async () => {
    await axios.put(`/api/rules/${localRule.id}`, localRule);
    onUpdate();
  };

  if (!localRule) return null;

  return (
    <div className="flex-1 bg-[var(--bg-dark)] p-4 overflow-y-auto">
      {/* Inspector Header */}
      <div className="flex items-center justify-between mb-4 border-b border-[var(--border-color)] pb-2 select-none">
        <span className="font-bold text-xs uppercase tracking-wider text-[var(--text-main)]">Inspector</span>
        <span className="text-[10px] text-[var(--text-muted)] font-mono">ID: {localRule.id}</span>
      </div>
      
      <div className="space-y-4">
        {/* Active & Rule Name Header */}
        <div className="flex items-center gap-3 bg-[var(--bg-darker)] p-2 border border-[var(--border-color)] rounded">
          <input type="checkbox" name="enabled" checked={localRule.enabled} onChange={handleChange} className="w-4 h-4 cursor-pointer" />
          <input className="w-full font-bold text-sm bg-[var(--bg-input)] border-none" name="name" value={localRule.name} onChange={handleChange} placeholder="Rule Name" />
        </div>

        {/* Trigger settings */}
        <div className="unity-panel">
          <div className="unity-panel-header">Trigger Configuration</div>
          <div className="space-y-2">
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">Event Type</span>
              <div className="unity-inspector-value">
                <select className="w-full" name="event_type" value={localRule.event_type} onChange={handleChange}>
                  <option>Danmaku</option>
                  <option>Gift</option>
                  <option>SC</option>
                  <option>Guard</option>
                  <option>Enter</option>
                </select>
              </div>
            </div>
            
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">Keyword Filter</span>
              <div className="unity-inspector-value">
                <input className="w-full" name="condition_keyword" value={localRule.condition_keyword || ''} onChange={handleChange} placeholder="e.g. hello (Danmaku only)" />
              </div>
            </div>
            
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">Minimum Value</span>
              <div className="unity-inspector-value">
                <input className="w-full" type="number" name="condition_min_value" value={localRule.condition_min_value || 0} onChange={handleChange} placeholder="e.g. 10 (Gifts/SC only)" />
              </div>
            </div>
          </div>
        </div>

        {/* Action settings */}
        <div className="unity-panel">
          <div className="unity-panel-header">Action (OSC Out)</div>
          <div className="space-y-2">
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">OSC Address</span>
              <div className="unity-inspector-value">
                <input className="w-full font-mono text-[13px]" name="osc_endpoint" value={localRule.osc_endpoint || ''} onChange={handleChange} placeholder="e.g. /avatar/parameters/Mute" />
              </div>
            </div>
            
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">Action Type</span>
              <div className="unity-inspector-value">
                <select className="w-full" name="action_type" value={localRule.action_type} onChange={handleChange}>
                  <option>Set</option>
                  <option>Toggle</option>
                  <option>Add</option>
                </select>
              </div>
            </div>
            
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">Value</span>
              <div className="unity-inspector-value">
                <input className="w-full font-mono text-[13px]" name="action_value" value={localRule.action_value || ''} onChange={handleChange} placeholder="e.g. true, 1.0, test" />
              </div>
            </div>
            
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">Sync Mode</span>
              <div className="unity-inspector-value">
                <select className="w-full" name="sync_mode" value={localRule.sync_mode} onChange={handleChange}>
                  <option>Overwrite</option>
                  <option>Respect</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <button onClick={save} className="w-full py-2 bg-[var(--accent-blue)] hover:bg-[var(--accent-blue-hover)] text-white border-none rounded font-bold transition-all text-xs">Save Settings</button>
      </div>
    </div>
  );
}
