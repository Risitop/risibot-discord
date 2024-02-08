import os
import aiohttp
import pickle
import time
import json
import dotenv

LEAGUE = os.getenv("LEAGUE")

async def fetch_poe_ninja():

    # Fetches poe.ninja prices, and caches them into a local file
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
                print('Data up to date. Nothing to fetch.')
                del data['_fetch_date']
                return data
            
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
    del container['_fetch_date']
    return container


def fuzzy(query, target):
    iq, it = 0, 0
    while iq < len(query) and it < len(target):
        iq += query[iq] == target[it]
        it += 1
    return iq == len(query)