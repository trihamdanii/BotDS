import discord
from discord.ext import commands
import asyncio
from yt_dlp import YoutubeDL
import os
import requests

# Intents and bot prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Global variables
queues = {}
loop_status = {}

# Path to cookies file (update this to your actual path)
COOKIES_PATH = "cookies.txt"

# YTDL configuration
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "extractaudio": True,
    "audioformat": "mp3",
    "cookiefile": COOKIES_PATH  # Use cookies for authenticated requests
}
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

ytdl = YoutubeDL(YTDL_OPTIONS)

# Helper functions
def play_next(ctx, guild_id):
    if guild_id in loop_status and loop_status[guild_id]:  # Loop current song
        ctx.voice_client.play(ctx.voice_client.source, after=lambda e: play_next(ctx, guild_id))
    elif guild_id in queues and queues[guild_id]:
        source = queues[guild_id].pop(0)
        ctx.voice_client.play(source, after=lambda e: play_next(ctx, guild_id))

async def join_channel(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()

# Commands
@bot.command()
async def join(ctx):
    """Join the voice channel."""
    await join_channel(ctx)

@bot.command()
async def leave(ctx):
    """Leave the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx, *, query: str):
    """Play a song from YouTube or SoundCloud."""
    if not ctx.voice_client:
        await join_channel(ctx)

    try:
        # Check if query is a YouTube URL
        if query.startswith("https://www.youtube.com/") or query.startswith("https://youtu.be/"):
            info = ytdl.extract_info(query, download=False)
            url = info["url"]
            title = info["title"]
        else:
            info = ytdl.extract_info(f"ytsearch:{query}", download=False)
            url = info["entries"][0]["url"]
            title = info["entries"][0]["title"]
        
        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)

        guild_id = ctx.guild.id
        if ctx.voice_client.is_playing():
            if guild_id not in queues:
                queues[guild_id] = []
            queues[guild_id].append(source)
            await ctx.send(f"**{title}** Berhasil Ditambahkan ke Antrian.")
        else:
            ctx.voice_client.play(source, after=lambda e: play_next(ctx, guild_id))
            await ctx.send(f"Sedang Memutar: **{title}**")

    except Exception as e:
        await ctx.send(f"Ada Yang Error Goblok!: {str(e)}")

@bot.command()
async def pause(ctx):
    """Pause the current song."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Lagu di Pause.")

@bot.command()
async def resume(ctx):
    """Resume the paused song."""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Lagunya di Lanjut.")

@bot.command()
async def skip(ctx):
    """Skip the current song."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skip Lagunya Bangsat!")

@bot.command()
async def stop(ctx):
    """Stop playback and clear the queue."""
    if ctx.voice_client:
        queues[ctx.guild.id] = []
        ctx.voice_client.stop()
        await ctx.send("Berhenti dan Menghapus Antrian")

@bot.command()
async def bassboost(ctx, intensity: int = 10):
    """Apply bassboost effect."""
    FFMPEG_OPTIONS["options"] = f"-af equalizer=f=40:width_type=o:width=2:g={intensity}"
    await ctx.send(f"Bassboost applied with intensity: {intensity}.")

@bot.command()
async def nightcore(ctx):
    """Apply nightcore effect."""
    FFMPEG_OPTIONS["options"] = "-af asetrate=44100*1.25,aresample=44100"
    await ctx.send("Nightcore effect applied.")

@bot.command()
async def queue(ctx):
    """Display the current song queue."""
    guild_id = ctx.guild.id
    if guild_id in queues and queues[guild_id]:
        await ctx.send(f"Queue:\n" + "\n".join([f"{i+1}. Song" for i, _ in enumerate(queues[guild_id])]))
    else:
        await ctx.send("Request Lagunya Dulu GOBLOK!")

@bot.command()
async def remove(ctx, index: int):
    """Remove a song from the queue."""
    guild_id = ctx.guild.id
    if guild_id in queues and 0 <= index-1 < len(queues[guild_id]):
        removed = queues[guild_id].pop(index-1)
        await ctx.send(f"Hapus Lagu {index} Dari Antrian.")
    else:
        await ctx.send("Gak Ada Lagunya GOBLOK!")

@bot.command()
async def loop(ctx):
    """Toggle looping for the current song."""
    guild_id = ctx.guild.id
    if guild_id not in loop_status:
        loop_status[guild_id] = False
    loop_status[guild_id] = not loop_status[guild_id]
    status = "enabled" if loop_status[guild_id] else "disabled"
    await ctx.send(f"Acak Lagu {status}.")

@bot.command()
async def volume(ctx, level: int):
    """Set the volume of the playback."""
    if ctx.voice_client and 0 <= level <= 200:
        ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
        ctx.voice_client.source.volume = level / 100
        await ctx.send(f"Atur Volume ke {level}%.")
    else:
        await ctx.send("Atur Volumenya Dari 0 - 200.")

@bot.command()
async def lyrics(ctx, *, title: str):
    """Fetch and display lyrics for a song."""
    try:
        response = requests.get(f"https://api.lyrics.ovh/v1/{title}")
        data = response.json()
        lyrics = data.get("lyrics", "Lyrics not found.")
        await ctx.send(lyrics[:2000])  # Discord limits messages to 2000 characters
    except Exception as e:
        await ctx.send(f"Gak Ada Liriknya Bangsat! {str(e)}")

# Run the bot
bot.run("")
