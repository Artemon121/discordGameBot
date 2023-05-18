from enum import Enum

import discord
from discord import ui, Interaction

import checks

class Player(Enum):
    X = True
    O = False


class Winner(Enum):
    X = 1
    O = 2
    DRAW = 3
    NONE = 4


class TickTackToe:
    SYMBOL_X = '❌'
    SYMBOL_O = '⭕'

    def __init__(self):
        """Initialize the game."""
        self.player_x: discord.User = ...
        self.player_o: discord.User = ...
        self.message: discord.Message = ...
        self.turn: Player = Player.X

        self.board: list[list[str]] = [['', '', ''],
                                       ['', '', ''],
                                       ['', '', '']]

    def get_field_from_pos(self, pos: int) -> str:
        """Get value of field at given pos (0 - 8)"""
        return self.board[pos // 3][pos % 3]

    def set_field_from_pos(self, pos: int, value: str) -> None:
        """Set value of field at given pos (0 - 8)"""
        self.board[pos // 3][pos % 3] = value

    def get_current_player(self) -> discord.User:
        """Get the user, who is currently making a move"""
        if self.turn == Player.X:
            return self.player_x
        else:
            return self.player_o

    def get_game_embed(self) -> discord.Embed:
        """Returns discord.Embed for the game"""
        e = discord.Embed(
            title='Крестики-Нолики'
        )
        if self.turn == Player.X:
            e.set_author(name=self.player_x.name + f'  {self.SYMBOL_X}', icon_url=self.player_x.display_avatar.url)
            e.set_footer(text=self.player_o.name + f'  {self.SYMBOL_O}', icon_url=self.player_o.display_avatar.url)
        else:
            e.set_author(name=self.player_o.name + f'  {self.SYMBOL_O}', icon_url=self.player_o.display_avatar.url)
            e.set_footer(text=self.player_x.name + f'  {self.SYMBOL_X}', icon_url=self.player_x.display_avatar.url)
        return e

    async def start_game(self, interaction: Interaction) -> None:
        """Start the game. Will respond to given interaction"""
        if self.player_x is None or self.player_o is None:
            raise ValueError('One of the players is missing!')
        if not checks.start_game_checks(interaction, self.player_x, self.player_o):
            return
        await interaction.response.send_message(embed=self.get_game_embed(), view=GameView(self))

    def check_winner(self) -> tuple[Winner, list[int | None]]:
        """Checks if someone has won the game and returns the winning positions"""
        # check rows
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] and self.board[row][0] != '':
                winner = Winner.X if self.board[row][0] == self.SYMBOL_X else Winner.O
                return winner, [row * 3, row * 3 + 1, row * 3 + 2]

        # check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] and self.board[0][col] != '':
                winner = Winner.X if self.board[0][col] == self.SYMBOL_X else Winner.O
                return winner, [col, col + 3, col + 6]

        # check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] != '':
            winner = Winner.X if self.board[0][0] == self.SYMBOL_X else Winner.O
            return winner, [0, 4, 8]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] != '':
            winner = Winner.X if self.board[0][2] == self.SYMBOL_X else Winner.O
            return winner, [2, 4, 6]

        # check draw
        if all(field != '' for row in self.board for field in row):
            return Winner.DRAW, list(range(9))

        # no winner yet
        return Winner.NONE, []

    def get_winner(self) -> discord.User | None:
        """Get winner user"""
        winner, _ = self.check_winner()
        if winner == winner.X:
            return self.player_x
        elif winner == winner.O:
            return self.player_o
        return None

    def mark_field(self, pos: int) -> None:
        """Marks field on the board"""
        if self.turn == Player.X:
            self.set_field_from_pos(pos, self.SYMBOL_X)
        elif self.turn == Player.O:
            self.set_field_from_pos(pos, self.SYMBOL_O)

    async def game_end_response(self, interaction: Interaction) -> None:
        """Response to the game ending (win or draw)"""
        winner, wining_position = self.check_winner()
        e: discord.Embed
        if winner == Winner.X:
            e = discord.Embed(
                description=f'{self.SYMBOL_X} ``{self.get_winner().name}`` выиграл!',
                color=discord.Color.green()
            )
        elif winner == Winner.O:
            e = discord.Embed(
                description=f'{self.SYMBOL_O} ``{self.get_winner().name}`` выиграл!',
                color=discord.Color.green()
            )
        elif winner == Winner.DRAW:
            e = discord.Embed(
                description='Ничья!',
                color=discord.Color.yellow()
            )
        else:
            raise Exception('There is no winner yet winner_response() was called!')
        return await interaction.response.edit_message(embed=e, view=GameView(self))

    async def button_callback(self, interaction: Interaction, pos: int) -> None:
        """Called when one of the field buttons is clicked"""
        if self.get_current_player().id != interaction.user.id:
            await interaction.response.send_message('Сейчас не ваш ход!', ephemeral=True)
            return
        if self.get_field_from_pos(pos) != '':
            await interaction.response.send_message('На это поле уже походили!', ephemeral=True)
            return

        self.mark_field(pos)
        winner, _ = self.check_winner()
        if winner != winner.NONE:
            return await self.game_end_response(interaction)

        self.turn = Player.O if self.turn == Player.X else Player.X
        await interaction.response.edit_message(embed=self.get_game_embed(), view=GameView(self))


class FieldButton(ui.Button):
    """Button that represents a field on the board"""

    def __init__(self, game: TickTackToe, pos: int) -> None:
        self.game = game
        self.pos = pos
        winner, winning_positions = game.check_winner()
        field = game.get_field_from_pos(pos)
        super().__init__(label='\u200B',  # Empty label
                         emoji=field if field else None,
                         style=discord.ButtonStyle.green if pos in winning_positions else discord.ButtonStyle.grey,
                         row=pos // 3,
                         disabled=winner != Winner.NONE)

    async def callback(self, interaction: Interaction) -> None:
        """Called when one of the field buttons is clicked"""
        await self.game.button_callback(interaction, self.pos)


class GameView(ui.View):
    """View that represents the game field"""

    def __init__(self, game: TickTackToe) -> None:
        super().__init__(timeout=None)
        self.game = game
        self.clear_items()

        for i in range(9):
            btn = FieldButton(self.game, i)
            self.add_item(btn)
