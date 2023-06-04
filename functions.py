import base64

import discord


def set_images(embed, attachments, author):
    with open("author.jpg", "wb") as fh:
        fh.write(base64.decodebytes(attachments[0].replace("data:image/png;base64,", "").encode()))

    file = discord.File("author.jpg", filename="author.jpg")
    embed.set_author(name=author, icon_url="attachment://author.jpg")

    file2 = None
    if len(attachments) == 2:
        with open("thumbnail.jpg", "wb") as fh:
            fh.write(base64.decodebytes(attachments[1].replace("data:image/jpeg;base64,", "").encode()))
        file2 = discord.File("thumbnail.jpg", filename="thumbnail.jpg")
        embed.set_thumbnail(url="attachment://thumbnail.jpg")

    return file, file2

def create_embed(stats, user):
    return discord.Embed(
        title=f"{user}'s Game (Day {stats['days']})",
        description=f"""**Credits**: `{stats['credits']}`
                        **Happiness:** `{stats['happiness']}%`
                        **Pollution:** `{stats['pollution']}%`
                        """, colour=discord.Color.blue()
    )