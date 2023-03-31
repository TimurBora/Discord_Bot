import disnake
from disnake.ext import commands

intents = disnake.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
        
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1083720706895908945)
    await channel.send(f"Cao {member.mention}, kako si?")

@bot.event
async def on_voice_state_update(ext, before, after):
    text_channel = bot.get_channel(1083720706895908946)
    if after.channel != None:
        await text_channel.send(f"{ext.mention} usao u kanal: {ext.voice.channel.name}")
    else:
        await text_channel.send(f"{ext.mention} izasao je iz kanala")

@bot.event
async def on_command_error(ext, error):
    await ext.send(error)
    
    

bot.load_extensions("cogs")
bot.run("MTA4MzcyMTAwNDkyNjM4MjA5MA.GKzblP.V7gHuUx4V6o32lNymFxkrfD_5rOjN1BYF4IqiE")
