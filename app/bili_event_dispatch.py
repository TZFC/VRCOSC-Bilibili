"""
Main event dispatcher from Bilibili danmaku stream events to event handlers

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - bilibili-api-python (see its license in the dependency's repository)

BILIBILI is a trademark of Shanghai Hode Information Technology Co., Ltd.
"""
from bilibili_api import Credential
from bilibili_api.live import LiveDanmaku
from app.config_loader import CONFIG
from app.browser_credential import get_credentials
import asyncio
from Utils.EVENT_IDX import *
from EventHandler.Danmaku_emoticon_handler import handle_emoticon
from EventHandler.Danmaku_text_handler import handle_text
from EventHandler.Enter_handler import handle_enter
from EventHandler.Gift_handler import handle_gift
from EventHandler.Guard_handler import handle_guard
from EventHandler.Warning_handler import handle_warning
from EventHandler.Sc_handler import handle_sc
import logging
logger = logging.getLogger(__name__)

# 获取登录信息
my_credential: Credential = get_credentials()
live_danmaku: LiveDanmaku = LiveDanmaku(
    room_display_id=CONFIG["room_id"],
    credential=my_credential)

# 创建异步OSC请求队列
# 更新参数请求      ("PARAMETER", (name, value))
# 更新聊天框请求    ("CHATBOX", (message, immediate))
osc_queue: asyncio.Queue = asyncio.Queue()

# 启动事件分发
def dispatch(event_name: str, event: dict, handler):
    if CONFIG['events'][event_name] == 0:
        return
    elif CONFIG['events'][event_name] == 1:
        handler(event, update_chatbox=True,
                update_osc_param=False, osc_queue=osc_queue)
    elif CONFIG['events'][event_name] == 2:
        handler(event, update_chatbox=False,
                update_osc_param=True, osc_queue=osc_queue)
    elif CONFIG['events'][event_name] == 3:
        handler(event, update_chatbox=True,
                update_osc_param=True, osc_queue=osc_queue)
    else:
        logger.warning(
            f"未知{event_name}用户设置{CONFIG['events'][event_name]}")
    logger.info(f"分发事件{event_name}")

# 收到进房
@live_danmaku.on('INTERACT_WORD_V2')
async def on_interact(event: dict):
    dispatch('enter', event, handle_enter)

# 收到弹幕或表情包
@live_danmaku.on('DANMU_MSG')
async def on_danmaku(event: dict):
    message_type: int = event["data"]["info"][0][MSG_TYPE_IDX]
    if message_type == TEXT_TYPE:  # 文字弹幕
        dispatch('danmaku', event, handle_text)
    elif message_type == EMOTICON_TYPE:  # 表情包
        dispatch('emoticon', event, handle_emoticon)
    else:
        logger.warning("未知弹幕类型 %d", message_type)

# 收到礼物
@live_danmaku.on('SEND_GIFT')
async def on_gift(event: dict):
    dispatch('gift', event, handle_gift)

# 收到sc
@live_danmaku.on('SUPER_CHAT_MESSAGE')
async def on_sc(event: dict):
    dispatch('sc', event, handle_sc)

# 收到舰长
@live_danmaku.on('GUARD_BUY')
async def on_guard_buy(event: dict):
    dispatch('guard', event, handle_guard)

# 收到警告
@live_danmaku.on('WARNING')
async def on_warning(event: dict):
    dispatch('warning', event, handle_warning)