import os
import time
import asyncio

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

global QUEUE
global RESULTS_LINKS


FILE_LOCATION = "C:/Users/corma/Desktop/Code/Python/Repos/Minecraft-Server-Discord-Bot/Audios/"
MAX_RESULTS = 5
RESULTS_LINKS = []
QUEUE = []

def download_audio(link):
    if os.path.exists("Audios/song.mp3"):
        os.remove("Audios/song.mp3")
    with yt_dlp.YoutubeDL({'extract_audio': True, 'format': 'bestaudio', 'outtmpl': FILE_LOCATION+'song.mp3'}) as video:
        video.download(link)    
        print("Successfully Downloaded Link " + link)

def yt_search(query):
    results = YoutubeSearch(query, max_results=MAX_RESULTS).to_dict()
    return results


# Add uBlock Origin to the Chrome Driver
chop = webdriver.ChromeOptions()
chop.add_extension('CJPALHDLNBPAFIAMEJDNHCPHJBKEIAGM_1_57_0_0.crx')
chop.add_argument('--headless=new')
chop.add_argument('--start-maximized')
driver = webdriver.Chrome(options = chop)

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
async def play(ctx, arg):
    download_audio(arg)

    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel
    if (voice_channel):
        # vc = await voice_channel.connect()
        ctx.guild.voice_client.play(discord.FFmpegPCMAudio(executable="C:/FFMPEG/bin/ffmpeg.exe", source="Audios/song.mp3"))
        # ctx.voice_client.disconnect()
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")

# TODO - change it so that the message sends with all the data together after it is stored
@bot.command(name="searchYT")
async def searchYT(ctx, *, arg):
    global RESULTS_LINKS
    RESULTS_LINKS.clear()
    results = yt_search(arg)
    for i in range(0, len(results)):
        RESULTS_LINKS.append([results[i].get("title"), "https://www.youtube.com/" + results[i].get("url_suffix")])
        await ctx.send(str(i+1) + ". " + results[i].get("title"))

@bot.command(name="Q")
async def Q(ctx, arg):
    global QUEUE
    global RESULTS_LINKS
    QUEUE.append(RESULTS_LINKS[int(arg)-1])
    await ctx.send("Queueing " + RESULTS_LINKS[int(arg)-1][0] + ".....")

@bot.command(name="DQ")
async def DQ(ctx):
    global QUEUE
    QUEUE.pop(1)

@bot.command(name="showQ")
async def showQ(ctx):
    global QUEUE
    for i in range(0, len(QUEUE)):
        await ctx.send(QUEUE[i][0])
        print(QUEUE[i][0])

@bot.command(name="playQ")
async def playQ(ctx):
    global QUEUE
    while len(QUEUE) > 0:
        download_audio(QUEUE[0][1])

        while (ctx.voice_client.is_playing()):
                await asyncio.sleep(1)
                print("Playing")

        # Gets voice channel of message author
        voice_channel = ctx.author.voice.channel
        if (voice_channel):
            ctx.guild.voice_client.play(discord.FFmpegPCMAudio(executable="C:/FFMPEG/bin/ffmpeg.exe", source="Audios/song.mp3"))
        else:
            await ctx.send(str(ctx.author.name) + "is not in a channel.")
        await ctx.send("Playing '" + QUEUE[0][0] + "'.....")
        QUEUE.pop(0)


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

# client = discord.Client(intents=intents)

# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to Discord!')

# client.run(TOKEN)