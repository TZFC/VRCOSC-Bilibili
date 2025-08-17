"""
Entry point of sending Bilibili events to VRCOSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - bilibili-api-python (see its license in the dependency's repository)

VRChat is a trademark of VRChat Inc.
BILIBILI is a trademark of Shanghai Hode Information Technology Co., Ltd.
"""
import asyncio
import sys
import argparse
import logging
from app.bili_event_dispatch import live_danmaku
from app.chatbox_consumer import chatbox_loop
from app.animation_consumer import animation_loop
from app.general_consumer import general_loop
from app.Utils.config_loader import CONFIG
logger = logging.getLogger(__name__)


async def main():
    """
    start tasks
    """
    try:
        async with asyncio.TaskGroup() as tg:
            # 聊天框队列
            tg.create_task(chatbox_loop())

            # 独立动画队列
            tg.create_task(animation_loop())

            # 通用动画队列
            tg.create_task(general_loop())

            # 连接直播间
            tg.create_task(live_danmaku.connect())
    except* asyncio.CancelledError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set the logging level"
    )
    args = parser.parse_args()
    log_level = getattr(logging, args.log.upper(), logging.WARNING)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    try:
        logger.info("配置： %s", str(CONFIG))
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
    else:
        sys.exit(0)
