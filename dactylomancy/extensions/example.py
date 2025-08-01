import tomlkit
from ..bot import DactylomancyBot


# The key under which to store the configuration information
# Could be specific to the extension file or the family it belongs to
CONFIG_KEY = 'example'


# key: value pairs for the defaults to be set
CONFIG_DEFAULTS = {
    'test1': 1010,
    'test2': 'Seven',
    'test3': ['Bee', 'Frog', 'Inés']
}


async def setup(bot: DactylomancyBot):
    # Block for any State variables to be registered if absent and defaults set

    # Basic table getter
    config_table = bot.config.get_table(CONFIG_KEY)
    # Simple default setting, override for complex behaviour
    for key in CONFIG_DEFAULTS:
        if key not in config_table:
            # Works with anything that tomlkit can handle being passed to `item`
            config_table[key] = tomlkit.item(CONFIG_DEFAULTS[key])

    # Block for any configuration commands for those variables to be registered

    # TODO

    # Main body for feature commands to be added

    # TODO

    pass


async def teardown(bot: DactylomancyBot):
    # Teardown hooks if needed
    pass
