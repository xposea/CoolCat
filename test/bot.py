import asyncio
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


@bot.listen()
async def join(event: hikari.MemberCreateEvent) -> None:
    if event.user.is_bot:
        return
    await verification(event.user)


async def verification(u: hikari.User):
    await db.checkEmptyOrMia(u.id, True)
    if not db.db.child('users').child(f'{u.id}').child('verified').get().val():
        await u.send("Are you a Rutgers Student, Alumni, or Guest?"
                     "\nPossible responses: Rutgers Student, Alumni, Guest")
        try:
            AccType = await bot.wait_for(
                hikari.DMMessageCreateEvent,
                timeout=300,
                predicate=lambda e: e.author_id == u.id and (
                            e.content == 'Rutgers Student' or e.content == 'Alumni' or e.content == 'Guest'))
            if AccType.content == 'Guest':
                await u.send("fill")
            else:
                await u.send("Enter your NetID")
            netid = await bot.wait_for(
                hikari.DMMessageCreateEvent,
                # How long to wait for
                timeout=300,
                # The event only matches if this returns True
                predicate=lambda e: ((db.db.child('netIDs').get().val() is None or e.content.lower() not in db.db.child('netIDs').
                                      get().val().values()) and e.author_id == u.id and e.content.isalnum() and
                                     len(e.content) < 10) or e.content == os.getenv('skipcode')
            )

            await u.send("You are not verified, please check your email for the verification code")
            if netid.content != os.getenv('skipcode'):
                await db.sendEmail(netid)
            else:
                await u.send(db.db.child('users').child(f'{u.id}').child('ver_code').get().val())
            await bot.wait_for(
                hikari.DMMessageCreateEvent,
                # How long to wait for
                timeout=300,
                # The event only matches if this returns True
                predicate=lambda e: e.author_id == u.id and e.content.isdigit() and len(
                    e.content) == 6 and db.checkVercode(int(e.content), e.author_id)
            )
            await u.send("You are now verified! Have fun :)")
            db.db.child('users').child(f'{u.id}').update({'netID': f'{netid.content.lower()}'})
            db.db.child('netIDs').push(f'{netid.content.lower()}')
        except asyncio.TimeoutError:
            await u.send("Your session has timed out. Please respond \"Retry\" to retry the verification process.")
    else:
        await u.send("You are already verified! Have fun :)")


@bot.listen()
async def retryVerification(event: hikari.DMMessageCreateEvent):
    if not event.is_human:
        return None
    if event.content.lower() == "retry":
        await verification(event.author)


# @bot.listen()
# async def botJoinServer(event: hikari.GuildJoinEvent) -> None:
#     overwrite = hikari.PermissionOverwrite(
#         id=event.guild_id,
#         type=hikari.PermissionOverwriteType.MEMBER,
#         allow=(
#             hikari.Permissions.NONE
#         ),
#     )
#     channel = await event.guild.create_news_channel(name="CoolCatConfig",
#                                                     position=0,
#                                                     topic="This channel with both serve as config and updates for the "
#                                                           "CoolCat Bot ",
#                                                     permission_overwrites=overwrite)
#     db.db.child('guilds').child(f'{event.guild_id}').child('updates').set(f'{channel.id}')
#     await channel.send("test")


bot.run()
