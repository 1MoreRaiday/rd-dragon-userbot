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

from contextlib import suppress

from pyrogram import Client, ContinuePropagation, errors, filters
from pyrogram.types import Message

from utils.db import db
from utils.misc import modules_help, prefix


@Client.on_message(filters.command("protector", prefix) & filters.me)
async def switcher(client: Client, message: Message):
    if not db.get("core.protector", "status"):
        db.set("core.protector", "status", True)
        await message.edit("<b>Protector enabled.</b>")
    else:
        db.set("core.protector", "status", False)
        await message.edit("<b>Protector disabled.</b>")


@Client.on_message(filters.text)
async def protector_t1(client: Client, message: Message):
    await hide(client, message)


@Client.on_edited_message(filters.text)
async def protector_t2(client: Client, message: Message):
    await hide(client, message)


async def hide(client: Client, message: Message):
    if not db.get("core.protector", "phone") and not db.get(
        "core.protector", "id"
    ):
        db.set("core.protector", "phone", (await client.get_me()).phone_number)
        db.set("core.protector", "id", (await client.get_me()).id)
    if (
        db.get("core.protector", "status")
        and db.get("core.protector", "phone") in message.text
    ):
        if message.from_user.id == int(db.get("core.protector", "id")):
            await message.edit(
                message.text.html.replace(
                    db.get("core.protector", "phone"), "447408857600"
                )
            )
        else:
            with suppress(errors.MessageDeleteForbidden):
                await message.delete()
    raise ContinuePropagation


modules_help["protector"] = {"protector": "Enable or disable phone protector."}
