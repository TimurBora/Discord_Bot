import disnake
from disnake.ext import commands
from disnake.ext.commands import CommandNotFound


intents = disnake.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot_run_file = open("C:\Users\admin\Desktop\Programming projects\Code\Code.txt", "r")
bot_api_code = bot_run_file.read()
        
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1083720706895908945)
    await channel.send(f"Cao {member.mention}, kako si?")

@bot.event
async def on_command_error(ext, error):
    if not isinstance(error, CommandNotFound):
        await ext.send(error)

bot.load_extensions("cogs")
bot.run(bot_api_code)
