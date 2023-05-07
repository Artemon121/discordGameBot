from discord.ext import commands
from discord import Intents


bot = commands.Bot(' ', intents=Intents.default())


if __name__ == '__main__':
    bot.load_extension('commands')
    with open('TOKEN.txt', 'r') as file:
        bot.run(file.read())
