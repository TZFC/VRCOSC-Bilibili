import asyncio
import logging
from typing import Any, Callable

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

logger = logging.getLogger(__name__)


class OSCManager:
    def __init__(self):
        self.client = None
        self.server = None
        self.transport = None
        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler(self._default_handler)
        self.on_message_callback = None

        # Keep track of our intended state to enforce "Overwrite" sync mode
        self.intended_state = {}

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
            self.client.send_message(address, value)
            logger.debug(f"Sent OSC: {address} -> {value}")


osc_manager = OSCManager()
