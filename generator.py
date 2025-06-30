import random
import asyncio
import time
import os
from pathlib import Path
from database import save_phrase, update_generation_count, get_user_stats, get_last_phrases
from config import MAX_GENERATION_PER_MINUTE
from typing import Tuple

# Базовый набор слов на случай отсутствия файла
DEFAULT_WORDS = [
    "asshole", "dumbass", "dickhead", "moron", "jackass",
    "idiot", "douchebag", "prick", "jerk", "loser",
    "cretin", "bastard", "dipshit", "numbskull", "twat",
    "cwel", "shithead", "bonehead", "fuckface", "motherfucker",
    "turd", "scumbag", "bullshit"
]

# Дополнительные шаблоны для генерации
TEMPLATES = [
    "you're such a {0} — total {1}, yo",
    "this {0} is just a damn {1}, fuck....",
    "a fucking real {0} on the shitty level of '{1}'",
    "when I see this — reminds me of a {0} and {1}",
    "100% {0} with a touch of {1}",
    "what a fucking {0}, just like a {1}",
    "complete {0} behaving like a {1}",
    "this {0} is worse than a {1}",
    "ay yo this {0} acting like a straight {1}",
    "bruh you deadass a {0} mixed with {1}",
    "homie really out here being a {0} and {1}",
    "nah fam this {0} got that {1} energy",
    "straight up {0} vibes with a dash of {1}",
    "this fool really a {0} pretending to be {1}",
    "mans is a certified {0} with {1} tendencies",
    "sheesh this {0} more annoying than a {1}",
    "bro really said lemme be a {0} today like a {1}",
    "this {0} built different... like a {1}",
    "homie got that {0} aura but acts like {1}",
    "certified {0} moment with extra {1}",
    "this {0} really thought they ate but they just a {1}",
    "nah this {0} is giving major {1} vibes",
    "ay this {0} really serving {1} realness",
    "periodt this {0} is nothing but a {1}",
    "this {0} really said hold my beer and became a {1}",
    "coño this {0} acting like a pendejo {1}",
    "ese {0} es un pinche {1}, hermano",
    "que {0} tan {1}, no mames",
    "this {0} straight outta the barrio like a {1}",
    "ay dios mio what a {0} mixed with {1}",
    "this {0} got that cuba libre {1} energy",
    "mi hermano this {0} is puro {1}",
    "este {0} está más loco que un {1}",
    "this {0} got more problems than a {1}",
    "órale this {0} acting like a straight {1}",
    "damn this {0} wilder than a {1} in miami",
    "this {0} got that calle {1} mentality",
    "straight up ghetto {0} with barrio {1} vibes",
    "this {0} from the hood acting like a {1}",
    "yo this {0} straight trash like a {1}",
    "this {0} ain't it chief, pure {1}",
    "deadass this {0} be acting like a {1}",
    "this {0} really hitting different like a {1}",
    "nah b this {0} is straight {1}",
    "this {0} really said lemme be toxic like a {1}",
    "yo this {0} got that energy of a {1}",
    "this {0} really wildin like a {1}",
    "facts this {0} is mid tier {1}",
    "this {0} really dogwater like a {1}",
    "yo this {0} got no skill just pure {1}",
    "this noob {0} playing like a {1}",
    "gg this {0} just griefed like a {1}",
    "this {0} really feeding like a {1}",
    "bruh this {0} straight inting like a {1}",
    "this {0} got that bronze {1} gameplay",
    "yo this {0} camping like a {1}",
    "this {0} really smurfing on {1} level",
    "damn this {0} more toxic than a {1}",
    "this {0} straight up hardstuck like a {1}",
    "yo this {0} trolling harder than a {1}",
    "this {0} got that {1} mentality in ranked",
    "nah this {0} playing like a {1} in casual",
    "this {0} really throwing like a {1}",
    "damn this {0} got worse aim than a {1}",
    "yo this {0} camping harder than a {1}",
    "this {0} really sweating like a {1}",
    "nah this {0} more cringe than a {1}",
    "this {0} got that school shooter {1} energy",
    "yo this {0} acting like a hall monitor {1}",
    "this {0} really being a teacher's pet {1}",
    "damn this {0} got that detention {1} vibe",
    "this {0} straight up cafeteria {1} behavior",
    "yo this {0} acting like a substitute {1}",
    "this {0} got that summer school {1} energy",
    "nah this {0} really being a {1} in gym class",
    "this {0} acting like a prom king {1}",
    "yo this {0} got that freshman {1} mentality",
    "this {0} straight up senior {1} arrogance",
    "damn this {0} more annoying than a {1} in chemistry",
    "this {0} really showing off like a {1} in math",
    "yo this {0} got that band kid {1} energy",
    "this {0} acting like a chess club {1}",
    "hooah this {0} acting like a {1} in basic",
    "this {0} got that drill sergeant {1} attitude",
    "yo this {0} straight up boot camp {1}",
    "damn this {0} more confused than a {1} on leave",
    "this {0} got that barracks {1} energy",
    "nah this {0} acting like a {1} in formation",
    "this {0} straight up mess hall {1} behavior",
    "yo this {0} got that deployment {1} mentality",
    "this {0} acting like a {1} with weekend pass",
    "damn this {0} more lost than a {1} in the field",
    "this {0} got that latrine {1} attitude",
    "yo this {0} straight up supply {1} energy",
    "this {0} acting like a {1} before inspection",
    "nah this {0} got that motor pool {1} vibe",
    "this {0} straight up chow hall {1} behavior",
    "yo this {0} acting like a cell block {1}",
    "this {0} got that yard {1} mentality",
    "damn this {0} straight up commissary {1}",
    "nah this {0} acting like a {1} in solitary",
    "this {0} got that shiv {1} energy",
    "yo this {0} straight up snitch {1} behavior",
    "this {0} acting like a {1} on parole",
    "damn this {0} got that contraband {1} vibe",
    "this {0} straight up lockdown {1} attitude",
    "yo this {0} acting like a {1} in gen pop",
    "this {0} got that prison wallet {1} energy",
    "nah this {0} straight up fish {1} behavior",
    "this {0} acting like a {1} with life sentence",
    "damn this {0} got that shower {1} mentality",
    "this {0} straight up rec time {1} attitude",
    "yo this {0} got that {1} energy no cap",
    "periodt this {0} is serving {1} realness hunty",
    "this {0} really said periodt and became a {1}",
    "bestie this {0} is giving {1} vibes and i'm here for it",
    "not this {0} really being a {1} in 2024",
    "this {0} ate and left no crumbs... of {1}",
    "the way this {0} is giving {1} energy",
    "bestie this {0} really thought they did something but they just a {1}",
    "not me watching this {0} act like a whole {1}",
    "this {0} really said let me serve {1} today"
]

class Generator:
    def __init__(self):
        self.user_cooldowns = {}  # {user_id: (timestamp, count)}
        self.words = self._load_words()

    def _load_words(self):
        """load words from file with error handling"""
        try:
            # try to find file in several functions
            possible_paths = [
                'words.txt',
                os.path.join(Path(__file__).parent, 'words.txt'),
                os.path.join(Path(__file__).parent.parent, 'words.txt')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        words = [line.strip() for line in f if line.strip()]
                        if words:  # if file is not empty
                            print(f"loaded {len(words)} words from {path}")
                            return words
            
            # if file not found or empty
            print("words.txt file not found or empty. using default word set")
            return DEFAULT_WORDS
            
        except Exception as e:
            print(f"fucking error: {e}. using default set")
            return DEFAULT_WORDS

    async def check_limit(self, user_id: int) -> bool:
        """check generation limit"""
        current_time = int(time.time())
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = (current_time, 1)
            return True
        
        last_time, count = self.user_cooldowns[user_id]
        if current_time - last_time >= 60:  # Сброс счетчика
            self.user_cooldowns[user_id] = (current_time, 1)
            return True
        
        if count >= MAX_GENERATION_PER_MINUTE:
            return False
        
        self.user_cooldowns[user_id] = (last_time, count + 1)
        return True

    async def generate_phrase(self, user_id: int) -> Tuple[str, bool]:
        """generate phrase with limit check"""
        if not await self.check_limit(user_id):
            return ("sorry bro, fucking generation limit reached. wait a minute plz", False)

        # check that we have at least two words
        if len(self.words) < 2:
            return ("N0T EN0UGH FUCK1NG W0RDZ F0R G3N3R@T10N", False)

        # choose random template and words
        template = random.choice(TEMPLATES)
        word1, word2 = random.sample(self.words, 2)
        
        phrase = template.format(word1, word2)

        # save to database (if functions are available)
        try:
            await asyncio.gather(
                update_generation_count(user_id),
                save_phrase(user_id, phrase)
            )
        except Exception as e:
            print(f"⚠️ error saving phrase, homie: {e}")

        return (phrase, True)

    async def get_stats(self, user_id: int) -> str:
        """get user statistics"""
        try:
            stats = await get_user_stats(user_id)
            if not stats:
                return "❌ statistics not found"
            
            count, created_at = stats
            return (
                f"📊 your statistics:\n"
                f"• total generation: {count}\n"
                f"• registration date: {created_at[:10]}"
            )
        except Exception as e:
            print(f"error getting statistics: {e}")
            return "error loading statistics"

    async def get_last_phrases(self, user_id: int, limit: int = 5) -> list:
        """get users last phrases"""
        try:
            return await get_last_phrases(user_id, limit)
        except Exception as e:
            print(f"error getting last phrases: {e}")
            return []