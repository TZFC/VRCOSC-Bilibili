"""
Loader for user config.toml

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
import tomllib
import logging
from typing import Any
logger = logging.getLogger(__name__)
_CONFIG_PATH = "./Config.toml"


def load_user_config() -> dict:
    """
    load user config from Config.toml
    """
    with open(_CONFIG_PATH, "rb") as f:
        logger.info("加载用户设置")
        config: dict[str, Any] = tomllib.load(f)
        verify_config(config)
        return config


def verify_config(unverified_config: dict) -> None:
    """
    verify user has filled in config correctly
    """
    try:
        int(unverified_config["room_id"])
    except Exception as e:
        logger.warning(
            """
            配置文件格式错误：房间号 room_id 应为数字
            """)
        raise ValueError("room_id should be int")
    for event, level in unverified_config["events"].items():
        if level not in [0, 1, 2, 3]:
            logger.warning(
                """
                配置文件格式错误：%s 等级应为 0/1/2/3
                """, event)
            raise ValueError("event level should be one of 0/1/2/3")
    enter_level_len: int = len(unverified_config["enter"]["enter_level"])
    enter_time_len: int = len(unverified_config["enter"]["min_display_time"])
    if enter_level_len != enter_time_len:
        logger.warning(
            """
            配置文件格式错误: enter_level 应与 min_display_time 等长
            """)
        raise ValueError(
            "enter_level and min_display_time should have same length")
    ani_name_len: int = len(
        unverified_config["animation_accumulate"]["animation"])
    ani_param_len: int = len(
        unverified_config["animation_accumulate"]["animated_parameter"])
    ani_time_len: int = len(
        unverified_config["animation_accumulate"]["animation_time"])
    ani_time_max_len: int = len(
        unverified_config["animation_accumulate"]["animation_max_per_time"])
    if not ani_name_len == ani_param_len == ani_time_len == ani_time_max_len:
        logger.warning(
            """
            配置文件格式错误: animation 应与 animated_parameter \
                和 animation_time 和 animation_max_per_time 等长
            """)
        raise ValueError("animation, animated_parameter, and animation_time \
                         should have same length")
    para_name_len: int = len(
        unverified_config["set_parameter"]["parameter_names"])
    para_default_len: int = len(
        unverified_config["set_parameter"]["parameter_default"])
    para_increment_len: int = len(
        unverified_config["set_parameter"]["parameter_increment"])
    para_kw_len: int = len(
        unverified_config["set_parameter"]["parameter_keywords"])
    para_dc_step_len: int = len(
        unverified_config["set_parameter"]["parameter_decay_step"])
    para_dc_time_len: int = len(
        unverified_config["set_parameter"]["parameter_decay_time"])
    if not 2*para_name_len == 2*para_default_len == 2*para_increment_len == 2*para_dc_step_len == 2*para_dc_time_len == para_kw_len:
        logger.warning(
            """
            配置文件格式错误: parameter_names 应与 parameter_default \
                和 parameter_decay_step 和 parameter_decay_time
                和 parameter_increment 等长且为 parameter_keywords 的一半
            """)
        raise ValueError("parameter_names, parameter_default, parameter_increment, \
                         half of parameter_keywords should have same length")


CONFIG: dict[str, Any] = load_user_config()
