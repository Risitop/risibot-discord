import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

import asyncio
import time
import json
import pickle
import aiohttp

RUN_LOCAL = False
LEAGUE = "Affliction"
POE_NINJA_DATA = None

if not RUN_LOCAL:
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')

client = commands.Bot(
    command_prefix="!",
    intents=discord.Intents.all()
)

async def fetch_poe_ninja():

    # Fetches poe.ninja prices, and caches them into a local file
    global POE_NINJA_DATA
    api_addresses = {
        "Currency":	            f"https://poe.ninja/api/data/currencyoverview?league={LEAGUE}&type=Currency",
        "Fragment":	            f"https://poe.ninja/api/data/currencyoverview?league={LEAGUE}&type=Fragment",
        "Oils":	                f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Oil",
        "Scarabs":	            f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Scarab",
        "Fossils":	            f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Fossil",
        "Resonators":	        f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Resonator",
        "Essence":	            f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Essence",
        "Divination Cards":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=DivinationCard",
        "Skill Gems":	        f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=SkillGem",
        "Unique Maps":	        f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueMap",
        "Unique Jewels":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueJewel",
        "Unique Flasks":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueFlask",
        "Unique Weapons":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueWeapon",
        "Unique Armours":	    f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueArmour",
        "Unique Accessories":	f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueAccessory",
        "Beasts":	            f"https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Beast"
    }

    # Checking if cache is up to date
    if not os.path.isdir('data'): os.mkdir('data')
    if os.path.isfile('data/ninja_cache.dat'):
        with open('data/ninja_cache.dat', 'rb') as f:
            data = pickle.load(f)
            if time.time() - data['_fetch_date'] < 900: # 15 min
                POE_NINJA_DATA = data
                print('Data up to date. Nothing to fetch.')
                return
            
    # Fetching poe.ninja
    container = {"_fetch_date": time.time()}
    async with aiohttp.ClientSession() as session:
        for key, addr in api_addresses.items():
            print(f'Fetching {key}...')
            async with session.get(addr) as response:
                if response.status != 200:
                    print(f'{addr} -> ERROR {response.status}')
                    continue
                text = await response.text()
                data = json.loads(text)
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
                    container[name.lower()] = {"price": price, "true_name": name, "is_equipment": "Unique" in key}

    # Updating the cache
    if os.path.isfile('data/ninja_cache.dat'):
        os.remove('data/ninja_cache.dat')
    with open('data/ninja_cache.dat', 'wb') as f:
        pickle.dump(container, f)
    POE_NINJA_DATA = container
        

@client.event
async def on_ready() -> None:
    """
    Sends an initialization message to the special bot channel.
    """
    for guild in client.guilds:
        if guild.name == GUILD: break
    channel = client.get_channel(1204886119032823878)
    await channel.send(f'Risibot connected to {guild.name}. id: {guild.id}.')
    await fetch_poe_ninja()


@client.command()
async def listcommands(context) -> None:
    """
    Prints available commands.
    """
    await context.send(
        "> **Risibot: available commands.**\n"
        "> **!price [item name]** *Fetches the poe.ninja price of an item.*"
    )


@client.command()
async def price(context, *argv) -> None:
    """
    Prints the poe.ninja price of the item passed in parameter (case-insensitive).

    Example:
    --------
    !price Mirror of Kalandra
    !price mageblood
    """
    if POE_NINJA_DATA is None:
        await context.send('No data available. Please wait a few seconds, or contact @Risitop for more info.')
        return
    target_item = ' '.join(argv)
    item = POE_NINJA_DATA.get(target_item.lower(), None)
    if item is None:
        if target_item.lower() == "chaos orb":
            await context.send(f'> 1 chaos = 1 chaos Poggers')
            return
        await context.send(f'> Item inconnu : {target_item}. Assurez-vous d\'utiliser le nom anglais.')
    else:
        true_name = item["true_name"]
        if not item["is_equipment"]:
            filters = f'%22type%22:%22{true_name}%22'
        else:
            filters = '%22filters%22:{%22type_filters%22:{%22filters%22:{}}},%22name%22:%22' + true_name + '%22'
        query = '{%22query%22:{' + filters + '}}'
        trade_link = f'[Buy/Sell](https://www.pathofexile.com/trade/search/{LEAGUE}?q={query})'
        trade_link = trade_link.replace(" ", "%20")
        price = item["price"]
        if price > .5:
            divine_price = POE_NINJA_DATA['divine orb']['price']
            if price < divine_price/2:
                divine_price_msg = ""
            else:
                divine_price_msg = f" ({(price/divine_price):.1f} divine)"
            await context.send(f'> 📈 {true_name} price: {price:.1f} chaos.{divine_price_msg} ⚖️ {trade_link}')
        else:
            await context.send(f'> 📈 {true_name} price: 1 chaos for {1/price:.1f} ({price:.1f} chaos). ⚖️ {trade_link}')

if __name__ == "__main__":    

    if not RUN_LOCAL: # Connecting the bot
        client.run(TOKEN)