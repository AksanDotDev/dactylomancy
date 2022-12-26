import tomlkit
from discord.utils import setup_logging as discord_logging


class ZerothRing():

    def __init__(self, config_path) -> None:
        self.path = config_path
        with open(config_path) as config_file:
            self.state = tomlkit.parse(config_file.read())

        if "logging" in self.state:
            self.setup_logging()
        else:
            discord_logging()

    def setup_logging(self):
        pass