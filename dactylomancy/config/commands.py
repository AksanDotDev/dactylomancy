import logging
import tomlkit
import regex
import discord
from discord import app_commands

from typing import Optional

from .. import __title__, __version__
from ..bot import DactylomancyBot
from ..utilities.files import TemporaryTOMLFile
from ..utilities.embeds import ReferenceConfigEmbed

# Setup a table for config specific options
CONFIG_KEY = 'config'
# key: value pairs for the defaults to be set
CONFIG_DEFAULTS = {
    'embed_colour': '32a889',
    'embed_duration': 90,
}
# Prefix testing regex
PREFIX_REGEX = regex.compile(r'^[-_\'\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$')


async def setup(bot: DactylomancyBot):

    # Block for any State variables to be registered if absent and defaults set

    # Basic table getter
    config_table = bot.config.get_table(CONFIG_KEY)
    # Simple default setting, override for complex behaviour
    for key in CONFIG_DEFAULTS:
        if key not in config_table:
            # Works with anything that tomlkit can handle being passed to `item`
            config_table[key] = tomlkit.item(CONFIG_DEFAULTS[key])

    # A parent group to be used for all configuration commands
    bot.config_group = app_commands.Group(
        name='config',
        description='Configuration tweaking commands for changing options and preferences.',
    )

    bot.tree.add_command(
        bot.config_group
    )

    bot.config_embed = ReferenceConfigEmbed(config_table['embed_colour'])

    # Note the direct addition to the tree
    @bot.tree.command(
        name='version',
        description=f'Get the current {__title__} version'
    )
    @bot.user_only()
    async def version(interaction: discord.Interaction):
        embed: discord.Embed = bot.config_embed.get_simple_embed(
            'Version Info', ''
        )
        embed.add_field(
            name=f'{__title__} Version',
            value=__version__
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
            delete_after=config_table['embed_duration'],
        )

    # Note the additions are now to the group
    @bot.config_group.command(
        name='share',
        description='Get a sharable version of the config file.'
    )
    @bot.user_only()
    async def share(interaction: discord.Interaction):
        logging.debug('Returing sanitised config file for sharing.')
        with TemporaryTOMLFile(bot.config.get_sanitised_doc()) as temp_file:
            await interaction.response.send_message(
                embed=bot.config_embed.get_simple_embed(
                    'Configuration File',
                    'Current `config.toml` sanitised of private information.'
                ),
                file=discord.File(
                    temp_file,
                    filename='config.toml',
                ),
                ephemeral=True,
                delete_after=config_table['embed_duration'],
            )

    @bot.config_group.command(
        name='sync',
        description='Resynchronise commands in the tree from the bot to discord.'
    )
    @bot.user_only()
    async def sync(interaction: discord.Interaction):
        await interaction.response.defer(
            ephemeral=True,
            thinking=True
        )
        logging.debug('Initiated user requested sync.')
        await bot.tree.sync()
        await interaction.followup.send(
            embed=bot.config_embed.get_simple_embed(
                    'Sync',
                    'Complete.'
                ),
            ephemeral=True,
        )

    @bot.config_group.command(
        name='core-settings',
        description='Displays or changes settings for the bot core.'
    )
    @discord.app_commands.describe(
        prefix_str='The word or term that should proceed all commands for this bot, must not contain spaces, must be lower case.',
        clear_prefix='Whether the current prefix should be removed entirely, making all bot commands bare.'
    )
    @discord.app_commands.rename(
        prefix_str='prefix',
        clear_prefix='clear-prefix',
    )
    @bot.user_only()
    async def core_settings(
        interaction: discord.Interaction,
        prefix_str: Optional[discord.app_commands.Range[str, 1, 32]],
        clear_prefix: Optional[bool] = False,
    ):
        await interaction.response.defer(
            ephemeral=True,
            thinking=True
        )
        embed: discord.Embed = bot.config_embed.get_simple_embed(
            'Core Settings', ''
        )
        update_message = ''
        core_config_table = bot.config.get_table('core')

        if prefix_str and not clear_prefix:
            if not PREFIX_REGEX.match(prefix_str):
                update_message = f'Prefix `{prefix_str}` unusable.\n'
                update_message += 'Bot prefix not updated.\n'
            else:
                logging.debug(f'Setting core prefix to {prefix_str.lower()}.')
                if core_config_table['prefix']:
                    bot.tree._modify_prefix(prefix_str.lower())
                else:
                    bot.tree._create_prefix(prefix_str.lower())
                core_config_table['prefix'] = prefix_str.lower()
                await bot.tree.sync()
                update_message = 'Bot prefix updated, commands synced.\n'
                update_message += 'Sync to clients may take 2 hours to propogate.\n'
                update_message += 'Rebooting Discord (`ctrl + R`) may preempt this.\n'
        elif clear_prefix:
            logging.debug('Clearing core prefix.')
            bot.tree._remove_prefix()
            core_config_table['prefix'] = ''
            await bot.tree.sync()
            update_message = 'Bot prefix cleared, commands synced.\n'
            update_message += 'Sync to clients may take 2 hours to propogate.\n'
            update_message += 'Rebooting Discord (`ctrl + R`) may preempt this.\n'
        else:
            update_message = ''

        if core_config_table['prefix']:
            prefix_display_str = core_config_table['prefix']
        else:
            prefix_display_str = 'None'

        embed.add_field(
            name='Prefix',
            value=f'{update_message}`{prefix_display_str}`',
        )

        update_message = ''

        embed.add_field(
            name='Extensions',
            value=f'{update_message}`{'`\n`'.join(core_config_table['extensions'])}`'
        )

        logging.debug('Returning core settings.')
        await interaction.followup.send(
            embed=embed,
            ephemeral=True,
        )

    @bot.config_group.command(
        name='embed-settings',
        description='Displays or changes settings for the config embeds.'
    )
    @discord.app_commands.describe(
        duration='The time, in seconds, for an ephemeral config embed to last.',
        colour_str='The new colour, given as 0x<hex>, #<hex>, 0x#<hex>, or rgb(<number>, <number>, <number>).',
    )
    @discord.app_commands.rename(
        colour_str='colour',
    )
    @bot.user_only()
    async def embed_settings(
        interaction: discord.Interaction,
        duration: Optional[discord.app_commands.Range[int, 0, 900]],
        colour_str: Optional[str],
    ):
        embed: discord.Embed = bot.config_embed.get_simple_embed(
            'Embed Settings', ''
        )
        update_message = ''

        if duration is not None:
            logging.debug(f'Setting embed duration to {duration} seconds.')
            config_table['embed_duration'] = duration
            update_message = 'Config embed duration updated.\n'
        else:
            update_message = ''
        embed.add_field(
            name='Duration',
            value=f'{update_message}`{config_table['embed_duration']}`',
        )

        if colour_str:
            logging.debug(f'Attempting to parse colour string {colour_str} for config embed.')
            try:
                colour = discord.Colour.from_str(colour_str)
                config_table['embed_colour'] = colour_str
                bot.config_embed = ReferenceConfigEmbed(config_table['embed_colour'])
                embed.colour = colour
                update_message = 'Config embed colour updated.\n'
                logging.debug(f'Sucessfully parsed colour string {colour_str} for config embed.')
            except ValueError:
                update_message = f'Config embed colour unchanged, falied to parse: `{colour_str}`.\n'
                logging.debug(f'Failed to parse colour string {colour_str} for config embed.')
        else:
            update_message = ''

        embed.add_field(
            name='Colour',
            value=f'{update_message}`{config_table['embed_colour']}`',
        )

        logging.debug('Returning embed settings.')
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
            delete_after=config_table['embed_duration'],
        )


async def teardown(bot: DactylomancyBot):
    # Remove the spe
    bot.config_group = None
    bot.config_embed = None
