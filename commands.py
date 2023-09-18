from typing import Literal, Optional

import discord
from discord.ext import commands
from discord import app_commands

import rock_paper_scissors
import tick_tack_toe


class CommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
            self,
            ctx: commands.Context,
            guilds: commands.Greedy[discord.Object],
            spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @app_commands.command(name='tick_tack_toe', description='Сыграть в крестики-нолики')
    @app_commands.describe(member='С кем вы хотите сыграть')
    async def play_tick_tack_toe(self, interaction: discord.Interaction, member: discord.Member) -> None:
        game = tick_tack_toe.TickTackToe()
        game.player_o = interaction.user
        game.player_x = member
        await game.start_game(interaction)

    @app_commands.command(name='rock_paper_scissors', description='Сыграть в камень-ножницы-бумагу')
    @app_commands.describe(user='С кем вы хотите сыграть')
    async def play_rock_paper_scissors(self, interaction: discord.Interaction, user: discord.User) -> None:
        game = rock_paper_scissors.RockPaperScissors()
        game.player1 = interaction.user
        game.player2 = user
        await game.start_game(interaction)


async def setup(bot: commands.Bot):
    await bot.add_cog(CommandsCog(bot))
