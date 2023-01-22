import tomlkit
import logging
from enum import Enum
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
                "switch_on": "Yes",
                "switch_off": "No",
            }

        self.timeout = self.state["interface"]["timeout"]
        self.switch = Enum(
            "SwitchInt",
            [
                (self.state["interface"]["switch_on"], 1),
                (self.state["interface"]["switch_off"], 0)
            ],
            type=int,
        )
