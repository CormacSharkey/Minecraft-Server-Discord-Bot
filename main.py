import os

from selenium import webdriver  

import discord
from discord.ext import commands
from dotenv import load_dotenv

driver = webdriver.Chrome()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.message_content = True


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(name='marco')
async def marco(ctx):
    await ctx.send("polo")

@bot.command(name='website')
async def website(ctx):
    driver.get('https://www.minecraftcraftingguide.net/')
    await ctx.send("Website open!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    elif message.content == "Hello":
        print(message.author.name)
        await message.channel.send("Hello there " + message.author.name + "!")
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print(bot.guilds[0].name)
    print("----------")

bot.run(TOKEN)

# client = discord.Client(intents=intents)

# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to Discord!')

# client.run(TOKEN)