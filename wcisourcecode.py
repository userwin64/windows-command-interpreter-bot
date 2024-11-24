import discord
from discord.ext import commands
from datetime import datetime
import random
import json
import os
import logging

# Enable intents (important for member join event)
intents = discord.Intents.all()

# Initialize bot with intents
bot = commands.Bot(intents=intents, command_prefix=">")

# Event to print when bot is running
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')
    await bot.tree.sync()

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

# Define an owner-only check
def is_owner():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == bot.owner_id
    return commands.check(predicate)

@bot.tree.command(description="Make the bot leave a guild (owner only)")
@commands.is_owner()
async def leaveguild(interaction: discord.Interaction, guild_id: int):
    guild = bot.get_guild(guild_id)
    if guild:
        await guild.leave()
        await interaction.response.send_message(f"Left guild: {guild.name}")
    else:
        await interaction.response.send_message("Guild not found.", ephemeral=True)

@bot.tree.command(description="Ban a user by ID (owner only)")
@commands.is_owner()
async def banuser(interaction: discord.Interaction, user_id: int):
    user = await bot.fetch_user(user_id)
    if user:
        await interaction.guild.ban(user, reason="Banned by owner command")
        await interaction.response.send_message(f"Banned user: {user.name}")
    else:
        await interaction.response.send_message("User not found.", ephemeral=True)

# Custom error handler for owner-only commands
@bot.event
async def on_application_command_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.CheckFailure):
        await interaction.response.send_message(":x:", ephemeral=True)
    else:
        raise error  # Re-raise other errors to let them be handled by default

@bot.tree.command(description="Kick a member from the server")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if interaction.user.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Member {member.mention} has been kicked. Reason: {reason}")
    else:
        await interaction.response.send_message(":x:")

@bot.tree.command(description="Ban a member from the server")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if interaction.user.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"Member {member.mention} has been banned. Reason: {reason}")
    else:
        await interaction.response.send_message(":x:")

@bot.tree.command(name="timeout", description="Timeouts a user")
async def timeout(ctx: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if ctx.user.guild_permissions.manage_roles:
        timeout_role = discord.utils.get(ctx.guild.roles, name="timeouted")
        if timeout_role is None:
            timeout_role = await ctx.guild.create_role(name="timeouted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(timeout_role, send_messages=False, speak=False)
        if timeout_role in member.roles:
            await ctx.send(f"{member.mention} is already timeouted!")
        else:
            await member.add_roles(timeout_role, reason=reason)
            await ctx.send(f"Timeouted {member.mention} for {reason}")
    else:
        await ctx.send(":x:")

@bot.tree.command(description="Display the server rules")
async def rules(interaction: discord.Interaction):
    rules_text = (
        "# Rules 📜\n"
        "- No spamming\n"
        "- No scamming\n"
        "- No racial jokes\n"
        "- Do not abuse admin power.\n"
        "- This rule is bound to change, so please do not complain when I warn you about the new rule"
    )
    await interaction.response.send_message(rules_text)

# changed echo cmd
@bot.tree.command(description="Echo a message")
async def echo(interaction: discord.Interaction, text: str):
    # check if the message contains any mentions
    if ("@everyone" in text or "@here" in text or "<@" in text) and interaction.user.id != bot.owner_id:
        await interaction.response.send_message("You are not allowed to use pings in this command.", ephemeral=True)
    else:
        await interaction.response.send_message(
            text,
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                users=True,
                roles=True
            ) if interaction.user.id == bot.owner_id else discord.AllowedMentions.none()
        )

@bot.tree.command(description="Say hello to the chat")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("hello chat")

@bot.tree.command(description="Say you'll be right back to the chat")
async def brb(interaction: discord.Interaction):
    await interaction.response.send_message("brb")

@bot.tree.command(description="Say goodbye to the chat")
async def bye(interaction: discord.Interaction):
    await interaction.response.send_message("bye")

@bot.tree.command(description="Make an announcement in the server")
async def announce(interaction: discord.Interaction, ping: str, channel: discord.TextChannel, message: str):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(":x:", ephemeral=True)
        return

    announcement = f"{ping}\n\n{message}"
    await channel.send(announcement, allowed_mentions=discord.AllowedMentions(roles=True, users=True, everyone=True))
    await interaction.response.send_message(f"Announcement sent in {channel.mention}.", ephemeral=True)

@bot.tree.command(description="Purge messages in a channel")
async def purge(interaction: discord.Interaction, channel: discord.TextChannel, count: int):
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

@bot.tree.command(description="Is bro capping?")
async def is_bro_lying(interaction: discord.Interaction):
    choices = [
        "https://tenor.com/view/cap-phone-call-calling-cap-calling-cap-is-calling-gif-27456793",
        ":x: Bro ain't capping"
    ]
    
    choice = random.choice(choices)
    await interaction.response.send_message(choice)

# Command to set the welcome channel
@bot.tree.command(description="Set the welcome channel for the server")
async def set_welcome_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if interaction.user.guild_permissions.manage_guild:
        welcome_channels[str(interaction.guild.id)] = channel.id
        save_welcome_channels()
        await interaction.response.send_message(f"Welcome channel set to {channel.mention}")
    else:
        await interaction.response.send_message(":x: You don't have permission to set the welcome channel.")

# Event to send a welcome message when a member joins
@bot.event
async def on_member_join(member: discord.Member):
    print(f"Member joined: {member.name} in guild {member.guild.name}")

    welcome_channel_id = welcome_channels.get(str(member.guild.id))
    if welcome_channel_id:
        print(f"Welcome channel found: {welcome_channel_id}")
        channel = member.guild.get_channel(int(welcome_channel_id))
        if channel:
            await channel.send(f"Welcome to {member.guild.name}, {member.mention}! We hope you have a great time here!")
        else:
            print(f"Channel not found for ID {welcome_channel_id}")
    else:
        print(f"No welcome channel set for guild {member.guild.name}")

# Replace your token with the bot token
bot.run("YOUR_TOKEN_GOES_HERE")