import discord
import datetime
from discord.ext import commands, tasks
from typing import Optional
from speech.parsing import get_message_snowflake


# A dictionary of names for UI, and IDs for implementation
stickers = {}

update_times = []
for i in range(2, 24, 4):
    update_times.append(datetime.time(
        hour=i, tzinfo=datetime.timezone.utc
    ))


async def setup(bot: commands.Bot):

    @tasks.loop(time=update_times)
    async def populate_stickers():
        for pack in await bot.fetch_premium_sticker_packs():
            for sticker in pack.stickers:
                stickers[f"{sticker.name}.{pack.name}"] = (sticker.id, None)
        for sticker in bot.stickers:
            stickers[f"{sticker.name}.{sticker.guild.name}"] = (sticker.id, sticker.guild.id)

    @bot.listen("on_ready")
    async def setup_presence():
        await populate_stickers()
        populate_stickers.start()

    @bot.tree.command()
    async def sticker(
        interaction: discord.Interaction,
        sticker_name: str,
        reply: Optional[str] = None,
        mention: Optional[bool] = False,
        silent: Optional[bool] = False
    ):
        try:
            sticker_obj = await bot.fetch_sticker(stickers[sticker_name][0])
        except KeyError:
            await interaction.response.send_message(
                "Sticker not found in dictionary.",
                ephemeral=True,
            )
            return
        except discord.NotFound:
            await interaction.response.send_message(
                "Sticker not found in API.",
                ephemeral=True,
            )
            return

        if reply:
            try:
                msg_id = get_message_snowflake(reply)
                msg = interaction.channel.get_partial_message(msg_id)
                await msg.reply(
                    stickers=[sticker_obj],
                    mention_author=mention,
                    silent=silent
                )
                await interaction.response.send_message(
                    "Replied.",
                    ephemeral=True,
                    silent=bot.zeroth_ring["interface"]["silent_success"],
                    delete_after=bot.zeroth_ring["interface"]["timeout"]
                )
            except ValueError:
                await interaction.response.send_message(
                    "Error in reply pararmeter, could not parse.",
                    ephemeral=True,
                )
            except TypeError:
                await interaction.response.send_message(
                    "Error in replying, could not find message.",
                    ephemeral=True,
                )
        else:
            await interaction.channel.send(
                stickers=[sticker_obj],
                silent=silent
            )
            await interaction.response.send_message(
                "Sent.",
                ephemeral=True,
                silent=bot.zeroth_ring["interface"]["silent_success"],
                delete_after=bot.zeroth_ring["interface"]["timeout"]
            )

    @sticker.autocomplete("sticker_name")
    async def sticker_name_autocomplete(
        interaction: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        return [
            discord.app_commands.Choice(name=option, value=option)
            for option in stickers.keys()
            if current.lower() in option.lower()
            and (stickers[option][1] is None or stickers[option][1] == interaction.guild.id)
        ][:25]
