'''
TODO List:

Make commands not be fancy message'd.
Log all changed information.
Allow replies with text bullying
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

import asyncio

from pydub import AudioSegment

import azure.cognitiveservices.speech as speechsdk

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
        if setToBully in ['y', 'Y']:
            bullyMode = True
            bullyModeFile.write(str(bullyMode))
            while setToBully not in ["a", "t", "b"]:
                setToBully = input("Audio, text, or both? a/t/b ")
                if setToBully in ["a", "t", "b"]:
                    bullyModeFile.write("\n"+str(setToBully))
        elif setToBully in ['n', 'N']:
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

# @bot.tree.command(name="addtemproyal")
# @app_commands.describe(arg = "Which user should be added?")
# async def addtemproyal(interaction: discord.Interaction, arg : str):
#     ranMemFile = open("ranMem.txt", "a")
#     ranMemFile.write("%s;%s\n" %(arg,interaction.guild.id))
#     ranMemFile.close()
#     await interaction.response.send_message(f'You added a temporary Royal with the username: {arg}')
    
@bot.tree.command(name="toggle", description="Toggle my access to the vc you're in.")
async def toggle(interaction: discord.Interaction):

    if interaction.user.voice is None:
        return await interaction.response.send_message('You need to be in a voice channel for this command.', ephemeral=True)

    bullyToggle = "Unbulliable"
    xBullyFile = open("xBullyChannels.txt", "r")
    xBullyFileRead = xBullyFile.readlines()
    if str(xBullyFileRead).find(str(interaction.user.voice.channel)) != -1:
        xBullyFileNew = [x for x in xBullyFileRead if x != f"{str(interaction.user.voice.channel)}\n"]
        xBullyFile.close()
        xBullyFile = open("xBullyChannels.txt", "w")
        xBullyFile.truncate()
        xBullyFile.write(''.join(xBullyFileNew))
        bullyToggle = "Bulliable"

    else:
        xBullyFile.close()
        xBullyFile = open("xBullyChannels.txt", "a")
        xBullyFile.write(f"{str(interaction.user.voice.channel)}\n")
    xBullyFile.close()
    return await interaction.response.send_message(f'Your vc will now be {bullyToggle}.', ephemeral=True)


@bot.tree.command(name="bully")
@app_commands.describe(arg = "Who should I bully?")
async def bully(interaction:discord.Interaction, arg: discord.Member, custom_insult: str="", full_custom: bool=False):
    if arg == bot.user:
        return
    
    xBullyFile = open("xBullyChannels.txt", "r")
    xBullyFileRead = xBullyFile.readlines()
    if str(xBullyFileRead).find(str(arg.voice.channel)) != -1:
        return await interaction.response.send_message('Error: This channel is not available to be bullied.', ephemeral=True)

    bullyModeFile = open("bullyMode.txt", "r")
    bullyModeFile.readline()
    bullyModeFileLine2 = bullyModeFile.readline()

    if bullyModeFileLine2 not in ["a", "b"]:
        return await interaction.response.send_message('Audio bully mode is not on.', ephemeral=True)

    voice_state = arg.voice
    if voice_state is None:
        return await interaction.response.send_message('The victim needs to be in a voice channel for this command.', ephemeral=True)

    speech_config = speechsdk.SpeechConfig(subscription=os.getenv('SPEECH_KEY'), region=os.getenv('SPEECH_REGION'))
    speech_config.speech_synthesis_voice_name='en-GB-OliverNeural'
    file_name = "bully2.mp3"
    file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

    if full_custom:
        if custom_insult != "" and (arg.name != "tigerinboots" or interaction.user.name == "tigerinboots"): text = custom_insult
        else: 
            await interaction.response.send_message(f'Error:\nYou attempted to create a custom insult without a custom message.', ephemeral=True)
            return

    elif custom_insult != "" and (arg.name != "tigerinboots" or interaction.user.name == "tigerinboots"): text = f"Hey {arg.nick}! " + custom_insult
    elif arg.name == "m_clarke": text = f"Haha Emily, you're so short and oh... so... bitchless!"
    elif arg.name == "calamity_starr": text = f"Haha Jona, you're a little avian twink cuck!"
    elif arg.name == "waterkipp": text = f"Haha Dane, you're a fucking giraffe!"
    elif arg.name == "oxx_cass_xxo": text = f"It's ok Cass, I'm sure your lean isn't too bad for you!"
    elif arg.name == "realcraft4ever": text = f"Hey Grandpa, you're too cool to insult. No words can hurt you."
    elif arg.name == "tigerinboots": text = f"You're so cool Adrien!"
    else: text = f"Haha {arg.nick}, you're so short!"
    result = speech_synthesizer.speak_text_async(text).get()
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("\nSpeech synthesized for text [{}] written by [{}], and the audio was saved to [{}]".format(text, interaction.user.name, file_name))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("\nSpeech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

    await interaction.response.send_message(f'{arg.nick} has been bullied.', ephemeral=True)

    vc = await arg.voice.channel.connect()
    audio_file_path = 'C:/Users/adnbr/OneDrive/Desktop/Other/Codes/My Royal Discord bot/audio/bully2.mp3'
    vc.play(FFmpegPCMAudio(executable='ffmpeg', source=audio_file_path))
    while vc.is_playing():
        await asyncio.sleep(.1)
    await vc.disconnect()

@bot.tree.command(name="kill")
@app_commands.describe(arg = "Who should I kill?", message = "What should I tell them?")
@app_commands.checks.has_role(1216137638944313685)
async def kill(interaction:discord.Interaction, arg: discord.Member, message: str=""):
    if arg == (bot.user or interaction.user):
        return

    voice_state = arg.voice
    if voice_state is None:
        return await interaction.response.send_message('The victim needs to be in a voice channel for this command.', ephemeral=True)

    speech_config = speechsdk.SpeechConfig(subscription=os.getenv('SPEECH_KEY'), region=os.getenv('SPEECH_REGION'))
    speech_config.speech_synthesis_voice_name='en-GB-OliverNeural'
    file_name = "bully2.mp3"
    file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

    text = f"Hey {arg.nick}! " + message + "\nGet banged!"

    result = speech_synthesizer.speak_text_async(text).get()
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("\nSpeech synthesized for text [{}] written by [{}], and the audio was saved to [{}]".format(text, interaction.user.name, file_name))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("\nSpeech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

    await interaction.response.send_message(f'{arg.nick} has a laser dot on their forehead.', ephemeral=True)

    vc = await arg.voice.channel.connect()
    audio_file_path = 'C:/Users/adnbr/OneDrive/Desktop/Other/Codes/My Royal Discord bot/audio/bully2.mp3'
    vc.play(FFmpegPCMAudio(executable='ffmpeg', source=audio_file_path))
    while vc.is_playing():
        await asyncio.sleep(.1)
    await arg.move_to(None)
    await vc.disconnect()

@bot.tree.command(name="roulette")
@app_commands.describe(arg = "Who should I roulette?", message = "What should I tell them?")
@app_commands.checks.has_role(1216137638944313685)
async def roulette(interaction:discord.Interaction, arg: discord.Member, message: str=""):
    if arg == (bot.user or interaction.user):
        return

    voice_state = arg.voice
    if voice_state is None:
        return await interaction.response.send_message('The victim needs to be in a voice channel for this command.', ephemeral=True)

    speech_config = speechsdk.SpeechConfig(subscription=os.getenv('SPEECH_KEY'), region=os.getenv('SPEECH_REGION'))
    speech_config.speech_synthesis_voice_name='en-GB-OliverNeural'
    file_name = "bully2.mp3"
    file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

    text = f"Hey {arg.nick}! " + message + "\nGood Luck!"

    result = speech_synthesizer.speak_text_async(text).get()
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("\nSpeech synthesized for text [{}] written by [{}], and the audio was saved to [{}]".format(text, interaction.user.name, file_name))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("\nSpeech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

    channelAmount = random.randint(5,25)
    await interaction.response.send_message(f'{arg.nick} has been spun {channelAmount} times.', ephemeral=True)

    vc = await arg.voice.channel.connect()
    audio_file_path = 'C:/Users/adnbr/OneDrive/Desktop/Other/Codes/My Royal Discord bot/audio/bully2.mp3'
    vc.play(FFmpegPCMAudio(executable='ffmpeg', source=audio_file_path))
    while vc.is_playing():
        await asyncio.sleep(.1)
    ogChannel = arg.voice.channel
    lastChannel = arg.voice.channel
    channel = arg.voice.channel
    for x in range(channelAmount):
        while channel == lastChannel:
            channel = arg.guild.voice_channels[random.randint(0,len(arg.guild.voice_channels)-1)]
        lastChannel = channel
        await arg.move_to(channel)
        time.sleep(0.25)
    await arg.move_to(ogChannel)
    await vc.disconnect()

@bot.tree.command(name="say",description="Speak command, only for Adrien.")
async def say(interaction:discord.Interaction, arg:str=""):
    if interaction.user.name == "tigerinboots":
        await interaction.channel.send(arg)
        return await interaction.response.send_message("I have spoken.", ephemeral=True)
    return await interaction.response.send_message("You're not Adrien, this won't work for you.", ephemeral=True)


#event when a new message appears
@bot.event
async def on_message(message):

    #does nothing if the message's author is the bot
    if message.author == bot.user:
        return
    
    #checks the message for commands
    await bot.process_commands(message)
    
    bullyModeFile = open("bullyMode.txt", "r")
    bullyModeFileLine1 = bullyModeFile.readline()
    bullyMode = bool(bullyModeFileLine1)
    bullyModeFileLine2 = bullyModeFile.readline()

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

    if message.author.name in BULLY and bullyMode == True and bullyModeFileLine2 in ["t", "b"]:
        randNum = random.randint(1,2)
        line1 = ""
        line2 = ""
        if randNum == 1:
            line1 = f'*You hear a tiny gremlin named {message.author.nick} say:*'
        elif randNum == 2:
            line1 = f'*You hear a tiny gremlin named {message.author.nick} shout:*'
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