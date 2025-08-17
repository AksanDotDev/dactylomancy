import discord

from .. import __title__, __url__


class ReferenceEmbed(discord.Embed):

    def __init__(self, colour: discord.Colour) -> None:
        super().__init__(colour=colour)
        self.set_author(
            name=f'{__title__}-system',
            url=__url__,
        )

    def get_simple_embed(self, title: str, description: str) -> discord.Embed:
        # Create a shallow copy for editing
        output = self.copy()
        output.title = title
        output.description = description
        return output


class ReferenceConfigEmbed(ReferenceEmbed):

    def __init__(self, colour_str: str) -> None:
        super().__init__(colour=discord.Colour.from_str(colour_str))


class ReferenceErrorEmbed(ReferenceEmbed):

    def __init__(self) -> None:
        super().__init__(colour=discord.Colour.red())
