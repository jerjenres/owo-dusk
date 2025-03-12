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

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_on_cooldown = False  # Prevents race conditions
        self.last_execution = 0  # Tracks last execution time

        self.cmd = {
            "cmd_name": "",
            "prefix": True,
            "checks": True,
            "retry_count": 0,
            "id": "battle",
            "slash_cmd_name": "battle",
            "removed": False
        }

    async def cog_load(self):
        if not self.bot.config_dict["commands"]["battle"]["enabled"]:
            try:
                asyncio.create_task(self.bot.unload_cog("cogs.battle"))
            except:
                pass
        else:
            self.cmd["cmd_name"] = (
                self.bot.alias["battle"]["shortform"]
                if self.bot.config_dict["commands"]["battle"]["useShortForm"]
                else self.bot.alias["battle"]["alias"]
            )
            await self.bot.put_queue(self.cmd)

    async def cog_unload(self):
        await self.bot.remove_queue(id="battle")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.reference is not None:
            return

        try:
            if message.channel.id == self.bot.cm.id and message.author.id == self.bot.owo_bot_id:
                if message.embeds:
                    for embed in message.embeds:
                        if embed.author.name is not None and "goes into battle!" in embed.author.name.lower():
                            # Timestamp-based cooldown check
                            current_time = time.time()
                            min_cooldown = self.bot.config_dict["commands"]["battle"]["cooldown"][0]

                            if current_time - self.last_execution < min_cooldown:
                                return  # Cooldown active, ignore command

                            self.last_execution = current_time  # Update last execution time

                            if not self.is_on_cooldown:
                                self.is_on_cooldown = True
                                await self.bot.remove_queue(id="battle")
                                await asyncio.sleep(self.bot.random_float(self.bot.config_dict["commands"]["battle"]["cooldown"]))

                                self.cmd["cmd_name"] = (
                                    self.bot.alias["battle"]["shortform"]
                                    if self.bot.config_dict["commands"]["battle"]["useShortForm"]
                                    else self.bot.alias["battle"]["alias"]
                                )
                                await self.bot.put_queue(self.cmd)
                                self.is_on_cooldown = False

        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Battle(bot))
