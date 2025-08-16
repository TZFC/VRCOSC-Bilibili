"""
Loader for user config.toml

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
import tomllib
import logging
logger = logging.getLogger(__name__)
_CONFIG_PATH = "./config.toml"


def load_user_config() -> dict:
    with open(_CONFIG_PATH, "rb") as f:
        logger.info("加载用户设置")
        return tomllib.load(f)


CONFIG = load_user_config()
