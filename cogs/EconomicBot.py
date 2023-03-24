import disnake
import random
import sqlite3
import time
from disnake.ext import commands

class SQL_Economic:
    def __init__(self):
        self.sqlite_connection = sqlite3.connect('Economic_Bot.db')
        self.cursor = self.sqlite_connection.cursor()
        self.create_table()
        
    def create_table(self):
        create_table_query = '''CREATE TABLE IF NOT EXISTS economic_members(
                                member_id INTEGER PRIMARY KEY,
                                cash INTEGER,
                                bank INTEGER,
                                work_time INTEGER,
                                crime_time INTEGER);'''
        self.cursor.execute(create_table_query)
        self.sqlite_connection.commit()

    async def registration(self, member_id):
        create_query_registration = '''INSERT INTO economic_members VALUES(?, ?, ?,
                                       strftime('%s', 'now', '-59 minutes'), strftime('%s', 'now', '-59 minutes'));'''
        self.cursor.execute(create_query_registration, (member_id, 0, 0))
        self.sqlite_connection.commit()

    async def check_member(self, member_id):
        self.cursor.execute("SELECT member_id FROM economic_members WHERE member_id = ?", (member_id,))
        if self.cursor.fetchone() is None:
            await self.registration(member_id)

    async def check_cash(self, member_id):
        create_query_check = '''SELECT cash FROM economic_members WHERE member_id = ?'''
        cash = self.cursor.execute(create_query_check, (member_id,))
        return cash.fetchone()[0]

    async def check_bank(self, member_id):
        create_query_check = '''SELECT bank FROM economic_members WHERE member_id = ?'''
        bank = self.cursor.execute(create_query_check, (member_id,))
        return bank.fetchone()[0]

    async def check_timer(self, member_id, check_from):
        create_query_check_timer = f'''SELECT {check_from} FROM economic_members WHERE member_id = ?'''
        last_timer = self.cursor.execute(create_query_check_timer, (member_id,)).fetchone()[0]

        now_timer = int(time.time())

        if now_timer - last_timer > 1800:
            return True
        else:
            return False

    async def timer_change(self, member_id, change_where):
        create_change_time_query = f'''UPDATE economic_members SET {change_where} = strftime("%s", "now") WHERE member_id = ?'''
        self.cursor.execute(create_change_time_query, (member_id,))
        self.sqlite_connection.commit()

        
        

class MoneyEarn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SQL = SQL_Economic()

    @commands.command()
    async def work(self, ext):
        await self.SQL.check_member(ext.author.id)
        if await self.SQL.check_timer(ext.author.id, 'work_time'):
            random_money = random.randint(500, 1000)
            update_cash = 'UPDATE economic_members SET cash = cash + ? WHERE member_id = ?;'
        
            self.SQL.cursor.execute(update_cash, (random_money, ext.author.id))
            self.SQL.sqlite_connection.commit()
        
            await ext.send(f"You work, and get {random_money}$")

            await self.SQL.timer_change(ext.author.id, 'work_time')

        else:
            await ext.send("Proslo je previse malo vremena od proslog puta!")

    @commands.command()
    async def crime(self, ext):
        await self.SQL.check_member(ext.author.id)
        if await self.SQL.check_timer(ext.author.id, 'crime_time'):
            random_money = random.randint(-4000, 4000)
            update_cash = 'UPDATE economic_members SET cash = cash + ? WHERE member_id = ?;'
        
            self.SQL.cursor.execute(update_cash, (random_money, ext.author.id))
            self.SQL.sqlite_connection.commit()
        
            await ext.send(f"You crime, and get {random_money}$")

            await self.SQL.timer_change(ext.author.id, 'crime_time')

        else:
            await ext.send("Proslo je previse malo vremena od proslog puta!")

    @commands.command()
    async def rob(self, ext, member: disnake.Member):
        await self.SQL.check_member(ext.author.id)
        
        random_money = random.randint(-(await self.SQL.check_cash(member.id)) // 1.25, await self.SQL.check_cash(member.id))

        if member.id == ext.author.id:
            await ext.send("Vi ne mozete da ukradete od samog sebe!")
            
        elif random_money > 0:
            update_cash_member = f'''UPDATE economic_members SET cash = cash - {random_money} WHERE member_id = ?'''
            self.SQL.cursor.execute(update_cash_member, (member.id,))
            self.SQL.sqlite_connection.commit()

            update_cash_robber = f'''UPDATE economic_members SET cash = cash + {random_money} WHERE member_id = ?'''
            self.SQL.cursor.execute(update_cash_robber, (ext.author.id,))
            self.SQL.sqlite_connection.commit()

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
        await self.SQL.check_member(member.id)
        
        cash = await self.SQL.check_cash(member.id)
        bank = await self.SQL.check_bank(member.id)
        
        await ext.send(f"{member.name}#{member.discriminator} Have {cash}$ in cash and {bank}$ in bank")

    @commands.command()
    async def give_money(self, ext, member:disnake.Member, quantity : int):
        await self.SQL.check_member(member.id)
        
        cash_quantity = await self.SQL.check_cash(ext.author.id)

        if member.id == ext.author.id:
            await ext.send("Vi ne mozete poslati samom sebi pare!")
        
        elif quantity <= 0 or quantity > cash_quantity:
            await ext.send("Vi ne mozete poslati toliko para!")
            
        else:
            update_cash_sender = 'UPDATE economic_members SET cash = cash - ? WHERE member_id = ?;'
            update_cash_recipient = 'UPDATE economic_members SET cash = cash + ? WHERE member_id = ?;'
            
            self.SQL.cursor.execute(update_cash_sender, (quantity, ext.author.id))
            self.SQL.sqlite_connection.commit()
            
            self.SQL.cursor.execute(update_cash_recipient, (quantity, member.id))
            self.SQL.sqlite_connection.commit()
            
            await ext.send(f"Vi ste poslali {quantity}$ coveku {member.name}#{member.discriminator}")

    @commands.command(name="deposit")
    async def cash_to_bank(self, ext, quantity=None):
        await self.SQL.check_member(ext.author.id)

        if quantity is None:
            quantity = await self.SQL.check_cash(ext.author.id)

        if quantity > await self.SQL.check_cash(ext.author.id) or quantity <= 0:
            await ext.send("Vi ne mozete toliko da depozivate!")

        else:
            create_deposit_query = '''UPDATE economic_members SET bank = bank + ? WHERE member_id = ?'''
            create_cashminus_query = '''UPDATE economic_members SET cash = cash - ? WHERE member_id = ?'''

            self.SQL.cursor.execute(create_deposit_query, (quantity, ext.author.id))
            self.SQL.sqlite_connection.commit()

            self.SQL.cursor.execute(create_cashminus_query, (quantity, ext.author.id))
            self.SQL.sqlite_connection.commit()

            await ext.send(f"Vi ste depozitovali {quantity}$")

    @commands.command()
    async def bank_to_cash(self, ext, quantity=None):
        await self.SQL.check_member(ext.author.id)

        if quantity is None:
            quantity = await self.SQL.check_bank(ext.author.id)

        if quantity > await self.SQL.check_bank(ext.author.id) or quantity <= 0:
            await ext.send("Vi ne mozete toliko da depozivate!")

        else:
            create_bankcash_query = '''UPDATE economic_members SET bank = bank - ? WHERE member_id = ?'''
            create_bankminus_query = '''UPDATE economic_members SET cash = cash + ? WHERE member_id = ?'''

            self.SQL.cursor.execute(create_bankcash_query, (quantity, ext.author.id))
            self.SQL.sqlite_connection.commit()

            self.SQL.cursor.execute(create_bankminus_query, (quantity, ext.author.id))
            self.SQL.sqlite_connection.commit()

            await ext.send(f"Vi ste uzeli {quantity}$ iz banke")
    
        
def setup(bot):
    bot.add_cog(MoneyEarn(bot))
    bot.add_cog(MoneyWork(bot))

    
