import asyncio
import discord
import re

from discord.ext import commands

import risibot.constants as constants
import risibot.data_manager as dm
import risibot.util as util

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(
    command_prefix="!",
    intents=intents
)


async def check_links(message: discord.Message) -> None:
    # Displays a warning message if links 
    authorized_links = dm.get_whitelist_links()
    words = message.content.split(' ')
    for word in words:
        if 'http://' not in word and 'https://' not in word: continue
        if (start := word.find('http://')) == -1: start = word.find('https://')
        link = '.'.join(''.join(word[start:].split('//')[1]).split('/')[0].split('.')[-2:])
        if link not in authorized_links:
            if constants.LOCAL:
                print(f'⚠️Attention : Le lien {link} n\'est pas reconnu comme sûr. Prudence.⚠️')
            else:
                context = await client.get_context(message)
                await context.send(f'⚠️Attention : Le lien {link} n\'est pas reconnu comme sûr. Prudence.⚠️')


@client.command()
@commands.has_any_role('Modérateur', 'Administrateur')
async def clear(context: commands.Context, n_remove) -> None:
    # Syntax: !clear {n}
    # Removes the $n last messages in the calling channel
    n_remove = int(n_remove) + 1
    await context.channel.purge(limit=n_remove)


@client.command()
async def listcommands(context: commands.Context) -> None:
    """
    Prints available commands.
    """
    if constants.LOCAL: return
    channel = await context.message.author.create_dm()
    await channel.send(
        "> **Risibot: available commands.**\n"
        "> **!price [item name]** *Fetches the poe.ninja price of an item.*\n"
        "> **[item]** *Detects any [item] in messages and links the poewiki page.*\n"
    )
    resp_roles = [discord.utils.get(context.guild.roles, name=r) for r in ("Administrateur", "Modérateur")]
    if any(r in resp_roles for r in context.message.author.roles):
        await channel.send(
            "> **Risibot: Mod-only commands.**\n"
            "> **!clear [n]** *Removes the $n last messages in the channel.*\n"
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
        if constants.LOCAL:
            print('No data available. Please wait a few seconds, or contact @Risitop for help.')
        else:
            await context.send('No data available. Please wait a few seconds, or contact @Risitop for help.')
        return

    if len(candidates) == 0: # No relevant item found
        if constants.LOCAL:
            print(f'> No item found : {target_item}. Please ensure you type the english name.')
        else:
            await context.send(f'> No item found : {target_item}. Please ensure you type the english name.')
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
        trade_link = f'[Buy/Sell](https://www.pathofexile.com/trade/search/{constants.LEAGUE}?q={query})'
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

    if constants.LOCAL:
        print(msg)
    else:
        message = await context.send(msg)
        await asyncio.sleep(0.5)
        await message.edit(suppress=True)


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

    if constants.LOCAL:
        print(output)
    else:
        context = await client.get_context(message)
        await context.send(output)


@client.command()
@commands.has_any_role('Modérateur', 'Administrateur')
async def whitelist_add(context: commands.Context, link: str) -> None:
    dm.add_whitelist_link(link)
    if constants.LOCAL:
        print(f'✅ Link {link} successfully added to the whitelist.')
    else:
        await context.send(f'✅ Link {link} successfully added to the whitelist.')


@client.command()
@commands.has_any_role('Modérateur', 'Administrateur')
async def whitelist_remove(context: commands.Context, link: str) -> None:
    if dm.remove_whitelist_link(link):
        if constants.LOCAL:
            print(f'✅ Link {link} successfully added to the whitelist.')
        else:
            await context.send(f'✅ Link {link} successfully added to the whitelist.')
    else:
        if constants.LOCAL:
            print(f'❌ Link {link} not found.')
        else:
            await context.send(f'❌ Link {link} not found.')

@client.command()
@commands.has_any_role('Modérateur', 'Administrateur')
async def whitelist(context: commands.Context) -> None:
    msg = "\n".join(f'> {link}' for link in sorted(dm.get_whitelist_links()))
    if constants.LOCAL:
        print(msg)
    else:
        await context.send(msg)