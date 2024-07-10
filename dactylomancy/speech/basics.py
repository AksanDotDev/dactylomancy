import discord
import tomlkit
from discord.ext import commands
from typing import Optional
from speech.parsing import emojify, get_message_snowflake


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
        await self.message.edit(content=emojify(str(self.body)))
        await interaction.response.defer(thinking=False)


async def setup(bot: commands.Bot):

    if "interface" not in bot.zeroth_ring:
        config_table = tomlkit.table()
        config_table["timeout"] = 0.0
        bot.zeroth_ring["interface"] = config_table

    @bot.tree.command()
    async def echo(
        interaction: discord.Interaction,
        body: str,
        reply: Optional[str] = None,
        mention: Optional[bool] = False,
        silent: Optional[bool] = False
    ):
        if reply:
            try:
                msg_id = get_message_snowflake(reply)
                msg = interaction.channel.get_partial_message(msg_id)
                await msg.reply(
                    emojify(body),
                    mention_author=mention,
                    silent=silent
                )
                await interaction.response.send_message(
                    "Replied.",
                    ephemeral=True,
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
                emojify(body),
                silent=silent
            )
            await interaction.response.send_message(
                "Sent.",
                ephemeral=True,
                delete_after=bot.zeroth_ring["interface"]["timeout"]
            )

    @bot.tree.command()
    async def thread(
        interaction: discord.Interaction,
        name: str,
        body: str,
        root: Optional[str] = ""
    ):
        if root:
            try:
                msg_id = get_message_snowflake(root)
                msg = interaction.channel.get_partial_message(msg_id)
                thread = await msg.create_thread(
                    name=name
                )
                await thread.send(
                    emojify(body)
                )
                await interaction.response.send_message(
                    "Thread created.",
                    ephemeral=True,
                    delete_after=bot.zeroth_ring["interface"]["timeout"]
                )
            except ValueError:
                await interaction.response.send_message(
                    "Error in root pararmeter, could not parse.",
                    ephemeral=True,
                )
            except TypeError:
                await interaction.response.send_message(
                    "Error in creation, could not find message.",
                    ephemeral=True,
                )
        else:
            thread = await interaction.channel.create_thread(
                name=name,
                type=discord.ChannelType.public_thread
            )
            await thread.send(
                emojify(body)
            )
            await interaction.response.send_message(
                "Thread created.",
                ephemeral=True,
                delete_after=bot.zeroth_ring["interface"]["timeout"]
            )

    @bot.tree.command()
    async def upload(
        interaction: discord.Interaction,
        attachment: discord.Attachment,
        spoiler: Optional[bool] = False,
        caption: Optional[str] = ""
    ):
        att_file = await attachment.to_file(spoiler=bool(spoiler))
        await interaction.channel.send(
            emojify(caption),
            file=att_file
        )
        await interaction.response.send_message(
            "Uploaded.",
            ephemeral=True,
            delete_after=bot.zeroth_ring["interface"]["timeout"]
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
                delete_after=bot.zeroth_ring["interface"]["timeout"]
            )
        else:
            await interaction.response.send_message(
                "Only proxied messages can be deleted.",
                ephemeral=True
            )
