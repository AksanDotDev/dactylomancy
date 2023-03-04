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
            interface = tomlkit.table()
            interface["timeout"] = 0.0
            self.state["interface"] = interface

        if "presence" not in self.state:
            presence = tomlkit.table()
            presence["status"] = "online"
            presence["follow"] = False
            presence["activity"] = False
            presence["message"] = False
            self.state["presence"] = presence

    def __getitem__(self, key):
        return self.state[key]

    def write_back(self):
        with open(self.path, "w") as config_file:
            config_file.write(tomlkit.dumps(self.state))
