from discord.ext import commands
from discord import Intents

intents = Intents.default()
intents.message_content = True
bot = commands.Bot('&&', intents=intents)


async def setup_hook():
    await bot.load_extension('commands')

bot.setup_hook = setup_hook

if __name__ == '__main__':
    with open('TOKEN.txt', 'r') as file:
        bot.run(file.read())
