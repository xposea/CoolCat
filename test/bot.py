import os

import dotenv
import hikari
import lightbulb
import Firebase as db


dotenv.load_dotenv()
bot = hikari.GatewayBot(token=os.getenv("token"), intents=hikari.Intents.ALL)


@bot.listen()
async def count(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human:
        return
    await db.place_msg(event)


@bot.listen()
async def join(event: hikari.MemberCreateEvent) -> None:
    if event.user.is_bot:
        return
    await db.verification(event)


@bot.listen()
async def checkCode(event: hikari.DMMessageCreateEvent) -> None:
    if not event.is_human:
        return
    if not event.content.isdigit() and 100000 <= int(event.content) <= 999999:
        return
    if await db.checkVercode(event):
        await event.author.send("You have been verified.")
    else:
        await event.author.send("That is incorrect.")

@bot.command()
# Adds cooldown between per verification requests, per user.
@lightbulb.add_cooldown(30, 1, lightbulb.UserBucket)
@lightbulb.command("Verification", "Verify your netID email")
@lightbulb.implements(lightbulb.SlashCommand) 
async def email(test: hikari.GuildMessageCreateEvent):
    channelID = test.get_channel
    await test.author.send('Hello, please enter your Rutgers NetID.')
    
    await channelID.send("Please check your DMs!")
    


@bot.listen()
async def botJoinServer(event: hikari.GuildJoinEvent) -> None:
    event.guild.fetch_public_updates_channel()


bot.run()

