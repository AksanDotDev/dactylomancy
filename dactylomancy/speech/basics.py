import discord
from discord.ext import commands


class ReplyModal(discord.ui.Modal, title="Reply"):
    body = discord.ui.TextInput(
        label="body",
        style=discord.TextStyle.long
    )

    def __init__(self, *, message: discord.Message) -> None:
        super().__init__()
        self.message = message

    async def on_submit(self, interaction: discord.Interaction):
        await self.message.reply(self.body)
        await interaction.response.defer(thinking=False)


async def setup(bot: commands.Bot):

    @bot.tree.command()
    async def echo(
                interaction: discord.Interaction,
                body: str
            ):
        await interaction.channel.send(body)
        await interaction.response.send_message(
            "Sent.",
            ephemeral=True,
            delete_after=0.0
        )

    @bot.tree.context_menu()
    async def reply(
                interaction: discord.Interaction,
                message: discord.Message
            ):
        await interaction.response.send_modal(ReplyModal(message=message))
