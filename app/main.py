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
from bilibili_api import Credential, sync
from bilibili_api.live import LiveDanmaku
from typing import *
import logging
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    ## 获取用户设置
    user_config: dict = load_user_config()

    ## 获取登录信息
    my_credential: Credential = get_credentials()

    live_danmaku: LiveDanmaku = LiveDanmaku(
        room_display_id=user_config["room_id"],
        credential=my_credential)
    
    ## 启动事件分发
    # 收到进房
    @live_danmaku.on('INTERACT_WORD')
    async def on_interact(event: Dict):
        await handle_enter(event)
    # 收到弹幕
    @live_danmaku.on('DANMU_MSG')
    async def on_danmaku(event: Dict):
        message_type: int = event["data"]["info"][0][MSG_TYPE_IDX]
        if message_type == TEXT_TYPE: # 文字弹幕
            await handle_text(event)
        elif message_type == EMOTICON_TYPE: # 表情包
            await handle_emoticon(event)
        else:
            logger.warning(f"未知弹幕类型{message_type}:\n{event}")
    # 收到礼物
    @live_danmaku.on('SEND_GIFT')
    async def on_gift(event: Dict):
        await handle_gift(event)
    # 其它事件
    @live_danmaku.on('ALL')
    async def on_all(event: Dict):
        # 收到sc
        if event['type'] in {'SUPER_CHAT_MESSAGE', 'SUPER_CHAT_MESSAGE_JPN'}: 
            await handle_sc(event)
        # 收到舰长
        elif event['type'] == 'GUARD_BUY':
            await handle_guard(event)
        # 收到警告
        elif event['type'] == 'WARNING':
            await handle_warning(event)
    

    # 连接直播间
    sync(live_danmaku.connect())