"""
Enter handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from app.config_loader import CONFIG
from app.osc_queue import chatbox_queue
import logging
logger = logging.getLogger(__name__)


async def handle_enter(event: dict, update_chatbox: bool, update_osc_param: bool):
    try:
        username: str = event["data"]["data"]["pb_decoded"]['uname']
        # 0: 路人 1: 粉丝牌 2: 舰长 3: 提督 4：总督
        identity: int = event["data"]["data"]["pb_decoded"]["identities"][0]
    except KeyError:
        logger.warning("进房信息缺失%s", str(event))
        return
    if update_chatbox:
        if identity == 0 and CONFIG['enter']['enter_level'][identity] == 1:
            await chatbox_queue.put((f"欢迎{username}进入直播间", CONFIG['enter']['min_display_time'][identity]))
        elif identity == 1 and CONFIG['enter']['enter_level'][identity] == 1:
            await chatbox_queue.put((f"粉丝{username}进入直播间", CONFIG['enter']['min_display_time'][identity]))
        elif identity == 2 and CONFIG['enter']['enter_level'][identity] == 1:
            await chatbox_queue.put((f"舰长{username}进入直播间", CONFIG['enter']['min_display_time'][identity]))
        elif identity == 3 and CONFIG['enter']['enter_level'][identity] == 1:
            await chatbox_queue.put((f"提督{username}进入直播间", CONFIG['enter']['min_display_time'][identity]))
        elif identity == 4 and CONFIG['enter']['enter_level'][identity] == 1:
            await chatbox_queue.put((f"总督{username}进入直播间", CONFIG['enter']['min_display_time'][identity]))
        elif identity not in [0, 1, 2, 3, 4]:
            logger.info("未知进房身份%s", str(
                event["data"]["data"]["pb_decoded"]["identities"]))
        else:
            pass
    else:
        pass
    # TODO: update params
