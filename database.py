import aiosqlite
import asyncio
from config import DATABASE_PATH

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                generation_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # table for generated phrases
        await db.execute('''
            CREATE TABLE IF NOT EXISTS phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                phrase_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        await db.commit()
        print("✅ yo database is ready for business")

async def add_user(telegram_id, username=None, first_name=None):
    """adding new homie to the crew"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            await db.execute('''
                INSERT OR IGNORE INTO users (telegram_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (telegram_id, username, first_name))
            await db.commit()
            print(f"✅ new homie {telegram_id} joined the crew")
        except Exception as e:
            print(f"❌ damn, couldn't add this fool: {e}")

async def update_generation_count(telegram_id):
    """keeping track of how many times this cat talked shit"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            await db.execute('''
                UPDATE users 
                SET generation_count = generation_count + 1 
                WHERE telegram_id = ?
            ''', (telegram_id,))
            await db.commit()
        except Exception as e:
            print(f"❌ couldn't update the count, shit's broken: {e}")

async def save_phrase(telegram_id, phrase_text):
    """saving that fire phrase this homie just dropped"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            # getting the user's id
            cursor = await db.execute(
                'SELECT id FROM users WHERE telegram_id = ?', (telegram_id,)
            )
            user = await cursor.fetchone()
            
            if user:
                await db.execute('''
                    INSERT INTO phrases (user_id, phrase_text)
                    VALUES (?, ?)
                ''', (user[0], phrase_text))
                await db.commit()
        except Exception as e:
            print(f"❌ couldn't save that phrase, database acting up: {e}")

async def get_user_stats(telegram_id):
    """checking how much this cat been talking"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            cursor = await db.execute('''
                SELECT generation_count, created_at 
                FROM users 
                WHERE telegram_id = ?
            ''', (telegram_id,))
            return await cursor.fetchone()
        except Exception as e:
            print(f"❌ can't get stats for this fool: {e}")
            return None

async def get_last_phrases(telegram_id, limit=5):
    """getting the last few things this homie said"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        try:
            cursor = await db.execute('''
                SELECT p.phrase_text, p.created_at
                FROM phrases p
                JOIN users u ON p.user_id = u.id
                WHERE u.telegram_id = ?
                ORDER BY p.created_at DESC
                LIMIT ?
            ''', (telegram_id, limit))
            return await cursor.fetchall()
        except Exception as e:
            print(f"❌ can't get the last phrases, database trippin': {e}")
            return []

# testing the database
async def test_database():
    """testing if this shit actually works"""
    print("🧪 testing the database like we in the lab...")
    
    # initialization
    await init_db()
    
    # adding test homie
    test_user_id = 123456789
    await add_user(test_user_id, "test_og", "test homie")
    
    # testing generation
    await update_generation_count(test_user_id)
    await save_phrase(test_user_id, "yo this a test phrase from the hood")
    
    # getting stats
    stats = await get_user_stats(test_user_id)
    if stats:
        print(f"📊 this homie's stats: {stats}")
    
    # getting last phrases
    phrases = await get_last_phrases(test_user_id)
    if phrases:
        print(f"📝 last things this cat said: {phrases}")
    
    print("✅ testing done, everything working smooth")

# running the test if this file gets called directly
if __name__ == "__main__":
    asyncio.run(test_database())