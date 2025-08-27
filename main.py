"""
Entry point of sending Bilibili events to VRCOSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - bilibili-api-python (see its license in the dependency's repository)

VRChat is a trademark of VRChat Inc.
BILIBILI is a trademark of Shanghai Hode Information Technology Co., Ltd.
"""
import argparse
import asyncio
import logging
import signal
from contextlib import asynccontextmanager, suppress
import sys
parser = argparse.ArgumentParser()
parser.add_argument(
    "--log",
    default="warning",
    choices=["debug", "info", "warning", "error", "critical"],
    help="Set the logging level"
)
args = parser.parse_args()
log_level = getattr(logging, args.log.upper(), logging.WARNING)
error_handler = logging.FileHandler("error-log.txt", encoding="utf-8")
error_handler.setLevel(logging.ERROR)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), error_handler],
)
from app.Utils.config_loader import CONFIG
from app.bili_event_dispatch import live_danmaku
from app.chatbox_consumer import chatbox_loop
from app.animation_consumer import animation_loop
from app.general_consumer import general_loop
from app.parameter_decay_consumer import parameter_decay_loop
logger = logging.getLogger(__name__)


@asynccontextmanager
async def bilibili_connection():
    """Manage LiveDanmaku connection."""
    task = asyncio.create_task(live_danmaku.connect())
    try:
        yield
    finally:
        task.cancel()
        with suppress(Exception):
            await live_danmaku.disconnect()


async def main():
    """Start tasks and handle graceful shutdown."""
    shutdown_event = asyncio.Event()

    def _handle_shutdown() -> None:
        logger.info("Received termination signal, shutting down...")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _handle_shutdown)

    async with bilibili_connection():
        async with asyncio.TaskGroup() as tg:
            tg.create_task(chatbox_loop())
            tg.create_task(animation_loop())
            tg.create_task(parameter_decay_loop())
            tg.create_task(general_loop())
            await shutdown_event.wait()
            tg.cancel_scope.cancel()


if __name__ == "__main__":
    logger.info("配置： %s", str(CONFIG))
    asyncio.run(main())
