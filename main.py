import botCommands as bc

import discord
from discord.ext import commands
from dotenv import load_dotenv

import asyncio
import os
import importlib

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Set the bot's intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.message_content = True
intents.voice_states = True

# Specify the bot's command prefix and intents
bot = commands.Bot(command_prefix='?', intents=intents)

@bot.command(name='reload')
async def reload(ctx):
    importlib.reload(bc)
    await ctx.send("Successfully reloaded")

# TODO: finish the comment
# Bot Event - 
@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)

    if message.author.bot:
        return
    elif message.content.startswith("!"):
        messageArguments = message.content.split(maxsplit=1)
        command = getattr(bc, messageArguments[0][1:], None)

        if (command):
            messageArguments[1] if len(messageArguments) > 1 else None
            await command(ctx, messageArguments[1])
        else:
            await ctx.send("Womp womp that's crazy talk")   
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if (before.channel):
        if bot.user in before.channel.members and len([m for m in before.channel.members if not m.bot]) == 0:
            channel = discord.utils.get(bot.voice_clients, channel=before.channel)
            await channel.disconnect()


# Bot Event - when the bot is ready, it prints out its self info and server info
@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print(bot.guilds[0].name)
    print("----------")

bot.run(TOKEN)