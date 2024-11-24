
import asyncio
import random
import json

from discord.ext import commands, tasks
from datetime import datetime, timezone
from queue import Empty



"""
Just redo this entire mess
"""

with open("config.json", "r") as config_file:
    config_dict = json.load(config_file)

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.log(f"conf2 - commands","purple")
        self.bot.checks = []

    async def start_commands(self, waitTime=config_dict["defaultCooldowns"]["briefCooldown"]):
        await asyncio.sleep(self.bot.random_float(waitTime))
        self.send_commands.start()
        self.bot.log(f"{self.bot.user}[+] started sending commands~~", "cyan3")
        self.monitor_checks.start()
    async def cog_load(self):
        """Run join_previous_giveaways when bot is ready"""
        asyncio.create_task(self.start_commands())

    """send commands"""
    @tasks.loop()
    async def send_commands(self):
        while not self.bot.queue.empty():
            try:
                if self.bot.state and not self.bot.captcha:
                    """
                    Here cmd tuple includes
                    cmd[0] = command to send
                    cmd[1] = whether to add to checks
                    cmd[2] = if it is to be added to checks, this is added.
                    (command without prefix)
                    """
                    print(list(self.bot.queue.queue))
                    cmd = self.bot.queue.get() # double check blocking in .get()
                    await self.bot.send(cmd[0])
                    if cmd[1]:
                        self.bot.checks.append((cmd[2], datetime.now(timezone.utc), cmd[0]))
                    await asyncio.sleep(random.uniform(0.7, 1.2))
                else:
                    await asyncio.sleep(random.uniform(0.7, 1.2))
            except Empty:
                # Break out of the loop if there are no more items
                await asyncio.sleep(random.uniform(0.7, 1.2))
                break

    @tasks.loop(seconds=1)
    async def monitor_checks(self):
        current_time = datetime.now(timezone.utc)
        """
        The [:] creates a new list containing all the same items as the original list.
        Using it directly may lead to issues if its removed meanwhile
        Like when owobot lags.
        """
        for command, timestamp in self.bot.checks[:]:  # Loop through a copy to avoid modification issues
            if (current_time - timestamp).total_seconds() > 5:
                """Put the command back to the queue
                Not using any sleeps here as the delay should randomize it enough."""
                #self.bot.queue.put(command)
                self.bot.put_queue(command, prefix=False)
                self.bot.log(f"added {command} from cmd","cornflower_blue")
                try:
                    self.bot.checks.remove((command, timestamp))
                    self.bot.log(f"removed {command} from cmd, from checks","cornflower_blue")
                except:
                    pass



async def setup(bot):
    await bot.add_cog(Commands(bot))