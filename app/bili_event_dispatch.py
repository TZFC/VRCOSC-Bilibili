"""
Main event dispatcher from Bilibili danmaku stream events to event handlers

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - bilibili-api-python (see its license in the dependency's repository)

BILIBILI is a trademark of Shanghai Hode Information Technology Co., Ltd.
"""
import logging
from bilibili_api import Credential
from bilibili_api.live import LiveDanmaku
from app.Utils.constants import MSG_TYPE_IDX, TEXT_TYPE, EMOTICON_TYPE
from app.Utils.config_loader import CONFIG
from app.Utils.browser_credential import get_credentials
from app.EventHandler.danmaku_emoticon_handler import handle_emoticon
from app.EventHandler.danmaku_text_handler import handle_text
from app.EventHandler.enter_handler import handle_enter
from app.EventHandler.gift_handler import handle_gift
from app.EventHandler.guard_handler import handle_guard
from app.EventHandler.warning_handler import handle_warning
from app.EventHandler.sc_handler import handle_sc
logger = logging.getLogger(__name__)

# 获取登录信息
my_credential: Credential = get_credentials()
live_danmaku: LiveDanmaku = LiveDanmaku(
    room_display_id=CONFIG["room_id"],
    credential=my_credential)


# 启动事件分发
async def dispatch(event_name: str, event: dict, handler) -> None:
    """
    dispatch events to corresponding handler according to user CONFIG
    """
    dispatch_level: int = CONFIG['events'][event_name]
    match dispatch_level:
        case 0:
            return
        case 1:
            await handler(event, update_chatbox=True, update_osc_param=False)
        case 2:
            await handler(event, update_chatbox=False, update_osc_param=True)
        case 3:
            await handler(event, update_chatbox=True, update_osc_param=True)
        case _:
            logger.error("%s 事件有未知等级 %d", event_name, dispatch_level)
            logger.debug("事件详情: %s", event)
    logger.debug("分发事件 %s", event_name)


@live_danmaku.on('INTERACT_WORD_V2')
async def on_interact(event: dict):
    """
    收到进房
    """
    await dispatch('enter', event, handle_enter)


@live_danmaku.on('DANMU_MSG')
async def on_danmaku(event: dict):
    """
    收到弹幕或表情包
    """
    try:
        message_type: int = event["data"]["info"][0][MSG_TYPE_IDX]
    except (IndexError, KeyError, TypeError) as e:
        logger.error("弹幕事件解析失败: %s", str(e))
        logger.debug("弹幕事件内容: %s", event, exc_info=True)
        return
    if message_type == TEXT_TYPE:  # 文字弹幕
        await dispatch('danmaku', event, handle_text)
    elif message_type == EMOTICON_TYPE:  # 表情包
        await dispatch('emoticon', event, handle_emoticon)
    else:
        logger.error("未知弹幕类型 %d", message_type)
        logger.debug("无法解析的弹幕事件: %s", event)


@live_danmaku.on('SEND_GIFT')
async def on_gift(event: dict):
    """
    收到礼物
    """
    await dispatch('gift', event, handle_gift)


@live_danmaku.on('SUPER_CHAT_MESSAGE')
async def on_sc(event: dict):
    """
    收到sc
    """
    await dispatch('sc', event, handle_sc)


@live_danmaku.on('GUARD_BUY')
async def on_guard_buy(event: dict):
    """
    收到舰长
    """
    await dispatch('guard', event, handle_guard)


@live_danmaku.on('WARNING')
async def on_warning(event: dict):
    """
    收到警告
    """
    await dispatch('warning', event, handle_warning)
