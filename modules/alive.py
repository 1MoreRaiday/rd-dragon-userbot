import time
from sys import version_info

from pyrogram import Client
from pyrogram import __version__ as __pyro_version__
from pyrogram import filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix, requirements_list

StartTime = time.time()


__major__ = 0
__minor__ = 2
__micro__ = 1

__python_version__ = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"


def get_readable_time(seconds: int) -> str:
    count = 0
    formatted_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = (
            divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        )
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        formatted_time += time_list.pop() + ", "

    time_list.reverse()
    formatted_time += ":".join(time_list)

    return formatted_time


@Client.on_message(filters.command("alive", prefix) & filters.me)
async def alive(client: Client, message: Message):
    reply = message.reply_to_message if message.reply_to_message else None
    uptime = get_readable_time((time.time() - StartTime))
    start = time.perf_counter()
    reply_msg = (
        f"<a href ="
        f" https://gitlab.com/visionavtr/dragon-userbot>Dragon-Userbot</a>\n"
    )
    reply_msg += f"<b>Python Version:</b> <code>{__python_version__}</code>\n"
    reply_msg += f"<b>Pyrogram Version:</b> <code>{__pyro_version__}</code>\n"
    reply_msg += f"\n<b>Uptime:</b> <code>{uptime}</code>\n"
    await message.delete()
    end = time.perf_counter()
    reply_msg += (
        f"<b>Ping:</b> <code>{round((end - start) * 1000, 2)}ms</code>\n"
    )
    await client.send_message(
        message.chat.id,
        reply_msg,
        disable_web_page_preview=True,
        message_thread_id=message.message_thread_id,
        reply_to_message_id=reply,
    )


modules_help["alive"] = {
    "alive": " check bot alive status",
}
