"""
Convert an int to VRChat Float8, capped from 0 to MAX_COUNT_PER_SECOND both included
VRChat Float8 is [0,255] mapped uniformly to [-1,1]
Using only the range from 0.0 to 1.0 in this project

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

VRChat is a trademark of VRChat Inc.
"""

from app.Utils.constants import MAX_COUNT_PER_SECOND


def int2f8(value: int) -> float:
    """Convert integer [0...MAX_COUNT_PER_SECOND] to VRChat Float8 [0.0 ... 1.0]"""
    value = max(0, min(MAX_COUNT_PER_SECOND, value))
    return value / MAX_COUNT_PER_SECOND
