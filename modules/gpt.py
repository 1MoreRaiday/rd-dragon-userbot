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
#
# requires: openai mistune

import mistune
import openai
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.db import db
from utils.misc import modules_help, prefix
from utils.scripts import get_args_raw, import_library

messages: list[openai.types.chat.ChatCompletionMessageParam] = db.get(
    "core.gpt", "messages", []
)
if not db.get("core.gpt", "version"):
    db.set("core.gpt", "version", "gpt-3.5-turbo-16k")


async def create_completion(
    message: Message,
    client: Client,
    oai: openai.AsyncClient,
    messages: list[openai.types.chat.ChatCompletionMessageParam] = messages,
):
    try:
        return await oai.chat.completions.create(
            model=db.get("core.gpt", "version"),
            messages=messages,
        )
    except Exception as e:
        await client.send_message("me", " ".join(message.text.split()[1:]))
        return await message.edit(str(e))


def get_client() -> openai.AsyncClient:
    if db.get("core.gpt", "api_key") is None:
        raise ValueError("<b>API key not set.</b>")
    oai = openai.AsyncClient(api_key=db.get("core.gpt", "api_key"))
    return oai


def get_prompt(message: Message):
    try:
        if args := get_args_raw(message, True):
            return args
        else:
            raise ValueError("<b>Provide a question.</b>")
    except AttributeError:
        raise ValueError("<b>Provide a question.</b>")


@Client.on_message(filters.command("gpt", prefix) & filters.me)
async def gpt(client: Client, message: Message):
    try:
        oai = get_client()
    except ValueError as e:
        return await message.edit(str(e))

    try:
        question = get_prompt(message)
    except ValueError as e:
        return await message.edit(str(e))
    messages.append({"role": "user", "content": question})

    await message.edit("<b>Thinking...</b>")
    response = await create_completion(message=message, client=client, oai=oai)

    if not isinstance(response, Message):
        messages.append({
            "role": "assistant",
            "content": str(response.choices[0].message.content),
        })
        await message.edit(
            f"{mistune.html(response.choices[0].message.content)}\n\n<b>Your"
            f" question was:</b> <code>{question}</code>",
        )


@Client.on_message(filters.command("g", prefix) & filters.me)
async def gpt_no_context(client: Client, message: Message):
    try:
        oai = get_client()
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
        oai=oai,
    )

    if not isinstance(response, Message):
        await message.edit(
            f"{mistune.html(response.choices[0].message.content)}\n\n<b>Your"
            f" question was:</b> <code>{question}</code>",
        )


@Client.on_message(filters.command("clearchat", prefix) & filters.me)
async def clear_chat(_: Client, message: Message):
    db.set("core.gpt", "messages", [])
    await message.edit("<b>Chat cleared.</b>")


@Client.on_message(filters.command("set_api_key", prefix) & filters.me)
async def set_api_key(_: Client, message: Message):
    if len(message.text.split()) < 2:
        return await message.edit("<b>Provide an API key.</b>")
    db.set("core.gpt", "api_key", str(message.text.split()[1]).strip())
    if message.chat.id != message.from_user.id:
        await message.delete()
    await message.edit("<b>API key set.</b>")


@Client.on_message(filters.command("set_version", prefix) & filters.me)
async def set_version(_: Client, message: Message):
    if len(message.text.split()) < 2:
        return await message.edit("<b>Provide a version.</b>")
    db.set("core.gpt", "version", message.text.split()[1])
    await message.edit("<b>Version set.</b>")


modules_help["gpt"] = {
    "gpt [question]*": "Ask a question to ChatGPT.",
    "g [question]*": "Ask a question to ChatGPT without context.",
    "set_api_key [key]*": "Set the API key. Use only in saved messages!",
    "clearchat": "Clear the chat history.",
    "set_version [version]*": "Set the version. Default: gpt-3.5-turbo-16k.",
}
