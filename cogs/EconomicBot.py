import disnake
import random
import aiosqlite
import asyncio
from disnake.ext import commands
from SQL_EconomicCommands import SQL_Economic

class MoneyEarn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SQL = SQL_Economic()

    @commands.command()
    async def work(self, ext):
        await self.SQL.check_member(ext.author.guild.id, ext.author.id)
        if await self.SQL.check_timer(ext.author.guild.id, ext.author.id, 'work_time'):
            random_money = random.randint(500, 1000)
            update_cash = 'UPDATE economic_members SET cash = cash + ? WHERE member_guild = ? AND member_id = ?;'
        
            await self.SQL.cursor.execute(update_cash, (random_money, ext.author.guild.id, ext.author.id))
            await self.SQL.sqlite_connection.commit()
        
            await ext.send(f"You work, and get {random_money}$")

            await self.SQL.timer_change(ext.author.guild.id, ext.author.id, 'work_time')

        else:
            await ext.send("Proslo je previse malo vremena od proslog puta!")

    @commands.command()
    async def crime(self, ext):
        await self.SQL.check_member(ext.author.guild.id, ext.author.id)
        if await self.SQL.check_timer(ext.author.guild.id, ext.author.id, 'crime_time'):
            random_money = random.randint(-4000, 4000)
            update_cash = 'UPDATE economic_members SET cash = cash + ? WHERE member_guild = ? AND member_id = ?;'
        
            await self.SQL.cursor.execute(update_cash, (random_money, ext.author.guild.id, ext.author.id))
            await self.SQL.sqlite_connection.commit()
        
            await ext.send(f"You crime, and get {random_money}$")

            await self.SQL.timer_change(ext.author.guild.id, ext.author.id, 'crime_time')

        else:
            await ext.send("Proslo je previse malo vremena od proslog puta!")

    @commands.command()
    async def rob(self, ext, member: disnake.Member):
        await self.SQL.check_member(ext.author.guild.id, ext.author.id)
        await self.SQL.check_member(member.guild.id, member.id)

        random_money = random.randrange(-1000, 1000)

        if member.id == ext.author.id:
            await ext.send("Vi ne mozete da ukradete od samog sebe!")
            
        elif random_money > 0:
            update_cash_member = f'''UPDATE economic_members SET cash = cash - {random_money} WHERE member_guild = ? AND member_id = ?'''
            await self.SQL.cursor.execute(update_cash_member, (member.guild.id, member.id))
            await self.SQL.sqlite_connection.commit()

            update_cash_robber = f'''UPDATE economic_members SET cash = cash + {random_money} WHERE member_guild = ? AND member_id = ?'''
            await self.SQL.cursor.execute(update_cash_robber, (ext.author.guild.id, ext.author.id))
            await self.SQL.sqlite_connection.commit()

            await ext.send(f"Kradjlivac je ukrao {random_money}$ od {member.name}#{member.discriminator}!")

        else:
            await ext.send(f"Kradljivac je pokusao da ukrade, ali je izgubio {random_money}$ para!")
            
        
class MoneyWork(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SQL = SQL_Economic()
        
    @commands.command()
    async def balance(self, ext, member:disnake.Member = None):
        member = member or ext.author
        await self.SQL.check_member(ext.author.guild.id, ext.author.id)
        
        cash = await self.SQL.check_cash(member.guild.id, member.id)
        bank = await self.SQL.check_bank(member.guild.id, member.id)
        
        await ext.send(f"{member.name}#{member.discriminator} Have {cash}$ in cash and {bank}$ in bank")

    @commands.command()
    async def give_money(self, ext, member:disnake.Member, quantity : int):
        await self.SQL.check_member(ext.author.guild.id, ext.author.id)
        
        cash_quantity = await self.SQL.check_cash(ext.author.guild.id, ext.author.id)

        if member.id == ext.author.id:
            await ext.send("Vi ne mozete poslati samom sebi pare!")
        
        elif quantity <= 0 or quantity > cash_quantity:
            await ext.send("Vi ne mozete poslati toliko para!")
            
        else:
            update_cash_sender = 'UPDATE economic_members SET cash = cash - ? WHERE member_guild = ? AND member_id = ?;'
            update_cash_recipient = 'UPDATE economic_members SET cash = cash + ? WHERE member_guild = ? AND member_id = ?;'
            
            await self.SQL.cursor.execute(update_cash_sender, (quantity, ext.author.guild.id, ext.author.id))
            await self.SQL.sqlite_connection.commit()
            
            await self.SQL.cursor.execute(update_cash_recipient, (quantity, member.guild.id, member.id))
            await self.SQL.sqlite_connection.commit()
            
            await ext.send(f"Vi ste poslali {quantity}$ coveku {member.name}#{member.discriminator}")

    @commands.command(name="deposit")
    async def cash_to_bank(self, ext, quantity:int=None):
        await self.SQL.check_member(ext.author.guild.id, ext.author.id)

        if quantity is None:
            quantity = await self.SQL.check_cash(ext.author.guild.id, ext.author.id)

        if quantity > await self.SQL.check_cash(ext.author.guild.id, ext.author.id) or quantity <= 0:
            await ext.send("Vi ne mozete toliko da depozivate!")

        else:
            create_deposit_query = '''UPDATE economic_members SET bank = bank + ? WHERE member_guild = ? AND member_id = ?'''
            create_cashminus_query = '''UPDATE economic_members SET cash = cash - ? WHERE member_guild = ? AND member_id = ?'''

            await self.SQL.cursor.execute(create_deposit_query, (quantity, ext.author.guild.id, ext.author.id))
            await self.SQL.sqlite_connection.commit()

            await self.SQL.cursor.execute(create_cashminus_query, (quantity, ext.author.guild.id, ext.author.id))
            await self.SQL.sqlite_connection.commit()

            await ext.send(f"Vi ste depozitovali {quantity}$")

    @commands.command()
    async def bank_to_cash(self, ext, quantity:int=None):
        await self.SQL.check_member(ext.author.guild.id, ext.author.id)

        if quantity is None:
            quantity = await self.SQL.check_bank(ext.author.guild.id, ext.author.id)

        if quantity > await self.SQL.check_bank(ext.author.guild.id, ext.author.id) or quantity <= 0:
            await ext.send("Vi ne mozete toliko da depozivate!")

        else:
            create_bankcash_query = '''UPDATE economic_members SET bank = bank - ? WHERE member_guild = ? AND member_id = ?'''
            create_bankminus_query = '''UPDATE economic_members SET cash = cash + ? WHERE member_guild = ? AND member_id = ?'''

            await self.SQL.cursor.execute(create_bankcash_query, (quantity, ext.author.guild.id, ext.author.id))
            await self.SQL.sqlite_connection.commit()

            await self.SQL.cursor.execute(create_bankminus_query, (quantity, ext.author.guild.id, ext.author.id))
            await self.SQL.sqlite_connection.commit()

            await ext.send(f"Vi ste uzeli {quantity}$ iz banke")
    
        
def setup(bot):
    bot.add_cog(MoneyEarn(bot))
    bot.add_cog(MoneyWork(bot))

    
