import nextcord
from nextcord.ext import commands
import asyncio
import logging
from datetime import datetime
import sys
import random
import json
import os

# Set up logging to log both to a file and suppress console output
log_filename = datetime.now().strftime("%d-%m-%Y.log")
logging.basicConfig(
    filename=log_filename,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Redirect stdout and stderr to the log file
class StreamToLogger(object):
    def __init__(self, logger, log_level):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

sys.stdout = StreamToLogger(logging.getLogger(), logging.INFO)
sys.stderr = StreamToLogger(logging.getLogger(), logging.ERROR)

# Custom exception handler to log uncaught exceptions
def log_exception(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = log_exception

# Enable intents
intents = nextcord.Intents.default()
intents.message_content = True  # Enable message content intent for prefix commands

# Initialize bot with intents
bot = commands.Bot()

# Event to print when bot is running
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')

# Command to kick a member
@bot.command(name="kick", help="Kick a member from the server")
async def kick(ctx, member: nextcord.Member, *, reason: str = "No reason provided"):
    if ctx.author.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await ctx.send(f"Member {member.mention} has been kicked. Reason: {reason}")
    else:
        await ctx.send(":x:")

# Command to ban a member
@bot.command(name="ban", help="Ban a member from the server")
async def ban(ctx, member: nextcord.Member, *, reason: str = "No reason provided"):
    if ctx.author.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await ctx.send(f"Member {member.mention} has been banned. Reason: {reason}")
    else:
        await ctx.send(":x:")

# Command to timeout a member for a specific duration
@bot.command(name="timeout", help="Timeout a member for a specific duration (in minutes)")
async def timeout(ctx, member: nextcord.Member, duration: int, *, reason: str = "No reason provided"):
    if ctx.author.guild_permissions.moderate_members:
        duration_seconds = duration / 60  # Convert minutes to seconds
        await member.timeout(duration=duration_seconds, reason=reason)
        await ctx.send(f"Member {member.mention} has been timed out for {duration} minutes. Reason: {reason}")
    else:
        await ctx.send(":x:")

# Command to display the server rules
@bot.command(name="rules", help="Display the server rules")
async def rules(ctx):
    rules_text = (
        "# Rules 📜\n"
        "- No spamming\n"
        "- No scamming\n"
        "- No racial jokes\n"
        "- Do not abuse admin power.\n"
        "- This rule is bound to change, so please do not complain when I warn you about the new rule"
    )
    await ctx.send(rules_text)

# Command to echo a message
@bot.command(name="echo", help="Echo a message")
async def echo(ctx, *, text: str):
    await ctx.send(text)

# Command to send a hello message
@bot.command(name="hello", help="Send a hello message to the chat")
async def hello(ctx):
    await ctx.send("hello chat")

# Command to say brb
@bot.command(name="brb", help="Say you'll be right back to the chat")
async def brb(ctx):
    await ctx.send("brb")

# Command to say goodbye
@bot.command(name="bye", help="Say goodbye to the chat")
async def bye(ctx):
    await ctx.send("bye")

# Command to make an announcement in the server
@bot.command(name="announce", help="Make an announcement in the server")
async def announce(ctx, ping: str, channel: nextcord.TextChannel, *, message: str):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send(":x:")
        return

    announcement = f"{ping}\n\n{message}"
    await channel.send(announcement, allowed_mentions=nextcord.AllowedMentions(roles=True, users=True, everyone=True))
    await ctx.send(f"Announcement sent in {channel.mention}.")

# Command to purge messages
@bot.command(name="purge", help="Purge messages in a channel")
async def purge(ctx, channel: nextcord.TextChannel, count: int):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send(":x:")
        return

    if count < 1:
        await ctx.send(":x: You need to specify a number greater than 0.")
        return

    total_deleted = 0
    async for message in channel.history(limit=None):
        if total_deleted >= count:
            break
        try:
            await message.delete()
            total_deleted += 1
        except Exception as e:
            logging.error(f"Failed to delete message: {e}")

    await ctx.send(f"Purged {total_deleted} messages in {channel.mention}.")

# Command to check if bro is capping
@bot.command(name="is_bro_lying", help="Is bro capping?")
async def is_bro_lying(ctx):
    choices = [
        "https://tenor.com/view/cap-phone-call-calling-cap-calling-cap-is-calling-gif-27456793",
        ":x: Bro ain't capping"
    ]
    
    choice = random.choice(choices)
    await ctx.send(choice)

# Slash command versions of the above commands
@bot.slash_command(description="Kick a member from the server")
async def kick(interaction: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason provided"):
    if interaction.user.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Member {member.mention} has been kicked. Reason: {reason}")
    else:
        await interaction.response.send_message(":x:")

@bot.slash_command(description="Ban a member from the server")
async def ban(interaction: nextcord.Interaction, member: nextcord.Member, reason: str = "No reason provided"):
    if interaction.user.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"Member {member.mention} has been banned. Reason: {reason}")
    else:
        await interaction.response.send_message(":x:")

@bot.slash_command(description="Timeout a member for a specific duration")
async def timeout(interaction: nextcord.Interaction, member: nextcord.Member, duration: int, reason: str = "No reason provided"):
    if interaction.user.guild_permissions.moderate_members:
        duration_seconds = duration * 60
        await member.timeout(duration=duration_seconds, reason=reason)
        await interaction.response.send_message(f"Member {member.mention} has been timed out for {duration} minutes. Reason: {reason}")
    else:
        await interaction.response.send_message(":x:")

@bot.slash_command(description="Display the server rules")
async def rules(interaction: nextcord.Interaction):
    rules_text = (
        "# Rules 📜\n"
        "- No spamming\n"
        "- No scamming\n"
        "- No racial jokes\n"
        "- Do not abuse admin power.\n"
        "- This rule is bound to change, so please do not complain when I warn you about the new rule"
    )
    await interaction.response.send_message(rules_text)

@bot.slash_command(description="Echo a message")
async def echo(interaction: nextcord.Interaction, text: str):
    await interaction.response.send_message(text)

@bot.slash_command(description="Send a hello message to the chat")
async def hello(interaction: nextcord.Interaction):
    await interaction.response.send_message("hello chat")

@bot.slash_command(description="Say you'll be right back to the chat")
async def brb(interaction: nextcord.Interaction):
    await interaction.response.send_message("brb")

@bot.slash_command(description="Say goodbye to the chat")
async def bye(interaction: nextcord.Interaction):
    await interaction.response.send_message("bye")

@bot.slash_command(description="Make an announcement in the server")
async def announce(interaction: nextcord.Interaction, ping: str, channel: nextcord.TextChannel, message: str):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(":x:", ephemeral=True)
        return

    announcement = f"{ping}\n\n{message}"
    await channel.send(announcement, allowed_mentions=nextcord.AllowedMentions(roles=True, users=True, everyone=True))
    await interaction.response.send_message(f"Announcement sent in {channel.mention}.", ephemeral=True)

@bot.slash_command(description="Purge messages in a channel, including those older than 14 days")
async def purge(interaction: nextcord.Interaction, channel: nextcord.TextChannel, count: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(":x:", ephemeral=True)
        return

    if count < 1:
        await interaction.response.send_message(":x: You need to specify a number greater than 0.", ephemeral=True)
        return

    total_deleted = 0
    async for message in channel.history(limit=None):
        if total_deleted >= count:
            break
        try:
            await message.delete()
            total_deleted += 1
        except Exception as e:
            logging.error(f"Failed to delete message: {e}")

    await interaction.response.send_message(f"Purged {total_deleted} messages in {channel.mention}.")

@bot.slash_command(description="Is bro capping?")
async def is_bro_lying(interaction: nextcord.Interaction):
    choices = [
        "https://tenor.com/view/cap-phone-call-calling-cap-calling-cap-is-calling-gif-27456793",
        ":x: Bro ain't capping"
    ]
    
    choice = random.choice(choices)
    await interaction.response.send_message(choice)

# File to store welcome channel data
WELCOME_DATA_FILE = "welcomedat.json"

# Load welcome channels from file
def load_welcome_channels():
    if os.path.exists(WELCOME_DATA_FILE):
        with open(WELCOME_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Save welcome channels to file
def save_welcome_channels():
    with open(WELCOME_DATA_FILE, "w") as file:
        json.dump(welcome_channels, file, indent=4)

# Load the welcome channels on startup
welcome_channels = load_welcome_channels()

sys.stdout = StreamToLogger(logging.getLogger(), logging.INFO)
sys.stderr = StreamToLogger(logging.getLogger(), logging.ERROR)

# Custom exception handler to log uncaught exceptions
def log_exception(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = log_exception

# Enable intents (important for member join event)
intents = nextcord.Intents.default()
intents.guilds = True  # Enable guild events
intents.members = True  # Enable member events
intents.message_content = True  # Enable message content intent for prefix commands

# Initialize bot with intents
bot = commands.Bot(intents=intents)

# Event to print when bot is running
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')

# File to store welcome channel data
WELCOME_DATA_FILE = "welcomedat.json"

# Load welcome channels from file
def load_welcome_channels():
    if os.path.exists(WELCOME_DATA_FILE):
        with open(WELCOME_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Save welcome channels to file
def save_welcome_channels():
    with open(WELCOME_DATA_FILE, "w") as file:
        json.dump(welcome_channels, file, indent=4)

# Load the welcome channels on startup
welcome_channels = load_welcome_channels()

# Command to set the welcome channel
@bot.slash_command(description="Set the welcome channel for the server")
async def set_welcome_channel(interaction: nextcord.Interaction, channel: nextcord.TextChannel):
    # Check if the user has the required permission
    if interaction.user.guild_permissions.manage_guild:
        # Store the welcome channel for the guild
        welcome_channels[str(interaction.guild.id)] = channel.id  # Store as string key
        save_welcome_channels()  # Save to file
        await interaction.response.send_message(f"Welcome channel set to {channel.mention}")
    else:
        await interaction.response.send_message(":x: You don't have permission to set the welcome channel.")

# Event to send a welcome message when a member joins
@bot.event
async def on_member_join(member: nextcord.Member):
    # Debugging: Check if member join event is firing
    print(f"Member joined: {member.name} in guild {member.guild.name}")

    # Get the welcome channel for the guild
    welcome_channel_id = welcome_channels.get(str(member.guild.id))

    if welcome_channel_id:
        print(f"Welcome channel found: {welcome_channel_id}")
        # Convert welcome_channel_id to integer
        channel = member.guild.get_channel(int(welcome_channel_id))
        if channel:
            # Send the welcome message if the channel is set
            await channel.send(f"Welcome to {member.guild.name}, {member.mention}! We hope you have a great time here!")
        else:
            print(f"Channel not found for ID {welcome_channel_id}")
    else:
        print(f"No welcome channel set for guild {member.guild.name}")

bot.run("NUH_UH")