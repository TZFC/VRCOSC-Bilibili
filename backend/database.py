import os
from typing import Any, Dict, List, Optional

from sqlmodel import (JSON, Column, Field, Session, SQLModel, create_engine,
                      select)

db_path = "vrcosc_bilibili_v3.db"
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url, echo=False)


class AppConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bili_room_id: int = Field(default=0)
    osc_client_ip: str = Field(default="127.0.0.1")
    osc_client_port: int = Field(default=9000)
    osc_server_ip: str = Field(default="127.0.0.1")
    osc_server_port: int = Field(default=9001)


class Rule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="New Rule")
    enabled: bool = Field(default=True)
    # Triggers
    event_type: str = Field(default="Danmaku")  # Danmaku, Gift, SC, Guard, Enter
    condition_keyword: str = Field(default="")
    condition_min_value: float = Field(default=0.0)  # Used for Gift price, SC price
    # Actions
    osc_endpoint: str = Field(default="/avatar/parameters/MyParam")
    action_type: str = Field(default="Set")  # Set, Add, Toggle
    action_value: str = Field(default="true")
    # Bi-directional sync
    sync_mode: str = Field(default="Overwrite")  # Overwrite, Respect


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


def init_db():
    create_db_and_tables()
    with Session(engine) as session:
        config = session.exec(select(AppConfig)).first()
        if not config:
            config = AppConfig()
            session.add(config)
            session.commit()
