import disnake
import random
import sqlite3
from disnake.ext import commands

class SQL_Economic:
    def __init__(self):
        self.sqlite_connection = sqlite3.connect('Economic_Bot.db')
        self.cursor = self.sqlite_connection.cursor()
        self.create_table()
        
    def create_table(self):
        create_table_query = '''CREATE TABLE IF NOT EXISTS economic_members(
                                member_id INTEGER PRIMARY KEY,
                                cash INTEGER);'''
        self.cursor.execute(create_table_query)
        self.sqlite_connection.commit()

    async def registration(self, member_id):
        create_query_registration = '''INSERT INTO economic_members VALUES(?, ?);'''
        self.cursor.execute(create_query_registration, (member_id, 0))
        self.sqlite_connection.commit()

    async def check_member(self, member_id):
        self.cursor.execute("SELECT member_id FROM economic_members WHERE member_id = ?", (member_id,))
        if self.cursor.fetchone() is None:
            await self.registration(member_id)
        

class Economic_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SQL = SQL_Economic()

    @commands.command()
    async def work(self, ext):
        await self.SQL.check_member(ext.author.id)
        random_money = random.randint(500, 1000)
        update_cash = 'UPDATE economic_members SET cash = cash + ? WHERE member_id = ?;'
        self.SQL.cursor.execute(update_cash, (random_money, ext.author.id))
        self.SQL.sqlite_connection.commit()
        await ext.send(f"You work, and get {random_money}")

    @commands.command()
    async def crime(self, ext):
        await self.SQL.check_member(ext.author.id)
        random_money = random.randint(-4000, 4000)
        update_cash = 'UPDATE economic_members SET cash = cash + ? WHERE member_id = ?;'
        self.SQL.cursor.execute(update_cash, (random_money, ext.author.id))
        self.SQL.sqlite_connection.commit()
        await ext.send(f"You crime, and get {random_money}")

    @commands.command()
    async def bank(self, ext, member:disnake.Member = None):
        member = member or ext.author
        await self.SQL.check_member(member.id)
        create_query_bank = "SELECT cash FROM economic_members WHERE member_id = ?"
        self.SQL.cursor.execute(create_query_bank, (member.id,))
        await ext.send(f"{member.name}#{member.discriminator} Have {self.SQL.cursor.fetchone()[0]}$")

    @commands.command()
    async def give_money(self, ext, member:disnake.Member, quantity : int):
        self.SQL.cursor.execute("SELECT cash FROM economic_members WHERE member_id = ?", (ext.author.id,))
        if quantity <= 0 or quantity > self.SQL.cursor.fetchone()[0]:
            await ext.send("Vi ne mozete poslati toliko para!")
        else:
            update_cash_sender = 'UPDATE economic_members SET cash = cash - ? WHERE member_id = ?;'
            update_cash_recipient = 'UPDATE economic_members SET cash = cash + ? WHERE member_id = ?;'
            self.SQL.cursor.execute(update_cash_sender, (quantity, ext.author.id))
            self.SQL.sqlite_connection.commit()
            self.SQL.cursor.execute(update_cash_recipient, (quantity, member.id))
            self.SQL.sqlite_connection.commit()
            await ext.send(f"Vi ste poslali {quantity}$ coveku {member.name}#{member.discriminator}")
    
        
        

     
        
        

def setup(bot):
    bot.add_cog(Economic_Commands(bot))
