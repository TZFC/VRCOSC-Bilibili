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
import logging
import threading
from typing import Callable
from pythonosc.udp_client import SimpleUDPClient
from pythonosc import dispatcher, osc_server

logger = logging.getLogger(__name__)
_MAX_CHAT_LEN = 144


class VRChatOSC:
    """
    OSC class that encapsulates a SimpleUDPClient conencted to VRChat ports and endpoints
    """
    def __init__(self, ip: str = "127.0.0.1", port: int = 9000):
        """
        initialize target OSC ip and ports, create the Client
        """
        self._ip = ip
        self._port = port
        self._client: SimpleUDPClient | None = SimpleUDPClient(ip, port)

         # Listener related state
        self._listener_port: int | None = None
        self._open_sound_control_dispatcher: dispatcher.Dispatcher | None = None
        self._open_sound_control_server: osc_server.ThreadingOSCUDPServer | None = None
        self._listener_thread: threading.Thread | None = None

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
        """
        update given avatar parameter with given value
        """
        if not param_name:
            raise ValueError("param_name must be non-empty")
        self._ensure_ready()
        addr = f"/avatar/parameters/{param_name}"
        self._client.send_message(addr, param_value)
        logger.debug("%s = %r", addr, param_value)

    def send_chat(self, message: str, immediate: bool = True) -> None:
        """
        update chackbox with given message, immediate default to True
        """
        self._ensure_ready()
        if len(message) > _MAX_CHAT_LEN:
            message = message[:_MAX_CHAT_LEN]
        self._client.send_message("/chatbox/input", [message, bool(immediate)])
        logger.debug("/chatbox/input = %r (%s)", message,
                    "immediate" if immediate else "fill-only")

    def typing_indicator(self, on: bool = True) -> None:
        """
        update typing indicator
        """
        self._ensure_ready()
        self._client.send_message("/chatbox/typing", [bool(on)])
        logger.debug("/chatbox/typing = %r", on)
    
    def update_camera(self, param_name: str, param_value: int | float | bool | tuple) -> None:
        """
        update given camera parameter with given value
        """
        if not param_name:
            raise ValueError("param_name must be non-empty")
        self._ensure_ready()
        addr = f"/usercamera/{param_name}"
        self._client.send_message(addr, param_value)
        logger.debug("%s = %r", addr, param_value)
        
    # --- Public API (listening) ---

    def start_listening(self, listen_port: int = 9001) -> None:
        """
        start a background Open Sound Control server to receive messages from VRChat
        """
        if self._open_sound_control_server is not None:
            raise RuntimeError("Listener already running")

        open_sound_control_dispatcher = dispatcher.Dispatcher()
        open_sound_control_server = osc_server.ThreadingOSCUDPServer(
            (self._ip, listen_port),
            open_sound_control_dispatcher,
        )

        listener_thread = threading.Thread(
            target=open_sound_control_server.serve_forever,
            daemon=True,
        )
        listener_thread.start()

        self._listener_port = listen_port
        self._open_sound_control_dispatcher = open_sound_control_dispatcher
        self._open_sound_control_server = open_sound_control_server
        self._listener_thread = listener_thread

        logger.info("开始监听 VRChatOSC 消息: %s:%d", self._ip, listen_port)

    def stop_listening(self) -> None:
        """
        stop the background Open Sound Control server if it is running
        """
        if self._open_sound_control_server is None:
            return

        self._open_sound_control_server.shutdown()
        self._open_sound_control_server.server_close()

        self._open_sound_control_server = None
        self._open_sound_control_dispatcher = None
        self._listener_thread = None
        self._listener_port = None

        logger.info("停止监听 VRChatOSC 消息")

    def add_handler(
        self,
        address_pattern: str,
        handler_function: Callable[..., None],
    ) -> None:
        """
        register a handler function for a given Open Sound Control address pattern
        """
        if self._open_sound_control_dispatcher is None:
            raise RuntimeError(
                "Listener is not running. Call start_listening() before add_handler()."
            )
        self._open_sound_control_dispatcher.map(address_pattern, handler_function)
        logger.info("注册 Open Sound Control 处理函数: %s", address_pattern)

    # --- Internal ---
    def _ensure_ready(self) -> None:
        """
        ensure VRChatOSC is connected
        """
        if self._client is None:
            raise RuntimeError(
                "VRChatOSC not connected. Use VRChatOSC.connect() first.")
