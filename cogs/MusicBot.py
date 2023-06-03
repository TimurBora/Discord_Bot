import disnake
import aiosqlite
import asyncio
import functools
import nacl
import ffmpeg
import sqlite3
from yt_dlp import YoutubeDL
from yt_dlp import DownloadError
from disnake.ext import commands
from disnake import FFmpegPCMAudio
from SQLMusicBot import SQLMusic


async def check_bot_voice(ext, bot_voice_client, voice_state):
    if bot_voice_client is None:
        await ext.send("Bot mora da bude u vojsu!")

    elif voice_state is None:
        await ext.send("Vi morati biti u vojsu!")

    elif bot_voice_client.channel != voice_state.channel:
        await ext.send("Vi morate biti zajedno sa botom u vojsu!")

    elif bot_voice_client.channel == voice_state.channel:
        return True
        

class MusicBotConnection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join')
    async def connect_to_voice(self, ext):
        voice_state = ext.author.voice
        if voice_state is None:
            await ext.send("Vi morate da udjete u voice!")

        else:
            await voice_state.channel.connect(timeout=60.0)

    @commands.command(name='leave')
    async def disconnect_voice(self, ext):
        voice_state = ext.author.voice
        bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=ext.guild)
        
        if await check_bot_voice(ext, bot_voice_client, voice_state):
            await bot_voice_client.disconnect()
            await ext.send("Iskljucili ste bota iz vojsa!")

            await MusicSQL.delete_all_row(ext.guild.id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and (not after.channel or before.channel != after.channel):
            bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=member.guild)
            
            if bot_voice_client and len(bot_voice_client.channel.members) == 1:
                await bot_voice_client.disconnect()
                await MusicSQL.delete_all_row(member.guild.id)


class MusicYoutube:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.youtube_options = {'format': 'bestaudio', 'noplaylist':'True'}
        self.youtube_dl = YoutubeDL(self.youtube_options)

    async def get_info(self, url):
        info_youtube = await self.loop.run_in_executor(None, self.youtube_dl.extract_info, url, False)

        return info_youtube

    async def get_info_with_query(self, query):
        max_results = 5
        video_results = (await self.loop.run_in_executor(None, self.youtube_dl.extract_info, f"ytsearch{max_results}:{query}", False))['entries']
        
        return video_results


class MusicBotPlaying(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = asyncio.get_event_loop()
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    async def play_song(self, ext, url, add_music=True):
        bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=ext.author.guild)
        voice_state = ext.author.voice

        if await check_bot_voice(ext, bot_voice_client, voice_state):
            video_info = await Youtube.get_info(url)
            if bot_voice_client.is_playing() or bot_voice_client.is_paused():
                await self.add_music_to_db(ext, url, video_info['title'])

            elif len(await MusicSQL.select_all_music(ext.guild.id)) == 0 and not bot_voice_client.is_playing():
                if await self.add_music_to_db(ext, url, video_info['title']):
                    audio_source = FFmpegPCMAudio(video_info['url'], **self.FFMPEG_OPTIONS)

                    bot_voice_client.play(audio_source, after=lambda error: self.next_song(error=error, ext=ext, url=url))

                    await ext.send(f"Play: {video_info['title']}")

            elif len(await MusicSQL.select_all_music(ext.guild.id)) > 0 and not add_music:
                audio_source = FFmpegPCMAudio(video_info['url'], **self.FFMPEG_OPTIONS)

                bot_voice_client.play(audio_source, after=lambda error: self.next_song(error=error, ext=ext, url=url))
                await ext.send(f"Playing: {video_info['title']}")

    async def add_music_to_db(self, ext, url, title):
        try:
            await MusicSQL.add_music(ext.guild.id, url, title)
            await ext.send('Ваша музыка поставлена в очередь')
            return True
        except sqlite3.IntegrityError:
            await ext.send('Ta muzika je vec u menu!')

    def next_song(self, error, ext, url):
        delete_row = asyncio.run(MusicSQL.delete_row(ext.guild.id, url))
            
        select_all_music = asyncio.run(MusicSQL.select_all_music(ext.guild.id))

        if len(select_all_music) > 0:
            info_url = asyncio.run(MusicSQL.select_music_url(ext.guild.id))
                
            play_next_song = self.play_song(ext, info_url, False)
            asyncio.run_coroutine_threadsafe(play_next_song, self.loop)

    @commands.command()
    async def play(self, ext, url : str, add_music=True):
        try:
            await self.play_song(ext, url)
        except DownloadError:
            await ext.send('Ne postoji taj link!')
            

    @commands.command()
    async def search(self, ext, *, query):
        bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=ext.author.guild)
        voice_state = ext.author.voice
        if await check_bot_voice(ext, bot_voice_client, voice_state):
            music_number = 1
            music_choice_embed = disnake.Embed(
                title='Music Choice',
                description='Выбирай число от 1 до 5.',
                color=disnake.Colour.blue())

            info_videos = await Youtube.get_info_with_query(query)

            for video in info_videos:
                music_choice_embed.add_field(name=video['title'], value=f"{music_number}. {video['webpage_url']}", inline=False)
                music_number += 1
                
            await ext.send(embed=music_choice_embed)
            
            choice = await self.choice(ext, info_videos)
            if choice is None:
                await ext.send("Proslo je vreme biranja!")
            else:
                await self.play_song(ext, info_videos[choice-1]['webpage_url'])

    async def choice(self, ext, info_videos):
        try:
            def check(message):
                return message.channel == ext.channel and message.author == ext.author and str(message.content) in ['1', '2', '3', '4', '5']
                
            music_choice = await self.bot.wait_for('message', check=check, timeout=30.0)
            return int(music_choice.content)
        except asyncio.exceptions.TimeoutError:
            return None


class MusicBotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='pause')
    async def resume_and_pause(self, ext):
        bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=ext.author.guild)
        voice_state = ext.author.voice

        if await check_bot_voice(ext, bot_voice_client, voice_state):
            if bot_voice_client.is_playing():
                bot_voice_client.pause()

            elif bot_voice_client.is_paused():
                bot_voice_client.resume()

            else:
                await ext.send("Bot nista ne igra!")

    @commands.command()
    async def skip(self, ext):
        bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=ext.author.guild)
        voice_state = ext.author.voice
        
        if await check_bot_voice(ext, bot_voice_client, voice_state):
            if not bot_voice_client.is_playing():
                await ext.send('Bot ne igra nista!')

            elif bot_voice_client.is_playing():
                bot_voice_client.stop()

    @commands.command()
    async def music_menu(self, ext):
        music_menu_embed = disnake.Embed(
            title='Music Menu',
            description='Ovde je sva muzika i njen redosled!',
            color=disnake.Colour.blue())

        
        all_music = await MusicSQL.select_all_music(ext.guild.id)
        for music in all_music:
            music_menu_embed.add_field(name=music[2], value=music[1], inline=False)

        await ext.send(embed=music_menu_embed)


MusicSQL = SQLMusic()
Youtube = MusicYoutube()

def setup(bot):
    bot.add_cog(MusicBotConnection(bot))
    bot.add_cog(MusicBotPlaying(bot))
    bot.add_cog(MusicBotCommands(bot))

    
