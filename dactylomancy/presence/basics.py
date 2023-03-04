import discord
from discord.ext import commands

status_mapping = {
    discord.Status.online: "online",
    discord.Status.idle: "idle",
    discord.Status.dnd: "dnd",
    discord.Status.offline: "invisible"
}


async def setup(bot: commands.Bot):

    async def update_status(new_status):
        new_status = discord.Status[new_status]
        if bot.zeroth_ring["presence"]["activity"]:
            old_activity = discord.Activity(
                type=discord.ActivityType[
                    bot.zeroth_ring["presence"]["activity"]
                ],
                name=bot.zeroth_ring["presence"]["message"]
            )
        else:
            old_activity = None

        await bot.change_presence(
            activity=old_activity,
            status=new_status
        )

    async def status_follower(before, after):
        if before.id == bot.zeroth_ring["discord"]["scribe"]:
            status = status_mapping[after.status]
            bot.zeroth_ring["presence"]["status"] = status
            await update_status(status)

    @bot.listen("on_ready")
    async def setup_presence():
        if bot.zeroth_ring["presence"]["follow"]:
            bot.add_listener(status_follower, "on_presence_update")
        await update_status(bot.zeroth_ring["presence"]["status"])

    @bot.tree.command()
    @discord.app_commands.choices(status=[
        discord.app_commands.Choice(name="Online", value="online"),
        discord.app_commands.Choice(name="Idle", value="idle"),
        discord.app_commands.Choice(name="Do Not Disturb", value="dnd"),
        discord.app_commands.Choice(name="Invisible", value="invisible"),
        discord.app_commands.Choice(name="Follow", value="follow")
    ])
    async def status(
                interaction: discord.Interaction,
                status: discord.app_commands.Choice[str],
            ):
        if status.value == "follow":
            bot.zeroth_ring["presence"]["follow"] = True
            bot.add_listener(status_follower, "on_presence_update")
        else:
            bot.zeroth_ring["presence"]["follow"] = False
            bot.zeroth_ring["presence"]["status"] = status.value
            bot.remove_listener(status_follower, "on_presence_update")
            await update_status(status.value)
        bot.zeroth_ring.write_back()
        await interaction.response.send_message(
            "Set.",
            ephemeral=True,
            delete_after=bot.zeroth_ring["interface"]["timeout"]
        )

    @bot.tree.command()
    @discord.app_commands.choices(activity=[
        discord.app_commands.Choice(name="Watching", value="watching"),
        discord.app_commands.Choice(name="Playing", value="playing"),
        discord.app_commands.Choice(name="Streaming", value="streaming"),
        discord.app_commands.Choice(name="Listening", value="listening"),
        discord.app_commands.Choice(name="Competing in", value="competing")
    ])
    async def activity(
                interaction: discord.Interaction,
                activity: discord.app_commands.Choice[str],
                message: str
            ):
        bot.zeroth_ring["presence"]["activity"] = activity.value
        bot.zeroth_ring["presence"]["message"] = message
        bot.zeroth_ring.write_back()

        new_activity = discord.Activity(
            type=discord.ActivityType[activity.value],
            name=message
        )

        await bot.change_presence(
            activity=new_activity,
            status=bot.zeroth_ring["presence"]["status"]
        )
        await interaction.response.send_message(
            "Set.",
            ephemeral=True,
            delete_after=bot.zeroth_ring["interface"]["timeout"]
        )
