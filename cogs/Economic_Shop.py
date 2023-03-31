import disnake
import aiosqlite
import asyncio
from disnake.ext import commands
from SQL_EconomicCommands import SQL_Economic, SQL_EconomicShop

class Economic_Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SQL_Economic = SQL_Economic()
        self.SQL_Shop = SQL_EconomicShop()

    @commands.slash_command(default_member_permissions=disnake.Permissions(administrator=True, manage_roles=True))
    async def add_role_from_shop(self, ext, role: disnake.Role, price : int, *, description : str):
        if price < 0:
            await ext.send('Vi ne mozete postaviti cenu manju od nule!')
            
        elif role in ext.author.guild.roles and not role.id in await self.SQL_Shop.select_all_roles_id(ext.author.guild.id):
            await self.SQL_Shop.add_role_in_shop(role.id, price, description, ext.guild.id)
            await ext.send(f"Vi ste dodali {role.name} u shop!")

        elif role.id in await self.SQL_Shop.select_all_roles_id(ext.author.guild.id):
            await ext.send("Takav rol je vec u prodavnici!")
            
        else:
            await ext.send('Takav role ne postoji!')
        
    @commands.slash_command(default_member_permissions=disnake.Permissions(administrator=True, manage_roles=True))
    async def remove_role_from_shop(self, ext, role: disnake.Role, reason=''):
        if role.id in await self.SQL_Shop.select_all_roles_id(ext.author.guild.id):
            await self.SQL_Shop.remove_role_from_shop(role.id, ext.author.guild.id)

            if reason == '':
                await ext.send("Vi ste izbrisali role iz prodavnice!")
                
            else:
                await ext.send(f"Vi ste izbrisali role zbog {reason}")
                
        else:
            await ext.send("Taj role nije u prodavnici!")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role : disnake.Role):
        await self.SQL_Shop.cursor.execute('SELECT role_id FROM shop_roles WHERE guild_id = ?', (role.guild.id,))
        shop_inventory = list(await self.SQL_Shop.cursor.fetchall())
        shop_inventory = [element[0] for element in shop_inventory]

        if role.id in shop_inventory:
            await self.SQL_Shop.remove_role_from_shop(role.id, role.guild.id)
        
    @commands.command()
    async def shop_menu(self, ext):
        await self.SQL_Shop.cursor.execute('SELECT * FROM shop_roles WHERE guild_id = ?', (ext.guild.id,))
        shop_inventory = await self.SQL_Shop.cursor.fetchall()

        shop_menu = ''

        for shop_element in shop_inventory: #ID_role, price, description
            role_name = ext.guild.get_role(shop_element[0]).name
            shop_menu += 'Ime: {}- {}$ \n Opis: {}\n'.format(role_name, shop_element[1], shop_element[2])

        if shop_menu == '':
            await ext.send('Nema nicega u prodavnici!')
            
        else:
            await ext.send(shop_menu)

    @commands.command()
    async def shop_buy(self, ext, *, role):
        await self.SQL_Economic.check_member(ext.author.guild.id, ext.author.id)
        guild = ext.guild

        shop_role = [guild_role for guild_role in guild.roles if role.upper() == guild_role.name.upper()]
        if shop_role != []:
            shop_role = shop_role[0] #Из List берём объект'
        
            author_cash = await self.SQL_Economic.check_cash(ext.author.guild.id, ext.author.id)
            role_price = await self.SQL_Shop.check_role_price(shop_role.id, ext.author.guild.id)

        member_roles = ext.author.roles
        if shop_role == []:
            await ext.send('Takav role ne postoji!')
                
        elif shop_role in member_roles:
            await ext.send("VI vec imate ovaj role!")

        elif author_cash < role_price:
            await ext.send("Vi nemate dosta para!")

        else:
            await self.SQL_Economic.cursor.execute('UPDATE economic_members SET cash = cash - ? WHERE member_guild = ? AND member_id = ?',
                                                   (role_price, ext.author.guild.id, ext.author.id))
            await self.SQL_Economic.sqlite_connection.commit()
                
            await ext.author.add_roles(shop_role, atomic=True)
            await ext.send(f"Vi ste kupili {shop_role.name}!")

        


def setup(bot):
    bot.add_cog(Economic_Shop(bot))










    
    
