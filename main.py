"""
Main event dispatcher from bilibili danmaku stream events to handlers
(c) 2025 TZFC tianzifangchen@gmail.com
"""
import asyncio
from app.browser_credential import get_credentials
from app.user_config import load_user_config
from Utils.EVENT_IDX import *
from EventHandler.Danmaku_emoticon_handler import handle_emoticon
from EventHandler.Danmaku_text_handler import handle_text
from EventHandler.Enter_handler import handle_enter
from EventHandler.Gift_handler import handle_gift
from EventHandler.Guard_handler import handle_guard
from EventHandler.Warning_handler import handle_warning
from EventHandler.Sc_handler import handle_sc
from app.vrc_osc_send import send_vrchat_osc
from app.vrc_osc_singleton_client import aclose
from bilibili_api import Credential
from bilibili_api.live import LiveDanmaku
import logging
logger = logging.getLogger(__name__)

async def main():
    try:
        # 获取用户设置
        user_config: dict = load_user_config()

        # 获取登录信息
        my_credential: Credential = get_credentials()
        live_danmaku: LiveDanmaku = LiveDanmaku(
            room_display_id=user_config["room_id"],
            credential=my_credential)

        # 创建异步OSC请求队列 
        # 更新参数请求      ("PARAMETER", (name, value)) 
        # 更新聊天框请求    ("CHATBOX", (message, immediate))
        osc_queue: asyncio.Queue = asyncio.Queue()
        
        # 启动事件分发
        async def dispatch(event_name: str, event: dict, handler):
            if user_config['events'][event_name] == 0:
                return
            elif user_config['events'][event_name] == 1:
                await handler(event, update_chatbox=True, update_osc_param=False, osc_queue = osc_queue)
            elif user_config['events'][event_name] == 2:
                await handler(event, update_chatbox=False, update_osc_param=True, osc_queue = osc_queue)
            elif user_config['events'][event_name] == 3:
                await handler(event, update_chatbox=True, update_osc_param=True, osc_queue = osc_queue)
            else:
                logger.warning(
                    f"未知{event_name}用户设置{user_config['events'][event_name]}")
            logger.info(f"分发事件{event_name}")
        
        # 收到进房
        @live_danmaku.on('INTERACT_WORD')
        async def on_interact(event: dict):
            await dispatch('enter', event, handle_enter)
        
        # 收到弹幕或表情包
        @live_danmaku.on('DANMU_MSG')
        async def on_danmaku(event: dict):
            message_type: int = event["data"]["info"][0][MSG_TYPE_IDX]
            if message_type == TEXT_TYPE:  # 文字弹幕
                await dispatch('danmaku', event, handle_text)
            elif message_type == EMOTICON_TYPE:  # 表情包
                await dispatch('emoticon', event, handle_emoticon)
        
        # 收到礼物
        @live_danmaku.on('SEND_GIFT')
        async def on_gift(event: dict):
            await dispatch('gift', event, handle_gift)
        
        # 其它事件
        @live_danmaku.on('ALL')
        async def on_all(event: dict):
            # 收到sc
            if event['type'] in {'SUPER_CHAT_MESSAGE', 'SUPER_CHAT_MESSAGE_JPN'}:
                await dispatch('sc', event, handle_sc)
            # 收到舰长
            elif event['type'] == 'GUARD_BUY':
                await dispatch('guard', event, handle_guard)
            # 收到警告
            elif event['type'] == 'WARNING':
                await dispatch('warning', event, handle_warning)
        
        async with asyncio.TaskGroup() as tg:
            # 链接VRChatOSC
            tg.create_task(send_vrchat_osc(osc_queue))

            # 连接直播间
            tg.create_task(live_danmaku.connect())
    except* asyncio.CancelledError:
        pass
    
def run():
    try:
        asyncio.run(main())
        return 0
    except KeyboardInterrupt:
        return 130

if __name__ == "__main__":
    run()

