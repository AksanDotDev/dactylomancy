import discord
import logging
import tomlkit
from discord.ext import commands


async def setup(bot: commands.Bot):

    if "dm_warn_and_log" not in bot.zeroth_ring:
        config_table = tomlkit.table()
        config_table["filename"] = "./res/dms.log"
        config_table["message"] = "I am not using DMs right now, but I am logging them."
        bot.zeroth_ring["dm_warn_and_log"] = config_table
        bot.zeroth_ring.write_back()

    dm_logger = logging.getLogger("dm_logger")
    handler = logging.FileHandler(bot.zeroth_ring["dm_warn_and_log"]["filename"])
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(message)s"
    ))
    dm_logger.propagate = False
    dm_logger.addHandler(handler)
    dm_logger.setLevel(logging.INFO)

    @bot.event
    async def on_message(message: discord.Message):
        if not isinstance(message.channel, discord.DMChannel) or message.author.id == bot.user.id:
            return

        await message.channel.send(bot.zeroth_ring["dm_warn_and_log"]["message"])
        dm_logger.info(f"{message.author.name} - {message.author.display_name} -    SENT:"
                       + f"{{{message.author.id}/{message.id}}} {message.content}")  # noqa: W503

    @bot.event
    async def on_message_edit(before: discord.Message, after: discord.Message):
        if not isinstance(after.channel, discord.DMChannel) or after.author.id == bot.user.id:
            return

        dm_logger.info(f"{after.author.name} - {after.author.display_name} -  EDITED:"
                       + f"{{{after.author.id}/{after.id}}} BEFORE: {{{before.content}}} AFTER: {{{after.content}}}")  # noqa: W503

    @bot.event
    async def on_message_delete(message: discord.Message):
        if not isinstance(message.channel, discord.DMChannel) or message.author.id == bot.user.id:
            return

        dm_logger.info(f"{message.author.name} - {message.author.display_name} - DELETED:"
                       + f"{{{message.author.id}/{message.id}}} {message.content}")  # noqa: W503
