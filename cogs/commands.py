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
import random
import json

from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta



class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.checks = []
        self.calc_time = timedelta(0)

    async def start_commands(self):
        await asyncio.sleep(self.bot.random_float(self.bot.config_dict["defaultCooldowns"]["briefCooldown"]))
        self.send_commands.start()
        self.monitor_checks.start()

    async def cog_load(self):
        """Run join_previous_giveaways when bot is ready"""
        asyncio.create_task(self.start_commands())
    
    """send commands"""
    @tasks.loop()
    async def send_commands(self):
        try:
            cmd = await self.bot.queue.get()
            await self.bot.send(self.bot.construct_command(cmd))
            if cmd.get("checks"):
                self.bot.checks.append((cmd, datetime.now(timezone.utc)))
            await asyncio.sleep(random.uniform(0.7, 1.2))
        except Exception as e:
            print(f"Error in send_commands loop: {e}")
            await asyncio.sleep(random.uniform(0.7, 1.2))

    """TASK: check monitor"""

    @tasks.loop(seconds=1)
    async def monitor_checks(self):
        try:
            current_time = datetime.now(timezone.utc)
            """
            The [:] creates a new list containing all the same items as the original list.
            Using it directly may lead to issues if its removed meanwhile
            Like when owobot lags.
            """
            if not self.bot.captcha and self.bot.state:
                for command, timestamp in self.bot.checks[
                    :
                ]:  # Loop through a copy to avoid modification issues
                    if (current_time+self.calc_time - timestamp).total_seconds() > 7:
                        """Put the command back to the queue
                        Not using any sleeps here as the delay should randomize it enough."""
                        # self.bot.queue.put(command)
                        await self.bot.put_queue(command)
                        self.bot.log(f"added {command} from cmd", "cornflower_blue")
                        try:
                            self.bot.checks.remove((command, timestamp))
                            self.bot.log(
                                f"removed {command} from cmd, from checks", "cornflower_blue"
                            )
                        except:
                            pass
                self.calc_time = timedelta(0)
            else:
                if hasattr(self, 'last_check_time'):
                    self.calc_time += current_time - self.last_check_time
                self.last_check_time = current_time
        except Exception as e:
            print(e)
            print("^ at command monitor")



async def setup(bot):
    await bot.add_cog(Commands(bot))