import sys
import discord
import asyncio
from discord.ext import commands
from config import ZerothRing


intents = discord.Intents.default()

intents.presences = True
intents.members = True
intents.dm_messages = True

hand = commands.Bot(
    command_prefix=commands.when_mentioned,
    intents=intents
)

# Assign the state management class to the bot for ease of keeping track of it.
hand.zeroth_ring = ZerothRing(sys.argv[1])


# Set a universal check on the command tree for scribe use
async def scribe_check(interaction: discord.Interaction, /) -> bool:
    return interaction.user.id == hand.zeroth_ring.state["discord"]["scribe"]


hand.tree.interaction_check = scribe_check


@hand.event
async def on_ready():
    await hand.tree.sync()


async def load_extensions():
    for cog in hand.zeroth_ring.state["features"]["cogs"]:
        await hand.load_extension(cog)


async def main():
    async with hand:
        await load_extensions()
        await hand.start(hand.zeroth_ring.state["discord"]["token"])


if __name__ == "__main__":
    asyncio.run(main())
