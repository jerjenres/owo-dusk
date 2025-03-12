# This file is part of owo-dusk.
#
# Copyright (c) 2024-present EchoQuill
#
# Portions of this file are based on code by EchoQuill, licensed under the
# GNU General Public License v3.0 (GPL-3.0).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import asyncio
import time
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

class Hunt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_on_cooldown = False
        self.last_execution = 0  # Track last execution time

        self.cmd = {
            "cmd_name": "",
            "prefix": True,
            "checks": True,
            "retry_count": 0,
            "id": "hunt",
            "slash_cmd_name": "hunt",
            "removed": False
        }

    async def cog_load(self):
        if not self.bot.config_dict["commands"]["hunt"]["enabled"]:
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.hunt"))
            except ExtensionNotLoaded:
                pass
        else:
            self.cmd["cmd_name"] = (
                self.bot.alias["hunt"]["shortform"]
                if self.bot.config_dict["commands"]["hunt"]["useShortForm"]
                else self.bot.alias["hunt"]["alias"]
            )
            await self.bot.put_queue(self.cmd)

    async def cog_unload(self):
        await self.bot.remove_queue(id="hunt")

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.channel.id == self.bot.cm.id and message.author.id == self.bot.owo_bot_id:
                if 'you found:' in message.content.lower() or "caught" in message.content.lower():
                    current_time = time.time()
                    min_cooldown = self.bot.config_dict["commands"]["hunt"]["cooldown"][0]

                    if current_time - self.last_execution < min_cooldown:
                        return  # Cooldown active, ignore command

                    self.last_execution = current_time  # Update last execution time

                    if not self.is_on_cooldown:
                        self.is_on_cooldown = True
                        await self.bot.remove_queue(id="hunt")
                        await asyncio.sleep(self.bot.random_float(self.bot.config_dict["commands"]["hunt"]["cooldown"]))

                        self.cmd["cmd_name"] = (
                            self.bot.alias["hunt"]["shortform"]
                            if self.bot.config_dict["commands"]["hunt"]["useShortForm"]
                            else self.bot.alias["hunt"]["alias"]
                        )
                        await self.bot.put_queue(self.cmd)
                        self.is_on_cooldown = False

        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Hunt(bot))
