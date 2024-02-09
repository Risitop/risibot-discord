import asyncio

import risibot.risibot as bot

async def main():
    pass

if __name__ == "__main__":

    if not bot.RUN_LOCAL: # Connecting the bot
        bot.client.run(bot.TOKEN)
    else:
        asyncio.run(main())