import asyncio
from Utils.pretty_print_event import pretty_print_event
from app.config_loader import CONFIG
import logging
logger = logging.getLogger(__name__)


async def handle_enter(event: dict, update_chatbox: bool, update_osc_param: bool, osc_queue: asyncio.Queue):
    username: str = event["data"]["data"]["pb_decoded"]['uname']
    # 0: 路人 1: 粉丝牌 2: 舰长 3: 提督 4：总督
    identity: int = event["data"]["data"]["pb_decoded"]["identities"][0]
    if update_chatbox:
        if identity == 0 and CONFIG['enter_level'][0] == 1:
            osc_queue.put(('CHATBOX', f"欢迎{username}进入直播间"))
        elif identity == 1 and CONFIG['enter_level'][1] == 1:
            osc_queue.put(('CHATBOX', f"粉丝{username}进入直播间"))
        elif identity == 2 and CONFIG['enter_level'][2] == 1:
            osc_queue.put(('CHATBOX', f"舰长{username}进入直播间"))
        elif identity == 3 and CONFIG['enter_level'][3] == 1:
            osc_queue.put(('CHATBOX', f"提督{username}进入直播间"))
        elif identity == 4 and CONFIG['enter_level'][4] == 1:
            osc_queue.put(('CHATBOX', f"总督{username}进入直播间"))
        else:
            logger.info("未知进房身份%s", str(
                event["data"]["data"]["pb_decoded"]["identities"]))

    else:
        pass
