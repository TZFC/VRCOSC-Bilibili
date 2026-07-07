import { useEffect, useState, useRef } from 'react';

export default function Console({ lang }: any) {
  const [logs, setLogs] = useState<string[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/logs');
    ws.onmessage = (event) => {
      setLogs(prev => [...prev, event.data].slice(-100));
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView();
  }, [logs]);

  return (
    <div className="h-full flex flex-col bg-[var(--bg-darker)] font-mono text-xs">
      {/* Console Toolbar */}
      <div className="bg-[var(--bg-dark)] px-3 py-1.5 font-bold border-b border-[var(--border-color)] flex items-center select-none">
        <span className="text-[10px] uppercase tracking-wider text-[var(--text-muted)]">
          {lang === 'zh' ? '控制台' : 'Console'}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto p-3 text-[var(--text-main)] space-y-1">
        {logs.map((l, i) => (
          <div key={i} className="border-b border-[var(--border-color)]/30 pb-1 last:border-0">{l}</div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
