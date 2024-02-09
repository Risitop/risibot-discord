import os
import aiohttp
import pickle
import time
import json

from dotenv import load_dotenv

import risibot.util as util

load_dotenv()
POE_NINJA_DATA = None
LEAGUE = os.getenv('LEAGUE')
DATA_FOLDER_PATH = os.sep.join(__file__.split(os.sep)[:-3] + ['data'])
NINJA_DATA_PATH = os.path.join(DATA_FOLDER_PATH, 'ninja_cache.dat')
FETCH_KEY = '_fetch_date'

def get_divine_price() -> float:
    # Returns the chaos price of one divine orb
    divprice = get_poe_ninja_data('divine orb')
    if not divprice: return -1.0
    return divprice[0][1]['price']

def get_poe_ninja_data(query: str, max_items: int = 5) -> list:
    # Returns a list of poe.ninja data elements corresponding to the query
    # Format: [(name1, item1), (name2, item2), ...]
    # > name: str
    # > item: {'price': float, 'true_name': str, 'is_equipment': bool}
    # Returns None if no data is loaded

    if POE_NINJA_DATA is None: return None
    
    # Gathering at most 5 query candidates
    item = POE_NINJA_DATA.get(query.lower(), None)
    if item is None: # If no exact match, fuzzy search
        candidates = [(k, v) for (k, v) in POE_NINJA_DATA.items() if util.fuzzy_match(query.lower(), k)]
    else:
        candidates = [(query, item)]

    return list(sorted(candidates, key=lambda t: t[1]['price'])[-max_items:])

async def fetch_poe_ninja() -> bool:
    # Loads data from poe.ninja (at most once every 15min) and caches it locally.
    # HTTP requests are performed asynchronously
    # Returns if data has been fetched

    global POE_NINJA_DATA

    # Fetches poe.ninja prices, and caches them into a local file
    api_addresses = {
        'Currency':	            f'https://poe.ninja/api/data/currencyoverview?league={LEAGUE}&type=Currency',
        'Fragment':	            f'https://poe.ninja/api/data/currencyoverview?league={LEAGUE}&type=Fragment',
        'Oils':	                f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Oil',
        'Scarabs':	            f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Scarab',
        'Fossils':	            f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Fossil',
        'Resonators':	        f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Resonator',
        'Essence':	            f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Essence',
        'Divination Cards':	    f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=DivinationCard',
        'Skill Gems':	        f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=SkillGem',
        'Unique Maps':	        f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueMap',
        'Unique Jewels':	    f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueJewel',
        'Unique Flasks':	    f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueFlask',
        'Unique Weapons':	    f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueWeapon',
        'Unique Armours':	    f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueArmour',
        'Unique Accessories':	f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=UniqueAccessory',
        'Beasts':	            f'https://poe.ninja/api/data/itemoverview?league={LEAGUE}&type=Beast'
    }

    # Checking if cache is up to date
    if not os.path.isdir(DATA_FOLDER_PATH): os.mkdir(DATA_FOLDER_PATH)
    if os.path.isfile(NINJA_DATA_PATH):
        with open(NINJA_DATA_PATH, 'rb') as f:
            data = pickle.load(f)
            if time.time() - data[FETCH_KEY] < 900: # 15 min
                print('Data is up to date. Nothing to fetch.')
                del data[FETCH_KEY]
                POE_NINJA_DATA = data
                return False

    # Fetching poe.ninja
    container = {FETCH_KEY: time.time()}
    async with aiohttp.ClientSession() as session:
        for key, addr in api_addresses.items():
            print(f'Fetching {key}...')
            async with session.get(addr) as response:
                if response.status != 200:
                    print(f'{addr} -> ERROR {response.status}')
                    continue
                print(f'Response received from {addr}.')
                text = await response.text()
                data = json.loads(text)
                if 'lines' not in data: 
                    print('Nothing to fetch.')
                    continue
                for elem in data['lines']:
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
                    container[name.lower()] = {'price': price, 'true_name': name, 'is_equipment': 'Unique' in key}

    # Updating the cache
    if os.path.isfile(NINJA_DATA_PATH):
        os.remove(NINJA_DATA_PATH)
    with open(NINJA_DATA_PATH, 'wb') as f:
        pickle.dump(container, f)
    del container[FETCH_KEY]
    POE_NINJA_DATA = container
    return True