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

    def __getitem__(self, key):
        return self.state[key]

    def __setitem__(self, key, value):
        self.state[key] = value

    def __delitem__(self, key):
        del self.state[key]

    def __contains__(self, key):
        return key in self.state

    def write_back(self):
        with open(self.path, "w") as config_file:
            config_file.write(tomlkit.dumps(self.state))
