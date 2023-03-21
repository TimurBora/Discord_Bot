import disnake
from disnake.ext import commands

class PingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def ping(self, ext: disnake.ApplicationCommandInteraction):
        await ext.response.send_message(f'Pong! {round(self.bot.latency * 1000)}мс')

def setup(bot):
    bot.add_cog(PingCommand(bot))
