import re
import asyncio
import requests
import string
import random
from configs import Config
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64


def clean_caption(caption: str) -> str:
    """Remove all @username mentions and collapse extra blank lines."""
    if not caption:
        return ""
    # Remove lines that are ONLY a @username (with optional spaces)
    lines = caption.splitlines()
    lines = [line for line in lines if not re.fullmatch(r'\s*@\w+\s*', line)]
    # Also remove inline @usernames within other lines
    lines = [re.sub(r'@\w+', '', line) for line in lines]
    # Remove lines that became empty after inline removal (including whitespace-only lines)
    lines = [line for line in lines if line.strip() and line.strip() != '\u200b']
    return '\n'.join(lines).strip()


async def reply_forward(message: Message, file_id: int):
    try:
        await message.reply_text(
            "Files will be deleted in 10 minutes to avoid copyright issues. Please forward and save them.",
            disable_web_page_preview=True,
            quote=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await reply_forward(message, file_id)


async def media_forward(bot: Client, user_id: int, file_id: int, prefix: str = ""):
    try:
        # Fetch the original message to get its caption
        original = await bot.get_messages(chat_id=Config.DB_CHANNEL, message_ids=file_id)
        original_caption = original.caption or ""

        # Strip existing @usernames, then prepend our prefix
        cleaned = clean_caption(original_caption)
        if prefix:
            new_caption = f"{prefix}\n\n{cleaned}" if cleaned else prefix
        else:
            new_caption = cleaned if cleaned else None

        if Config.FORWARD_AS_COPY is True:
            return await bot.copy_message(
                chat_id=user_id,
                from_chat_id=Config.DB_CHANNEL,
                message_id=file_id,
                caption=new_caption
            )
        else:
            # forward_messages doesn't support caption editing, so fall back to copy
            return await bot.copy_message(
                chat_id=user_id,
                from_chat_id=Config.DB_CHANNEL,
                message_id=file_id,
                caption=new_caption
            )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await media_forward(bot, user_id, file_id, prefix)


async def send_media_and_reply(bot: Client, user_id: int, file_id: int, prefix: str = ""):
    sent_message = await media_forward(bot, user_id, file_id, prefix)
    await reply_forward(message=sent_message, file_id=file_id)
    task = asyncio.create_task(delete_after_delay(sent_message, 600))
    # Hold a reference to prevent garbage collection
    sent_message._delete_task = task


async def delete_after_delay(message, delay):
    await asyncio.sleep(delay)
    await message.delete()
