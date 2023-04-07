import disnake
import aiosqlite
import asyncio
import functools
import nacl
import ffmpeg
import sqlite3
from yt_dlp import YoutubeDL
from disnake.ext import commands
from disnake import FFmpegPCMAudio
from SQLMusicBot import SQLMusic

class MusicBotConnection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MusicSQL = SQLMusic()

    @commands.command(name='join')
    async def connect_to_voice(self, ext):
        voice_state = ext.author.voice
        if voice_state is None:
            await ext.send("Vi morate da udjete u voice!")

        else:
            await voice_state.channel.connect(timeout=30.0)

    @commands.command(name='leave')
    async def disconnect_voice(self, ext):
        voice_state = ext.author.voice
        bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=ext.guild)
        
        if self.check_bot_voice(ext, bot_voice_client, voice_state):
            await bot_voice_client.disconnect()
            await ext.send("Iskljucili ste bota iz vojsa!")

            await self.MusicSQL.delete_all_row(ext.guild.id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and (not after.channel or before.channel != after.channel):
            bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=member.guild)
            
            if bot_voice_client and len(bot_voice_client.channel.members) == 1:
                await bot_voice_client.disconnect()
                await self.MusicSQL.delete_all_row(ext.guild.id)
                

    async def check_bot_voice(self, ext, bot_voice_client, voice_state):
        if bot_voice_client is None:
            await ext.send("Bot mora da bude u vojsu!")

        elif voice_state is None:
            await ext.send("Vi morati biti u vojsu!")

        elif bot_voice_client.channel != voice_state.channel:
            await ext.send("Vi morate biti zajedno sa botom u vojsu!")

        elif bot_voice_client.channel == voice_state.channel:
            return True


class MusicYoutube:
    def __init__(self):
        self.youtube_options = {'format': 'bestaudio', 'noplaylist':'True'}
        self.youtube_dl = YoutubeDL(self.youtube_options)

    async def get_url(self, url):
        info_youtube = self.youtube_dl.extract_info(url, download=False)
        URL_video = info_youtube['url']

        return URL_video

    async def get_name(self, url):
        info_youtube = self.youtube_dl.extract_info(url, download=False)
        name_video = info_youtube['title']

        return name_video


class MusicBotPlaying(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = asyncio.get_event_loop()
        self.MusicSQL = SQLMusic()
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.youtube = MusicYoutube()

    async def play_song(self, ext, url, add_music=True):
        URL_video = await self.youtube.get_url(url)
        bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=ext.author.guild)
        voice_state = ext.author.voice

        def next_song(error):
            delete_row = self.MusicSQL.delete_row(ext.guild.id, url)
            asyncio.run_coroutine_threadsafe(delete_row, self.loop)
            
            select_all_music_sync = self.MusicSQL.select_all_music(ext.guild.id)
            select_all_music_async = len(asyncio.run_coroutine_threadsafe(select_all_music_sync, self.loop).result())

            if select_all_music_async > 0:
                info_url_sync = self.MusicSQL.select_music_url(ext.guild.id)
                info_url_async = asyncio.run_coroutine_threadsafe(info_url_sync, self.loop)
                
                play_next_song = self.play_song(ext, info_url_async.result(), False)
                asyncio.run_coroutine_threadsafe(play_next_song, self.loop)

        if await self.check_bot_voice(ext, bot_voice_client, voice_state):
            if bot_voice_client.is_playing() or bot_voice_client.is_paused():
                try:
                    await self.MusicSQL.add_music(ext.guild.id, url, await self.youtube.get_name(url))
                except sqlite3.IntegrityError:
                    await ext.send('Ta muzika je vec u menu!')

            elif len(await self.MusicSQL.select_all_music(ext.guild.id)) == 0 and not bot_voice_client.is_playing():
                await self.MusicSQL.add_music(ext.guild.id, url, await self.youtube.get_name(url))
                audio_source = FFmpegPCMAudio(URL_video, **self.FFMPEG_OPTIONS)

                bot_voice_client.play(audio_source, after=next_song)

            elif len(await self.MusicSQL.select_all_music(ext.guild.id)) > 0 and not add_music:
                audio_source = FFmpegPCMAudio(URL_video, **self.FFMPEG_OPTIONS)

                bot_voice_client.play(audio_source, after=next_song)
        

    @commands.command()
    async def play(self, ext, url : str, add_music=True):
        await self.play_song(ext, url)

    @commands.command()
    async def skip(self, ext):
        bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=ext.author.guild)
        voice_state = ext.author.voice
        
        if await self.check_bot_voice(ext, bot_voice_client, voice_state):
            if not bot_voice_client.is_playing():
                await ext.send('Bot ne igra nista!')

            if len(await self.MusicSQL.select_all_music(ext.guild.id)) == 1:
                bot_voice_client.stop()

            elif bot_voice_client.is_playing():
                bot_voice_client.stop()

                url = await self.MusicSQL.select_music_url(ext.guild.id)
                await self.play_song(ext, url, add_music=False)

    async def check_bot_voice(self, ext, bot_voice_client, voice_state):
        if bot_voice_client is None:
            await ext.send("Bot mora da bude u vojsu!")

        elif voice_state is None:
            await ext.send("Vi morati biti u vojsu!")

        elif bot_voice_client.channel != voice_state.channel:
            await ext.send("Vi morate biti zajedno sa botom u vojsu!")

        elif bot_voice_client.channel == voice_state.channel:
            return True


class MusicBotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MusicSQL = SQLMusic()

    @commands.command()
    async def pause(self, ext):
        bot_voice_client = disnake.utils.get(self.bot.voice_clients, guild=ext.author.guild)
        voice_state = ext.author.voice

        if await self.check_bot_voice(ext, bot_voice_client, voice_state):
            if bot_voice_client.is_playing():
                bot_voice_client.pause()

            elif bot_voice_client.is_paused():
                bot_voice_client.resume()

            else:
                await ext.send("Bot nista ne igra!")

    @commands.command()
    async def music_menu(self, ext):
        music_menu_embed = disnake.Embed(
            title='Music Menu',
            description='Ovde je sva muzika i njen redosled!',
            color=disnake.Colour.blue())

        
        all_music = await self.MusicSQL.select_all_music(ext.guild.id)
        for music in all_music:
            music_menu_embed.add_field(name=music[2], value=music[1], inline=False)

        await ext.send(embed=music_menu_embed)
    
    async def check_bot_voice(self, ext, bot_voice_client, voice_state):
        if bot_voice_client is None:
            await ext.send("Bot mora da bude u vojsu!")

        elif voice_state is None:
            await ext.send("Vi morati biti u vojsu!")

        elif bot_voice_client.channel != voice_state.channel:
            await ext.send("Vi morate biti zajedno sa botom u vojsu!")

        elif bot_voice_client.channel == voice_state.channel:
            return True

           
def setup(bot):
    bot.add_cog(MusicBotConnection(bot))
    bot.add_cog(MusicBotPlaying(bot))
    bot.add_cog(MusicBotCommands(bot))

    
