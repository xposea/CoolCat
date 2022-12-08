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


def checkEmptyOrMia(author_id: int, join: bool) -> bool:
    if db.get().val() is None or f'{author_id}' not in db.child('users').get().val():
        db.child('users').child(f'{author_id}').set({
            'msg_count': 0,
        })
        return True
    return False

# async def email() -> bool:

async def verification(event: hikari.MemberCreateEvent):
    if db.child('verified').get().val() is None:
        db.child('verifiedcount').set(1)
        db.child('verified').child('key0').set({'193736005239439360'})
    db.update({'verifiedcount': ver_count + 1})
    ver_count = db.child('verifiedcount').get().val()
    db.child('verified').child(f'key{ver_count}').set(f'{event.user_id}')


async def place_msg(event: hikari.GuildMessageCreateEvent):
    if not event.is_human:
        return
    checkEmptyOrMia(event.author_id, False)
    msg_count = db.child('users').child(f'{event.author_id}').child('msg_count').get().val()
    db.child('users').child(f'{event.author_id}').update({'msg_count': msg_count + 1})
    db.child('users').child(f'{event.author_id}').child('msgs').child(f'key{msg_count + 1}').set(event.content)
