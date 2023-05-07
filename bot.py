from discord.ext import commands
from discord import Intents


bot = commands.Bot(' ', intents=Intents.default())


async def setup_hook():
    await bot.load_extension('commands')

bot.setup_hook = setup_hook

if __name__ == '__main__':
    with open('TOKEN.txt', 'r') as file:
        bot.run(file.read())
