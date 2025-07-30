import tomllib
from importlib import resources
import logging
logger = logging.getLogger(__name__)
CONFIG_PATH = "./config.toml"

def load_user_config() -> dict:
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)