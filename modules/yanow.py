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

import html
import io

from pyrogram import Client, filters
from pyrogram.types import Message
from yandex_music import ClientAsync

from utils.db import db
from utils.misc import modules_help, prefix
from utils.scripts import import_library

_ = import_library("yandex_music", "yandex-music")
__ = import_library("aiohttp")

playing = (
    "<b>🎧 Now playing: </b><code>{}</code><b> -"
    " </b><code>{}</code>\n<b><a href='{}'>song.link</a></b>"
)


@Client.on_message(filters.command("set_ya_token", prefix) & filters.me)
async def set_token(_: Client, message: Message):
    if len(message.text.split()) != 2:
        if message.chat.id != message.from_user.id:
            return await message.delete()
        return await message.edit("<b>Provide a token.</b>")
    token = message.text.split()[1]
    db.set("core.yanow", "token", token)
    if message.chat.id != message.from_user.id:
        return await message.delete()
    return await message.edit("<b>Token set.</b>")


# noinspection PyBroadException
@Client.on_message(
    filters.command(["yanow", "ynow", "y", "н"], prefix) & filters.me
)
async def get_now_playing(client: Client, message: Message):
    if not db.get("core.yanow", "token"):
        return await message.edit("<b>Yandex Music token not set.</b>")

    await message.edit("<b>Fetching...</b>")

    ya_client = ClientAsync(db.get("core.yanow", "token"))
    await ya_client.init()
    try:
        queues = await ya_client.queues_list()
        last_queue = await ya_client.queue(queues[0].id)
    except:
        return await message.edit(
            '<b>You are listening track from "My Vibe"</b>.'
        )
    try:
        last_track_id = last_queue.get_current_track()
        last_track = await last_track_id.fetch_track_async()
    except:
        return await message.edit(
            '<b>You are listening track from "My Vibe"</b>.'
        )

    artists = ", ".join(last_track.artists_name())
    title = last_track.title
    if last_track.version:
        title += f" ({last_track.version})"
    else:
        pass

    try:
        lnk = last_track.id.split(":")[1]
    except IndexError:
        lnk = last_track.id
    else:
        pass

    caption = playing.format(
        html.escape(artists),
        html.escape(title),
        f"https://song.link/ya/{lnk}",
    )

    await message.edit(
        f"<b>Fetching... </b>\n\n{caption}", disable_web_page_preview=True
    )

    await client.send_audio(
        chat_id=message.chat.id,
        audio=io.BytesIO(await last_track.download_bytes_async()),
        caption=caption,
        title=title,
        performer=artists,
        thumb=io.BytesIO(
            await last_track.download_cover_bytes_async(size="1000x1000")
        ),
        file_name=f"{artists} - {title}.mp3",
        reply_to_message_id=message.reply_to_message_id,
        message_thread_id=message.message_thread_id,
    )
    await message.delete()


modules_help["yanow"] = {
    "yanow": "Get now playing from Yandex Music.",
    "set_ya_token [token]*": (
        "Set Yandex Music token. Use only in saved messages!"
    ),
}
