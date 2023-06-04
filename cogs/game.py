import json

import discord
from discord import app_commands
from discord.ext import commands

from functions import create_embed
from views import GameView


class GameCommandfs(commands.Cog, name="Game", description="Get general stuffinojrkf djvndlcx"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="start", description="Start an environmental based game.",
        extras={'examples': ['', '2015']}
    )
    @app_commands.checks.cooldown(1, 5)
    async def start(self, interaction):
        self.bot.redis.hset("environment_game", interaction.user.id,
                            json.dumps({
                                "credits": 10,
                                "days": 0,
                                "happiness": 50,
                                "pollution": 50,
                            }))
        stats = json.loads(self.bot.redis.hget("environment_game", interaction.user.id))
        embed = create_embed(stats, interaction.user)
        await interaction.response.send_message(embed=embed, view=GameView(self.bot.redis))

async def setup(bot):
    await bot.add_cog(GameCommandfs(bot))