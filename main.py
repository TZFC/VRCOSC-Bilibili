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
from app.bili_event_dispatch import live_danmaku, osc_queue
from app.request_consumer import process_request_loop
from app.osc_queue import osc_queue
import argparse
import logging
logger = logging.getLogger(__name__)


async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            # 链接VRChatOSC
            tg.create_task(process_request_loop())

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
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
    else:
        sys.exit(0)
