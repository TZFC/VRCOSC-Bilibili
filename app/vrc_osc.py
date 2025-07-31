"""
An async UDP Client that sends parameter updates and chatbox messages to VRChat via OSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in THIRD_PARTY_NOTICES or the dependency's repository)

VRChat is a trademark of VRChat Inc.

Notes:
  - AI assistance was used in drafting parts of this file.
"""
from pythonosc.udp_client import AsyncIOOSCUDPClient
import logging
logger = logging.getLogger(__name__)
_MAX_CHAT_LEN = 144


class VRChatOSC:
    def __init__(self, ip: str = "127.0.0.1", port: int = 9000):
        self._ip = ip
        self._port = port
        self._client: AsyncIOOSCUDPClient = None
        self._transport = None
        self._protocol = None
        logger.info("起始化VRChatOSC客户端")

    @classmethod
    async def connect(cls, ip: str = "127.0.0.1", port: int = 9000) -> "VRChatOSC":
        """Factory that opens the UDP endpoint asynchronously."""
        self = cls(ip, port)
        self._client = AsyncIOOSCUDPClient(ip, port)
        # create_endpoint() -> (asyncio.DatagramTransport, OSCProtocol)
        self._transport, self._protocol = await self._client.create_endpoint()
        logger.info("开启向VRC发送UDP数据")
        return self

    async def aclose(self) -> None:
        """Close the UDP transport."""
        if self._transport is not None:
            self._transport.close()
        self._transport = None
        self._protocol = None
        self._client = None
        logger.info("关闭VRChatOSC客户端")

    # --- Public API ---

    async def update_parameter(self, param_name: str, param_value: int | float | bool) -> None:
        """
        Update an avatar parameter.
        Address: /avatar/parameters/<ParamName>
        Types: bool, int, float (must match the avatar parameter type).
        """
        if not param_name:
            raise ValueError("param_name must be non-empty")
        self._ensure_ready()
        addr = f"/avatar/parameters/{param_name}"
        # send_message is non-blocking on UDP; no await needed
        self._protocol.send_message(addr, param_value)
        logger.debug(f"{addr} = {param_value}")

    async def send_chat(self, message: str, immediate: bool = True) -> None:
        """
        Send to VRChat chatbox.
        Address: /chatbox/input
        Args: [message:str, immediate:bool]
          - immediate=True posts immediately; False just fills the input box.
        """
        self._ensure_ready()
        self._protocol.send_message(
            "/chatbox/input", [str(message), bool(immediate)])
        logger.debug(f"/chatbox/input = {message} {'immediate' if immediate else 'fill-only'}")

    async def typing_indicator(self, on: bool = True) -> None:
        """
        Toggle the 'typing' indicator.
        Address: /chatbox/typing
        Args: [on:bool]
        """
        self._ensure_ready()
        self._protocol.send_message("/chatbox/typing", [bool(on)])
        logger.debug(f"/chatbox/typing = {on}")

    # --- Internal ---
    def _ensure_ready(self) -> None:
        if self._protocol is None:
            raise RuntimeError(
                "VRChatOSC not connected. Use `await VRChatOSC.connect()` or `async with VRChatOSC.connect() as v:`")
