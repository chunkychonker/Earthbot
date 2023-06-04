import os
import random

import aiohttp
import discord
from discord.ext import commands, tasks
import redis

from states import environmental_tips


class GlobeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents
        )
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.minutes = 0
        self.session = None

    async def setup_hook(self):
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15"
        self.session = aiohttp.ClientSession(headers={"User-Agent": user_agent})

        for filename in os.listdir(f"cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

        self.environment_tip.start()

    @tasks.loop(minutes=1)
    async def environment_tip(self):
        self.minutes += 1
        tips = self.redis.hgetall("environment_tips")
        for k, v in tips.copy().items():
            if int(v) % self.minutes == 0:
                webhook = discord.Webhook.from_url(k, session=self.session)
                await webhook.send(random.choice(environmental_tips))

    @environment_tip.before_loop
    async def before_tasks(self):
        await self.wait_until_ready()


bot = GlobeBot()


@bot.command()
async def sync(ctx) -> None:
    synced = await ctx.bot.tree.sync()
    local = bot.tree.get_commands()
    for lhs, rhs in zip(local, synced):
        lhs.extras['mention'] = rhs.mention

    await ctx.send(f"Synced {len(synced)} commands globally")

bot.run("MTExNDYyNTEyMTc2MDU5MTg3Mg.GDWjBg.pbm_ljw7e-nibcQu6U6lKXUCgbWjL4sfwEhPXI")
