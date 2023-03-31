import disnake
import googletrans
import random
from disnake.ext import commands
from disnake import Option, OptionType, SelectMenu, SelectOption
from googletrans import Translator


class Announcement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def ping_member(self, ext, member : disnake.Member, *, text : str = ''):
        await ext.send(f'{member.mention} {text}')

    @commands.slash_command()
    async def announce_roles(self, ext, role : disnake.Role, *, text : str):
        await ext.send(f'{role.mention} {text}')

class Translator_Disnake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()

    @commands.slash_command(name="translate")
    async def _translate(self, ext, from_language , to_language, *, text_to_translate : str):
        '''Функция бота переводить'''
        try:
            result = self.translator.translate(text_to_translate, src=from_language, dest=to_language)
            await ext.send(result.text)
        except ValueError:
            await ext.send("Ошибка: неверный код языка.")
        except Exception as e:
            await ext.send(f"Ошибка: {e}")

class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def quote(self, ext):
        '''Случайное сообщение из чата'''
        messages = []
        async for message in ext.channel.history(limit=100):
            if message.author == self.bot.user or message.content.startswith("!"): #Выбрасываем все сообщения которые сделал бот и которые начинаются с!(т.е. комманды)
                continue
            else:
                messages.append(message)

        quote = random.choice(messages)
        await ext.send(quote.content)

class Count(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def counting(self, ext, start : int, limit : int):
        for i in range(start, limit):
            await ext.send(i)
        
        
def setup(bot):
    bot.add_cog(Announcement(bot))
    bot.add_cog(Translator_Disnake(bot))
    bot.add_cog(Quote(bot))
    bot.add_cog(Count(bot))
