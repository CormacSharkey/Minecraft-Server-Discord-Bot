import os
import time

import yt_dlp

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import discord
from discord.ext import commands
from dotenv import load_dotenv

FILE_LOCATION = "C:/Users/corma/Desktop/Code/Python/Repos/Minecraft-Server-Discord-Bot/Audios/"

def download_audio(link):
    with yt_dlp.YoutubeDL({'extract_audio': True, 'format': 'bestaudio', 'outtmpl': FILE_LOCATION+'jangle.mp3'}) as video:
        video.download(link)    
        print("Successfully Downloaded Link " + link)

# Add uBlock Origin to the Chrome Driver
chop = webdriver.ChromeOptions()
chop.add_extension('CJPALHDLNBPAFIAMEJDNHCPHJBKEIAGM_1_57_0_0.crx')
chop.add_argument('--headless=new')
chop.add_argument('--start-maximized')
driver = webdriver.Chrome(options = chop)

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

@bot.command(name='search')
async def website(ctx, arg):
    # Open the Minecraft Crafting Guide website
    driver.get('https://www.minecraftcraftingguide.net/')
    # Wait for 2 seconds to load it
    driver.implicitly_wait(0.1)
    # Dealing with a cookie consent popup (not needed with uBlock Origin)
    # popUp = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/button[1]").click()

    # Find the search box
    searchBox = driver.find_element(By.XPATH, "/html/body/div/div/header/div/form/input[1]")
    # Send the search query
    searchBox.send_keys(arg)
    # Find the search button and click it
    searchButton = driver.find_element(By.XPATH, "/html/body/div/div/header/div/form/input[2]")
    # Click the search button
    searchButton.click()

    # Change the webpage height and width to max
    height = driver.execute_script('return document.documentElement.scrollHeight')
    width  = driver.execute_script('return document.documentElement.scrollWidth')
    driver.set_window_size(width, height)  # the trick
    time.sleep(0.1)

    # Exception Handling - to catch when the search argument isn't valid or no search results
    try:
        # Find the search results
        searchResults = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[1]/div[2]/table/tbody")

        # Save a screenshot of the search results
        searchResults.screenshot("Searches/image.png")
    
        # Save a screenshot of the website
        # driver.save_screenshot("Searches/image.png")
    
        # Open the screenshot and send it
        with open("Searches/image.png", "rb") as f:
            picture = discord.File(f)
            f.close()
            # os.remove("Searches/image.png")
            await ctx.send(file=picture)
    
        # await ctx.send("Website open!")
    except:
        await ctx.send("Womp womp spell better")

# @bot.command(name="connect")
# async def connect(ctx):
#     # Gets voice channel of message author
#     voice_channel = ctx.author.voice.channel
#     # Connect to voice chat if author is in one
#     if (voice_channel):
#         vc = await voice_channel.connect()
#     else:
#         await ctx.send(str(ctx.author.name) + "is not in a channel.")

@bot.command(name="jingle")
async def jingle(ctx):
    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel
    if (voice_channel):
        vc = await voice_channel.connect()
        # ctx.guild.voice_client.play(discord.FFmpegPCMAudio(executable="C:/FFMPEG/bin/ffmpeg.exe", source="Audios/jingle.m4a"))
        vc.play(discord.FFmpegPCMAudio(executable="C:/FFMPEG/bin/ffmpeg.exe", source="Audios/jingle.m4a"))
        ctx.voice_client.disconnect()
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")

@bot.command(name="play")
async def play(ctx, arg):
    download_audio(arg)

    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel
    if (voice_channel):
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio(executable="C:/FFMPEG/bin/ffmpeg.exe", source="Audios/jangle.mp3"))
        ctx.voice_client.disconnect()
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")



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