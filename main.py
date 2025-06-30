import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, add_user
from generator import Generator

# setting up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class SwearBot:
    def __init__(self):
        # initializing bot with html markup by default
        self.bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        self.generator = Generator()
        
        # registering handlers with new syntax
        self.dp.message.register(self.cmd_start, Command(commands=['start']))
        self.dp.message.register(self.cmd_help, Command(commands=['help']))
        self.dp.message.register(self.cmd_generate, Command(commands=['generate']))
        self.dp.message.register(self.cmd_stats, Command(commands=['stats']))
        self.dp.message.register(self.cmd_last, Command(commands=['last']))
        self.dp.message.register(self.cmd_admin, Command(commands=['admin']))
        self.dp.message.register(self.handle_any_message)

    async def on_startup(self):
        """initialization on startup"""
        await init_db()
        logger.info("bot is up and running smooth")
        
        # checking if we got admins in the list
        if ADMIN_IDS and len(ADMIN_IDS) > 0:
            try:
                await self.bot.send_message(ADMIN_IDS[0], "yo bot is live and ready to talk shit!")
                logger.info(f"notification sent to admin: {ADMIN_IDS[0]}")
            except Exception as e:
                logger.error(f"couldn't hit up the admin: {e}")
        else:
            logger.warning("admin list empty, nobody to notify")

    async def cmd_start(self, message: types.Message):
        """handling /start command"""
        user = message.from_user
        await add_user(user.id, user.username, user.first_name)
        
        welcome_text = (
            "<b>yo yo welcome to the FUCK1NG SW3AR G3N3R@T0R, homie =)</b>\n\n"
            "here's what you can do:\n"
            "/generate - get some fire insults\n"
            "/stats - check your numbers\n"
            "/last - see your recent burns\n"
            "/help - get the full rundown"
        )
        await message.answer(welcome_text)
        logger.info(f"new homie joined: {user.id}")

    async def cmd_help(self, message: types.Message):
        """bot help info"""
        help_text = (
            "<b>yo here's what's good:</b>\n"
            "/generate - drop some heat on fools\n"
            "/stats - see how much you been talking\n"
            "/last - check your last 5 roasts\n\n"
            "hold up: max 10 burns per minute, don't spam"
        )
        await message.answer(help_text)

    async def cmd_generate(self, message: types.Message):
        """generating swear phrases"""
        user = message.from_user
        phrase, success = await self.generator.generate_phrase(user.id)
        
        if success:
            response = f"<b>yo here's your fucking roast:</b>\n{phrase}"
            logger.info(f"dropped fire for {user.id}")
        else:
            response = "chill out homie! you hitting this too hard, wait a minute."
            logger.warning(f"this fool {user.id} going too fast")
        
        await message.answer(response)

    async def cmd_stats(self, message: types.Message):
        """getting user stats"""
        stats = await self.generator.get_stats(message.from_user.id)
        await message.answer(stats)

    async def cmd_last(self, message: types.Message):
        """getting last phrases"""
        phrases = await self.generator.get_last_phrases(message.from_user.id)
        if not phrases:
            await message.answer("yo you ain't said nothing yet!")
            return
        
        text = "📝 <b>your recent burns:</b>\n" + "\n".join(
            f"{i+1}. {phrase[0]}" for i, phrase in enumerate(phrases)
        )
        await message.answer(text[:4000])

    async def cmd_admin(self, message: types.Message):
        """admin commands"""
        if not ADMIN_IDS or message.from_user.id not in ADMIN_IDS:
            await message.answer("nah fam, you ain't got the juice for this!")
            return
        
        await message.answer("🛠 boss mode activated:\n/stats_all - check all the homies stats")

    async def handle_any_message(self, message: types.Message):
        """handling any messages"""
        text = message.text.lower()
        if text in ("yo", "what's good", "sup", "hello", "hi"):
            await message.answer("yo what's good homie...")
        elif text in ("peace", "later", "bye", "see ya"):
            await message.answer("aight catch you later!")
        elif text in ("fuck", "shit", "damn"):
            await message.answer("yo watch that mouth... or not, i don't give a damn")
        else:
            await message.answer("yo i don't understand that. hit me with /help")

    async def run(self):
        """running the bot"""
        await self.on_startup()
        try:
            await self.dp.start_polling(self.bot)
        finally:
            await self.bot.close()

if __name__ == "__main__":
    bot = SwearBot()
    asyncio.run(bot.run())