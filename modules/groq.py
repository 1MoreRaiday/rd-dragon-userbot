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

import groq
import mistune
from pyrogram import Client, filters
from pyrogram.types import Message
import httpx
from utils.db import db
from utils.misc import modules_help, prefix
from utils.scripts import get_args_raw, import_library

_ = import_library("groq")
__ = import_library("mistune")


if not db.get("core.groq", "version"):
    db.set("core.groq", "version", "mixtral-8x7b-32768")


async def create_completion(
    message: Message,
    client: Client,
    gcl: groq.AsyncClient,
    messages: list[str],
):
    try:
        return await gcl.chat.completions.create(
            model=db.get("core.groq", "version"),
            messages=messages,
        )
    except Exception as e:
        await client.send_message("me", " ".join(message.text.split()[1:]))
        return await message.edit(str(e))


def get_client() -> groq.AsyncClient:
    if db.get("core.groq", "api_key") is None:
        raise ValueError("<b>API key not set.</b>")
    proxy = db.get("core.groq", "proxy")
    if not proxy:
        gcl = groq.AsyncClient(api_key=db.get("core.groq", "api_key"))
    else:
        gcl = groq.AsyncClient(api_key=db.get("core.groq", "api_key"), 
            http_client=httpx.AsyncClient(
            proxies=proxy
            ))
    return gcl


def get_prompt(message: Message):
    try:
        if args := get_args_raw(message, True):
            return args
        else:
            raise ValueError("<b>Provide a question.</b>")
    except AttributeError:
        raise ValueError("<b>Provide a question.</b>")


@Client.on_message(filters.command("groq", prefix) & filters.me)
async def ask_groq(client: Client, message: Message):
    try:
        gcl = get_client()
    except ValueError as e:
        return await message.edit(str(e))

    try:
        question = get_prompt(message)
    except ValueError as e:
        return await message.edit(str(e))

    await message.edit("<b>Thinking...</b>")
    response = await create_completion(
        message=message,
        messages=[{"role": "user", "content": question}],
        client=client,
        gcl=gcl,
    )

    if not isinstance(response, Message):
        await message.edit(
            f"{mistune.html(response.choices[0].message.content)}\n\n<b>Your"
            f" question was:</b> <code>{question}</code>",
        )


@Client.on_message(filters.command("set_groq_key", prefix) & filters.me)
async def set_api_key(_: Client, message: Message):
    if len(message.text.split()) < 2:
        return await message.edit("<b>Provide an API key.</b>")
    db.set("core.groq", "api_key", str(message.text.split()[1]).strip())
    if message.chat.id != message.from_user.id:
        await message.delete()
    await message.edit("<b>API key set.</b>")


@Client.on_message(filters.command("set_groq_version", prefix) & filters.me)
async def set_version(_: Client, message: Message):
    if len(message.text.split()) < 2:
        return await message.edit("<b>Provide a version.</b>")
    db.set("core.groq", "version", message.text.split()[1])
    await message.edit("<b>Version set.</b>")

@Client.on_message(filters.command("set_groq_proxy", prefix) & filters.me)
async def set_proxy(_: Client, message: Message):
    if len(message.text.split()) == 1: 
        db.set("core.groq", "proxy", '')
        await message.edit("<b>Proxy unset.</b>")
    else: 
        db.set("core.groq", "proxy", message.text.split()[1])
    await message.edit("<b>Proxy set.</b>")


modules_help["groq"] = {
    "groq [question]*": "Ask a question to GroqCloud (w/o context only).",
    "set_groq_key [key]*": "Set the GroqCloud API key. Use only in saved messages!",
    "set_groq_version [version]*": "Set the version. Default: mixtral-8x7b-32768.",
    "set_groq_proxy [proxy|none]*": "Set the proxy. Default: None.",
}
