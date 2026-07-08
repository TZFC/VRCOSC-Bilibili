import os
import sys
from typing import Any, Dict, List, Optional

from sqlmodel import JSON, Column, Field, Session, SQLModel, create_engine, select

if getattr(sys, "frozen", False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

db_path = os.path.join(application_path, "vrcosc_bilibili_v3.db")
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url, echo=False)


class AppConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bili_room_id: int = Field(default=0)
    osc_client_ip: str = Field(default="127.0.0.1")
    osc_client_port: int = Field(default=9000)
    osc_server_ip: str = Field(default="127.0.0.1")
    osc_server_port: int = Field(default=9001)
    
    camera_move_x_step: float = Field(default=0.5)
    camera_move_y_step: float = Field(default=0.5)
    camera_move_z_step: float = Field(default=0.5)
    camera_rotate_x_step: float = Field(default=15.0)
    camera_rotate_y_step: float = Field(default=15.0)
    camera_rotate_z_step: float = Field(default=15.0)

    camera_kw_rotate_left: str = Field(default="rotate left,向左旋转,left rotation")
    camera_kw_rotate_right: str = Field(default="rotate right,向右旋转,right rotation")
    camera_kw_tilt_up: str = Field(default="tilt up,向上倾斜,look up,抬头")
    camera_kw_tilt_down: str = Field(default="tilt down,向下倾斜,look down,低头")
    camera_kw_pivot_left: str = Field(default="pivot left,向左偏转,left yaw,左转")
    camera_kw_pivot_right: str = Field(default="pivot right,向右偏转,right yaw,右转")
    camera_kw_move_left: str = Field(default="move left,向左移动,左移")
    camera_kw_move_right: str = Field(default="move right,向右移动,右移")
    camera_kw_move_up: str = Field(default="move up,向上移动,上移")
    camera_kw_move_down: str = Field(default="move down,向下移动,下移")
    camera_kw_move_forward: str = Field(default="move forward,向前移动,前移,前进")
    camera_kw_move_backward: str = Field(default="move backward,向后移动,后移,后退")


class Rule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="New Rule")
    enabled: bool = Field(default=True)
    event_type: str = Field(default="Danmaku")
    condition_keyword: str = Field(default="")
    condition_min_value: float = Field(default=0.0)
    osc_endpoint: str = Field(default="/avatar/parameters/MyParam")
    action_type: str = Field(default="Set")
    action_value: str = Field(default="true")
    sync_mode: str = Field(default="Overwrite")


class AuthProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uid: int
    name: str
    face_url: str
    bili_jct: str
    dedeuserid: str
    sessdata: str
    buvid3: str
    is_active: bool = Field(default=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def migrate_db():
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(appconfig)")
    columns = [row[1] for row in cursor.fetchall()]
    
    new_cols = {
        "camera_move_x_step": "REAL DEFAULT 0.5",
        "camera_move_y_step": "REAL DEFAULT 0.5",
        "camera_move_z_step": "REAL DEFAULT 0.5",
        "camera_rotate_x_step": "REAL DEFAULT 15.0",
        "camera_rotate_y_step": "REAL DEFAULT 15.0",
        "camera_rotate_z_step": "REAL DEFAULT 15.0",
        "camera_kw_rotate_left": "TEXT DEFAULT 'rotate left,向左旋转,左旋'",
        "camera_kw_rotate_right": "TEXT DEFAULT 'rotate right,向右旋转,右旋'",
        "camera_kw_tilt_up": "TEXT DEFAULT 'tilt up,向上倾斜,仰角,抬头'",
        "camera_kw_tilt_down": "TEXT DEFAULT 'tilt down,向下倾斜,俯角,低头'",
        "camera_kw_pivot_left": "TEXT DEFAULT 'pivot left,向左偏转,左偏,左转'",
        "camera_kw_pivot_right": "TEXT DEFAULT 'pivot right,向右偏转,右偏,右转'",
        "camera_kw_move_left": "TEXT DEFAULT 'move left,向左移动,左移'",
        "camera_kw_move_right": "TEXT DEFAULT 'move right,向右移动,右移'",
        "camera_kw_move_up": "TEXT DEFAULT 'move up,向上移动,上移'",
        "camera_kw_move_down": "TEXT DEFAULT 'move down,向下移动,下移'",
        "camera_kw_move_forward": "TEXT DEFAULT 'move forward,向前移动,前移,前进'",
        "camera_kw_move_backward": "TEXT DEFAULT 'move backward,向后移动,后移,后退'"
    }
    
    for col, col_type in new_cols.items():
        if col not in columns:
            try:
                cursor.execute(f"ALTER TABLE appconfig ADD COLUMN {col} {col_type}")
                print(f"Database migration: Added column {col} to appconfig")
            except Exception as e:
                print(f"Failed to add column {col}: {e}")
                
    conn.commit()
    conn.close()


def init_db():
    create_db_and_tables()
    migrate_db()
    with Session(engine) as session:
        config = session.exec(select(AppConfig)).first()
        if not config:
            config = AppConfig()
            session.add(config)
            session.commit()

