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

# Dynamically reload the botCommands library.
# Error checking not needed since reload will crash if the library is not found.
async def reload(ctx):
    print("INFO: Received intent to reload")
    importlib.reload(bc)
    await ctx.send("Successfully reloaded")

# Command runs on every message and checks to see if it is a command message (i.e. any message starting with '!') 
@bot.event
async def on_message(message):
    #Grab the context to pass to commands
    ctx = await bot.get_context(message)

    if message.author.bot:
        return
    elif message.content.startswith("!"):
        print("INFO: Received command intent")
        # Split at the first whitespace character since every thing after that will be some type of argument.
        # Commands in botCommands should deal with splitting the argument string further if it expects multiple args.
        messageArguments = message.content.split(maxsplit=1)

        if(messageArguments[0][1:] == 'reload'):
            await reload(ctx)
            return


        # Dynamically find the function based on the command provided. If command not found, return None.
        command = getattr(bc, messageArguments[0][1:], None)

        if (command):
            # Since commands can have no arguments, we check to see if the length of the split command is greater than
            # 1. Indicating that there are arguments passed. Otherwise pass in None.
            await command(ctx, messageArguments[1] if len(messageArguments) > 1 else None)
        else:
            # Error if command isb't found
            await ctx.send("Womp womp that's crazy talk")   
            print(f"ERROR: Command '{messageArguments[0][1:]}' is not a valid command")


# Disconnect the bot from the voice channel if no members are there
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