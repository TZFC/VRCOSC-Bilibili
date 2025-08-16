"""
Convert an event name to custom event_id

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

VRChat is a trademark of VRChat Inc.
BILIBILI is a trademark of Shanghai Hode Information Technology Co., Ltd.
"""

NAME_EVENT_ID: dict[str, int] ={
    'ENTER': 0,
    'DANMAKU': 1,
    'EMOTICON': 2,
    'WARNING': 3,
    'SC': 4,
    'GUARD': 5,
    '小花花': 6,
    '牛哇牛哇': 7,
    '粉丝团灯牌': 8,
    '人气票': 9,
    '口水黄豆': 10,
    '这个好耶': 11
    }

def name2id(name: str) -> int:
    return NAME_EVENT_ID[name]