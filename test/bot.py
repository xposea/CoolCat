import os

import dotenv
import hikari
import Firebase as db


dotenv.load_dotenv()
bot = hikari.GatewayBot(token=os.getenv("token"), intents=hikari.Intents.ALL)


@bot.listen()
async def count(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human:
        return
    await db.place_msg(event)


bot.run()

