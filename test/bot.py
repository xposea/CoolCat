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
    await verification(event)


async def verification(event: hikari.MemberCreateEvent):
    u = event.user
    await db.checkEmptyOrMia(event.user_id, True)
    if not db.db.child('users').child(f'{event.user_id}').child('verified').get().val():
        await u.send("Are you a Rutgers Student, Alumni, or Guest?"
                     "\nPossible responses: Rutgers Student, Alumni, Guest")
        type = await bot.wait_for(
            hikari.DMMessageCreateEvent,
            timeout=300,
            predicate=lambda e: e.author_id == event.user_id and (e.content == 'Rutgers Student' or e.content == 'Alumni' or e.content == 'Guest'))
        if type.content == 'Guest':
            await u.send("fill")
        else:
            await u.send("Enter your NetID")
        netid = await bot.wait_for(
            hikari.DMMessageCreateEvent,
            # How long to wait for
            timeout=300,
            # The event only matches if this returns True
            predicate=lambda e: (e.author_id == event.user_id and e.content.isalnum() and len(e.content) < 10) or e.content == os.getenv('skipcode')
        )
        # while not netid.content.isalnum() and event.user_id == netid.author_id:
        #     netid = await hikari.DMMessageCreateEvent
        await u.send("You are not verified, please check your email for the verification code")
        if netid.content != os.getenv('skipcode'):
            await db.sendEmail(netid)
        else:
            await u.send(db.db.child('users').child(f'{event.user_id}').child('ver_code').get().val())
        code = await bot.wait_for(
            hikari.DMMessageCreateEvent,
            # How long to wait for
            timeout=300,
            # The event only matches if this returns True
            predicate=lambda e: e.author_id == event.user_id and e.content.isdigit() and len(
                e.content) == 6 and db.checkVercode(int(e.content), e.author_id)
        )
        # while not code.content.isdigit() and 100000 <= int(code.content) <= 999999 and event.user_id == code.author_id \
        #         and db.checkVercode(code):
        #     code = await hikari.DMMessageCreateEvent
        #     await channel.send("That is not the correct code. Please try again.")
        await u.send("You are now verified! Have fun :)")
        db.db.child('users').child(f'{event.user_id}').update({'netID': f'{netid.content}'})
    else:
        await u.send("You are already verified! Have fun :)")

    # print(db.db.child('users').child(f'{event.user_id}').child('verified').get().val(), db.db.child('users').child(f'{event.user_id}').child('ver_code').get().val())
    # if db.child('verified').get().val() is None:
    #     db.child('verifiedcount').set(1)
    #     db.child('verified').child('key0').set('193736005239439360')
    # ver_count = db.child('verifiedcount').get().val()
    # db.update({'verifiedcount': ver_count + 1})
    # db.child('verified').child(f'key{ver_count}').set(f'{event.user_id}')


# @bot.listen()
# async def checkCode(event: hikari.DMMessageCreateEvent) -> None:
#     if not event.is_human:
#         return
#     if not event.content.isdigit() and 100000 <= int(event.content) <= 999999:
#         return
#     if await db.checkVercode(event):
#         await event.author.send("You have been verified.")
#     else:
#         await event.author.send("That is incorrect.")
#
#
# @bot.listen()
# async def sendNetID(event: hikari.DMMessageCreateEvent):
#     if not event.is_human:
#         return
#     if not event.content.isalnum() or len(event.content) > 10:
#         await event.author.send("That is not a valid NetID")
#         return
#     db.db.child('users').child(f'{event.author_id}').child()


@bot.listen()
async def response(event: hikari.DMMessageCreateEvent):
    if not event.is_human:
        return None
    return event


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
