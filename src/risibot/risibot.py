import asyncio

import discord
from discord.ext import commands as discord_commands

import risibot.constants as constants
import risibot.commands as risibot_commands
import risibot.data_manager as dm

from risibot.commands import client

@client.event
async def on_ready() -> None:
    """
    Sends an initialization message to the special bot channel.
    """
    if constants.TEST:
        channel = client.get_channel(1205505802912137219)
        guild = client.get_guild(1205505801939197952)
    else:
        channel = client.get_channel(1204886119032823878)
        guild = client.get_guild(1103589587751817299)    
    await channel.send(f'Risibot connected to {guild.name}. id: {guild.id}.')
    while True:
        await dm.fetch_poe_ninja()
        await asyncio.sleep(900) # 15min waiting time


@client.event
async def on_message(message: discord.Message):
    if message.author.bot: return
    await risibot_commands.search_poewiki(message)
    await risibot_commands.check_links(message)
    await client.process_commands(message)