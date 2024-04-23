import os
import time

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



#Made the path relative
FILE_LOCATION = "Audios/"
MAX_RESULTS = 8
RESULTS_LINKS = []
AUDIO_QUEUE = []


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

#? Perhaps replace this with __download_audio to indicate that it is an internal function? Moreso just to stick with
#?  python library conventions.
#TODO[1]: Very slow downloads when providing youtu.be links from phone... could be trinity wifi tho... 
def download_audio(link):
    #This will download the video and title it with the video title.
    #Reason being that we can push the title to AUDIO_QUEUE and then it can serve as the path name when playing  it in
    # the play function 

    #Creating a callback for the postprocessing steps in youtube_dl 
    def __postprocessing_callback(postprocess_response):
        #There are 3 postprocessing steps and this call back gets called each time.
        #The 'status' field will contain whether this dict is from the "started", "processing" or "finished"
        # postprocessing step. We check if the status is "finished" and then append the filename to the queue.
        if postprocess_response['status'] == "finished":
            AUDIO_QUEUE.append(postprocess_response['info_dict']['filename'])

    #Extraxted the options from the context manager since I think this looks a bit cleaner 
    yt_dlp_options = {'extract_audio': True, 
                      'format': 'bestaudio', 
                      'outtmpl': FILE_LOCATION+"%(title)s.mp3",
                      'postprocessor_hooks': [__postprocessing_callback]}
    
    with yt_dlp.YoutubeDL(yt_dlp_options) as video:
        video.download(link)    
        print("Successfully Downloaded Link " + link)

#? Similar idea to the suggestion for download_audio
def yt_search(query):
    results = YoutubeSearch(query, max_results=MAX_RESULTS).to_dict()
    return results


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
    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel
    if (voice_channel):
        # Checking to see if the OS is Linux or Windows (P.S WSL is better ;) )
        if os.name == 'posix':
            executable = "/usr/bin/ffmpeg"
        else:
            executable = "C:/FFMPEG/bin/ffmpeg.exe"

        #See if there is anything to play
        if not len(AUDIO_QUEUE):
            ctx.send("There is nothing in the queue. Add to the queue using !queue")
        
        #Play until there is nothing in the queue
        while len(AUDIO_QUEUE):
            #TODO[1]: Assuming .play is blocking (which I hope to God it is), delete the file.
            #TODO[2]: Test the blocking assumption. Also please please set a breakpoint on the os.remove function.... I
            #TODO:      do not want to brick your pc lol. Like 99% sure it won't... but I am writing this code at 3:30am
            #TODO:      so anything is possible really. 
            # vc = await voice_channel.connect()
            source = AUDIO_QUEUE.pop(0)
            ctx.guild.voice_client.play(discord.FFmpegPCMAudio(executable=executable, source=source))
            os.remove(source)
            # ctx.voice_client.disconnect()
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")

@bot.command(name="queue")
async def queue(ctx, arg):
    await download_audio(arg)

@bot.command(name="dequeue")
async def dequeue(ctx, *args):
    if not len(AUDIO_QUEUE):
        await ctx.send("There is nothing to dequeue")
        return
    
    #If they didn't provide any arguments and there is stuff on the queue
    if not len(args):
        print("Which song do you want to dequeue?")
        await current_queue(ctx)
    else:
        #Loop over all the indicies provided and pop them from the queue
        for i in args:
            if i.isnumeric() and int(i) >= 0 and int(i) < len(AUDIO_QUEUE):
                song = AUDIO_QUEUE.pop(int(i))
                os.remove(song)
        
        await ctx.send("Dequeuing complete!")
        await ctx.send("The current queue:")
        await current_queue(ctx)

async def current_queue(ctx):
    for i in range(0, len(AUDIO_QUEUE)):
        song = AUDIO_QUEUE[i].split("/")[-1]
        await ctx.send(f"{i}) {song}")

@bot.command(name="searchYT")
async def searchYT(ctx, *, arg):
    results = yt_search(arg)
    for i in range(0, len(results)):
        await ctx.send(results[i].get("title") + "\t" + "https://www.youtube.com/" + results[i].get("url_suffix"))


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

