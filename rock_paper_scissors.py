from enum import Enum

import discord
from discord.ui import View, Button

import checks


class Choice(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3


class RockPaperScissors:
    ROCK_SYMBOL = '🪨'
    PAPER_SYMBOL = '📄'
    SCISSORS_SYMBOL = '✂️'

    def __init__(self) -> None:
        """Initialize game variables"""
        self.player1: discord.User = ...
        self.player2: discord.User = ...

        self.player1_choice: Choice | None = None
        self.player2_choice: Choice | None = None

        self.message: discord.Message = ...

    @classmethod
    def get_symbol(cls, choice: Choice) -> str:
        """Get symbol for Choice"""
        if choice == Choice.ROCK:
            return cls.ROCK_SYMBOL
        elif choice == Choice.PAPER:
            return cls.PAPER_SYMBOL
        else:
            return cls.SCISSORS_SYMBOL

    def get_player_choice(self, player: discord.User) -> Choice:
        """Returns choice for given player"""
        if player.id == self.player1.id:
            return self.player1_choice
        elif player.id == self.player2.id:
            return self.player2_choice
        else:
            raise ValueError('Unknown player')

    def player_in_game(self, player: discord.User) -> bool:
        """Checks if given user is a player in this game"""
        return player == self.player1 or player == self.player2

    def _player_game_embed(self, player: discord.User) -> discord.Embed:
        """Returns embed for given player"""
        player_choice = self.get_player_choice(player)
        embed = discord.Embed(
            color=discord.Color.yellow() if player_choice is None else discord.Color.green(),
            description=f'Ждём, пока ``{player.display_name} сделает выбор...``'
            if player_choice is None else
            f'``{player.display_name}`` сделал свой выбор!'
        )
        embed.set_author(name=player.display_name, icon_url=player.display_avatar.url)
        return embed

    def get_game_embeds(self) -> list[discord.Embed]:
        """Returns a list of discord.Embed for the game"""
        player1_embed = self._player_game_embed(self.player1)
        player2_embed = self._player_game_embed(self.player2)
        return [player1_embed, player2_embed]

    async def start_game(self, interaction: discord.Interaction) -> None:
        """Start the game"""
        if not await checks.start_game_checks(interaction, self.player1, self.player2):
            return

        await interaction.response.send_message(embeds=self.get_game_embeds(), view=GameView(self))
        self.message = await interaction.original_response()

    async def check_winners(self) -> None:
        """Checks if somebody has won the game"""
        if self.player1_choice is None or self.player2_choice is None:
            return
        e = discord.Embed()
        if self.player1_choice == self.player2_choice:
            # Draw
            e = discord.Embed(
                description='Ничья!',
                color=discord.Color.yellow()
            )
        elif (self.player1_choice == Choice.ROCK and self.player2_choice == Choice.SCISSORS) or \
             (self.player1_choice == Choice.SCISSORS and self.player2_choice == Choice.PAPER) or \
             (self.player1_choice == Choice.PAPER and self.player2_choice == Choice.ROCK):
            # Player 1 won!
            e = discord.Embed(
                description=f'``{self.player1.display_name}`` выиграл! {self.get_symbol(self.player1_choice)} ⚔️ {self.get_symbol(self.player2_choice)}',
                color=discord.Color.brand_green()
            )
        elif (self.player2_choice == Choice.ROCK and self.player1_choice == Choice.SCISSORS) or \
             (self.player2_choice == Choice.SCISSORS and self.player1_choice == Choice.PAPER) or \
             (self.player2_choice == Choice.PAPER and self.player1_choice == Choice.ROCK):
            # Player 2 won!
            e = discord.Embed(
                description=f'``{self.player2.display_name}`` выиграл! {self.get_symbol(self.player2_choice)} ⚔️ {self.get_symbol(self.player1_choice)}',
                color=discord.Color.brand_green()
            )
        await self.message.edit(embed=e, view=None)

    async def player_choice_response(self, interaction: discord.Interaction, choice: Choice) -> None:
        """Response to player making a choice"""
        if self.player1.id == interaction.user.id:
            if self.player1_choice is not None:
                await interaction.response.send_message(ephemeral=True, embed=discord.Embed(
                    color=discord.Color.brand_red(),
                    description='Вы уже сделали выбор!'
                ))
                return
            self.player1_choice = choice
        elif self.player2.id == interaction.user.id:
            if self.player2_choice is not None:
                await interaction.response.send_message(ephemeral=True, embed=discord.Embed(
                    color=discord.Color.brand_red(),
                    description='Вы уже сделали выбор!'
                ))
                return
            self.player2_choice = choice

        await interaction.response.send_message(ephemeral=True, embed=discord.Embed(
            color=discord.Color.brand_green(),
            description=f'Вы выбрали {self.get_symbol(choice)}!'
        ))
        await self.message.edit(embeds=self.get_game_embeds())
        await self.check_winners()


class ChoiceButton(Button):
    def __init__(self, game: RockPaperScissors, choice: Choice) -> None:
        self.game = game
        self.choice = choice
        super().__init__(label='\u200B',  # Empty label
                         emoji=RockPaperScissors.get_symbol(choice),
                         style=discord.ButtonStyle.grey,
                         row=0)

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.game.player_choice_response(interaction, self.choice)


class ChoiceView(View):
    def __init__(self, game: RockPaperScissors) -> None:
        super().__init__(timeout=None)

        self.add_item(ChoiceButton(game, Choice.ROCK))
        self.add_item(ChoiceButton(game, Choice.PAPER))
        self.add_item(ChoiceButton(game, Choice.SCISSORS))


class GameView(View):
    def __init__(self, game: RockPaperScissors) -> None:
        super().__init__(timeout=None)

        self.game = game
        button = Button(
            label='Выбрать',
            style=discord.ButtonStyle.blurple
        )
        button.callback = self.button_callback
        self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction) -> None:
        if not self.game.player_in_game(interaction.user):
            return await interaction.response.send_message(ephemeral=True, embed=discord.Embed(
                color=discord.Color.brand_red(),
                description='Вы не учавствуете в этой игре!'
            ))
        if self.game.get_player_choice(interaction.user) is not None:
            return await interaction.response.send_message(ephemeral=True, embed=discord.Embed(
                color=discord.Color.brand_red(),
                description='Вы уже сделали свой выбор!'
            ))

        await interaction.response.send_message(ephemeral=True, view=ChoiceView(self.game), embed=discord.Embed(
            color=discord.Color.yellow(),
            description='Что вы выбираете?'
        ))
