import multiprocessing
import discord
import logging
from ..bot import DactylomancyBot
from .. import __title__
from .._targets import core_process, update_process
from ..utilities.views import ConfirmationQuery


async def setup(bot: DactylomancyBot):

    # Main body for feature commands to be added

    if bot.config_group:
        logging.debug('Adding config commands for extension tasks.')

        @bot.config_group.command(
            name='shutdown',
            description='Neatly shuts down the Dactylomancy process.'
        )
        @bot.user_only()
        async def shutdown(interaction: discord.Interaction):
            view = ConfirmationQuery(
                'Shutdown',
                discord.ButtonStyle.danger
            )
            query_message = await interaction.response.send_message(
                embed=bot.config_embed.get_simple_embed(
                    'Warning',
                    'Shutting down Dactylomancy is the **last** action that can be performed via Discord.\n'
                    + 'Are you sure you wish to proceed?',
                ),
                view=view,
                ephemeral=True,
                delete_after=None,
            )
            await view.wait()
            await query_message.resource.delete()
            await view.interaction.response.send_message(
                embed=bot.config_embed.get_simple_embed(
                        'Shutdown',
                        'Initiated . . .' if view.proceed else 'Aborted.'
                    ),
                ephemeral=True,
                delete_after=bot.config['config']['embed_duration']
            )
            if view.proceed:
                logging.info('Shutting down bot.')
                await bot.close()

        @bot.config_group.command(
            name='update-and-restart',
            description=f'Shuts down the bot, pulls any updates to {__title__}, and tries to bring the bot back up.'
        )
        @bot.user_only()
        async def update_and_restart(
            interaction: discord.Interaction,
        ):
            view = ConfirmationQuery(
                'Update and Restart',
                discord.ButtonStyle.danger
            )
            query_message = await interaction.response.send_message(
                embed=bot.config_embed.get_simple_embed(
                    'Warning',
                    'Though the update and restart process is intended to be robust, the bot may not restart.\n'
                    + 'Are you sure you wish to proceed?',
                ),
                view=view,
                ephemeral=True,
                delete_after=None,
            )
            await view.wait()
            await query_message.resource.delete()
            await view.interaction.response.defer(
                ephemeral=True,
                thinking=True
            )
            if view.proceed:
                new_update_process = multiprocessing.Process(
                    target=update_process,
                    args=(
                        bot._args,
                        bot.login_lock,
                        view.interaction.followup.url,
                    )
                )
                logging.info('Spawning update process.')
                new_update_process.start()
                logging.info('Shuting down bot.')
                await bot.close()

        @bot.config_group.command(
            name='restart',
            description='Shuts down the bot and tries to bring the bot back up.'
        )
        @bot.user_only()
        async def restart(
            interaction: discord.Interaction,
        ):
            view = ConfirmationQuery(
                'Restart',
                discord.ButtonStyle.danger
            )
            query_message = await interaction.response.send_message(
                embed=bot.config_embed.get_simple_embed(
                    'Warning',
                    'Though the restart process is intended to be robust, the bot may not restart.\n'
                    + 'Are you sure you wish to proceed?',
                ),
                view=view,
                ephemeral=True,
                delete_after=None,
            )
            await view.wait()
            await query_message.resource.delete()
            await view.interaction.response.defer(
                ephemeral=True,
                thinking=True
            )
            if view.proceed:
                new_update_process = multiprocessing.Process(
                    target=core_process,
                    args=(
                        bot._args,
                        bot.login_lock,
                        view.interaction.followup.url,
                    )
                )
                logging.info('Spawning new core process.')
                new_update_process.start()
                logging.info('Shuting down bot.')
                await bot.close()
