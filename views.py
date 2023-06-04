import json
import random
from collections import deque
from discord import ui
import discord

from functions import set_images, create_embed


class EmbedPaginator(ui.View):
    def __init__(self, embeds):
        super().__init__()
        self.queue = deque(embeds)

    async def send(self, interaction):
        content = self.queue[0]
        file, file2 = set_images(content['embed'], content['attachments'], content['author'])
        await interaction.response.edit_message(embed=content["embed"], attachments=[file]+([file2] if file2 else []))

    @ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def previous_embed(self, interaction, _):
        self.queue.rotate(-1)
        await self.send(interaction)

    @ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_embed(self, interaction, _):
        self.queue.rotate(1)
        await self.send(interaction)

class Dropdown(ui.Select):
    def __init__(self, embed_dict):
        super().__init__(
            placeholder="Choose a volunteer opportunity...",
            options=[discord.SelectOption(label=x) for x in embed_dict]
        )
        self.embed_dict = embed_dict

    async def callback(self, interaction):
        await interaction.response.edit_message(embed=self.embed_dict[self.values[0]])

class DropdownView(ui.View):
    def __init__(self, embed_dict):
        super().__init__()
        self.add_item(Dropdown(embed_dict))

class TriviaButton(ui.Button):
    def __init__(self, label):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.blurple
        )

    async def callback(self, interaction):
        for child in self.view.children:
            if child.label == self.view.correct_answer:
                child.style = discord.ButtonStyle.green
            elif child == self:
                child.style = discord.ButtonStyle.red
            else:
                child.style = discord.ButtonStyle.gray
            child.disabled = True

        embed = interaction.message.embeds[0]
        embed.add_field(name="Explanation", value=self.view.explanation)
        await interaction.response.edit_message(view=self.view, embed=embed)

class TriviaView(ui.View):
    def __init__(self, incorrect_answers, correct_answer, explanation):
        super().__init__()
        self.incorrect_answers = incorrect_answers
        self.correct_answer = correct_answer
        self.explanation = explanation

        x = incorrect_answers+[correct_answer]
        random.shuffle(x)
        for answer in x:
            self.add_item(TriviaButton(answer))

async def game_function(self, interaction):
    stats = json.loads(self.view.redis.hget("environment_game", interaction.user.id))
    for k, v in self.projects[self.values[0]].items():
        stats[k] = min(max(0, stats[k]+v), 100) if k not in ["credits", "days"] else stats[k]+v


    if stats["credits"] < 0:
        return await interaction.response.send_message("You don't have enough credits to complete this action!")
    if stats["days"] > 100:
        return await interaction.response.send_message("You don't have enough days left to complete this action!")

    embed = create_embed(stats, interaction.user)
    await interaction.response.edit_message(embed=embed)

    if stats["days"] == 100:
        score = (stats["happiness"]*(100-stats["pollution"]))/10
        self.view.redis.hdel("environment_game", interaction.user.id)
        await interaction.followup.send(f"Your 100 days is over! You finished with a score of `{score}`.")
    else:
        self.view.redis.hset("environment_game", interaction.user.id, json.dumps(stats))

class EnvironmentDropdown(ui.Select):
    projects = {
        "Plant 10 trees":
            {
                "credits": -5,
                "happiness": 1,
                "pollution": -5,
                "days": 5
            },
        "Stage a cleanup":
            {
                "credits": -10,
                "pollution": -10,
                "days": 10
            },
        "Start a renewable energy project":
            {
                "credits": -25,
                "pollution": -30,
                "days": 20
            }
    }

    def __init__(self):
        super().__init__(
            placeholder="Choose an environmental project...",
            options=[
                discord.SelectOption(
                    label="Plant 10 trees",
                    emoji="🌳",
                    description="Credits -5 | Happiness +1 | Pollution -5 | Days +5"
                ),
                discord.SelectOption(
                    label="Stage a cleanup",
                    emoji="🧹",
                    description="Credits -10 | Happiness +0 | Pollution -10 | Days +10"
                ),
                discord.SelectOption(
                    label="Start a renewable energy project",
                    emoji="🌿",
                    description="Credits -25 | Happiness +0 | Pollution -30 | Days +20"
                ),
            ]
        )

    async def callback(self, interaction):
        await game_function(self, interaction)

class CitizenDropdown(ui.Select):
    projects = {
        "Start a community event":
            {
                "credits": 5,
                "happiness": 5,
                "days": 5
            },
        "Start beautification project":
            {
                "credits": 25,
                "happiness": 15,
                "days": 20
            }
    }
    def __init__(self):
        super().__init__(
            placeholder="Choose an citizen-based project...",
            options=[
                discord.SelectOption(
                    label="Start a community event",
                    emoji="🎉",
                    description="Credits +5 | Happiness +5 | Pollution +0 | Days +5"
                ),
                discord.SelectOption(
                    label="Start beautification project",
                    emoji="🌼",
                    description="Credits +25 | Happiness +15 | Pollution +0 | Days +20"
                ),
            ]
        )

    async def callback(self, interaction):
        await game_function(self, interaction)

class GameView(ui.View):
    def __init__(self, redis):
        super().__init__()
        self.add_item(EnvironmentDropdown())
        self.add_item(CitizenDropdown())
        self.redis = redis
