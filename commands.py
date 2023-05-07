from discord.ext import commands


class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot):
    CommandsCog(bot)
