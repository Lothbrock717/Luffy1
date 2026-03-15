from asyncio import sleep
from pyrogram.filters import create, chat
from pyrogram.handlers import MessageHandler

from common import batch_files, is_batch
from configs import Config

batch_files = {}

async def receive_files(client, message):
    is_batch = True
    msg_id = message.id
    batch_files[msg_id] = []

    async def event_filter(__, msg):
        nonlocal is_batch 
        if msg and msg.text:
            text = msg.text
            if text.startswith('/cancel'):
                is_batch = False
                batch_files.pop(msg_id, None)
                await message.delete()
                await msg.reply("Cancelled")
                return None
            elif text.startswith('/done'):
                is_batch = False
                return

        batch_files[msg_id].append(msg)
        await msg.delete()

    handler = MessageHandler(event_filter, chat(Config.BOT_OWNER))
    client.add_handler(handler, group=-1)

    while is_batch:
        await sleep(0.5)

    client.remove_handler(handler, group=-1)

    return batch_files.pop(msg_id, [])
