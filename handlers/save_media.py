import asyncio
import aiohttp
import string
import random
from configs import Config
from pyrogram import Client
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64

def generate_random_alphanumeric():
    """Generate a random 8-letter alphanumeric string."""
    characters = string.ascii_letters + string.digits
    random_chars = ''.join(random.choice(characters) for _ in range(8))
    return random_chars

async def get_short(url):
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"https://{Config.SHORTLINK_URL}/api?api={Config.SHORTLINK_API}&url={url}&alias={generate_random_alphanumeric()}"
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                rjson = await resp.json()
                if rjson.get("status") == "success" or resp.status == 200:
                    return rjson.get("shortenedUrl", url)
    except Exception:
        pass
    return url

    
async def forward_to_channel(bot: Client, message: Message, editable: Message):
    try:
        __SENT = await message.forward(Config.DB_CHANNEL)
        return __SENT
    except FloodWait as sl:
        if sl.value > 45:
            await asyncio.sleep(sl.value)
            await bot.send_message(
                chat_id=int(Config.LOG_CHANNEL),
                text=f"#FloodWait:\nGot FloodWait of `{str(sl.value)}s` from `{str(editable.chat.id)}` !!",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                    ]
                )
            )
        return await forward_to_channel(bot, message, editable)


