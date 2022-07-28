from discord.ext import commands
from discord import Guild, TextChannel, Message
from random import choice
from cachetools import LFUCache
from os import environ
from aiohttp import ClientSession
from typing import Optional
from db import GuildSettings, session

# initiate the object

dunno = [  # List of error responses for ai
    "IDK.",
    "I don't really know.",
    "Could you rephrase that?",
    "Come again?",
    "Say that again?",
    "Huh?",
    "What?",
]


class chatbot(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            4, 10, commands.BucketType.member
        )
        self.cache: LFUCache[int, int] = LFUCache(100)
        self.bid = environ.get("BRAINSHOP_ID")
        self.bkey = environ.get("BRAINSHOP_KEY")
        self.http = ClientSession()



    @commands.command()
    async def aichannel(self, ctx: commands.Context, channel: TextChannel):
        g = GuildSettings.get
        await GuildSettings.update_chatbot_channel(ctx.guild.id, channel.id)
        self.cache[ctx.guild.id] = channel.id
        await ctx.send("Set ai channel to " + channel.name)
        await channel.send("Hi I am Pog Memer, you can chat with me here")

    async def get_ai_channel(self, guild: Guild) -> Optional[int]:
        if guild.id in self.cache:
            return self.cache[guild.id]
        d = await GuildSettings.get(guild.id)
        if d:
            self.cache[guild.id] = d
        return d

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if (
            message.author.id == self.client.user.id
            or not message.guild
            or message.channel.id != (await self.get_ai_channel(message.guild))
        ):
            return
        channel = message.channel
        if channel.id != (await self.get_ai_channel(message.guild)):
            return
        bucket = self.cd_mapping.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return await channel.send("Woah, slow down!")
        try:
            response = await self.http.get(
                f"http://api.brainshop.ai/get?bid=168192&key=kFWvQk6738l0yFTM&uid={message.author.id}&msg={message.content}"
            )
            res = await response.json()
            await message.reply(res["cnt"])
        except:
            await message.reply(choice(dunno)) # # nosec: B311

    @commands.command()
    async def ai(self, ctx: commands.Context, message: Message):
        bucket = self.cd_mapping.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return await ctx.send("Woah, slow down!")
        try:
            response = await self.http.get(
                f"http://api.brainshop.ai/get?bid=168192&key=kFWvQk6738l0yFTM&uid={message.author.id}&msg={message.content}"
            )
            res = await response.json()
            await message.reply(res["cnt"])
        except:
            await message.reply(choice(dunno)) # nosec: B311


def setup(client):
    client.add_cog(chatbot(client))
