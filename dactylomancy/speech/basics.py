import discord
from discord.ext import commands
from typing import Optional


class ReplyModal(discord.ui.Modal, title="Reply"):
    body = discord.ui.TextInput(
        label="body",
        style=discord.TextStyle.long
    )

    def __init__(self, *, message: discord.Message, mention: bool) -> None:
        super().__init__()
        self.message = message
        self.mention = mention

    async def on_submit(self, interaction: discord.Interaction):
        await self.message.reply(
            self.body,
            mention_author=self.mention
        )
        await interaction.response.defer(thinking=False)


class EditModal(discord.ui.Modal, title="Edit"):
    body = discord.ui.TextInput(
        label="body",
        style=discord.TextStyle.long
    )

    def __init__(self, *, message: discord.Message) -> None:
        super().__init__()
        self.message = message
        self.body.default = self.message.content

    async def on_submit(self, interaction: discord.Interaction):
        await self.message.edit(content=self.body)
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
            delete_after=bot.zeroth_ring.timeout
        )

    @bot.tree.command()
    async def upload(
                interaction: discord.Interaction,
                attachment: discord.Attachment,
                spoiler: bool,
                caption: Optional[str] = ""
            ):
        att_file = await attachment.to_file(spoiler=bool(spoiler))
        await interaction.channel.send(
            caption,
            file=att_file
        )
        await interaction.response.send_message(
            "Uploaded.",
            ephemeral=True,
            delete_after=bot.zeroth_ring.timeout
        )

    @bot.tree.context_menu()
    async def reply(
                interaction: discord.Interaction,
                message: discord.Message
            ):
        await interaction.response.send_modal(
            ReplyModal(message=message, mention=True)
        )

    @bot.tree.context_menu(
        name="Silent Reply"
    )
    async def silent_reply(
                interaction: discord.Interaction,
                message: discord.Message
            ):
        await interaction.response.send_modal(
            ReplyModal(message=message, mention=False)
        )

    @bot.tree.context_menu()
    async def edit(
                interaction: discord.Interaction,
                message: discord.Message
            ):
        if message.author.id == bot.user.id:
            await interaction.response.send_modal(EditModal(message=message))
        else:
            await interaction.response.send_message(
                "Only proxied messages can be edited.",
                ephemeral=True
            )

    @bot.tree.context_menu()
    async def delete(
                interaction: discord.Interaction,
                message: discord.Message
            ):
        if message.author.id == bot.user.id:
            await message.delete()
            await interaction.response.send_message(
                "Deleted.",
                ephemeral=True,
                delete_after=bot.zeroth_ring.timeout
            )
        else:
            await interaction.response.send_message(
                "Only proxied messages can be deleted.",
                ephemeral=True
            )
