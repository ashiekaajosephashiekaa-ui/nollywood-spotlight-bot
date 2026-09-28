import aiosqlite
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TEXT,
                last_active TEXT,
                referrer_id INTEGER
            )
        ''')
        await db.commit()

async def add_user(user_id, username, first_name, referrer_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at, last_active, referrer_id)
            VALUES (?, ?, ?, datetime('now'), datetime('now'), ?)
        ''', (user_id, username, first_name, referrer_id))
        await db.execute('''
            UPDATE users SET last_active = datetime('now') WHERE user_id = ?
        ''', (user_id,))
        await db.commit()

async def get_total_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT COUNT(*) FROM users') as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def get_referral_count(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT COUNT(*) FROM users WHERE referrer_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
