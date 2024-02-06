#  Dragon-Userbot - telegram userbot
#  Copyright (C) 2020-present Dragon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import html
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from time import perf_counter
from traceback import print_exc

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.db import db
from utils.misc import modules_help, prefix
from utils.scripts import paste_yaso


async def aexec(code, *args, timeout=None):
    exec(
        f"async def __todo(client, message, *args):\n"
        + " app = client; "
        + " c = client; "
        + " m = message; "
        + " reply = m.reply_to_message; "
        + " r = reply; "
        + " p = print; "
        + " me = await c.get_me(); "
        + " api_key = db.get('core.gpt', 'api_key'); "
        + " u = m.from_user\n"
        + "".join(f"\n {_l}" for _l in code.split("\n"))
    )

    f = StringIO()
    with redirect_stdout(f):
        await asyncio.wait_for(locals()["__todo"](*args), timeout=timeout)

    return f.getvalue()


code_result = (
    "<b>Code:</b>\n<pre language='{pre_language}'>{code}</pre>\n\n{result}"
)


# noinspection PyUnusedLocal
@Client.on_message(
    ~filters.scheduled
    & filters.command(["e", "exec", "ex"], prefix)
    & filters.me
    & ~filters.forwarded
)
async def python_t1(client: Client, message: Message):
    await python_exec(client, message)


@Client.on_edited_message(
    ~filters.scheduled
    & filters.command(["e", "exec", "ex"], prefix)
    & filters.me
    & ~filters.forwarded
)
async def python_t2(client: Client, message: Message):
    await python_exec(client, message)


async def python_exec(client: Client, message: Message):
    if len(message.command) == 1:
        return await message.edit("<b>Code to execute isn't provided</b>")

    code = message.text.split(maxsplit=1)[1]

    await message.edit("<b>Executing...</b>")

    try:
        start_time = perf_counter()
        result = await aexec(
            code,
            client,
            message,
            db,
            globals(),
            timeout=db.get("core.python", "timeout", None),
        )
        stop_time = perf_counter()

        result = result.replace(
            (await client.get_me()).phone_number, "+447408857600"
        )

        if len(result) > 1024:
            result = html.escape(await paste_yaso(result))
        else:
            result = f"<pre>{html.escape(result)}</pre>"

        return await message.edit(
            code_result.format(
                pre_language="python",
                code=code,
                result=(
                    f"<b>Result</b>:\n{result}\n<b>Completed in"
                    f" {round(stop_time - start_time, 5)}s.</b>"
                ),
            ),
            disable_web_page_preview=True,
        )
    except asyncio.TimeoutError:
        return await message.edit(
            code_result.format(
                pre_language="python",
                code=code,
                result="<b>Timeout Error!</b>",
            ),
            disable_web_page_preview=True,
        )
    except Exception as e:
        err = StringIO()
        with redirect_stderr(err):
            print_exc()

        return await message.edit(
            code_result.format(
                pre_language="python",
                code=code,
                result=(
                    f"<b> {e.__class__.__name__}: {e}</b>\nTraceback:"
                    f" {html.escape(await paste_yaso(err.getvalue()))}"
                ),
            ),
            disable_web_page_preview=True,
        )


modules_help["python"] = {
    "e [code]*": "Execute python code.",
}
