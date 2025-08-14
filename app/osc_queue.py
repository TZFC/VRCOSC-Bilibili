"""
Async queue, bilibili events as producer, osc client as consumer

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - bilibili-api-python (see its license in the dependency's repository)

BILIBILI is a trademark of Shanghai Hode Information Technology Co., Ltd.
"""
import asyncio

# 创建异步OSC请求队列
# 更新参数请求      ("PARAMETER", (name, value))
# 更新聊天框请求    ("CHATBOX", (message, immediate))
osc_queue: asyncio.Queue = asyncio.Queue()