import discord
from discord.ext import commands


async def setup(bot: commands.Bot):

    @bot.tree.command()
    @discord.app_commands.choices(activity=[
        discord.app_commands.Choice(name="Watching", value="watching"),
        discord.app_commands.Choice(name="Playing", value="playing"),
        discord.app_commands.Choice(name="Streaming", value="streaming"),
        discord.app_commands.Choice(name="Listening", value="listening"),
        discord.app_commands.Choice(name="Competing in", value="competing")
    ])
    async def status(
                interaction: discord.Interaction,
                activity: discord.app_commands.Choice[str],
                status: str
            ):
        new_activity = discord.Activity(
            type=discord.ActivityType[activity.value],
            name=status
        )
        await bot.change_presence(
            activity=new_activity
        )
        await interaction.response.send_message(
            "Set.",
            ephemeral=True,
            delete_after=bot.zeroth_ring.timeout
        )
