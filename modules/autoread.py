#  ______     ______     ______     ______     ______   __     ______     ______
# /\  ___\   /\  == \   /\  ___\   /\  __ \   /\__  _\ /\ \   /\___  \   /\  ___\
# \ \ \____  \ \  __<   \ \  __\   \ \  __ \  \/_/\ \/ \ \ \  \/_/  /__  \ \  __\
#  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\ \_\    \ \_\  \ \_\   /\_____\  \ \_____\
#   \/_____/   \/_/ /_/   \/_____/   \/_/\/_/     \/_/   \/_/   \/_____/   \/_____/
#
# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

from pyrogram import Client, filters
from pyrogram.raw.functions.account import UpdateStatus
from pyrogram.types import Message

from utils.db import db
from utils.misc import modules_help, prefix
from utils.scripts import restart


@Client.on_message(filters.command("autoread", prefix) & filters.me)
async def switcher(_: Client, message: Message):
    if not db.get("core.autoread", "status"):
        db.set("core.autoread", "status", True)
        return await message.edit("<b>Autoread enabled.</b>")
    else:
        db.set("core.autoread", "status", False)
        return await message.edit("<b>Autoread disabled.</b>")


@Client.on_message(filters.command("addchat", prefix) & filters.me)
async def addchat(_: Client, message: Message):
    if len(message.command) != 2:
        return await message.edit("<b>Provide a chat ID.</b>")
    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.edit("<b>Invalid chat ID.</b>")
    if chat_id in db.get("core.autoread", "chats", []):
        return await message.edit("<b>Chat already added.</b>")
    ids = db.get("core.autoread", "chats", [])
    ids.append(chat_id)
    db.set("core.autoread", "chats", ids)
    await message.edit("<b>Chat added.</b>")
    return restart()


@Client.on_message(filters.command("rmchat", prefix) & filters.me)
async def rmchat(_: Client, message: Message):
    if len(message.command) != 2:
        return await message.edit("<b>Provide a chat ID.</b>")
    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.edit("<b>Invalid chat ID.</b>")
    if chat_id not in db.get("core.autoread", "chats", []):
        return await message.edit("<b>Chat not added.</b>")
    ids: list = db.get("core.autoread", "chats", [])
    ids.remove(chat_id)
    db.set("core.autoread", "chats", ids)
    await message.edit("<b>Chat removed.</b>")
    return restart()


@Client.on_message(filters.command("auto_offline", prefix) & filters.me)
async def switcher_off(_: Client, message: Message):
    if not db.get("core.autoread", "auto_offline"):
        db.set("core.autoread", "auto_offline", True)
        return await message.edit("<b>Auto offline enabled.</b>")
    else:
        db.set("core.autoread", "auto_offline", False)
        return await message.edit("<b>Auto offline disabled.</b>")


@Client.on_message(filters.chat(db.get("core.autoread", "chats", "me")))
async def autoread(client: Client, message: Message):
    if not db.get("core.autoread", "status"):
        return
    await client.read_chat_history(message.chat.id)
    if db.get("core.autoread", "auto_offline"):
        await client.invoke(UpdateStatus(offline=True))


modules_help["autoread"] = {
    "autoread": "Enable or disable autoread.",
    "addchat [id]*": "Add a chat to autoread.",
    "rmchat [id]*": "Remove a chat from autoread.",
    "auto_offline": "Enable or disable auto offline.",
}
