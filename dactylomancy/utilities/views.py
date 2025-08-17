from typing import Optional, Iterable, Container
import discord


class ConfirmationQuery(discord.ui.View):

    def __init__(
        self,
        label: Optional[str] = None,
        style: Optional[discord.ButtonStyle] = None
    ):
        super().__init__(timeout=None)
        if label:
            self.confirm.__setattr__('label', label)
        if style:
            self.confirm.style = style

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.primary)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.interaction = interaction
        self.proceed = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.interaction = interaction
        self.proceed = False
        self.stop()


class SelectionQuery(discord.ui.View):

    def __init__(
        self,
        placeholder: Optional[str],
        options: list[discord.SelectOption],
        max_selections: Optional[int] = None,
        min_selections: Optional[int] = None,
    ):
        super().__init__(timeout=None)
        self.select_options.__setattr__('placeholder', placeholder)
        if max_selections:
            self.select_options.max_values = max_selections
        else:
            self.select_options.max_values = len(options)
        if min_selections:
            self.select_options.min_values = min_selections
        else:
            self.select_options.min_values = 0
        for option in options:
            self.select_options.append_option(option)

    @discord.ui.select(
        cls=discord.ui.Select,
    )
    async def select_options(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.interaction = interaction
        self.values = select.values
        self.stop()


def generate_options(
    labels: Iterable[str],
    values: Optional[Iterable[str]] = None,
    descriptions: Optional[Iterable[str]] = None,
    defaults: Optional[Container[str]] = None,
) -> list[str]:
    if not values:
        values = labels
    if not descriptions:
        descriptions = [None] * len(labels)
    if not defaults:
        defaults = []

    options = []

    for label, value, description in zip(
        labels, values, descriptions
    ):
        options.append(
            discord.SelectOption(
                label=label,
                value=value,
                description=description,
                default=label in defaults
            )
        )

    return options
