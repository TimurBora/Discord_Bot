import disnake
import random
import requests
import sqlite3
import bs4
from io import BytesIO
from PIL import Image
from disnake.ext import commands

class Random_Images(commands.Cog):
    '''Комманды которые используют рандом'''
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def random_image(self, ext, width=500, height=500):
        random_image_url = f"https://random.imagecdn.app/{width}/{height}"
        image_response = requests.get(random_image_url)
        
        image = Image.open(BytesIO(image_response.content)) # Перекодируем фотографию
        image.save("random_image.jpeg")
        file = disnake.File("random_image.jpeg") # Создаём файл который отправим в чат
        
        await ext.send(file=file)

    @commands.command()
    async def random_gif(self, ext):
        random_gif_url = "https://api.giphy.com/v1/gifs/random?api_key=nrdmtTBWMMqbJCOJqAP9huzApy8se4Y7&tag=&rating=g"
        gif_response = requests.get(random_gif_url).json() # Получаем ответ в .json формате
        gif = gif_response["data"]["url"] # Получаем из ответа только "url", его отправляем в чат
        
        await ext.send(gif)

    @commands.command()
    async def random_meme(self, ext):
        random_meme_url = 'https://www.reddit.com/r/meme/random.json?limit=1'
        meme_response = requests.get(random_meme_url, headers={"User-agent": "MyBot"}).json()
        meme_image = meme_response[0]["data"]["children"][0]["data"]["url"]

        await ext.send(meme_image)
        

        
class Random_Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="random_joke")
    async def random_anekdot(self, ext):
        random_anekdot_url = "https://anekdotme.ru/random"
        response = requests.get(random_anekdot_url) 
        response_html = bs4.BeautifulSoup(response.text, "html.parser")     #Парсируем html файл
        
        anekdot_texts = response_html.select(".anekdot_text") # Берём из него текст
        random_anekdot_text = random.choice(anekdot_texts).getText().strip()
        
        await ext.send(random_anekdot_text)

    @commands.command()
    async def random_number(self, ext):
        await ext.send(f'{random.randrange(0, 100)}')

    @commands.command()
    async def random_password(self, ext, long_password=8):
        letters = 'qwertyuiopasdfghjklzxcvbnm'
        upper_letters = 'QWERTYUIOPASDFGHJKLZXCVBNM'
        numbers = '1234567890'
        characters = '!@#$%^&*()+=<>?/'
        all_symbols = letters + numbers + upper_letters + characters
        password = ''
        
        for i in range(long_password):
            password += random.choice(list(all_symbols))
            
        await ext.author.send(password)
    

def setup(bot):
    bot.add_cog(Random_Text(bot))
    bot.add_cog(Random_Images(bot))



    
