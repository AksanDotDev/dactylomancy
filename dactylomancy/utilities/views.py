import discord


class ConfirmationQuery(discord.ui.View):

    def __init__(
        self,
        label: str,
        style: discord.ButtonStyle
    ):
        super().__init__(timeout=None)
        self.confirm.__setattr__('label', label)
        self.confirm.style = style

    @discord.ui.button(label='Placeholder', style=discord.ButtonStyle.primary)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.interaction = interaction
        self.proceed = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.interaction = interaction
        self.proceed = False
        self.stop()
