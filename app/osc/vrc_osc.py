"""
An UDP Client that sends parameter updates and chatbox messages to VRChat via OSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in the dependency's repository)

VRChat is a trademark of VRChat Inc.

Notes:
  - AI assistance was used in drafting parts of this file.
"""
from pythonosc.udp_client import SimpleUDPClient
import logging

logger = logging.getLogger(__name__)
_MAX_CHAT_LEN = 144


class VRChatOSC:
    def __init__(self, ip: str = "127.0.0.1", port: int = 9000):
        self._ip = ip
        self._port = port
        self._client: SimpleUDPClient | None = SimpleUDPClient(ip, port)
        logger.info("初始化 VRChatOSC 客户端: %s:%d", ip, port)

    @classmethod
    def connect(cls, ip: str = "127.0.0.1", port: int = 9000) -> "VRChatOSC":
        """Create a UDP client connects to VRC OSC address."""
        return cls(ip, port)

    def close(self) -> None:
        """Close the UDP client."""
        self._client = None
        logger.info("关闭 VRChatOSC 客户端")

    # --- Public API ---

    def update_parameter(self, param_name: str, param_value: int | float | bool) -> None:
        if not param_name:
            raise ValueError("param_name must be non-empty")
        self._ensure_ready()
        addr = f"/avatar/parameters/{param_name}"
        self._client.send_message(addr, param_value)
        logger.info("%s = %r", addr, param_value)

    def send_chat(self, message: str, immediate: bool = True) -> None:
        self._ensure_ready()
        if len(message) > _MAX_CHAT_LEN:
            message = message[:_MAX_CHAT_LEN]
        self._client.send_message("/chatbox/input", [message, bool(immediate)])
        logger.info("/chatbox/input = %r (%s)", message,
                     "immediate" if immediate else "fill-only")

    def typing_indicator(self, on: bool = True) -> None:
        self._ensure_ready()
        self._client.send_message("/chatbox/typing", [bool(on)])
        logger.debug("/chatbox/typing = %r", on)

    # --- Internal ---
    def _ensure_ready(self) -> None:
        if self._client is None:
            raise RuntimeError(
                "VRChatOSC not connected. Use VRChatOSC.connect() first.")
