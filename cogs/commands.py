import disnake
from disnake.ext import commands

class MathCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    async def gcd(cls, a, b):
        if b == 0:
            return a
        else:
            return await cls.gcd(b, a % b)

    @commands.command(name="gcd")
    async def result_gcd(self, ext, a : int, b : int):
        result = await MathCommands.gcd(a, b)
        await ext.send(f"The GCD of {a} and {b} is {result}")
            

def setup(bot):
    bot.add_cog(MathCommands(bot))
    
        
        
        
    
