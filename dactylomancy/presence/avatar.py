import datetime
import discord
from discord.ext import commands, tasks
from pathlib import Path


# Set the resource path
# Not in config because this module is intended to beself contained
# It is also likely to require overhaul for your purposes
resources = Path("/res")

utc = datetime.timezone.utc
update_times = []
simple_dates = {
    1: 0,
    2: 0,
    4: 1,
    5: 1,
    7: 2,
    8: 2,
    10: 3,
    11: 3
}
complex_dates = {
    3: (20, 0, 1),
    6: (21, 1, 2),
    9: (23, 2, 3),
    12: (21, 3, 0)
}

for i in range(0, 24, 4):
    update_times.append(datetime.time(
        hour=i, tzinfo=utc
    ))


async def setup(bot: commands.Bot):

    def get_current_avatar_folder():
        now = datetime.utcnow()
        if now.month in simple_dates:
            season = simple_dates[now.month]
        else:
            info = complex_dates[now.month]
            season = info[1] if now.day < info[0] else info[2]
        if bot.zeroth_ring["presence"]["makeup"]:
            avatar_folder = resources / season / (now.hour // 4)
        else:
            avatar_folder = resources / season
        return avatar_folder

    @tasks.loop(time=update_times)
    async def update_avatar():
        avatar_folder = get_current_avatar_folder()
        with open(avatar_folder / "avatar.png", "rb") as avatar:
            avatar_bytes = avatar.read()
        await bot.user.edit(avatar=avatar_bytes)

    @bot.tree.command()
    async def avatar(interaction: discord.Interaction):
        avatar_folder = get_current_avatar_folder()
        await interaction.channel.send(
            file=avatar_folder / "avatar_xl.png"
        )
        await interaction.response.send_message(
            "Shared.",
            ephemeral=True,
            delete_after=bot.zeroth_ring["interface"]["timeout"]
        )

    @bot.tree.command()
    async def basic(interaction: discord.Interaction):
        with open("./resources/basic.png", "rb") as image:
            f = image.read()
        await bot.user.edit(avatar=f)
        await interaction.response.send_message(
            "Done."
        )

    @bot.tree.command()
    async def invert(interaction: discord.Interaction):
        with open("./resources/invert.png", "rb") as image:
            f = image.read()
        await bot.user.edit(avatar=f)
        await interaction.response.send_message(
            "Done."
        )
