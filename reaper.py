import discord
import random
import os
import json
import youtube_dl
import asyncio
from discord import channel
from discord.ext import commands, tasks
from itertools import cycle

def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

bot = commands.Bot(command_prefix = ".", get_prefix)
status = cycle(['Status 1', 'Status 2'])
TOKEN = "TOKEN"
players = {}

# Bot is online
@bot.event
async def on_ready():
    change_status.start()
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game('Hello there!'))
    print("Bot is online")

#Status
@tasks.loop(seconds=20)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))

#Ping
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

#8-Ball
@bot.command(aliases=['8ball', 'test'])
async def _8ball(ctx, *, question):
    responses = ['It is certain.',
                'It is decidedly so.',
                'Without a doubt.',
                'Most likely.',
                'Yes.',
                'Really hazy, try again.',
                'Cannot predict now.',
                "Don't count on it.",
                'My sources say NO.']

    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

#Error invalid command
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Invalid command used.')

#Clear messages
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit=amount)

#ERROR amount of messages
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the amount of messages to delete')

#Kick
@bot.command()
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)

#Ban
@bot.command()
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')

#Unban
@bot.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

@bot.command() 
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

#Member-Join
@bot.event
async def on_member_join(member):
    print(f'{member} has joined the server.')

#Member-Leave
@bot.event
async def on_member_remove(member):
    print(f'{member} has left the server.')

#Prefixes
@bot.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '='

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

#prefix pop
@bot.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

#pass in prefix
@bot.command()
async def changeprefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

        await ctx.send(f"Prefix changed to {prefix}")


bot.run(TOKEN)
