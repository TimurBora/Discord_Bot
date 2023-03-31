import aiosqlite
import asyncio
import time

class SQL_Economic:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.async_init())

    async def async_init(self):
        self.sqlite_connection = await aiosqlite.connect('Economic_Bot.db')
        self.cursor = await self.sqlite_connection.cursor()
        await self.create_table()
        
    async def create_table(self):
        create_table_query = '''CREATE TABLE IF NOT EXISTS economic_members(
                                guild_id INTEGER,
                                member_id INTEGER,
                                cash INTEGER,
                                bank INTEGER,
                                work_time INTEGER,
                                crime_time INTEGER);'''
        await self.cursor.execute(create_table_query)
        await self.sqlite_connection.commit()

    async def registration(self, member_guild, member_id):
        create_query_registration = '''INSERT INTO economic_members VALUES(?, ?, ?, ?,
                                       strftime('%s', 'now', '-59 minutes'), strftime('%s', 'now', '-59 minutes'));'''
        await self.cursor.execute(create_query_registration, (member_guild, member_id, 0, 0))
        await self.sqlite_connection.commit()

    async def check_member(self, member_guild, member_id):
        await self.cursor.execute("SELECT member_id FROM economic_members WHERE member_guild = ? AND member_id = ?", (member_guild, member_id))
        if await self.cursor.fetchone() is None:
            await self.registration(member_guild, member_id)

    async def check_cash(self, member_guild, member_id):
        create_query_check = '''SELECT cash FROM economic_members WHERE member_guild = ? AND member_id = ?'''
        cash = await self.cursor.execute(create_query_check, (member_guild, member_id))
        return (await cash.fetchone())[0]

    async def check_bank(self, member_guild, member_id):
        create_query_check = '''SELECT bank FROM economic_members WHERE member_guild = ? AND member_id = ?'''
        bank = await self.cursor.execute(create_query_check, (member_guild, member_id))
        return (await bank.fetchone())[0]

    async def check_timer(self, member_guild, member_id, check_from):
        create_query_check_timer = f'''SELECT {check_from} FROM economic_members WHERE member_guild = ? AND member_id = ?'''

        await self.cursor.execute(create_query_check_timer, (member_guild, member_id))
        last_timer = (await self.cursor.fetchone())[0]

        now_timer = int(time.time())

        if now_timer - last_timer > 1800:
            return True
        else:
            return False

    async def timer_change(self, member_guild, member_id, change_where):
        create_change_time_query = f'''UPDATE economic_members SET {change_where} = strftime("%s", "now") WHERE member_guild = ? AND member_id = ?'''
        await self.cursor.execute(create_change_time_query, (member_guild, member_id))
        await self.sqlite_connection.commit()

class SQL_EconomicShop:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.async_init())

    async def async_init(self):
        self.sqlite_connection = await aiosqlite.connect('Shop.db')
        self.cursor = await self.sqlite_connection.cursor()
        await self.create_table()

    async def create_table(self):
        create_table_query = '''CREATE TABLE IF NOT EXISTS shop_roles(
                                role_id INTEGER PRIMARY KEY,
                                quild_id INTEGER,
                                price INTEGER,
                                description TEXT);'''
        await self.cursor.execute(create_table_query)
        await self.sqlite_connection.commit()

    async def add_role_in_shop(self, role_id, guild_id, price, description=None):
        create_add_role_query = '''INSERT INTO shop_roles VALUES (?, ?, ?, ?)'''

        await self.cursor.execute(create_add_role_query, (role_id, guild_id, price, description))
        await self.sqlite_connection.commit()

    async def remove_role_from_shop(self, role_id, guild_id):
        create_remove_role_query = '''DELETE FROM shop_roles WHERE guild_id = ? AND role_id = ?'''

        await self.cursor.execute(create_remove_role_query, (guild_id, role_id))
        await self.sqlite_connection.commit()


    async def check_role_price(self, role_id, guild_id):
        create_check_roleprice_query = '''SELECT price FROM shop_roles WHERE guild_id = ? AND role_id = ?'''

        await self.cursor.execute(create_check_roleprice_query, (guild_id, role_id))
        return (await self.cursor.fetchone())[0]

    async def select_all_roles_id(self, guild_id):
        create_select_query = '''SELECT role_id FROM shop_roles WHERE guild_id = ?'''

        await self.cursor.execute(create_select_query, (guild_id,))
        role_id_tuple = await self.cursor.fetchall()
        
        role_id_list = [element[0] for element in role_id_tuple]
        return role_id_list
    




    

        
