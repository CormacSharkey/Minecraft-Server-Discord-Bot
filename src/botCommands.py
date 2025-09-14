import os
import asyncio
import undetected_chromedriver as uc
import random

import yt_dlp
from youtubesearchpython import VideosSearch


from selenium import webdriver
from selenium.webdriver.common.by import By

import discord
from discord.ext import commands


# import logging
# logging.basicConfig(level=logging.DEBUG)
# # then run your bot — look for websocket/voice close codes and stack traces



global QUEUE, RESULTS_LINKS, DRIVER_SLEEP, DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP

#Made the path relative
FILE_LOCATION = "Audios/"
MAX_RESULTS = 5

DRIVER_SLEEP = 5
DRIVER_MIN_SLEEP = 1
DRIVER_MAX_SLEEP = 3

QUEUE = []
RESULTS_LINKS = []


chop = webdriver.FirefoxOptions()
chop.add_argument('--headless')
chop.add_argument("--width=1280")
chop.add_argument("--height=1450")
driver = webdriver.Firefox(options = chop)
driver.install_addon('Resources/uBlock0@raymondhill.net.xpi') # Add uBlock Origin

# Add uBlock Origin to the Chrome Driver
# chop.add_extension('CJPALHDLNBPAFIAMEJDNHCPHJBKEIAGM_1_57_0_0.crx')
# chop.add_argument('--start-maximized')

# load_dotenv()
ATERNOS_USERNAME = os.getenv('ATERNOS_USERNAME')
ATERNOS_PASSWORD = os.getenv('ATERNOS_PASSWORD')

#! Working
# Bot Command - when user sends "!marco", bot responds with "polo"
async def marco(ctx, arg):
    await ctx.send("polo")

#! Working
# Bot Command - when user sends "!search [arg]", the bot searches a MC wiki for the arg value as a recipe
# Returns an image of the recipe(s) or an error message for spelling
async def search(ctx, arg):
    # Open the Minecraft Crafting Guide website
    driver.get(f'https://www.minecraftcraftingguide.net/search/?s={arg}')
    # Wait for 0.1 seconds to load it
    driver.implicitly_wait(0.1)

    # Exception Handling - to catch when the search argument isn't valid or no search results
    try:
        # Save a screenshot of the website
        driver.save_screenshot("Searches/image.png")
    
        # Open the screenshot and send it
        with open("Searches/image.png", "rb") as f:
            picture = discord.File(f)
            f.close()
            # os.remove("Searches/image.png")
            await ctx.send(file=picture)
    except:
        await ctx.send("Womp womp spell better")

#! Working
# Bot Command - when user sends "!connect", the bot will connect to the same voice chat as the user
# Returns an error message if the user is not in a voice chat
async def connect(ctx, arg):
    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel
    # Connect to voice chat if author is in one
    if (voice_channel):
        vc = await voice_channel.connect()
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")

#! Working
# Bot Command - when user sends "!disconnect", the bot will disconnect from its voice channel
async def disconnect(ctx, arg):
    # Disconnect the bot from the voice channel its in
    await ctx.voice_client.disconnect()

#! Working
async def play(ctx):
    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel
    if (voice_channel):
        # Checking to see if the OS is Linux or Windows (P.S Linux is better ;) )
        if os.name == 'posix':
            executable = "/usr/bin/ffmpeg"
        else:
            executable = "C:/FFMPEG/bin/ffmpeg.exe"
        
        ffmpeg_options = {'options': '-vn'}
        
        try:
            while len(QUEUE) > 0:
                source = QUEUE.pop(0)
                ctx.guild.voice_client.play(discord.FFmpegPCMAudio(executable=executable, source=source, **ffmpeg_options))
                while (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
                    await asyncio.sleep(1)
        except Exception as e:
            print(e)
            await ctx.send("Womp womp why did you leave?")

    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")

#? Untested
async def pause(ctx):
    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel

    ctx.guild.voice_client.pause()

#? Untested
async def resume(ctx):
    # Gets voice channel of message author
    voice_channel = ctx.author.voice.channel

    ctx.guild.voice_client.resume()

#! Working
def __yt_search(query):
    results = VideosSearch(query, limit=MAX_RESULTS).result()
    return results.get("result")

#! Working
async def searchYT(ctx, arg):
    global RESULTS_LINKS
    RESULTS_LINKS.clear()
    results = __yt_search(arg)
    
    for i in range(0, len(results)):
        RESULTS_LINKS.append([results[i].get("title"), results[i].get("link")])
    
    for i in range(0, len(results)):
        await ctx.send(f"{RESULTS_LINKS[i][0]}\n{RESULTS_LINKS[i][1]}")

#! Working
async def queue(ctx, arg):
    with yt_dlp.YoutubeDL({'format':'bestaudio'}) as downloader:
        songinfo = downloader.extract_info(RESULTS_LINKS[int(arg)-1][1], download=False)
    QUEUE.append(songinfo["url"])

#! Working
async def dequeue(ctx, arg):
    if not len(QUEUE):
        await ctx.send("There is nothing to dequeue")
        return
    
    if arg.isnumeric() and int(arg) >= 1 and int(arg) < len(QUEUE):
        QUEUE.pop(int(arg) - 1)

async def start(ctx, arg):
    global DRIVER_SLEEP, DRIVER_MAX_SLEEP, DRIVER_MIN_SLEEP
    await ctx.send("Starting the server...")
    chrome_opt = uc.ChromeOptions()
    prefs = {"credentials_enable_service": False,
     "profile.password_manager_enabled": False}
    chrome_opt.add_experimental_option("prefs", prefs)
    chrome_opt.add_argument("--password-store=basic")
    chrome_opt.add_argument("--incognito")
   
    driver = uc.Chrome(chrome_options=chrome_opt, headless=False,use_subprocess=False)
    driver.get('https://aternos.org/go/')
    
    #Sleep to prevent bot detection
    await asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)
    
    #Find the username input box
    driver.find_element(By.XPATH, '//input[@class="username"]').send_keys(ATERNOS_USERNAME)

    await asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    driver.find_element(By.XPATH, '//input[@class="password"]').send_keys(ATERNOS_PASSWORD)

    driver.find_element(By.XPATH, '//button[@title="Login"]').click()
    
    await asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)
    
    try:
        driver.find_element(By.XPATH, '//button[@class=" css-47sehv"]').click()
    except:
        print("No cookies to agree too. Passing...")
    
    await asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    driver.find_element(By.XPATH, '//div[@class="server-body"]').click()

    await asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    try:
        print("Ad blocker detected. Moving around this")
        driver.find_element(By.XPATH, '//div[@text() = "Continue with adblocker anyway"]').click()
    except:
        print("Ad blocker not detected.")

    if(driver.find_element(By.XPATH, '//span[@class="statuslabel-label"]').text != "Offline"):
        await ctx.send("The server is already online")
        return


    driver.find_element(By.XPATH, '//div[@id="start"]').click()

    await asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    try:
        driver.find_element(By.XPATH, '//button[@class="btn btn-danger"]').click()
    except:
        print("No notifications to accept")   

    try:
        driver.find_element(By.XPATH, '//button[@class = "btn btn-success"]').click()
        while(driver.find_element(By.XPATH, '//div[@id = "count_down]').text() != "Reward in 0 seconds"):
            await asyncio.sleep(2)
        driver.find_element(By.XPATH, '//div[@id = "close_button"]').click()
    except:
        print("No ad to watch")

    


    while(driver.find_element(By.XPATH, '//span[@class="statuslabel-label"]').text != "Online"):
        await asyncio.sleep(5)

    await ctx.send("The server is now online")
    driver.close()

# @bot.command(name="status")
async def status(ctx, arg):
    global DRIVER_SLEEP, DRIVER_MAX_SLEEP, DRIVER_MIN_SLEEP
    chrome_opt = uc.ChromeOptions()
    driver = uc.Chrome(headless=False,use_subprocess=True)
    driver.get('https://aternos.org/go/')
    
    #Sleep to prevent bot detection
    await asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)
    
    #Find the username input box
    driver.find_element(By.XPATH, '//input[@class="username"]').send_keys(ATERNOS_USERNAME)

    # await asyncio.sleep(DRIVER_SLEEP)
    # DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    driver.find_element(By.XPATH, '//input[@class="password"]').send_keys(ATERNOS_PASSWORD)

    await asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    driver.find_element(By.XPATH, '//button[@title="Login"]').click()

    await asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)
    
    try:
        driver.find_element(By.XPATH, '//button[@class=" css-47sehv"]').click()
    except:
        print("No cookies to agree too. Passing...")
    
    # await asyncio.sleep(DRIVER_SLEEP)
    # DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    driver.find_element(By.XPATH, '//div[@class="server-body"]').click()

    await asyncio.sleep(DRIVER_SLEEP)
    DRIVER_SLEEP = random.randint(DRIVER_MIN_SLEEP, DRIVER_MAX_SLEEP)

    if(driver.find_element(By.XPATH, '//span[@class="statuslabel-label"]').text == "Offline"):
        await ctx.send("The server is offline")

    elif(driver.find_element(By.XPATH, '//span[@class="statuslabel-label"]').text == "Online"):
        await ctx.send("The server is online")
    
    driver.close()
