import random
import typing

import discord
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands

from states import questions
from views import TriviaView


class GeneralCommands(commands.Cog, name="General", description="Get general stuffinojrkf djvndlcx"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="environmental-tip", description="Give environmental tips!",
        extras={'examples': ['', '2015']}
    )
    @app_commands.checks.cooldown(1, 5)
    async def tip(self, interaction, channel: discord.TextChannel = None, hour_interval: app_commands.Range[int, 0, 24] = 0, minute_interval: app_commands.Range[int, 1, 59] = 1):
        channel = channel or interaction.channel
        webhook = await channel.create_webhook(name="Environmental Tips", avatar=await self.bot.user.avatar.read())
        self.bot.redis.hset("environment_tips", webhook.url, hour_interval+minute_interval*60)
        await interaction.response.send_message(f"Environment tips will be sending every `{hour_interval}h{minute_interval}m` in {channel.mention}", ephemeral=True)

    @app_commands.command(
        name="trivia", description="Start an environment based trivia game.",
        extras={'examples': ['', '2015']}
    )
    @app_commands.checks.cooldown(1, 5)
    async def trivia(self, interaction, difficulty: typing.Literal["Easy", "Medium", "Hard"] = None):
        difficulty = difficulty or random.choice(["Easy", "Medium", "Hard"])
        color = {
            "Easy": discord.Color.green(),
            "Medium": discord.Color.yellow(),
            "Hard": discord.Color.red()
        }
        question = random.choice(questions[difficulty])
        embed = discord.Embed(description=question['question'], color=color[difficulty])
        embed.set_footer(text=f"Difficulty: {difficulty}")
        await interaction.response.send_message(embed=embed, view=TriviaView(question['incorrect_answers'], question['correct_answer'], question['explanation']))


async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))