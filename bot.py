'''
TODO List:

Make commands not be fancy message'd.
Implement pictures to work.
Log all changed information.
'''


#importing file manager
import os

#importing discord and dotenv commands
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from discord import FFmpegPCMAudio, FFmpegAudio, FFmpegOpusAudio

#importing random commands
import random

import datetime
import time

from pydub import AudioSegment

#importing shouldGo methods
from shouldGoMethods import *

#stating necessary intents of the bot (can view members and view/edit messages)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

#grabs the discord token and servers from another file (.env)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ROYALS = os.getenv('DISCORD_ROYALS').split(",")
BULLY = os.getenv('DISCORD_BULLY').split(",")

#sets the client to be a discord client with the chosen intents
bot = commands.Bot(command_prefix='!', intents=intents)

#event when the discord bot starts
@bot.event
async def on_ready():
    bullyModeFile = open("bullyMode.txt", "w")
    bullyMode = None
    while bullyMode == None:
        setToBully = input("Set to bully mode? y/n ")
        if setToBully == 'y' or 'Y':
            bullyMode = True
            bullyModeFile.write(str(bullyMode))
        elif setToBully == 'n' or 'N':
            bullyMode = False
            bullyModeFile.write(str(bullyMode))
    bullyModeFile.close()
    
    #sets guild to be the server in the other file if it's connected to the bot
    specialGuild = discord.utils.get(bot.guilds, name=GUILD)

    for guild in bot.guilds:
        if guild != specialGuild:
            print(
            f'{bot.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
            )
            #prints the members of the server
            members = '\n - '.join([member.name for member in guild.members])
            print(f'Guild Members:\n - {members}\n')
        
        else:
            print(
            f'{bot.user} is connected to the following special guild:\n'
            f'{specialGuild.name}(id: {specialGuild.id})'
            )
            #prints the members of the server
            members = '\n - '.join([member.name for member in guild.members])
            print(f'Guild Members:\n - {members}\n')

    #creates a file called ranMem.txt that is blank
    ranMemFile = open("ranMem.txt", "w")
    #chooses a random server member and puts their name into the ranMem.txt file
    for guild in bot.guilds:
        randomMember = guild.members[random.randint(0,guild.member_count-1)]
        ranMemFile.write(str(randomMember) + ";" + str(guild.id) + "\n")
    ranMemFile.close()

    
    shouldGoFile = open("shouldGo.txt", "w")
    for guild in bot.guilds:
        shouldGoFile.write("True;" + str(guild.id) + "\n")
    shouldGoFile.close()

    logFile = open("log.txt", "a")
    timestamp = datetime.datetime.now()
    logFile.write("\nCode started on %s.\n" %(str(timestamp.strftime('%d %b %Y, at %H:%M'))))

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}!", ephemeral=True)

@bot.tree.command(name="say")
@app_commands.describe(arg = "What should I say?")
async def say(interaction: discord.Interaction, arg: str):
    await interaction.response.send_message(f"{interaction.user.name} said: '{arg}'")

# @bot.tree.command(name="addtemproyal")
# @app_commands.describe(arg = "Which user should be added?")
# async def addtemproyal(interaction: discord.Interaction, arg : str):
#     ranMemFile = open("ranMem.txt", "a")
#     ranMemFile.write("%s;%s\n" %(arg,interaction.guild.id))
#     ranMemFile.close()
#     await interaction.response.send_message(f'You added a temporary Royal with the username: {arg}')

# @bot.command
# async def addTempRoyal(ctx, arg):
#     ranMemFile = open("ranMem.txt", "a")
#     ranMemFile.write("%s;%s\n" %(arg,ctx.guild.id))
#     ranMemFile.close()
#     await ctx.send(f'You added a temporary Royal with the username: {arg}')

@bot.tree.command(name="bully")
@app_commands.describe(arg = "Who should I bully?")
async def say(interaction: discord.Interaction, arg: discord.Member):
    vc = await arg.voice.channel.connect()
    try:
        audio_file_path = 'C:/Users/adnbr/OneDrive/Desktop/Other/Codes/My Royal Discord bot/bully.mp3'
        vc.play(FFmpegPCMAudio(executable='ffmpeg', source=audio_file_path))
        while vc.is_playing():
                time.sleep(.1)
    # script_dir = os.path.dirname(__file__)  # Get the directory of the current script
    # audio_file_path = os.path.join(script_dir, "bully.mp3")  # Join the directory with the audio file name
    # vc.play(AudioSegment.from_file(audio_file_path))
    finally:
        await vc.disconnect()

#event when a new message appears
@bot.event
async def on_message(message):

    #does nothing if the message's author is the bot
    if message.author == bot.user:
        return
    
    #checks the message for commands
    await bot.process_commands(message)
    
    bullyModeFile = open("bullyMode.txt", "r")
    bullyModeFileLine = bullyModeFile.readline()
    bullyMode = bool(bullyModeFileLine)

    messageGuild = message.guild.id
    ranMemFile = open("ranMem.txt", "r")
    ranMemFileLine = ranMemFile.readline()

    shouldGoTell = ""
    shouldGo = open("shouldGo.txt", "r")
    shouldGoLines = shouldGo.readlines()
    for number, shouldGoLine in enumerate(shouldGoLines):
        splitShouldGoLine = shouldGoLine.split(";")
        if int(splitShouldGoLine[1][:-1:]) == int(messageGuild):
            shouldGoTell = splitShouldGoLine[0]
    shouldGo.close()

    for royal in (ROYALS):
        if message.author.name == royal:
            if message.content == "!stop":
                shouldGoFalse(messageGuild)
                timestamp = datetime.datetime.now()
                logFile = open("log.txt", "a")
                logFile.write("User %s stopped the code in server %s.    Timestamp: %s\n" %(message.author.name,message.guild.name,str(timestamp.strftime('%d %b %Y, %H:%M'))))
                logFile.close()
                return
    
    for royal in (ROYALS):
        if message.author.name == royal:
            if message.content == "!start" and bullyMode == False:
                shouldGoTrue(messageGuild)
                timestamp = datetime.datetime.now()
                logFile = open("log.txt", "a")
                logFile.write("User %s started the code in server %s.    Timestamp: %s\n" %(message.author.name,message.guild.name,str(timestamp.strftime('%d %b %Y, %H:%M'))))
                logFile.close()
                return

    if message.author.name in BULLY and bullyMode == True:
        randNum = random.randint(1,2)
        line1 = ""
        line2 = ""
        if randNum == 1:
            line1 = f'*You hear a tiny gremlin named {message.author.name} say:*'
        elif randNum == 2:
            line1 = f'*You hear a tiny gremlin named {message.author.name} shout:*'
        if message.content != "" and 'https://' not in message.content:
            line2 = '\n> "%s"' %(message.content)
        await message.channel.send(line1 + line2)
        if 'https://' in message.content:
            await message.channel.send(message.content)
        if message.attachments:
            await message.channel.send(message.attachments[0])
        await message.delete()
        return
    
    #if the message author is a royal it sends a new fancy message and deletes the royal's original message
    for royal in (ROYALS):
        if message.author.name == royal and bullyMode == False:
            if shouldGoTell == "True":
                await message.channel.send('**Hear ye, Hear ye.**\nThe fart baron ***%s*** has made the following statement:\n> "%s"' %(message.author.display_name,message.content))
                await message.delete()
                return

    #if the message author is the random person chosen earlier it sends a new fancy message and deletes the random person's original message
    while ranMemFileLine != "":
        ranMemFileLineSplit = ranMemFileLine.split(";")
        if int(ranMemFileLineSplit[1][:-1:]) == int(messageGuild):
            if ranMemFileLineSplit[0] == message.author.name and bullyMode == False:
                if shouldGoTell == "True":
                    await message.channel.send('**Hear ye, Hear ye.**\nThe randomly chosen fart baron ***%s*** has made the following statement:\n> "%s"' %(message.author.display_name,message.content))
                    await message.delete()
                    return
        ranMemFileLine = ranMemFile.readline()
    
    shouldGo.close()
    ranMemFile.close()

bot.run(TOKEN)