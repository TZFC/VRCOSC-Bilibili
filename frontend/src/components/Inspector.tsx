import { useState, useEffect } from 'react';
import axios from 'axios';

const T: Record<string, any> = {
  zh: {
    inspector: "属性检查器",
    id: "ID",
    ruleName: "规则名称",
    triggerConfig: "触发配置",
    eventType: "事件类型",
    keywordFilter: "关键词过滤",
    minValue: "最低价值",
    actionConfig: "动作配置 (OSC 出)",
    oscAddress: "OSC 地址",
    actionType: "操作类型",
    value: "数值",
    syncMode: "同步模式",
    saveSettings: "保存配置",
    placeholderKeyword: "例如: 666 (仅限弹幕)",
    placeholderMinVal: "例如: 10 (仅限礼物/醒目留言)",
    placeholderOsc: "例如: /avatar/parameters/Mute",
    placeholderVal: "例如: true, 1.0, test",
    syncHint: {
      overwrite: "用户在游戏中手动修改参数时，应用会将其恢复为自动化设定的值。",
      respect: "用户在游戏中手动修改参数时，应用会接受新值，后续自动化将基于该值继续。"
    },
    options: {
      danmaku: "弹幕 (Danmaku)",
      gift: "礼物 (Gift)",
      sc: "醒目留言 (SC)",
      guard: "大航海 (Guard)",
      enter: "进入直播间 (Enter)",
      set: "设置 (Set)",
      toggle: "切换 (Toggle)",
      add: "相加 (Add)",
      overwrite: "覆盖现有输入",
      respect: "保留现有输入"
    }
  },
  en: {
    inspector: "Inspector",
    id: "ID",
    ruleName: "Rule Name",
    triggerConfig: "Trigger Configuration",
    eventType: "Event Type",
    keywordFilter: "Keyword Filter",
    minValue: "Minimum Value",
    actionConfig: "Action (OSC Out)",
    oscAddress: "OSC Address",
    actionType: "Action Type",
    value: "Value",
    syncMode: "Sync Mode",
    saveSettings: "Save Settings",
    placeholderKeyword: "e.g. hello (Danmaku only)",
    placeholderMinVal: "e.g. 10 (Gifts/SC only)",
    placeholderOsc: "e.g. /avatar/parameters/Mute",
    placeholderVal: "e.g. true, 1.0, test",
    syncHint: {
      overwrite: "When the user manually changes this parameter in-game, the app will restore it to the automation-intended value.",
      respect: "When the user manually changes this parameter in-game, the app will accept the new value and continue automation from it."
    },
    options: {
      danmaku: "Danmaku",
      gift: "Gift",
      sc: "Super Chat (SC)",
      guard: "Guard (Fleet)",
      enter: "Enter Room",
      set: "Set",
      toggle: "Toggle",
      add: "Add",
      overwrite: "Overwrite",
      respect: "Respect"
    }
  }
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export default function Inspector({ rule, onUpdate, lang }: any) {
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
        <span className="font-bold text-xs uppercase tracking-wider text-[var(--text-main)]">
          {T[lang].inspector}
        </span>
        <span className="text-[10px] text-[var(--text-muted)] font-mono">{T[lang].id}: {localRule.id}</span>
      </div>
      
      <div className="space-y-4">
        {/* Active & Rule Name Header */}
        <div className="flex items-center gap-3 bg-[var(--bg-darker)] p-2 border border-[var(--border-color)] rounded">
          <input type="checkbox" name="enabled" checked={localRule.enabled} onChange={handleChange} className="w-4 h-4 cursor-pointer" />
          <input className="w-full font-bold text-sm bg-[var(--bg-input)] border-none" name="name" value={localRule.name} onChange={handleChange} placeholder={T[lang].ruleName} />
        </div>

        {/* Trigger settings */}
        <div className="unity-panel">
          <div className="unity-panel-header">{T[lang].triggerConfig}</div>
          <div className="space-y-2">
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">{T[lang].eventType}</span>
              <div className="unity-inspector-value">
                <select className="w-full" name="event_type" value={localRule.event_type} onChange={handleChange}>
                  <option value="Danmaku">{T[lang].options.danmaku}</option>
                  <option value="Gift">{T[lang].options.gift}</option>
                  <option value="SC">{T[lang].options.sc}</option>
                  <option value="Guard">{T[lang].options.guard}</option>
                  <option value="Enter">{T[lang].options.enter}</option>
                </select>
              </div>
            </div>
            
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">{T[lang].keywordFilter}</span>
              <div className="unity-inspector-value">
                <input className="w-full" name="condition_keyword" value={localRule.condition_keyword || ''} onChange={handleChange} placeholder={T[lang].placeholderKeyword} />
              </div>
            </div>
            
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">{T[lang].minValue}</span>
              <div className="unity-inspector-value">
                <input className="w-full" type="number" name="condition_min_value" value={localRule.condition_min_value || 0} onChange={handleChange} placeholder={T[lang].placeholderMinVal} />
              </div>
            </div>
          </div>
        </div>

        {/* Action settings */}
        <div className="unity-panel">
          <div className="unity-panel-header">{T[lang].actionConfig}</div>
          <div className="space-y-2">
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">{T[lang].oscAddress}</span>
              <div className="unity-inspector-value">
                <input className="w-full font-mono text-[13px]" name="osc_endpoint" value={localRule.osc_endpoint || ''} onChange={handleChange} placeholder={T[lang].placeholderOsc} />
              </div>
            </div>
            
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">{T[lang].actionType}</span>
              <div className="unity-inspector-value">
                <select className="w-full" name="action_type" value={localRule.action_type} onChange={handleChange}>
                  <option value="Set">{T[lang].options.set}</option>
                  <option value="Toggle">{T[lang].options.toggle}</option>
                  <option value="Add">{T[lang].options.add}</option>
                </select>
              </div>
            </div>
            
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">{T[lang].value}</span>
              <div className="unity-inspector-value">
                <input className="w-full font-mono text-[13px]" name="action_value" value={localRule.action_value || ''} onChange={handleChange} placeholder={T[lang].placeholderVal} />
              </div>
            </div>
            
            <div className="unity-inspector-row">
              <span className="unity-inspector-label">{T[lang].syncMode}</span>
              <div className="unity-inspector-value">
                <select className="w-full" name="sync_mode" value={localRule.sync_mode} onChange={handleChange}>
                  <option value="Overwrite">{T[lang].options.overwrite}</option>
                  <option value="Respect">{T[lang].options.respect}</option>
                </select>
              </div>
            </div>
            <div className="px-2 py-1">
              <p className="text-[10px] text-[var(--text-muted)] leading-relaxed">
                {localRule.sync_mode === 'Respect' ? T[lang].syncHint.respect : T[lang].syncHint.overwrite}
              </p>
            </div>
          </div>
        </div>

        <button onClick={save} className="w-full py-2 bg-[var(--accent-blue)] hover:bg-[var(--accent-blue-hover)] text-white border-none rounded font-bold transition-all text-xs">
          {T[lang].saveSettings}
        </button>
      </div>
    </div>
  );
}
