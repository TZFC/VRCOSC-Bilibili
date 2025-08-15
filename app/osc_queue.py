"""
Async queues and accumulators, bilibili events as producer, osc client as consumer

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - bilibili-api-python (see its license in the dependency's repository)

BILIBILI is a trademark of Shanghai Hode Information Technology Co., Ltd.
"""
import asyncio
import logging
from app.config_loader import CONFIG
logger = logging.getLogger(__name__)

# 创建聊天框队列
# 事件：(text, min_display_time=0)
chatbox_queue: asyncio.Queue = asyncio.Queue()

# 创建特殊动画累积
animation_counts: dict[str:int] = {}
for animation_name in CONFIG["animation_accumulate"]["animation"]:
    animation_counts[animation_name] = 0

# 创建设置参数累积
set_parameter_value: dict[str:int] = {}
for parameter_name, value in zip(CONFIG["set_parameter"]["parameter_names"], CONFIG["set_parameter"]["parameter_default"]):
    set_parameter_value[parameter_name] = value

# 创建通用礼物队列
# 事件: (gift_name, gift_num)
general_gift_queue: asyncio.Queue = asyncio.Queue()
