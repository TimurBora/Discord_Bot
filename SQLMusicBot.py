import aiosqlite
import asyncio
import time
import atexit


class SQLMusic:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.async_init())

    async def async_init(self):
        self.sqlite_connection = await aiosqlite.connect('MusicSQL.db')
        self.cursor = await self.sqlite_connection.cursor()
        await self.create_table()
        

    async def create_table(self):
        create_table_query = '''CREATE TABLE IF NOT EXISTS music_menu(
                                guild_id INTEGER,
                                webpage_url TEXT,
                                music_name TEXT,
                                date_added TEXT DEFAULT (CURRENT_TIMESTAMP),
                                UNIQUE (guild_id, webpage_url));'''
        await self.cursor.execute(create_table_query)
        await self.sqlite_connection.commit()

    @atexit.register
    async def shutdown_delete(self):
        shutdown_delete_query = '''DELETE FROM music_menu'''

        await self.cursor.execute(create_table_query)
        await self.sqlite_connection.commit()

    async def delete_all_row(self, guild_id):
        delete_rows_query = '''DELETE FROM music_menu WHERE guild_id = ?'''

        await self.cursor.execute(delete_rows_query, (guild_id,))
        await self.sqlite_connection.commit()

    async def delete_row(self, guild_id, url):
        delete_row_query = '''DELETE FROM music_menu WHERE guild_id = ? AND webpage_url = ?'''

        await self.cursor.execute(delete_row_query, (guild_id, url))
        await self.sqlite_connection.commit()

    async def add_music(self, guild_id, webpage_url, music_name):
        create_insert_query = '''INSERT INTO music_menu VALUES(?, ?, ?, CURRENT_TIMESTAMP)'''
        
        await self.cursor.execute(create_insert_query, (guild_id, webpage_url, music_name))
        await self.sqlite_connection.commit()

    async def select_all_music(self, guild_id):
        create_select_query = '''SELECT * FROM music_menu WHERE guild_id = ? ORDER BY date_added'''

        await self.cursor.execute(create_select_query, (guild_id,))
        return (await self.cursor.fetchall())

    async def select_music_url(self, guild_id):
        create_select_query = '''SELECT webpage_url FROM music_menu WHERE guild_id = ? ORDER BY date_added'''

        await self.cursor.execute(create_select_query, (guild_id,))
        return (await self.cursor.fetchone())[0]















            
        
        
