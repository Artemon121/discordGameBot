from discord.ext import commands
from discord.app_commands import ContextMenu
import discord

import tick_tack_toe


async def play_tick_tack_toe(interaction: discord.Interaction, member: discord.Member) -> None:
    game = tick_tack_toe.TickTackToe()
    game.player_o = interaction.user
    game.player_x = member
    await game.start_game(interaction)


all_context_menus: list[ContextMenu] = [
        ContextMenu(name='Сыграть в крестики-нолики', callback=play_tick_tack_toe)
]


async def setup(bot: commands.Bot) -> None:
    for menu in all_context_menus:
        bot.tree.add_command(menu)
