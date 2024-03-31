import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.message_content = True


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command
async def marco(ctx):
    await ctx.send("polo")


bot.run(TOKEN)

# client = discord.Client(intents=intents)

# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to Discord!')

# client.run(TOKEN)