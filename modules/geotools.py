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

from ast import literal_eval
from functools import partial

from geopy.geocoders import Nominatim
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import import_library

_ = import_library("geopy")


@Client.on_message(filters.command("geo", prefix) & filters.me)
async def geo(client: Client, message: Message):
    args = " ".join(message.command[1:])

    if message.reply_to_message:
        r = message.reply_to_message
    else:
        r = None

    if not args:
        return await message.edit("<b>No arguments provided.</b>")

    geo_client = Nominatim(user_agent="Dragon-Userbot")
    geocode = partial(geo_client.geocode, language="en")
    if "-c" in args:
        args = args.replace("-c", "")
        place = tuple(literal_eval(args))
    else:
        args = args.replace("-c", "")
        place = geocode(args)
        if not place:
            return await message.edit("<b>Place not found.</b>")
        place = (place.latitude, place.longitude)

    await message.delete()

    await client.send_location(
        message.chat.id,
        latitude=place[0],
        longitude=place[1],
        reply_to_message_id=r.message_id if r else None,
    )


modules_help["geotools"] = {"geo": "Get location of a place."}
