import asyncio
import webbrowser
import contextlib
import uvicorn
import os
from fastapi import FastAPI, Depends, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import select, Session
from pydantic import BaseModel
from typing import List, Optional

from database import init_db, get_session, AppConfig, Rule, AuthProfile, engine
from auth.bili_auth import get_bilibili_cookies_from_browser, save_auth_profile, get_active_auth_profile
from engine.rule_engine import rule_engine
from engine.osc_manager import osc_manager
from bili_client import bili_client_manager

import logging

logger = logging.getLogger(__name__)

# Websocket manager for logs
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

ws_manager = ConnectionManager()

class WsLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(ws_manager.broadcast(msg))
        except:
            pass

ws_handler = WsLogHandler()
ws_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logging.getLogger().addHandler(ws_handler)
logging.getLogger().setLevel(logging.INFO)

# Determine if we are running from PyInstaller
base_dir = os.path.dirname(__file__)
static_dir = os.path.join(base_dir, "static")

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    with Session(engine) as session:
        config = session.exec(select(AppConfig)).first()
        active_auth = get_active_auth_profile(session)
        
    osc_manager.setup(
        config.osc_client_ip, 
        config.osc_client_port, 
        config.osc_server_ip, 
        config.osc_server_port, 
        rule_engine.on_osc_message_received
    )
    
    await osc_manager.start_server()
    
    if config.bili_room_id > 0:
        cred = active_auth.model_dump() if active_auth else None
        await bili_client_manager.connect(config.bili_room_id, cred)
        
    # Open browser
    if os.path.exists(static_dir):
        webbrowser.open("http://localhost:8000")
    else:
        webbrowser.open("http://localhost:5173") # Dev mode
    
    yield
    
    await bili_client_manager.disconnect()
    osc_manager.stop_server()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/api/config")
def get_config(session: Session = Depends(get_session)):
    return session.exec(select(AppConfig)).first()

@app.post("/api/config")
async def update_config(config_data: AppConfig, session: Session = Depends(get_session)):
    config = session.exec(select(AppConfig)).first()
    config.bili_room_id = config_data.bili_room_id
    config.osc_client_ip = config_data.osc_client_ip
    config.osc_client_port = config_data.osc_client_port
    config.osc_server_ip = config_data.osc_server_ip
    config.osc_server_port = config_data.osc_server_port
    session.add(config)
    session.commit()
    
    # Reconfigure OSC and Bilibili
    osc_manager.setup(config.osc_client_ip, config.osc_client_port, config.osc_server_ip, config.osc_server_port, rule_engine.on_osc_message_received)
    await osc_manager.start_server()
    
    active_auth = get_active_auth_profile(session)
    cred = active_auth.model_dump() if active_auth else None
    await bili_client_manager.connect(config.bili_room_id, cred)
    return {"status": "ok"}

@app.get("/api/rules")
def get_rules(session: Session = Depends(get_session)):
    return session.exec(select(Rule)).all()

@app.post("/api/rules")
def create_rule(rule: Rule, session: Session = Depends(get_session)):
    session.add(rule)
    session.commit()
    session.refresh(rule)
    rule_engine.reload_rules()
    return rule

@app.put("/api/rules/{rule_id}")
def update_rule(rule_id: int, rule_data: Rule, session: Session = Depends(get_session)):
    rule = session.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for k, v in rule_data.model_dump(exclude_unset=True).items():
        setattr(rule, k, v)
    session.add(rule)
    session.commit()
    session.refresh(rule)
    rule_engine.reload_rules()
    return rule

@app.delete("/api/rules/{rule_id}")
def delete_rule(rule_id: int, session: Session = Depends(get_session)):
    rule = session.get(Rule, rule_id)
    if rule:
        session.delete(rule)
        session.commit()
        rule_engine.reload_rules()
    return {"status": "ok"}

@app.get("/api/rules/export")
def export_rules(session: Session = Depends(get_session)):
    rules = session.exec(select(Rule)).all()
    return [r.model_dump() for r in rules]

@app.post("/api/rules/import")
def import_rules(rules: List[Rule], session: Session = Depends(get_session)):
    # Clear existing rules
    existing = session.exec(select(Rule)).all()
    for r in existing:
        session.delete(r)
    
    for r in rules:
        r.id = None # Let DB auto-increment
        session.add(r)
        
    session.commit()
    rule_engine.reload_rules()
    return {"status": "ok", "imported": len(rules)}

@app.get("/api/auth/scan")
def scan_browser_auth(session: Session = Depends(get_session)):
    profiles = get_bilibili_cookies_from_browser()
    return profiles

@app.post("/api/auth/select")
async def select_auth_profile(profile: dict, session: Session = Depends(get_session)):
    saved = save_auth_profile(session, profile, set_active=True)
    config = session.exec(select(AppConfig)).first()
    if config.bili_room_id > 0:
        await bili_client_manager.connect(config.bili_room_id, saved.model_dump())
    return {"status": "ok"}

@app.get("/api/auth/active")
def get_active_auth(session: Session = Depends(get_session)):
    return get_active_auth_profile(session)

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        ws_manager.disconnect(websocket)

# Serve React App
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
