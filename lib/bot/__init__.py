from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Intents
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound
from apscheduler.triggers.cron import CronTrigger
from glob import glob

from ..db import db

PREFIX = "as?"
OWNER_ID = [914245474159067187]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]


class Bot(BotBase):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX, owner_ids=OWNER_ID, intents=Intents.all()
        )
        self.scheduler = AsyncIOScheduler()
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None

        db.autosave(self.scheduler)

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"Loaded {cog}")
        print(f"{cog} complete!")

    def run(self, version):
        self.VERSION = version
        print("Running...")
        self.setup()

        with open("lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("Locked and loaded!")

    async def on_disconnect(self):
        print("I'll be back")

    async def on_error(self, event_method, *args, **kwargs):
        pass

    async def bump_reminder(self, context, exception):
        channel = self.get_channel(977579293947330560)
        role = 976555162128773150
        await channel.send("Time to /bump {}".format(role.mention))

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            await context.send("Command not found :eyes:")

        elif hasattr(exception, "original"):
            raise exception.original
        else:
            raise exception

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.stdout = self.get_channel(984213140898205706)
            self.scheduler.add_job(
                self.bump_reminder, CronTrigger(hour=2, minute=0, second=0)
            )
            self.scheduler.start()
            self.guild = self.get_guild(971846626299752459)
            print("Bot is ready!")

            await self.stdout.send("**Aitamah has awaken form her long sleep...**")

        else:
            print("Bot reconnected")

    async def on_message(self, message):
        pass


bot = Bot()
