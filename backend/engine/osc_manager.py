import asyncio
import logging
import time
from typing import Any, Callable

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

logger = logging.getLogger(__name__)

# Time window (seconds) within which an incoming message matching our last send
# is considered an echo rather than a genuine user change.
ECHO_WINDOW_SECONDS = 0.2


class OSCManager:
    def __init__(self):
        self.client = None
        self.server = None
        self.transport = None
        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler(self._default_handler)
        self.on_message_callback = None

        # Keep track of our intended state to enforce "Overwrite" sync mode.
        # Maps OSC address -> value that our app last decided the parameter should be.
        self.intended_state = {}

        # Echo detection: maps OSC address -> (value, timestamp) of last send.
        # Used to distinguish VRChat echoing our own sent value from a genuine
        # user-initiated change via the in-game menu.
        self._last_sent = {}

    def setup(
        self,
        client_ip: str,
        client_port: int,
        server_ip: str,
        server_port: int,
        on_message: Callable,
    ):
        self.client_ip = client_ip
        self.client_port = client_port
        self.server_ip = server_ip
        self.server_port = server_port
        self.on_message_callback = on_message

        self.client = SimpleUDPClient(self.client_ip, self.client_port)
        logger.info(f"OSC Client configured to send to {client_ip}:{client_port}")

    async def start_server(self):
        if self.transport:
            self.transport.close()

        loop = asyncio.get_running_loop()
        self.server = AsyncIOOSCUDPServer(
            (self.server_ip, self.server_port), self.dispatcher, loop
        )
        self.transport, self.protocol = await self.server.create_serve_endpoint()
        logger.info(f"OSC Server listening on {self.server_ip}:{self.server_port}")

    def stop_server(self):
        if self.transport:
            self.transport.close()
            self.transport = None
            logger.info("OSC Server stopped")

    def _default_handler(self, address: str, *args):
        if self.on_message_callback:
            self.on_message_callback(address, *args)

    def send_message(self, address: str, value: Any):
        if self.client:
            self.intended_state[address] = value
            self._last_sent[address] = (value, time.monotonic())
            self.client.send_message(address, value)
            logger.debug(f"Sent OSC: {address} -> {value}")

    def is_echo(self, address: str, value: Any) -> bool:
        """Check whether an incoming OSC message is an echo of our own recent send.

        VRChat re-broadcasts parameter values on port 9001 whenever they change,
        including changes that *we* initiated by sending to port 9000.  This
        method returns True when the incoming (address, value) matches a message
        we sent within the last ECHO_WINDOW_SECONDS, so callers can ignore it.
        """
        entry = self._last_sent.get(address)
        if entry is None:
            return False

        sent_value, sent_time = entry
        elapsed = time.monotonic() - sent_time

        if elapsed > ECHO_WINDOW_SECONDS:
            return False

        # Compare values.  VRChat may convert types (e.g. int ↔ float) so we
        # do a loose numeric comparison when possible.
        try:
            return float(sent_value) == float(value)
        except (TypeError, ValueError):
            return sent_value == value


osc_manager = OSCManager()
