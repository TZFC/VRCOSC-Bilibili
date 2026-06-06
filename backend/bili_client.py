import asyncio
from bilibili_api import live, sync, Credential
from engine.rule_engine import rule_engine
import logging

logger = logging.getLogger(__name__)

class BiliClientManager:
    def __init__(self):
        self.room = None
        self.task = None

    async def connect(self, room_id: int, credential_dict: dict = None):
        await self.disconnect()
        
        cred = None
        if credential_dict:
            cred = Credential(
                sessdata=credential_dict.get("sessdata", ""),
                bili_jct=credential_dict.get("bili_jct", ""),
                buvid3=credential_dict.get("buvid3", ""),
                dedeuserid=credential_dict.get("dedeuserid", "")
            )
            
        self.room = live.LiveDanmaku(room_id, credential=cred)
        
        @self.room.on("DANMU_MSG")
        async def on_danmaku(event):
            msg = event["data"]["info"][1]
            uname = event["data"]["info"][2][1]
            logger.info(f"[Danmaku] {uname}: {msg}")
            rule_engine.process_bili_event("Danmaku", {"message": msg, "user": uname})

        @self.room.on("SEND_GIFT")
        async def on_gift(event):
            data = event["data"]["data"]
            gift_name = data["giftName"]
            uname = data["uname"]
            price = data["price"] * data["num"] / 1000 # coin to rmb approx
            logger.info(f"[Gift] {uname} sent {gift_name} (Value: {price})")
            rule_engine.process_bili_event("Gift", {"gift_name": gift_name, "user": uname, "price": price})

        @self.room.on("SUPER_CHAT_MESSAGE")
        async def on_superchat(event):
            data = event["data"]["data"]
            msg = data["message"]
            uname = data["user_info"]["uname"]
            price = data["price"]
            logger.info(f"[SuperChat] {uname}: {msg} (¥{price})")
            rule_engine.process_bili_event("SC", {"message": msg, "user": uname, "price": price})
            
        @self.room.on("INTERACT_WORD")
        async def on_interact(event):
            data = event["data"]["data"]
            uname = data["uname"]
            msg_type = data.get("msg_type", 1) # 1=Enter
            if msg_type == 1:
                logger.info(f"[Enter] {uname} joined")
                rule_engine.process_bili_event("Enter", {"user": uname})

        self.task = asyncio.create_task(self.room.connect())
        logger.info(f"Connecting to Bilibili Room {room_id}...")

    async def disconnect(self):
        if self.room and self.task:
            logger.info("Disconnecting from Bilibili...")
            await self.room.disconnect()
            self.task.cancel()
            self.room = None
            self.task = None

bili_client_manager = BiliClientManager()
