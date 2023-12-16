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

import datetime
import random

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import (
    gitrepo,
    modules_help,
    prefix,
    python_version,
    userbot_version,
)


@Client.on_message(filters.command(["support", "repo"], prefix) & filters.me)
async def support(_, message: Message):
    devs = ["@john_ph0nk", "@fuccsoc2"]
    random.shuffle(devs)

    commands_count = float(
        len([cmd for module in modules_help for cmd in module])
    )

    await message.edit(
        "<b>Dragon-Userbot\n\nGitHub: <a"
        " href=https://github.com/Dragon-Userbot/Dragon-Userbot>Dragon-Userbot/Dragon-Userbot</a>\nCustom"
        " modules repository: <a"
        " href=https://github.com/Dragon-Userbot/custom_modules>Dragon-Userbot/custom_modules</a>\nLicense:"
        " <a href=https://github.com/Dragon-Userbot/Dragon-Userbot/blob/master/LICENSE>GNU"
        " GPL v3</a>\n\nChannel: @Dragon_Userb0t\nCustom modules:"
        " @Dragon_Userb0t_modules\nChat [RU]: @Dragon_Userb0t_chat\nMain"
        f" developers: {', '.join(devs)}\n\nPython version:"
        f" {python_version}\nModules count: {len(modules_help) / 1}\nCommands"
        f" count: {commands_count}</b>",
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command(["version", "ver"], prefix) & filters.me)
async def version(client: Client, message: Message):
    changelog = ""
    ub_version = ".".join(userbot_version.split(".")[:2])
    async for m in client.search_messages(
        "dRaGoN_uB_cHaNgElOg", query=ub_version + "."
    ):
        if ub_version in m.text:
            changelog = m.id

    await message.delete()

    remote_url = list(gitrepo.remote().urls)[0]
    commit_time = (
        datetime.datetime.fromtimestamp(gitrepo.head.commit.committed_date)
        .astimezone(datetime.timezone.utc)
        .strftime("%Y-%m-%d %H:%M:%S %Z")
    )

    await message.reply(
        f"<b>Dragon Userbot version: {userbot_version}\nChangelog </b><i><a"
        f" href=https://t.me/dRaGoN_uB_cHaNgElOg/{changelog}>in"
        " channel</a></i>.<b>\nChangelogs are written by </b><i><a"
        " href=tg://user?id=318865588>\u2060</a><a"
        " href=tg://user?id=293490416>♿️</a><a"
        " href=https://t.me/acnxua>asphuy</a><a"
        " href=https://t.me/artemjj2>♿️</a></i>\n\n"
        + (
            "<b>Branch: <a"
            f" href={remote_url}/tree/{gitrepo.active_branch}>{gitrepo.active_branch}</a>\n"
            if gitrepo.active_branch != "master"
            else ""
        )
        + "Commit: <a"
        f" href={remote_url}/commit/{gitrepo.head.commit.hexsha}>{gitrepo.head.commit.hexsha[:7]}</a>"
        f" by {gitrepo.head.commit.author.name}\nCommit time:"
        f" {commit_time}</b>",
    )


modules_help["support"] = {
    "support": "Information about userbot",
    "version": "Check userbot version",
}
