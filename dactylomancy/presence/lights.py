import discord
import tomlkit
from discord.ext import commands
from typing import Optional
from python_hue_v2 import Hue


async def setup(bot: commands.Bot):

    hue: Hue

    @bot.listen("on_ready")
    async def connect_bridge():
        if "app_key" in bot.zeroth_ring["lights"]:
            hue = Hue(
                ip_address=bot.zeroth_ring["lights"]["bridge_ip"],
                hue_application_key=bot.zeroth_ring["lights"]["app_key"]
            )
        else:
            hue = Hue(
                ip_address=bot.zeroth_ring["lights"]["bridge_ip"]
            )

    @bot.tree.command()
    class Lighting(discord.app_commands.Group):
        pass
    
