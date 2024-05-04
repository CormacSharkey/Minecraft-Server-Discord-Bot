import os
import time
import asyncio
import undetected_chromedriver as uc
import random

import yt_dlp
from youtube_search import YoutubeSearch

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Youtube Searching Mock Code
# results = YoutubeSearch('a-ha', max_results=10).to_dict()
# for i in range(0, len(results)):
#     print(results[i].get("title") + "\t")
#     print("https://www.youtube.com/" + results[i].get("url_suffix"))
# print(results[0].get("title"))

global QUEUE, RESULTS_LINKS, DRIVER_SLEEP, DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP

#Made the path relative
FILE_LOCATION = "Audios/"
MAX_RESULTS = 5

DRIVER_SLEEP = 5
DRIVER_MIN_SLEEP = 1
DRIVER_MAX_SLEEP = 3

QUEUE = []
RESULTS_LINKS = []

# Add uBlock Origin to the Chrome Driver
chop = webdriver.ChromeOptions()
chop.add_extension('CJPALHDLNBPAFIAMEJDNHCPHJBKEIAGM_1_57_0_0.crx')
chop.add_argument('--headless=new')
chop.add_argument('--start-maximized')
driver = webdriver.Chrome(options = chop)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ATERNOS_USERNAME = os.getenv('ATERNOS_USERNAME')
ATERNOS_PASSWORD = os.getenv('ATERNOS_PASSWORD')
# Set the bot's intents
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.message_content = True
intents.voice_states = True

# Specify the bot's command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Bot Command - when user sends "!marco", bot responds with "polo"
@bot.command(name='marco')
async def marco(ctx):
    await ctx.send("polo")

# Bot Command - when user sends "!search [arg]", the bot searches a MC wiki for the arg value as a recipe
# Returns an image of the recipe(s) or an error message for spelling
@bot.command(name='search')
async def website(ctx, *, arg):
    # Open the Minecraft Crafting Guide website
    driver.get('https://www.minecraftcraftingguide.net/')
    # Wait for 0.1 seconds to load it
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
    driver.set_window_size(width, height)
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


# Bot Command - when user sends "!connect", the bot will connect to the same voice chat as the user
# Returns an error message if the user is not in a voice chat
@bot.command(name="connect")
async def connect(ctx):
    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel
    # Connect to voice chat if author is in one
    if (voice_channel):
        vc = await voice_channel.connect()
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")

# Bot Command - when user sends "!disconnect", the bot will disconnect from its voice channel
@bot.command(name="disconnect")
async def disconnect(ctx):
    # Disconnect the bot from the voice channel its in
    await ctx.voice_client.disconnect()

@bot.event
async def on_voice_state_update(member, before, after):
    if (before.channel):
        if bot.user in before.channel.members and len([m for m in before.channel.members if not m.bot]) == 0:
            channel = discord.utils.get(bot.voice_clients, channel=before.channel)
            await channel.disconnect()
    # ctx = await bot.get_context(before)

    # def check_VC():
    #     voice = set()
    #     for v in ctx.guild.voice_channels:
    #         for member in v.members:
    #             voice.add(member.id)
    #     return len(voice) == 0
    
    # if (check_VC()):
    #     await ctx.voice_client.disconnect()



# Bot Command - when user sends "!jingle", the bot will connect to the user's voice chat and play "Aww Creeper!" audio
# Returns an error message if the user is not in a voice chat
# @bot.command(name="jingle")
# async def jingle(ctx):
#     # Gets voice channel of message author
#     voice_channel = ctx.author.voice.channel
#     if (voice_channel):
#         vc = await voice_channel.connect()
#         # ctx.guild.voice_client.play(discord.FFmpegPCMAudio(executable="C:/FFMPEG/bin/ffmpeg.exe", source="Audios/jingle.m4a"))
#         vc.play(discord.FFmpegPCMAudio(executable="C:/FFMPEG/bin/ffmpeg.exe", source="Audios/jingle.m4a"))
#         ctx.voice_client.disconnect()
#     else:
#         await ctx.send(str(ctx.author.name) + "is not in a channel.")

# Bot Command - when user sends "!play [arg]", the bot downloads the audio of the provided arg Youtube video, joins voice chat and plays it
@bot.command(name="play")
async def play(ctx, arg=None):

    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel
    if (voice_channel):
        # Checking to see if the OS is Linux or Windows (P.S WSL is better ;) )
        if os.name == 'posix':
            executable = "/usr/bin/ffmpeg"
        else:
            executable = "C:/FFMPEG/bin/ffmpeg.exe"
        
        ffmpeg_options = {'options': '-vn'}
        
        try:
            while len(QUEUE) > 0:
                source = QUEUE.pop(0)
                ctx.guild.voice_client.play(discord.FFmpegPCMAudio(executable=executable, source=source, **ffmpeg_options))
                while (ctx.voice_client.is_playing()):
                    await asyncio.sleep(1)
        except:
            await ctx.send("Womp womp why did you leave?")

    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")


def yt_search(query):
    results = YoutubeSearch(query, max_results=MAX_RESULTS).to_dict()
    return results

@bot.command(name="searchYT")
async def searchYT(ctx, *, arg):
    global RESULTS_LINKS
    RESULTS_LINKS.clear()
    results = yt_search(arg)
    
    for i in range(0, len(results)):
        RESULTS_LINKS.append([results[i].get("title"), "https://www.youtube.com" + results[i].get("url_suffix")])
    
    for i in range(0, len(results)):
        await ctx.send(results[i].get("title") + "\t" + "https://www.youtube.com" + results[i].get("url_suffix"))


@bot.command(name="queue")
async def queue(ctx, arg):
    #TODO: Use REGEX to santize input before we append

    with yt_dlp.YoutubeDL({'format':'bestaudio'}) as downloader:
        songinfo = downloader.extract_info(RESULTS_LINKS[int(arg)-1][1], download=False)
    QUEUE.append(songinfo["url"])

@bot.command(name="dequeue")
async def dequeue(ctx, arg):
    if not len(QUEUE):
        await ctx.send("There is nothing to dequeue")
        return
    
    if arg.isnumeric() and int(arg) >= 1 and int(arg) < len(QUEUE):
        QUEUE.pop(int(arg) - 1)


@bot.command(name="start")
async def start(ctx):
    global DRIVER_SLEEP, DRIVER_MAX_SLEEP, DRIVER_MIN_SLEEP
    driver = uc.Chrome(headless=False,use_subprocess=False)
    driver.get('https://aternos.org/go/')
    
    #Sleep to prevent bot detection
    asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)
    
    #Find the username input box
    driver.find_element(By.XPATH, '//input[@class="username"]').send_keys(ATERNOS_USERNAME)

    asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    driver.find_element(By.XPATH, '//input[@class="password"]').send_keys(ATERNOS_PASSWORD)

    driver.find_element(By.XPATH, '//button[@title="Login"]').click()
    
    try:
        driver.find_element(By.XPATH, '//button[@class=" css-47sehv"]').click()
    except:
        print("No cookies to agree too. Passing...")
    
    asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    driver.find_element(By.XPATH, '//div[@class="server-body"]').click()

    asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    if(driver.find_element(By.XPATH, '//span[@class="statuslabel-label"]').text != "Offline"):
        await ctx.send("The server is already online")
        return


    driver.find_element(By.XPATH, '//div[@id="start"]').click()

    try:
        driver.find_element(By.XPATH, '//button[@class="btn btn-danger"]').click()
    except:
        print("No notifications to accept")


    while(driver.find_element(By.XPATH, '//span[@class="statuslabel-label"]').text != "Online"):
        asyncio.sleep(5)

    await ctx.send("The server is now online")

@bot.command(name="status")
async def status(ctx):
    global DRIVER_SLEEP, DRIVER_MAX_SLEEP, DRIVER_MIN_SLEEP
    driver = uc.Chrome(headless=False,use_subprocess=False)
    driver.get('https://aternos.org/go/')
    
    #Sleep to prevent bot detection
    asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)
    
    #Find the username input box
    driver.find_element(By.XPATH, '//input[@class="username"]').send_keys(ATERNOS_USERNAME)

    asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    driver.find_element(By.XPATH, '//input[@class="password"]').send_keys(ATERNOS_PASSWORD)

    driver.find_element(By.XPATH, '//button[@title="Login"]').click()
    
    try:
        driver.find_element(By.XPATH, '//button[@class=" css-47sehv"]').click()
    except:
        print("No cookies to agree too. Passing...")
    
    asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    driver.find_element(By.XPATH, '//div[@class="server-body"]').click()

    asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    if(driver.find_element(By.XPATH, '//span[@class="statuslabel-label"]').text == "Offline"):
        await ctx.send("The server is offline")

    elif(driver.find_element(By.XPATH, '//span[@class="statuslabel-label"]').text == "Online"):
        await ctx.send("The server is online")

# Bot Event - when the user sends "Hello", the bot sends back "Hello there user!", where "user" is the user's name
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    elif message.content == "Hello":
        print(message.author.name)
        await message.channel.send("Hello there " + message.author.name + "!")
    await bot.process_commands(message)

# Bot Event - when the bot is ready, it prints out its self info and server info
@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print(bot.guilds[0].name)
    print("----------")

bot.run(TOKEN)
