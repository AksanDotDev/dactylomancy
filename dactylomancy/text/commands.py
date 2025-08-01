import tomlkit
import logging
import discord

from typing import Optional

from ..bot import DactylomancyBot
from ..utilities.views import ConfirmationQuery
from ..utilities.embeds import ReferenceErrorEmbed
from ..utilities.parsing import PARSERS
from ..utilities.files import TemporaryTextFile


# The key under which to store the configuration information
# Could be specific to the extension file or the family it belongs to
CONFIG_KEY = 'text'


# key: value pairs for the defaults to be set
CONFIG_DEFAULTS = {
    'ephemeral_duration': 0,
    'parsers': [
        'newlines',
        'emoji',
    ]
}

ERROR_EMBED = ReferenceErrorEmbed()


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

    def build_parser_stack():
        bot.active_parsers = []
        unfound = []
        for parser_key in config_table['parsers']:
            logging.debug(f'Attempting to add active parser: {parser_key}')
            if parser_key in PARSERS:
                bot.active_parsers.append(PARSERS[parser_key])
            else:
                unfound.append(parser_key)
                logging.info(f'Skipping over, and marking for removal unfound parser: {parser_key}')
        for parser_key in unfound:
            config_table['parsers'].remove(parser_key)

    build_parser_stack()

    if bot.config_group:
        logging.debug('Adding config command for text settings.')

        @bot.config_group.command(
            name='text-settings',
            description='Displays or changes settings for the text functionality.'
        )
        @discord.app_commands.describe(
            duration='The time, in seconds, for a text ephemeral to last.',
            enable_parser='Parser(s) to enable as a comma separated list.',
            disable_parser='Parser(s) to enable as a comma separated list.',
        )
        @discord.app_commands.rename(
            enable_parser='enable-parser-s',
            disable_parser='disable-parser-s',
        )
        @bot.user_only()
        async def text_settings(
            interaction: discord.Interaction,
            duration: Optional[discord.app_commands.Range[int, 0, 900]],
            enable_parser: Optional[str],
            disable_parser: Optional[str],
        ):
            embed: discord.Embed = bot.config_embed.get_simple_embed(
                'Text Settings', ''
            )
            update_message = ''

            if duration is not None:
                logging.debug(f'Setting text ephemeral duration to {duration} seconds.')
                config_table['ephemeral_duration'] = duration
                update_message = 'Text ephemeral duration updated.\n'
            else:
                update_message = ''
            embed.add_field(
                name='Duration',
                value=f'{update_message}`{config_table['ephemeral_duration']}`',
            )

            rebuild = False
            if enable_parser:
                for parser_key in map(lambda s: s.strip(), enable_parser.split(',')):
                    if parser_key in config_table['parsers']:
                        update_message += f'`{parser_key}` already enabled, skipping.\n'
                    elif parser_key not in PARSERS:
                        update_message += f'`{parser_key}` not in , skipping.\n'
                    else:
                        config_table['parsers'].append(parser_key)
                        update_message += f'`{parser_key}` enabled.\n'
                        rebuild = True
            if disable_parser:
                for parser_key in map(lambda s: s.strip(), disable_parser.split(',')):
                    if parser_key not in config_table['parsers']:
                        update_message += f'`{parser_key}` is not enabled, skipping.\n'
                    else:
                        config_table['parsers'].remove(parser_key)
                        update_message += f'`{parser_key}` disabled.\n'
                        rebuild = True
            if rebuild:
                build_parser_stack()

            if config_table['parsers']:
                parsers_display_str = f'{'`\n`'.join(config_table['parsers'])}'
            else:
                parsers_display_str = 'None'
            embed.add_field(
                name='Parsers',
                value=f'{update_message}`{parsers_display_str}`',
            )

            logging.debug('Returning text settings.')
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
                delete_after=bot.config['config']['embed_duration'],
            )

    # Main body for feature commands to be added

    def parse_text(input_txt: str) -> str:
        for parser in bot.active_parsers:
            input_txt = parser(input_txt)
        return input_txt

    async def proxy_via_user_install(
        interaction: discord.Interaction,
        text: Optional[str] = None,
        reply: Optional[str] = None,
        mention: Optional[bool] = False,
        silent: Optional[bool] = False,
        files: Optional[list[discord.File]] = None,
    ):
        await interaction.response.send_message(
            content=text,
            silent=silent,
            files=files
        )

    async def proxy_via_bot(
        interaction: discord.Interaction,
        text: Optional[str] = None,
        reply: Optional[str] = None,
        mention: Optional[bool] = False,
        silent: Optional[bool] = False,
        files: Optional[list[discord.File]] = None,
    ):
        await interaction.channel.send(
            content=text,
            silent=silent,
            files=files,
        )
        await interaction.response.send_message(
            "Sent.",
            ephemeral=True,
            silent=True,
            delete_after=config_table['ephemeral_duration']
        )

    @bot.tree.command(
        name='invoke',
        description='Proxy a message, using either a response message, or a bot message, as appropriate.',
    )
    @bot.user_only()
    @discord.app_commands.describe(
        text='The text of the message to be proxied.',
    )
    @discord.app_commands.rename(
        text='message',
    )
    async def invoke(
        interaction: discord.Interaction,
        text: str,
        reply: Optional[str] = None,
        mention: Optional[bool] = False,
        silent: Optional[bool] = False

    ):
        if bot.present_in_guild(interaction.guild_id):
            proxy_function = proxy_via_bot
        else:
            proxy_function = proxy_via_user_install

        text = parse_text(text)

        if (length := len(text)) > 2000:
            with TemporaryTextFile(text) as temp_file:
                view = ConfirmationQuery(
                    'Send as file',
                    discord.ButtonStyle.primary
                )
                query_message = await interaction.response.send_message(
                    embed=ERROR_EMBED.get_simple_embed(
                        'Error',
                        f'Your message is {length - 2000} character{'s' if length > 2001 else ''} over length to be sent as a message.\n'
                        + 'Do you wish to send it as an attachment?',
                    ),
                    view=view,
                    ephemeral=True,
                    delete_after=None,
                    file=discord.File(
                        temp_file,
                        filename='message.txt'
                    ),
                )
                await view.wait()
                await query_message.resource.delete()
                if view.proceed:
                    await proxy_function(
                        interaction=view.interaction,
                        text=None,
                        reply=reply,
                        mention=mention,
                        silent=silent,
                        files=[discord.File(
                            temp_file,
                            filename='message.txt'
                        )],
                    )
                else:
                    await view.interaction.response.send_message(
                        content='Cancelled',
                        ephemeral=True,
                        delete_after=config_table['ephemeral_duration'],
                    )
        else:
            await proxy_function(interaction, text, reply, mention, silent)


async def teardown(bot: DactylomancyBot):
    # Teardown hooks if needed
    pass
