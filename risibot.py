import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

import json
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
NINJA_API = os.getenv('NINJA_API')

client = commands.Bot(
    command_prefix="!",
    intents=discord.Intents.all()
)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD: break
    channel = client.get_channel(1204886119032823878)
    await channel.send(f'Risibot connected to {guild.name}. id: {guild.id}')

@client.command()
async def price(context, *argv):
    target_item = ' '.join(argv).lower()
    response = requests.get(NINJA_API)
    data = json.loads(response.text)["lines"]
    found = False
    for elem in data:
        if elem["currencyTypeName"].lower() == target_item:
            print(elem)
            found = True
            await context.send(f'> {elem["currencyTypeName"]} price: {elem["receive"]["value"]} chaos.')
            break
    if not found:
        await context.send(f'Item inconnu : {target_item}. Assurez-vous d\'utiliser le nom anglais.')

if __name__ == "__main__":
    client.run(TOKEN)