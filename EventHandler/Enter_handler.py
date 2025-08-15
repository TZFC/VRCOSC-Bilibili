"""
Enter handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from app.config_loader import CONFIG
from Utils.int2float8 import int2f8
from app.osc.vrc_osc_singleton_client import update_parameter
from app.osc_queue import chatbox_queue, general_gift_queue, animation_counts, set_parameter_value
import logging
logger = logging.getLogger(__name__)


async def handle_enter(event: dict, update_chatbox: bool, update_osc_param: bool):
    try:
        username: str = event["data"]["data"]["pb_decoded"]['uname']
        # 0: 路人 1: 粉丝牌 2: 舰长 3: 提督 4：总督
        identity: int = 0 # TODO: new protobuf need investigation https://github.com/Nemo2011/bilibili-api/issues/955
        logger.debug("Got event %s", str(event))
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
    if update_osc_param:
        if str(identity) in CONFIG["animation_accumulate"]["animation"]:  # 动画
            animation_counts[text] += 1
            logger.info("动画进房 %s", text)
        elif str(identity) in CONFIG["set_parameter"]["parameter_keywords"]:  # 变化
            set_index: int = CONFIG["set_parameter"]["parameter_keywords"].index(
                str(identity))
            is_increase: bool = set_index % 2 == 0
            set_index = set_index // 2
            parameter_name: str = CONFIG["set_parameter"]["parameter_names"][set_index]
            step: int = CONFIG["set_parameter"]["parameter_increment"][set_index]
            if is_increase:
                set_parameter_value[parameter_name] += step * 1
            else:
                set_parameter_value[parameter_name] -= step * 1
            logger.info("变化进房 %s", str(identity))
            update_parameter(parameter_name, int2f8(
                set_parameter_value[parameter_name]))
        else:  # 通用表情
            logger.info("通用进房 %s", str(identity))
            await general_gift_queue.put((str(identity), 1))
