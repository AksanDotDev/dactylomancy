import tomlkit
import logging
from discord.utils import setup_logging as discord_logging


class ZerothRing():

    def __init__(self, config_path) -> None:
        self.path = config_path
        with open(config_path) as config_file:
            self.state = tomlkit.parse(config_file.read())

        if "logging" in self.state:
            handler = logging.FileHandler(self.state["logging"]["filename"])
            level = logging._nameToLevel[
                self.state["logging"].get("level", "INFO")
            ]
            discord_logging(handler=handler, level=level)
        else:
            discord_logging()

        if "interface" not in self.state:
            self.state["interface"] = {
                "timeout": 0.0,
            }

        self.timeout = self.state["interface"]["timeout"]
