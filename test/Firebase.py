import random

import hikari
import pyrebase
import json


config = {
    "apiKey": "AIzaSyDgNsYG2aGG-RJGDt_bz0MkxeGX25fHork",
    "authDomain": "pythonbotdb-cad4c.firebaseapp.com",
    "databaseURL": "https://pythonbotdb-cad4c-default-rtdb.firebaseio.com",
    "projectId": "pythonbotdb-cad4c",
    "storageBucket": "pythonbotdb-cad4c.appspot.com",
    "messagingSenderId": "260373616410",
    "appId": "1:260373616410:web:193940940f8812a4edbea3",
    "measurementId": "G-R72ZQSCHDW",
    "serviceAccount": "pythonbotdb-cad4c-firebase-adminsdk-ulnp0-4a7838cc77.json"
}

db = pyrebase.initialize_app(config).database()

async def checkEmptyOrMia(author_id: int, join: bool) -> bool:
    if db.child('users').get().val() is None or f'{author_id}' not in db.child('users').get().val():
        db.child('users').child(f'{author_id}').set({
            'msg_count': 0,
            'verified': False,
            'ver_code': random.randrange(100000, 999999),
            'netID': 'unknown'
        })
        return False
    return True

async def sendEmail(event: hikari.DMMessageCreateEvent):
    from email.message import EmailMessage
    import ssl
    import smtplib

    # Declare var, FIX NETID/ver_code input parsing
    email_sender = 'rkundoze@gmail.com'
    email_password = 'FETCH PASSWORD FROM SECURED SOURCE'
    email_receiver = netID + '@scarletmail.rutgers.edu'
    ver_code = db.child('users').child(f'{event.user_id}').child('ver_code').get().val()
    netID = db.child('users').child(f'{event.user_id}').child('netID').get().val()

    subject = 'Your CoolCat Verification'
    body = """
    Here is your CoolCat verification code:

    {ver_code}

    Please send it back to the bot through its DM!
    """.format(ver_code = "ver_code")

    # Email formatting, em is the object
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Establish SSL security
    context = ssl.create_default_context()

    # Send email using SSL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:

        smtp.login(email_sender, email_password)

        smtp.sendmail(email_sender, email_receiver, em.as_string())
# async def email() -> bool:

async def checkVercode(event: hikari.DMMessageCreateEvent) -> bool:
    if db.child('users').child(f'{event.author_id}').child('ver_code').get().val() == int(event.content):
        db.child('users').child(f'{event.author_id}').update({'verified': True})
        return True
    return False


async def verification(event: hikari.MemberCreateEvent):
    await checkEmptyOrMia(event.user_id, True)
    if not db.child('users').child(f'{event.user_id}').child('verified').get().val():
        channel = await event.user.fetch_dm_channel()
        await channel.send("You are not verified, please check your email for the verification code")

    print(db.child('users').child(f'{event.user_id}').child('verified').get().val(), db.child('users').child(f'{event.user_id}').child('ver_code').get().val())
    # if db.child('verified').get().val() is None:
    #     db.child('verifiedcount').set(1)
    #     db.child('verified').child('key0').set('193736005239439360')
    # ver_count = db.child('verifiedcount').get().val()
    # db.update({'verifiedcount': ver_count + 1})
    # db.child('verified').child(f'key{ver_count}').set(f'{event.user_id}')


async def place_msg(event: hikari.GuildMessageCreateEvent):
    if not event.is_human:
        return
    await checkEmptyOrMia(event.author_id, False)
    msg_count = db.child('users').child(f'{event.author_id}').child('msg_count').get().val()
    db.child('users').child(f'{event.author_id}').update({'msg_count': msg_count + 1})
    db.child('users').child(f'{event.author_id}').child('msgs').child(f'key{msg_count}').set(event.content)


