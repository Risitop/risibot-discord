import asyncio
import discord
from discord.ext import commands

import risibot.constants as constants
import risibot.data_manager as dm
import risibot.private as private
import risibot.util as util

LEAGUE = constants.LEAGUE
RUN_LOCAL = constants.LOCAL

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


@client.command()
async def listcommands(context: commands.Context) -> None:
    """
    Prints available commands.
    """
    if RUN_LOCAL: return
    await context.send(
        "> **Risibot: available commands.**\n"
        "> **!price [item name]** *Fetches the poe.ninja price of an item.*\n"
        "> **[item]** *Detects any [item] in messages and links the poewiki page.*\n"
    )


@client.command()
async def price(context: commands.Context, *argv) -> None:
    """
    Prints the poe.ninja price of the item passed in parameter (case-insensitive).

    Example:
    --------
    !price Mirror of Kalandra
    !price mageblood
    """
    
    target_item = ' '.join(argv)
    candidates = dm.get_poe_ninja_data(target_item)

    if candidates is None: # No data loaded
        if RUN_LOCAL:
            print('No data available. Please wait a few seconds, or contact @Risitop for more info.')
        else:
            await context.send('No data available. Please wait a few seconds, or contact @Risitop for more info.')
        return

    if len(candidates) == 0: # No relevant item found
        if RUN_LOCAL:
            print(f'> Aucun item trouvé : {target_item}. Assurez-vous d\'utiliser le nom anglais.')
        else:
            await context.send(f'> Aucun item trouvé : {target_item}. Assurez-vous d\'utiliser le nom anglais.')
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
            divine_price = dm.get_divine_price()
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


@client.command()
@commands.has_any_role('Modérateur', 'Administrateur')
async def clear(context: commands.Context, n_remove) -> None:
    # Syntax: !clear {n}
    # Removes the $n last messages in the calling channel
    n_remove = int(n_remove) + 1
    await context.channel.purge(limit=n_remove)


async def search_poewiki(message: discord.Message) -> None:
    # Search for [[s]] pattern: [[s]] -> s
    text = message.content
    occurences = util.extract_pattern_between(text, '[[', ']]')
    
    output = ""
    for target in occurences:
        if not len(target): continue
        words = target.split(' ')
        for i, w in enumerate(words):
            if i == 0 or w not in ['of', 'in', 'the', 'on', 'in', 'a']:
                words[i] = w.title()
        target = '_'.join(words)
        output += f'https://www.poewiki.net/wiki/{target}\n'

    if not len(output): return

    if RUN_LOCAL:
        print(output)
    else:
        context = await client.get_context(message)
        await context.send(output)


@client.event
async def on_message(message: discord.Message):
    if message.author.bot: return
    await search_poewiki(message)
    await client.process_commands(message)