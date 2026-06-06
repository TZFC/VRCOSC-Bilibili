import { useEffect, useState, useRef } from 'react';

export default function Console() {
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
    <div className="h-full flex flex-col bg-[#1e1e1e] font-mono text-xs">
      <div className="bg-[#2d2d2d] p-1 font-bold border-b border-[#383838]">Console</div>
      <div className="flex-1 overflow-y-auto p-2">
        {logs.map((l, i) => <div key={i}>{l}</div>)}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
