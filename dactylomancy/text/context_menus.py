import tomlkit
from ..bot import DactylomancyBot
from .. import __title__

__dactylomancy_dependencies__ = [
    f'{__title__}.text.commands',
]


async def setup(bot: DactylomancyBot):

    # Main body for feature commands to be added

    # TODO

    pass


async def teardown(bot: DactylomancyBot):
    # Teardown hooks if needed
    pass
