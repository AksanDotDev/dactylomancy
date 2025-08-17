import tomlkit
import logging
import discord

from typing import Optional

from ..bot import DactylomancyBot
from ..utilities.views import ConfirmationQuery, SelectionQuery, generate_options
from ..utilities.embeds import ReferenceErrorEmbed
from ..utilities.parsing import PARSERS
from ..utilities.files import TemporaryTextFile


_log = logging.getLogger(__name__)


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
            _log.debug(f'Attempting to add active parser: {parser_key}')
            if parser_key in PARSERS:
                bot.active_parsers.append(PARSERS[parser_key])
            else:
                unfound.append(parser_key)
                _log.warning(f'Skipping over, and marking for removal unfound parser: {parser_key}')
        for parser_key in unfound:
            config_table['parsers'].remove(parser_key)

    build_parser_stack()

    if bot.config_group:
        _log.debug('Adding config command for text settings.')

        @bot.config_group.command(
            name='text-settings',
            description='Displays or changes settings for the text functionality.'
        )
        @discord.app_commands.describe(
            duration='The time, in seconds, for a text ephemeral to last.',
        )
        @bot.user_only()
        async def text_settings(
            interaction: discord.Interaction,
            duration: Optional[discord.app_commands.Range[int, 0, 900]],
        ):
            embed: discord.Embed = bot.config_embed.get_simple_embed(
                'Text Settings', ''
            )
            update_message = ''

            if duration is not None:
                _log.debug(f'Setting text ephemeral duration to {duration} seconds.')
                config_table['ephemeral_duration'] = duration
                update_message = 'Text ephemeral duration updated.\n'
            else:
                update_message = ''
            embed.add_field(
                name='Duration',
                value=f'{update_message}`{config_table['ephemeral_duration']}`',
            )

            if config_table['parsers']:
                parsers_display_str = f'{'`\n`'.join(config_table['parsers'])}'
            else:
                parsers_display_str = 'None'
            embed.add_field(
                name='Parsers',
                value=f'`{parsers_display_str}`',
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
                delete_after=bot.config['config']['embed_duration'],
            )

        @bot.config_group.command(
            name='select-parsers',
            description='Allows the selection of the chosen parsers for text messages.'
        )
        @bot.user_only()
        async def select_parsers(
            interaction: discord.Interaction,
        ):
            options = generate_options(
                labels=PARSERS.keys(),
                descriptions=map(
                    lambda x: x.description,
                    PARSERS.values(),
                ),
                defaults=config_table['parsers'],
            )
            select_view = SelectionQuery(
                'No parsers enabled',
                options,
            )

            query_message = await interaction.response.send_message(
                embed=bot.config_embed.get_simple_embed(
                    'Parsers',
                    'Select your desired parser functions below.'
                ),
                view=select_view,
                ephemeral=True,
                delete_after=None
            )
            await select_view.wait()
            await query_message.resource.delete()

            old_parser_str = f'{'`\n`'.join(config_table['parsers'])}'
            new_parser_str = f'{'`\n`'.join(select_view.values)}'
            confirm_embed = bot.config_embed.get_simple_embed(
                'Parsers',
                'Confirm the changed specification.'
            )
            confirm_embed.add_field(
                name='Current parsers',
                value=f'`{old_parser_str}`',
            )
            confirm_embed.add_field(
                name='Proposed parsers',
                value=f'`{new_parser_str}`',
            )

            confirm_view = ConfirmationQuery()
            query_message = await select_view.interaction.response.send_message(
                embed=confirm_embed,
                view=confirm_view,
                ephemeral=True,
                delete_after=None
            )
            await confirm_view.wait()
            await query_message.resource.delete()

            if confirm_view.proceed:
                _log.debug(f'Changing active parsers to {select_view.values} and rebuilding.')
                config_table['parsers'] = select_view.values
                build_parser_stack()
                embed: discord.Embed = bot.config_embed.get_simple_embed(
                    'Parsers',
                    'The list of active parsers has been updated and implemented.'
                )
                embed.add_field(
                    name='Active parsers',
                    value=f'`{new_parser_str}`',
                )
                await confirm_view.interaction.response.send_message(
                    embed=embed,
                    ephemeral=True,
                    delete_after=bot.config['config']['embed_duration'],
                )
            else:
                embed: discord.Embed = bot.config_embed.get_simple_embed(
                    'Parsers',
                    'The list of active parsers has been not been changed.'
                )
                embed.add_field(
                    name='Active parsers',
                    value=f'`{old_parser_str}`',
                )
                await confirm_view.interaction.response.send_message(
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
    @discord.app_commands.describe(
        text='The text of the message to be proxied.',
    )
    @discord.app_commands.rename(
        text='message',
    )
    @bot.user_only()
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
