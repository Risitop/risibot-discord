import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

from datetime import date
import json
import pickle
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
LEAGUE = os.getenv("LEAGUE")

client = commands.Bot(
    command_prefix="!",
    intents=discord.Intents.all()
)
poe_ninja_data = None

def fetch_poe_ninja():
    global poe_ninja_data
    api_addresses = {
        "Currency":	            f"https://poe.ninja/api/data/currencyoverview?league={LEAGUE}&type=Currency",
        "Fragment":	            f"https://poe.ninja/api/data/currencyoverview?league={LEAGUE}&type=Fragment",
        "Oils":	                f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Oil",
        "Incubators":	        f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Incubator",
        "Scarabs":	            f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Scarab",
        "Fossils":	            f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Fossil",
        "Resonators":	        f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Resonator",
        "Essence":	            f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Essence",
        "Divination Cards":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=DivinationCard",
        "Prophecies":	        f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Prophecy",
        "Skill Gems":	        f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=SkillGem",
        "Base Types":	        f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=BaseType",
        "Helmet Enchants":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=HelmetEnchant",
        "Unique Maps":	        f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueMap",
        "Maps":	                f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Map",
        "Unique Jewels":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueJewel",
        "Unique Flasks":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueFlask",
        "Unique Weapons":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueWeapon",
        "Unique Armours":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueArmour",
        "Unique Accessories":	f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueAccessory",
        "Beasts":	            f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Beast"
    }
    if not os.path.isdir('data'): os.mkdir('data')
    if os.path.isfile('data/ninja_cache.dat'):
        with open('data/ninja_cache.dat', 'rb') as f:
            data = pickle.load(f)
            if data['_fetch_date'] == date.today():
                poe_ninja_data = data
                print('Data up to date. Nothing to fetch.')
                return
    poe_ninja_data = {"_fetch_date": date.today()}
    for key, addr in api_addresses.items():
        print(f'Fetching {key}...')
        response = requests.get(addr)
        data = json.loads(response.text)
        if "lines" not in data: 
            print('Nothing to fetch.')
            continue
        for elem in data["lines"]:
            name = elem.get('currencyTypeName', elem.get('name', None))
            if name is None:
                print(f'Cannot find name: {elem}')
                continue
            price = elem.get('chaosValue', None)
            if price is None:
                price = elem.get('receive', None)
                if price is None:
                    print(f'Cannot find price: {elem}')
                    continue
                price = price['value']
            poe_ninja_data[name.lower()] = price
    with open('data/ninja_cache.dat', 'wb') as f:
        pickle.dump(poe_ninja_data, f)
        

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD: break
    channel = client.get_channel(1204886119032823878)
    await channel.send(f'Risibot connected to {guild.name}. id: {guild.id}')

@client.command()
async def price(context, *argv):
    target_item = ' '.join(argv)
    price = poe_ninja_data.get(target_item.lower(), None)
    if price is None:
        if target_item.lower() == "chaos orb":
            await context.send(f'> 1 chaos = 1 chaos Poggers')
            return
        await context.send(f'> Item inconnu : {target_item}. Assurez-vous d\'utiliser le nom anglais.')
    else:
        await context.send(f'> {target_item} price: {price} chaos.')
        

if __name__ == "__main__":
    fetch_poe_ninja()
    client.run(TOKEN)