import discord
import tomlkit
from discord.ext import commands
from typing import Optional
from speech.parsing import format_message, get_message_snowflake


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
        await self.message.edit(content=format_message(str(self.body)))
        await interaction.response.defer(thinking=False)


async def setup(bot: commands.Bot):

    if "interface" not in bot.zeroth_ring:
        config_table = tomlkit.table()
        config_table["timeout"] = 0.0
        config_table["silent_success"] = True
        bot.zeroth_ring["interface"] = config_table

    @bot.tree.command()
    @discord.app_commands.user_install()
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def invoke(
        interaction: discord.Interaction,
        body: str
    ):
        await interaction.response.send_message(
            format_message(body)
        )

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
                msg = await interaction.channel.fetch_message(msg_id)
                await msg.reply(
                    format_message(body),
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
                format_message(body),
                silent=silent
            )
            await interaction.response.send_message(
                "Sent.",
                ephemeral=True,
                silent=bot.zeroth_ring["interface"]["silent_success"],
                delete_after=bot.zeroth_ring["interface"]["timeout"]
            )

    @bot.tree.command()
    async def thread(
        interaction: discord.Interaction,
        name: str,
        body: str,
        root: Optional[str] = None
    ):
        if root:
            try:
                msg_id = get_message_snowflake(root)
                msg = await interaction.channel.fetch_message(msg_id)
                thread = await msg.create_thread(
                    name=name
                )
                await thread.send(
                    format_message(body)
                )
                await interaction.response.send_message(
                    "Thread created.",
                    ephemeral=True,
                    silent=bot.zeroth_ring["interface"]["silent_success"],
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
                format_message(body)
            )
            await interaction.response.send_message(
                "Thread created.",
                ephemeral=True,
                silent=bot.zeroth_ring["interface"]["silent_success"],
                delete_after=bot.zeroth_ring["interface"]["timeout"]
            )

    @bot.tree.command()
    async def upload(
        interaction: discord.Interaction,
        attachment: discord.Attachment,
        spoiler: Optional[bool] = False,
        caption: Optional[str] = "",
        reply: Optional[str] = None,
        mention: Optional[bool] = False,
        silent: Optional[bool] = False,
        ancillary_i: Optional[discord.Attachment] = None,
        ancillary_ii: Optional[discord.Attachment] = None,
        ancillary_iii: Optional[discord.Attachment] = None,
        ancillary_iv: Optional[discord.Attachment] = None,
        ancillary_v: Optional[discord.Attachment] = None,
        ancillary_vi: Optional[discord.Attachment] = None,
        ancillary_vii: Optional[discord.Attachment] = None,
        ancillary_viii: Optional[discord.Attachment] = None,
        ancillary_ix: Optional[discord.Attachment] = None,
    ):
        await interaction.response.defer(
            ephemeral=True,
            thinking=True
        )
        attachments = [
            attachment, ancillary_i, ancillary_ii, ancillary_iii,
            ancillary_iv, ancillary_v, ancillary_vi, ancillary_vii,
            ancillary_viii, ancillary_ix
        ]

        att_files = []
        skipped = []

        for file in attachments:
            if file:
                if file.size > interaction.guild.filesize_limit:
                    skipped.append(file.filename)
                else:
                    att_files.append(
                        await file.to_file(spoiler=spoiler)
                    )

        if not att_files:
            await interaction.followup.send(
                content="No file below server file size limit attached, message not sent."
            )

        if reply:
            try:
                msg_id = get_message_snowflake(reply)
                msg = await interaction.channel.fetch_message(msg_id)

                await msg.reply(
                    format_message(caption),
                    mention_author=mention,
                    silent=silent,
                    files=att_files
                )
                if skipped:
                    await interaction.followup.send(
                        content="Uploaded as a reply, while skipping: "
                        + f"{', '.join(skipped)}, due to file sizes.",
                        ephemeral=True,
                        silent=bot.zeroth_ring["interface"]["silent_success"]
                    )
                else:
                    await interaction.followup.send(
                        content="Uploaded as a reply.",
                        ephemeral=True,
                        silent=bot.zeroth_ring["interface"]["silent_success"]
                    )
            except ValueError:
                await interaction.followup.send(
                    content="Error in reply pararmeter, could not parse.",
                    ephemeral=True
                )
            except TypeError:
                await interaction.followup.send(
                    content="Error in replying, could not find message.",
                    ephemeral=True
                )
        else:
            await interaction.channel.send(
                format_message(caption),
                silent=silent,
                files=att_files
            )
            if skipped:
                await interaction.followup.send(
                    content="Uploaded, while skipping: "
                    + f"{', '.join(skipped)}, due to file sizes.",
                    ephemeral=True,
                    silent=bot.zeroth_ring["interface"]["silent_success"]
                )
            else:
                await interaction.followup.send(
                    content="Uploaded.",
                    ephemeral=True,
                    silent=bot.zeroth_ring["interface"]["silent_success"]
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
                silent=bot.zeroth_ring["interface"]["silent_success"],
                delete_after=bot.zeroth_ring["interface"]["timeout"]
            )
        else:
            await interaction.response.send_message(
                "Only proxied messages can be deleted.",
                ephemeral=True
            )
