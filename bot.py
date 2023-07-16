import discord
from discord.ext import commands
import requests
import json
import urllib.request,re
import asyncio
import random
import os
import youtube_dl
import time

bot = commands.Bot(command_prefix='*')

@bot.event
async def on_ready():
    print("bot is ready")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("The Specified Command is not found")


@bot.command()
async def hi(ctx):
    await ctx.send("hello")


@bot.command()
async def gif(ctx, *, search):
    apikey = "4HCOHD7AIVS7"
    lmt = 1
    search_term = search
    r = requests.get("https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, apikey, lmt))
    if r.status_code == 200:
        result = json.loads(r.content)
        await ctx.send(result['results'][0]['url'])
    else:
        result = None


@bot.command()
async def youtube(ctx, *, search):
    search_query = search.replace(' ', '+')
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?search_query=' + search_query
    )
    search_results = re.findall(r"watch\?v=(\S{11})", htm_content.read().decode())
    await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])


@bot.command()
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send('Bot joined')
    else:
        await ctx.send("You must be in a voice channel first so I can join it.")


@bot.command()
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send('Bot left')
    else:
        await ctx.send("I'm not in a voice channel, use the join command to make me join")


@bot.command()
async def say(ctx, *, message):
    await ctx.channel.purge(limit=1)
    await ctx.send(f"{message}")


@bot.command()
@commands.has_any_role('Manager', 'Server Dictator', 'Server Owner')
async def clear(ctx, amount=2):
    await ctx.channel.purge(limit=amount)


@bot.command()
async def spam(ctx, *, message):
    await ctx.send(f"{message} \n " * 10)

@bot.command()
@commands.has_any_role("Server Owner", "Server Dictator")
async def ban(ctx, member: discord.Member = None, *, reason=None):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot ban yourself")
        return
    if reason == None:
        reason = "For bisbehaving!"
    message = f"You have been banned from {ctx.guild.name} for {reason}"
    await member.send(message)
    await ctx.guild.ban(member, reason=reason)
    await ctx.channel.send(f"{member} is banned!")


@bot.command()
@commands.has_any_role("Server Owner", "Server Dictator")
async def kick(ctx, member: discord.User = None, *, reason=None):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot kick yourself")
        return
    if reason == None:
        reason = "For bisbehaving!"
    message = f"You have been kicked from {ctx.guild.name} for {reason}"
    await member.send(message)
    await ctx.guild.kick(member, reason=reason)
    await ctx.channel.send(f"{member} is kicked!")


@bot.command()
async def saygif(ctx, *, message):
    await ctx.channel.purge(limit=1)
    apikey = "4HCOHD7AIVS7"
    lmt = 1
    search_term = message
    r = requests.get("https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, apikey, lmt))
    if r.status_code == 200:
        result = json.loads(r.content)
        await ctx.send(result['results'][0]['url'])
    else:
        result = None


@bot.command()
@commands.has_any_role("Server Owner", "Server Dictator")
async def mute(ctx, member: discord.Member):
    if ctx.message.author.server_permissions.administrator:
        role = discord.utils.get(member.server.roles, name='Muted')
        await ctx.add_roles(member, role)
        embed = discord.Embed(title="User Muted!")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.",
                              color=0xff00f6)
        await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def test_my_luck(ctx, *, number):
    foo = ['1', '2', '3', '4', '5', '6', '7', '8', '9''10']
    await ctx.send(random.choice(foo))
    if number == random.choice:
        await ctx.send("you are lucky")
    else:
        await ctx.send("Better luck next time")


@bot.command()
async def play(ctx, *, search):
    search_query = search.replace(' ', '+')
    htm_content = urllib.request.urlopen(
        'http://www.youtube.com/results?search_query=' + search_query
    )
    search_results = re.findall(r"watch\?v=(\S{11})", htm_content.read().decode())
    url = 'https://www.youtube.com/watch?v=' + search_results[0]
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")
    voice.play(discord.FFmpegPCMAudio("song.mp3"))
    await ctx.send('Playing' + url)


@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_client, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


@bot.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()

    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.channel.send(f"Unbanned: {user.mention}")


@bot.command()
async def ping(ctx):
    msg = "Pong :CustomEmoji: {0.author.mention}"
    await ctx.send(msg)


bot.run("")  #Your bot token to be entered
