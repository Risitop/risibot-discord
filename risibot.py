import os
from dotenv import load_dotenv

import asyncio
import discord
from discord.ext import commands
import util

RUN_LOCAL = False
POE_NINJA_DATA = None
LEAGUE = "Affliction"

if not RUN_LOCAL:
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(
    command_prefix="!",
    intents=intents
)
        

@client.event
async def on_ready() -> None:
    """
    Sends an initialization message to the special bot channel.
    """
    global POE_NINJA_DATA
    for guild in client.guilds:
        if guild.name == GUILD: break
    channel = client.get_channel(1204886119032823878)
    await channel.send(f'Risibot connected to {guild.name}. id: {guild.id}.')
    while True:
        POE_NINJA_DATA = await util.fetch_poe_ninja()
        await asyncio.sleep(900)


@client.command()
async def listcommands(context) -> None:
    """
    Prints available commands.
    """
    if RUN_LOCAL: return
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
        if RUN_LOCAL:
            print('No data available. Please wait a few seconds, or contact @Risitop for more info.')
            return
        await context.send('No data available. Please wait a few seconds, or contact @Risitop for more info.')
        return
    
    # Gathering at most 5 query candidates
    target_item = ' '.join(argv)
    item = POE_NINJA_DATA.get(target_item.lower(), None)
    if item is None: # If no exact match, take all candidates
        candidates = [(k, v) for (k, v) in POE_NINJA_DATA.items() if util.fuzzy(target_item.lower(), k)]
    else:
        candidates = [(target_item, item)]
    candidates = sorted(candidates, key=lambda t: t[1]['price'])[-5:]

    # No relevant item found
    if item is None and len(candidates) == 0:
        if RUN_LOCAL:
            print(f'Unkown item: {target_item}')
        else:
            await context.send(f'> Item inconnu : {target_item}. Assurez-vous d\'utiliser le nom anglais.')
        return

    # We print the results
    msg = ""
    for target_item, item in candidates:
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
            msg += f'> 📈 {true_name} price: {price:.1f} chaos.{divine_price_msg} ⚖️ {trade_link}\n'
        else:
            msg += f'> 📈 {true_name} price: 1 chaos for {1/price:.1f} ({price:.1f} chaos). ⚖️ {trade_link}\n'

    if RUN_LOCAL:
        print(msg)
    else:
        message = await context.send(msg)
        await message.edit(suppress=True)


@client.event
async def on_message(message):
    if message.author.bot: return
    text = message.content
    if text.startswith('!price'):
        context = await client.get_context(message)
        await price(context, *text.split(' ')[1:])
        return
    if not "[" in text or "]" not in text:
        return
    p0 = text.find("[")
    p1 = text.find("]")
    if p0 > p1: return
    target = text[p0+1:p1]
    words = target.split(' ')
    for i, w in enumerate(words):
        if i > 0 and w not in ['of', 'in', 'the', 'on', 'in', 'a']:
            words[i] = w.title()
    target = '_'.join(words)

    if RUN_LOCAL:
        print(f'https://www.poewiki.net/wiki/{target}')
    else:
        context = await client.get_context(message)
        await context.send(f'> https://www.poewiki.net/wiki/{target}')
        

async def main():
    global POE_NINJA_DATA
    POE_NINJA_DATA = await util.fetch_poe_ninja()
    await on_message("un [Mirror]")

if __name__ == "__main__":

    if not RUN_LOCAL: # Connecting the bot
        client.run(TOKEN)
    else:
        asyncio.run(main())