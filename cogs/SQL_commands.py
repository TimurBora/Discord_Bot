import disnake
import random
import aiosqlite
import googletrans
from googletrans import Translator
from disnake.ext import commands

class SQL_Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()

    @commands.command()
    async def random_aphorism(self, ext):
        '''Высылаем в Дискорд из базы данных случайный афоризм'''
        db = await aiosqlite.connect("main.db")
        cursor = await db.cursor()
        random_aphorism_query = '''SELECT "AFORIZM", "AUTHOR"         
                                   FROM "TB4"
                                   ORDER BY RANDOM()
                                   LIMIT 1;''' # Получаем из базы данных случайный афоризм   
        await cursor.execute(random_aphorism_query)
        aphorism_rus = await cursor.fetchall() 
        aphorism_rus = aphorism_rus[0][0] + '---' + aphorism_rus[0][1] # Из tuple делаем обычную строку
        aphorism_sr = self.translator.translate(aphorism_rus, dest="sr")
        await cursor.close()
        await db.close()
        await ext.send(aphorism_rus)
        
        

def setup(bot):
    bot.add_cog(SQL_Random(bot))
