from discord import Interaction, User, Embed, Color


async def start_game_checks(interaction: Interaction, player1: User, player2: User) -> bool:
    """
    Checks if one of the players is bot and if player1 and player2 is the same player.
    If check fails it responds to given interaction and returns False.
    Otherwise, returns True.
    """
    if player1.bot or player2.bot:
        await interaction.response.send_message(
            embed=Embed(
                color=Color.brand_red(),
                description='Вы не можете играть с ботами!'),
            ephemeral=True
        )
        return False
    if player1.id == player2.id:
        await interaction.response.send_message(
            embed=Embed(
                color=Color.brand_red(),
                description='Вы не можете играть с самим собой!'),
            ephemeral=True
        )
        return False
    return True
