from datetime import datetime

from functions import set_images
from transformers import StateTransformer, State
from views import EmbedPaginator, DropdownView
import discord
from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

class CityCommands(commands.Cog, name="City", description="Get city stuffinojrkf djvndlcx"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="environmental-news", description="Get recent environmental news for a specific city.",
        extras={'examples': ['', '2015']}
    )
    @app_commands.describe(city="The city to get the news from.")
    @app_commands.checks.cooldown(1, 5)
    async def environmental_news(self, interaction, city: str):
        await interaction.response.defer()
        driver.get(f"https://www.google.com/search?client=safari&rls=en&sxsrf=APwXEdcbB_ekodd2TuBTnMlh4vFi-UimGg:1685818812195&q=environmental+news+in+{city.replace(' ', '+')}&tbm=nws&sa=X&ved=2ahUKEwj_i9O75Kf_AhXNF1kFHXITC9UQ0pQJegQICBAB&biw=1470&bih=840&dpr=2")

        page_source = driver.page_source

        embeds = []
        soup = BeautifulSoup(page_source, "lxml")
        for article in soup.find_all("div", {"class": "SoaBEf"}):
            header = article.find("div", {"role": "heading"})
            embed = discord.Embed(title=header.text.replace("\n", " "), description=header.find_next("div").text.replace("\n", " "), url=article.find("a")["href"], color=discord.Color.blue())
            author, _, date = [i.text for i in article.find_all("span")]
            embed.set_footer(text=date)
            authorimg, image, *_ = list(reversed([i["src"] for i in article.find_all("img")])) + [None]
            embeds.append({"embed": embed, "author": author, "attachments": [authorimg] + ([image] if image else [])})

        file, file2 = set_images(embeds[0]['embed'], embeds[0]['attachments'], embeds[0]['author'])
        await interaction.followup.send(embed=embeds[0]["embed"], files=[file]+([file2] if file2 else []), view=EmbedPaginator(embeds))

    @app_commands.command(
        name="volunteer", description="Get volunteer opportunities for a specific city.",
        extras={'examples': ['', '2015']}
    )
    @app_commands.describe(city="The city to get the volunteer opportunities from.")
    @app_commands.checks.cooldown(1, 5)
    async def volunteer(self, interaction, city: str, state: app_commands.Transform[State, StateTransformer]):
        await interaction.response.defer()
        driver.get(f"https://www.volunteermatch.org/search/?l={city.title().replace(' ', '+')}%2C+{state.code}%2C+USA&v=false&cats=13")
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'lxml')
        embed_dict = {}

        for li in soup.find_all("li", {"class": "pub-srp-opps__opp"}):
            name = li.find("h3")
            org = li.find("div", {"class": "pub-srp-opps__org"}).find("a")
            location, *schedule = reversed(li.find("div", {"class": "pub-srp-opps__info"}).get_text(strip=True).split("|"))
            embed = discord.Embed(
                title=name.find("span").text,
                url="https://www.volunteermatch.org"+name.find("a")['href'],
                color=discord.Color.blue(),
                description=li.find("p", {"class": "pub-srp-opps__desc"}).text+"..."
            ).add_field(
                name="Organization",
                value=f"[{org.text}](https://www.volunteermatch.org{org['href']})",
                inline=False
            ).add_field(
                name="Time",
                value=" @ ".join(schedule)
            ).add_field(
                name="Location",
                value=location
            ).set_footer(
                text=li.find("div", {"class": "pub-srp-opps__posted pub-srp-opps__sml-txt"}).text
            )
            embed_dict[name.find("span").text] = embed

        await interaction.followup.send(embed=list(embed_dict.values())[0], view=DropdownView(embed_dict))

    @app_commands.command(
        name="weather", description="Get the weather for a specific city."
    )
    @app_commands.describe(city="The city to get the weather from.")
    @app_commands.checks.cooldown(1, 5)
    async def weather(self, interaction, city: str):
        api_key = '398663e783bf63c2db8e8f0a4878941f'
        async with self.bot.session.get(f"https://api.openweathermap.org/data/2.5/weather?q={city.lower().replace(' ', '-')}&units=imperial&APPID={api_key}") as r:
            weather_data = await r.json()

        embed = discord.Embed(
            title=f"{city.title()} Weather",
            color=discord.Color.blue(),
            description=f"{weather_data['weather'][0]['description'].title()}"
        ).add_field(
            name="Current Temperature: ",
            value=f"`{round(weather_data['main']['temp'])}°F`"
        ).add_field(
            name="Max Temperature: ",
            value=f"`{round(weather_data['main']['temp_max'])}°F`"
        ).add_field(
            name="Min Temperatures: ",
            value=f"`{round(weather_data['main']['temp_min'])}°F`"
        ).set_footer(
            text=f"{datetime.now().date().strftime('%m/%d/%y')}"
        )
        images = {
            "Clouds": "https://ssl.gstatic.com/onebox/weather/64/cloudy.png",
            "Mist": "https://ssl.gstatic.com/onebox/weather/64/fog.png",
            "Clear": "https://ssl.gstatic.com/onebox/weather/64/sunny.png",
            "Rain": "https://ssl.gstatic.com/onebox/weather/64/rain_light.png"
        }
        embed.set_thumbnail(url=images[weather_data['weather'][0]['main']])

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="air-quality", description="Get the air quality index for a specific city.",
        extras={'examples': ['', '2015']}
    )
    @app_commands.describe(city="The city to get the AQI from.")
    @app_commands.checks.cooldown(1, 5)
    async def aq(self, interaction, city: str, state: app_commands.Transform[State, StateTransformer] ):
        image2 = "https://bazallergy.com/wp-content/uploads/2022/03/Baz-Allergy-Air-Quality-Index-EDITS2.png"
        async with self.bot.session.get(f"https://www.iqair.com/us/usa/{state.name.lower().replace(' ', '-')}/{city.lower().replace(' ', '-')}") as r:
            soup = BeautifulSoup(await r.text(), "html.parser")

        main = soup.find("table", class_="aqi-overview-detail__main-pollution-table")
        aqi = main.find_all("td")[1].text
        values = aqi.split()
        aq_value = int(values[0])
        embed = discord.Embed(
            title=f"{city.title()} {state.name.title()} Air Quality",
            color=discord.Color.blue(),
            description=f"**AQI LEVEL**: ``{aq_value}``"
        ).set_thumbnail(
            url=image2
        ).set_footer(
            text=f"{datetime.now().date().strftime('%m/%d/%y')}"
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CityCommands(bot))