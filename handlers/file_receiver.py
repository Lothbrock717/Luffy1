from asyncio import sleep
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from configs import Config

batch_files = {}


async def receive_files(client, message):
    is_batch = True
    msg_id = message.id
    batch_files[msg_id] = []

    async def event_filter(_, __, msg: Message):
        nonlocal is_batch

        if msg and msg.text:
            text = msg.text
            if text.startswith('/cancel'):
                is_batch = False
                batch_files.pop(msg_id, None)
                await message.delete()
                await msg.reply("Cancelled")
                return False
            elif text.startswith('/done'):
                is_batch = False
                return False
            # Ignore other text commands — let them propagate normally
            return False

        # Only collect media files, don't block text or other message types
        if msg and (msg.document or msg.video or msg.audio or msg.photo):
            batch_files[msg_id].append(msg)
            await msg.delete()

        # Always return False so other handlers can still run if needed
        return False

    user_filter = filters.create(
        lambda _, __, msg: msg.from_user and msg.from_user.id == Config.BOT_OWNER
    )

    handler = MessageHandler(event_filter, filters.private & user_filter)
    client.add_handler(handler, group=-1)

    while is_batch:
        await sleep(0.5)

    # Always remove handler when done — prevent leaking into normal file uploads
    client.remove_handler(handler, group=-1)

    return batch_files.pop(msg_id, [])
