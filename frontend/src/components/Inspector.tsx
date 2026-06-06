import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Inspector({ rule, onUpdate }: any) {
  const [localRule, setLocalRule] = useState(rule);

  useEffect(() => {
    setLocalRule(rule);
  }, [rule]);

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
    <div className="flex-1 bg-[#3e3e42] p-4 overflow-y-auto">
      <div className="font-bold text-lg mb-4 border-b border-gray-600 pb-2">Inspector</div>
      
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <input type="checkbox" name="enabled" checked={localRule.enabled} onChange={handleChange} />
          <input className="bg-[#282828] text-white p-1 rounded w-full border border-gray-600" name="name" value={localRule.name} onChange={handleChange} />
        </div>

        <div className="bg-[#424242] p-2 rounded">
          <div className="font-bold mb-2">Trigger</div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <span>Event Type:</span>
            <select className="bg-[#282828] text-white p-1" name="event_type" value={localRule.event_type} onChange={handleChange}>
              <option>Danmaku</option>
              <option>Gift</option>
              <option>SC</option>
              <option>Guard</option>
              <option>Enter</option>
            </select>
            
            <span>Keyword:</span>
            <input className="bg-[#282828] text-white p-1" name="condition_keyword" value={localRule.condition_keyword} onChange={handleChange} />
            
            <span>Min Value:</span>
            <input className="bg-[#282828] text-white p-1" type="number" name="condition_min_value" value={localRule.condition_min_value} onChange={handleChange} />
          </div>
        </div>

        <div className="bg-[#424242] p-2 rounded">
          <div className="font-bold mb-2">Action (OSC)</div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <span>Endpoint:</span>
            <input className="bg-[#282828] text-white p-1" name="osc_endpoint" value={localRule.osc_endpoint} onChange={handleChange} />
            
            <span>Action Type:</span>
            <select className="bg-[#282828] text-white p-1" name="action_type" value={localRule.action_type} onChange={handleChange}>
              <option>Set</option>
              <option>Toggle</option>
              <option>Add</option>
            </select>
            
            <span>Value:</span>
            <input className="bg-[#282828] text-white p-1" name="action_value" value={localRule.action_value} onChange={handleChange} />
            
            <span>Sync Mode:</span>
            <select className="bg-[#282828] text-white p-1" name="sync_mode" value={localRule.sync_mode} onChange={handleChange}>
              <option>Overwrite</option>
              <option>Respect</option>
            </select>
          </div>
        </div>

        <button onClick={save} className="bg-[#007acc] w-full p-2 rounded mt-4 font-bold hover:bg-blue-600">Save</button>
      </div>
    </div>
  );
}
