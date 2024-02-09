import asyncio

import risibot.data_manager as dm
import risibot.risibot as bot

async def main():
    await dm.fetch_poe_ninja()
    await bot.price(None, "chs", 'rb')

if __name__ == "__main__":

    if not bot.RUN_LOCAL: # Connecting the bot
        bot.client.run(bot.TOKEN)
    else:
        asyncio.run(main())