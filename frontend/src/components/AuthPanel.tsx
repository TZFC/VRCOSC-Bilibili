import { useState, useEffect } from 'react';
import axios from 'axios';
import { QRCodeSVG } from 'qrcode.react';

const T: Record<string, any> = {
  zh: {
    projectSettings: "VRCOSC-Bilibili 项目设置",
    connectionConfig: "1. 连接配置 (Connection)",
    biliRoomId: "哔哩哔哩直播间 ID",
    oscClientIp: "OSC 客户端 IP (VRC 接收地址)",
    oscClientPort: "OSC 客户端端口 (VRC 接收端口)",
    oscServerIp: "OSC 服务端 IP (VRC 发送地址)",
    oscServerPort: "OSC 服务端端口 (VRC 发送端口)",
    saveConfig: "保存并应用配置",
    configSaved: "配置已保存并应用！",
    authentication: "4. 身份验证 (Authentication)",
    activeProfile: "当前活动账号",
    active: "活动中",
    scanning: "未检测到处于活动状态的账号。正在自动扫描本地浏览器...",
    availableSessions: "检测到的浏览器登录会话 (点击即可切换并登录):",
    qrLogin: "扫码登录 Bilibili",
    qrInstructions: "请使用哔哩哔哩手机客户端扫描下方二维码登录:",
    qrStatusWaiting: "等待扫码...",
    qrStatusScanned: "已扫码，请在手机上确认...",
    qrStatusExpired: "二维码已过期，点击刷新",
    qrClose: "关闭二维码",
    firefoxOnlyNotice: "注意：本地浏览器自动扫描目前仅支持 Firefox。如果您使用的是 Chrome、Edge 或其他浏览器，请使用下方的“扫码登录”方式。",
    cameraSettings: "2. 相对相机控制步长设置 (Camera Steps)",
    cameraMoveXStep: "左右移动步长 (X轴) / 米",
    cameraMoveYStep: "上下移动步长 (Y轴) / 米",
    cameraMoveZStep: "前后移动步长 (Z轴) / 米",
    cameraRotateXStep: "上下倾斜步长 (Pitch) / 度",
    cameraRotateYStep: "左右偏转步长 (Yaw) / 度",
    cameraRotateZStep: "左右旋转步长 (Roll) / 度",
    cameraKeywords: "3. 相对相机控制指令关键词 (Camera Keywords, 逗号分隔)",
    rotateLeft: "向左旋转 (Rotate Left)",
    rotateRight: "向右旋转 (Rotate Right)",
    tiltUp: "向上倾斜 (Tilt Up)",
    tiltDown: "向下倾斜 (Tilt Down)",
    pivotLeft: "向左偏转 (Pivot Left)",
    pivotRight: "向右偏转 (Pivot Right)",
    moveLeft: "向左移动 (Move Left)",
    moveRight: "向右移动 (Move Right)",
    moveUp: "向上移动 (Move Up)",
    moveDown: "向下移动 (Move Down)",
    moveForward: "向前移动 (Move Forward)",
    moveBackward: "向后移动 (Move Backward)",
  },
  en: {
    projectSettings: "VRCOSC-Bilibili Project Settings",
    connectionConfig: "1. Connection Config",
    biliRoomId: "Bilibili Room ID",
    oscClientIp: "OSC Client IP (VRC Address)",
    oscClientPort: "OSC Client Port (VRC In)",
    oscServerIp: "OSC Server IP (VRC Out Address)",
    oscServerPort: "OSC Server Port (VRC Out)",
    saveConfig: "Save & Apply Config",
    configSaved: "Config Saved & Applied!",
    authentication: "4. Authentication",
    activeProfile: "Active Profile",
    active: "Active",
    scanning: "No active authentication profile. Scanning local browsers...",
    availableSessions: "Available Browser Sessions (Click to log in):",
    qrLogin: "QR Code Login",
    qrInstructions: "Scan the QR code below using your Bilibili mobile app to log in:",
    qrStatusWaiting: "Waiting for scan...",
    qrStatusScanned: "Scanned! Please confirm on your mobile app...",
    qrStatusExpired: "QR code expired. Click to refresh",
    qrClose: "Close",
    firefoxOnlyNotice: "Note: Automatic local browser scanning only supports Firefox. For Google Chrome, Microsoft Edge, or other browsers, please use the QR Code Login option instead.",
    cameraSettings: "2. Relative Camera Control Steps",
    cameraMoveXStep: "Move Left/Right Step (X) / m",
    cameraMoveYStep: "Move Up/Down Step (Y) / m",
    cameraMoveZStep: "Move Forward/Backward Step (Z) / m",
    cameraRotateXStep: "Tilt Up/Down Step (Pitch) / °",
    cameraRotateYStep: "Pivot Left/Right Step (Yaw) / °",
    cameraRotateZStep: "Rotate Left/Right Step (Roll) / °",
    cameraKeywords: "3. Relative Camera Control Keywords (comma-separated)",
    rotateLeft: "Rotate Left",
    rotateRight: "Rotate Right",
    tiltUp: "Tilt Up",
    tiltDown: "Tilt Down",
    pivotLeft: "Pivot Left",
    pivotRight: "Pivot Right",
    moveLeft: "Move Left",
    moveRight: "Move Right",
    moveUp: "Move Up",
    moveDown: "Move Down",
    moveForward: "Move Forward",
    moveBackward: "Move Backward",
  }
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export default function AuthPanel({ authActive, onAuthUpdate, config, onConfigUpdate, lang }: any) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [profiles, setProfiles] = useState<any[]>([]);
  const [localConfig, setLocalConfig] = useState(config || {
    bili_room_id: 0,
    osc_client_ip: '127.0.0.1',
    osc_client_port: 9000,
    osc_server_ip: '127.0.0.1',
    osc_server_port: 9001,
    camera_move_x_step: 0.5,
    camera_move_y_step: 0.5,
    camera_move_z_step: 0.5,
    camera_rotate_x_step: 15.0,
    camera_rotate_y_step: 15.0,
    camera_rotate_z_step: 15.0,
    camera_kw_rotate_left: "rotate left,向左旋转,左旋",
    camera_kw_rotate_right: "rotate right,向右旋转,右旋",
    camera_kw_tilt_up: "tilt up,向上倾斜,仰角,抬头",
    camera_kw_tilt_down: "tilt down,向下倾斜,俯角,低头",
    camera_kw_pivot_left: "pivot left,向左偏转,左偏,左转",
    camera_kw_pivot_right: "pivot right,向右偏转,右偏,右转",
    camera_kw_move_left: "move left,向左移动,左移",
    camera_kw_move_right: "move right,向右移动,右移",
    camera_kw_move_up: "move up,向上移动,上移",
    camera_kw_move_down: "move down,向下移动,下移",
    camera_kw_move_forward: "move forward,向前移动,前移,前进",
    camera_kw_move_backward: "move backward,向后移动,后移,后退"
  });

  const [qrUrl, setQrUrl] = useState<string | null>(null);
  const [qrStatus, setQrStatus] = useState<string>(''); // 'none', 'waiting', 'scanned', 'done', 'expired'
  const [showQr, setShowQr] = useState<boolean>(false);


  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (config) setLocalConfig(config);
  }, [config]);

  const scan = async () => {
    try {
      const res = await axios.get('/api/auth/scan');
      setProfiles(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    scan();
  }, []);

  useEffect(() => {
    let interval: any = null;
    if (showQr && qrUrl && qrStatus !== 'done' && qrStatus !== 'expired') {
      interval = setInterval(async () => {
        try {
          const res = await axios.get('/api/auth/qr/check');
          if (res.data.status === 'done') {
            setQrStatus('done');
            setShowQr(false);
            setQrUrl(null);
            onAuthUpdate();
          } else if (res.data.status === 'expired') {
            setQrStatus('expired');
          } else if (res.data.status === 'scanned') {
            setQrStatus('scanned');
          }
        } catch (e) {
          console.error(e);
        }
      }, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [showQr, qrUrl, qrStatus]);

  const startQrLogin = async () => {
    try {
      setShowQr(true);
      setQrStatus('waiting');
      const res = await axios.get('/api/auth/qr/generate');
      setQrUrl(res.data.url);
    } catch (e) {
      console.error(e);
      setQrStatus('error');
    }
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const selectProfile = async (profile: any) => {
    await axios.post('/api/auth/select', profile);
    onAuthUpdate();
  };

  const saveConfig = async () => {
    await axios.post('/api/config', localConfig);
    onConfigUpdate();
    alert(T[lang].configSaved);
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleConfigChange = (e: any) => {
    setLocalConfig({ ...localConfig, [e.target.name]: e.target.value });
  };

  return (
    <div className="p-6 h-full overflow-y-auto max-w-4xl mx-auto">
      {/* Title */}
      <div className="flex items-center justify-between mb-6 border-b border-[var(--border-color)] pb-3 select-none">
        <span className="font-bold text-sm uppercase tracking-wider text-[var(--text-main)]">
          {T[lang].projectSettings}
        </span>
        <span className="text-[10px] text-[var(--text-muted)] font-mono">v3.0.0</span>
      </div>
      
      {/* Connection Config Panel */}
      <div className="unity-panel">
        <div className="unity-panel-header">{T[lang].connectionConfig}</div>
        <div className="space-y-2">
          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].biliRoomId}</span>
            <div className="unity-inspector-value">
              <input name="bili_room_id" type="number" value={localConfig.bili_room_id} onChange={handleConfigChange} className="w-full" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].oscClientIp}</span>
            <div className="unity-inspector-value">
              <input name="osc_client_ip" value={localConfig.osc_client_ip} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].oscClientPort}</span>
            <div className="unity-inspector-value">
              <input name="osc_client_port" type="number" value={localConfig.osc_client_port} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].oscServerIp}</span>
            <div className="unity-inspector-value">
              <input name="osc_server_ip" value={localConfig.osc_server_ip} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].oscServerPort}</span>
            <div className="unity-inspector-value">
              <input name="osc_server_port" type="number" value={localConfig.osc_server_port} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>
        </div>
        <button onClick={saveConfig} className="mt-4 w-full py-2 bg-[var(--accent-blue)] hover:bg-[var(--accent-blue-hover)] text-white border-none rounded font-bold text-xs">
          {T[lang].saveConfig}
        </button>
      </div>

      {/* Camera Steps Config Panel */}
      <div className="unity-panel">
        <div className="unity-panel-header">{T[lang].cameraSettings}</div>
        <div className="space-y-2">
          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].cameraMoveXStep}</span>
            <div className="unity-inspector-value">
              <input name="camera_move_x_step" type="number" step="0.01" value={localConfig.camera_move_x_step} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].cameraMoveYStep}</span>
            <div className="unity-inspector-value">
              <input name="camera_move_y_step" type="number" step="0.01" value={localConfig.camera_move_y_step} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].cameraMoveZStep}</span>
            <div className="unity-inspector-value">
              <input name="camera_move_z_step" type="number" step="0.01" value={localConfig.camera_move_z_step} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].cameraRotateXStep}</span>
            <div className="unity-inspector-value">
              <input name="camera_rotate_x_step" type="number" step="0.1" value={localConfig.camera_rotate_x_step} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].cameraRotateYStep}</span>
            <div className="unity-inspector-value">
              <input name="camera_rotate_y_step" type="number" step="0.1" value={localConfig.camera_rotate_y_step} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].cameraRotateZStep}</span>
            <div className="unity-inspector-value">
              <input name="camera_rotate_z_step" type="number" step="0.1" value={localConfig.camera_rotate_z_step} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>
        </div>
        <button onClick={saveConfig} className="mt-4 w-full py-2 bg-[var(--accent-blue)] hover:bg-[var(--accent-blue-hover)] text-white border-none rounded font-bold text-xs">
          {T[lang].saveConfig}
        </button>
      </div>

      {/* Camera Keywords Config Panel */}
      <div className="unity-panel">
        <div className="unity-panel-header">{T[lang].cameraKeywords}</div>
        <div className="space-y-2">
          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].rotateLeft}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_rotate_left" value={localConfig.camera_kw_rotate_left || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].rotateRight}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_rotate_right" value={localConfig.camera_kw_rotate_right || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].tiltUp}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_tilt_up" value={localConfig.camera_kw_tilt_up || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].tiltDown}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_tilt_down" value={localConfig.camera_kw_tilt_down || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].pivotLeft}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_pivot_left" value={localConfig.camera_kw_pivot_left || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].pivotRight}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_pivot_right" value={localConfig.camera_kw_pivot_right || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].moveLeft}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_move_left" value={localConfig.camera_kw_move_left || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].moveRight}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_move_right" value={localConfig.camera_kw_move_right || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].moveUp}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_move_up" value={localConfig.camera_kw_move_up || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].moveDown}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_move_down" value={localConfig.camera_kw_move_down || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].moveForward}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_move_forward" value={localConfig.camera_kw_move_forward || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>

          <div className="unity-inspector-row">
            <span className="unity-inspector-label">{T[lang].moveBackward}</span>
            <div className="unity-inspector-value">
              <input name="camera_kw_move_backward" value={localConfig.camera_kw_move_backward || ''} onChange={handleConfigChange} className="w-full font-mono text-[13px]" />
            </div>
          </div>
        </div>
        <button onClick={saveConfig} className="mt-4 w-full py-2 bg-[var(--accent-blue)] hover:bg-[var(--accent-blue-hover)] text-white border-none rounded font-bold text-xs">
          {T[lang].saveConfig}
        </button>
      </div>

      {/* Authentication Config Panel */}
      <div className="unity-panel">
        <div className="unity-panel-header">{T[lang].authentication}</div>
        
        <div className="flex flex-col gap-2 bg-[var(--bg-darker)] p-3 border border-[var(--border-color)] rounded mb-4 text-xs text-[var(--text-muted)]">
          <div className="flex items-start gap-2">
            <span className="text-[var(--accent-blue)] font-bold text-sm leading-none">ℹ</span>
            <span>{T[lang].firefoxOnlyNotice}</span>
          </div>
        </div>
        
        {authActive ? (
          <div className="flex items-center gap-4 bg-[var(--bg-darker)] p-3 border border-[var(--border-color)] rounded mb-4">
            <img 
              src={authActive.face_url} 
              className="rounded-full border border-[var(--border-color)] object-cover flex-shrink-0" 
              style={{ width: '48px', height: '48px', minWidth: '48px', minHeight: '48px' }}
              alt={authActive.name} 
            />
            <div>
              <div className="font-bold text-xs text-[var(--text-active)]">{authActive.name}</div>
              <div className="text-[10px] text-[var(--text-muted)] font-mono">UID: {authActive.uid}</div>
            </div>
            <div className="ml-auto flex items-center gap-1.5 bg-[var(--bg-dark)] px-2.5 py-1 border border-[var(--border-color)] rounded">
              <span className="w-2 h-2 rounded-full bg-[var(--accent-green)] animate-pulse"></span>
              <span className="text-[10px] font-bold text-[var(--accent-green)] uppercase tracking-wider">
                {T[lang].active}
              </span>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 bg-[var(--bg-darker)]/40 p-3 border border-dashed border-[var(--border-color)] rounded mb-4 text-xs text-[var(--accent-yellow)] font-medium">
            <span className="w-2 h-2 rounded-full bg-[var(--accent-yellow)] animate-pulse"></span>
            {T[lang].scanning}
          </div>
        )}

        {/* QR Code login section */}
        {showQr && qrUrl ? (
          <div className="flex flex-col items-center justify-center bg-[var(--bg-darker)] p-6 border border-[var(--border-color)] rounded mb-4 text-center">
            <div className="text-xs text-[var(--text-main)] mb-3 font-semibold">{T[lang].qrInstructions}</div>
            <div className="bg-white p-3 rounded border border-gray-300 shadow-sm inline-block mb-3">
              <QRCodeSVG value={qrUrl} size={160} />
            </div>
            <div className="text-xs font-semibold mb-4">
              {qrStatus === 'waiting' && <span className="text-[var(--accent-blue-hover)]">{T[lang].qrStatusWaiting}</span>}
              {qrStatus === 'scanned' && <span className="text-[var(--accent-green)] animate-pulse">{T[lang].qrStatusScanned}</span>}
              {qrStatus === 'expired' && <span onClick={startQrLogin} className="text-red-400 cursor-pointer underline">{T[lang].qrStatusExpired}</span>}
            </div>
            <button onClick={() => { setShowQr(false); setQrUrl(null); }} className="px-4 py-1.5 bg-[var(--bg-dark)] border border-[var(--border-color)] hover:bg-[var(--bg-hover)] text-xs rounded font-medium">
              {T[lang].qrClose}
            </button>
          </div>
        ) : (
          <div className="mb-4">
            <button onClick={startQrLogin} className="py-1.5 px-4 bg-[var(--bg-dark)] border border-[var(--border-color)] hover:bg-[var(--bg-hover)] rounded text-xs font-bold text-[var(--text-active)]">
              {T[lang].qrLogin}
            </button>
          </div>
        )}

        {profiles.length > 0 && (
          <div className="mt-4">
            <div className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-2 select-none">
              {T[lang].availableSessions}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {profiles.map(p => (
                <div 
                  key={p.uid} 
                  onClick={() => selectProfile(p)} 
                  className="flex items-center gap-3 bg-[var(--bg-darker)] p-3 rounded cursor-pointer border border-[var(--border-color)] hover:border-[var(--accent-blue)] hover:bg-[var(--bg-hover)] transition-all duration-150 group"
                >
                  <img 
                    src={p.face_url} 
                    className="rounded-full border border-[var(--border-color)] object-cover flex-shrink-0" 
                    style={{ width: '36px', height: '36px', minWidth: '36px', minHeight: '36px' }}
                    alt={p.name} 
                  />
                  <div className="truncate">
                    <div className="font-bold text-xs text-[var(--text-active)] group-hover:text-[var(--accent-blue-hover)] transition-colors duration-150 truncate">{p.name}</div>
                    <div className="text-[10px] text-[var(--text-muted)] font-mono truncate">UID: {p.uid}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
