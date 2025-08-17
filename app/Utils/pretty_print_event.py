"""
Pretty print a bilibili-api event for inspection convenience

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

BILIBILI is a trademark of Shanghai Hode Information Technology Co., Ltd.
"""
import json


def pretty_print_event(event: dict) -> None:
    """
    print the event content with 4 space indent
    """
    print(json.dumps(event, indent=4, ensure_ascii=False))
