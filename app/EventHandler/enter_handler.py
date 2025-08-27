"""
Enter handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
import logging
from app.Utils.config_loader import CONFIG
from app.Utils.int2float8 import int2f8
from app.Utils.name2id import NAME_EVENT_ID
from app.osc.vrc_osc_singleton_client import update_parameter
from app.osc_queue import chatbox_queue, general_gift_queue, animation_counts, set_parameter_value
logger = logging.getLogger(__name__)


async def handle_enter(event: dict, update_chatbox: bool, update_osc_param: bool):
    """
    handle audience enter events
    """
    try:
        username: str = event["data"]["data"]["pb_decoded"]['uname']
        # uid: int = event["data"]["data"]["pb_decoded"]['uid']
        # 0: 路人 1: 粉丝牌 2: 舰长 3: 提督 4：总督
        # TODO: new protobuf need investigation https://github.com/Nemo2011/bilibili-api/issues/955
        identity: int = 0
        # logger.debug("Got event %s", str(event))
    except KeyError:
        logger.error("进房信息缺失")
        logger.debug("进房事件解析失败: %s", event, exc_info=True)
        return
    if update_chatbox:
        if CONFIG['enter']['enter_level'][identity] == 1:
            min_display_time: int = CONFIG['enter']['min_display_time'][identity]
            identity_str: str = ""
            match identity:
                case 0:
                    identity_str = "欢迎"
                case 1:
                    identity_str = "粉丝"
                case 2:
                    identity_str = "舰长"
                case 3:
                    identity_str = "提督"
                case 4:
                    identity_str = "总督"
                case _:
                    logger.info("未知进房身份%s", str(identity))
            await chatbox_queue.put((f"{identity_str}{username}进入直播间", min_display_time))
        else:
            pass
    if update_osc_param:
        str_identity = 'enter_' + str(identity)
        if str_identity in CONFIG["animation_accumulate"]["animation"]:  # 动画
            animation_counts[str_identity] += 1
            logger.info("动画进房 %s", str_identity)
        elif str_identity in CONFIG["set_parameter"]["parameter_keywords"]:  # 变化
            set_index: int = CONFIG["set_parameter"]["parameter_keywords"].index(
                str_identity)
            is_increase: bool = set_index % 2 == 0
            set_index = set_index // 2
            parameter_name: str = CONFIG["set_parameter"]["parameter_names"][set_index]
            step: int = CONFIG["set_parameter"]["parameter_increment"][set_index]
            if is_increase:
                set_parameter_value[parameter_name] = min(
                    set_parameter_value[parameter_name] + step * 1, 100)
            else:
                set_parameter_value[parameter_name] = max(
                    set_parameter_value[parameter_name] - step * 1, 0)
            logger.info("变化进房 %s", str_identity)
            update_parameter(parameter_name, int2f8(
                set_parameter_value[parameter_name]))
        else:  # 通用表情
            logger.info("通用进房 %s", str(identity))
            await general_gift_queue.put((NAME_EVENT_ID['ENTER'], 1))
