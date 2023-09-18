from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
from os import environ

intents = Intents.default()
intents.message_content = True
bot = commands.Bot('&&', intents=intents)


async def setup_hook():
    await bot.load_extension('commands')
    await bot.load_extension('context_menus')

bot.setup_hook = setup_hook

if __name__ == '__main__':
    load_dotenv()

    bot.run(environ.get('TOKEN'))
