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
    'gift_小花花': 6,
    'gift_牛哇牛哇': 7,
    'gift_粉丝团灯牌': 8,
    'gift_人气票': 9,
    'gift_口水黄豆': 10,
    'gift_这个好耶': 11
    }

def name2id(name: str) -> int:
    return NAME_EVENT_ID[name]