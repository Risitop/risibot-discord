import asyncio

import risibot.constants as constants
import risibot.private as private
import risibot.risibot as bot

async def main():
    pass

if __name__ == "__main__":

    if not constants.LOCAL: # Connecting the bot
        bot.client.run(private.DISCORD_TOKEN)
    else:
        asyncio.run(main())