from pathlib import Path
import tomllib
from importlib import resources
import logging
logger = logging.getLogger(__name__)
Path = "../config.toml"

def load_user_config() -> dict:
    with open(Path, "rb") as f:
        return tomllib.load(f)