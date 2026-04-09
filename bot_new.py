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

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is ready!')
    # Start auto-disconnect task
    bot.loop.create_task(auto_disconnect())

async def auto_disconnect():
    while True:
        await asyncio.sleep(300)  # Check every 5 minutes
        for guild in bot.guilds:
            vc = guild.voice_client
            if vc and not vc.is_playing() and len(vc.channel.members) == 1:  # Only bot
                await vc.disconnect()
                print(f"Auto-disconnected from {guild.name}")

# Global variables

# Global variables
queues = {}
loop_status = {}
current_song = {}  # Track current song title per guild
votes = {}  # Track skip votes per guild
autoplay_status = {}  # Autoplay status per guild

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
        title, source = queues[guild_id].pop(0)
        current_song[guild_id] = title
        ctx.voice_client.play(source, after=lambda e: play_next(ctx, guild_id))
    elif guild_id in autoplay_status and autoplay_status[guild_id] and guild_id in current_song:
        # Autoplay: search similar song
        last_song = current_song[guild_id]
        try:
            query = f"{last_song} music"  # Simple similar search
            info = ytdl.extract_info(f"ytsearch:{query}", download=False)
            url = info["entries"][0]["url"]
            title = info["entries"][0]["title"]
            source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
            current_song[guild_id] = title
            ctx.voice_client.play(source, after=lambda e: play_next(ctx, guild_id))
            # Optional: send message
            asyncio.create_task(ctx.send(f"Autoplay: Memutar **{title}**"))
        except Exception as e:
            print(f"Autoplay error: {e}")
            current_song.pop(guild_id, None)
    else:
        current_song.pop(guild_id, None)  # Clear current song when queue empty

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
            queues[guild_id].append((title, source))  # Store as tuple
            await ctx.send(f"**{title}** Berhasil Ditambahkan ke Antrian.")
        else:
            current_song[guild_id] = title  # Store current song
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
        # Simple skip for now, can add vote later
        ctx.voice_client.stop()
        await ctx.send("Skip Lagunya Bangsat!")
    else:
        await ctx.send("Gak ada lagu yang bisa di-skip!")

@bot.command()
async def autoplay(ctx):
    """Toggle autoplay mode."""
    guild_id = ctx.guild.id
    if guild_id not in autoplay_status:
        autoplay_status[guild_id] = False
    autoplay_status[guild_id] = not autoplay_status[guild_id]
    status = "enabled" if autoplay_status[guild_id] else "disabled"
    await ctx.send(f"Autoplay {status}.")

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
    embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.blue())
    if guild_id in queues and queues[guild_id]:
        queue_list = "\n".join([f"{i+1}. {song[0] if isinstance(song, tuple) else 'Song'}" for i, song in enumerate(queues[guild_id][:10])])
        embed.add_field(name="Queue", value=queue_list or "Empty", inline=False)
        embed.set_footer(text=f"Total songs: {len(queues[guild_id])}")
    else:
        embed.add_field(name="Queue", value="Request Lagunya Dulu Goblok!", inline=False)
    await ctx.send(embed=embed)

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
async def shuffle(ctx):
    """Shuffle the current queue."""
    guild_id = ctx.guild.id
    if guild_id in queues and queues[guild_id]:
        import random
        random.shuffle(queues[guild_id])
        await ctx.send("Queue berhasil diacak!")
    else:
        await ctx.send("Queue kosong, gak ada yang bisa diacak goblok!")

@bot.command()
async def nowplaying(ctx):
    """Show the currently playing song."""
    guild_id = ctx.guild.id
    embed = discord.Embed(title="🎶 Now Playing", color=discord.Color.green())
    if guild_id in current_song:
        embed.add_field(name="Song", value=current_song[guild_id], inline=False)
        embed.set_footer(text="Enjoy the music!")
    else:
        embed.add_field(name="Status", value="Gak ada lagu yang lagi diputar!", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def seek(ctx, time: str):
    """Seek to a specific time in the song (format: MM:SS)."""
    # This is basic; full seek needs more work with FFmpeg.
    await ctx.send(f"Seeking to {time} - fitur ini masih basic, perlu implementasi lebih lanjut.")

@bot.command()
async def playlist(ctx, *, url: str):
    """Load a YouTube playlist."""
    if not ctx.voice_client:
        await join_channel(ctx)

    try:
        info = ytdl.extract_info(url, download=False)
        if 'entries' in info:
            guild_id = ctx.guild.id
            if guild_id not in queues:
                queues[guild_id] = []
            for entry in info['entries']:
                if entry:
                    title = entry.get('title', 'Unknown')
                    url_audio = entry['url']
                    source = discord.FFmpegPCMAudio(url_audio, **FFMPEG_OPTIONS)
                    queues[guild_id].append((title, source))  # Store as tuple
            await ctx.send(f"Playlist loaded with {len(info['entries'])} songs!")
        else:
            await ctx.send("Invalid playlist URL!")
    except Exception as e:
        await ctx.send(f"Error loading playlist: {str(e)}")

# Run the bot / Masukan Token Bot
bot.run("")
