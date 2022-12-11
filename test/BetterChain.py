import hikari
import pyrebase
import math

# Initialize Firebase
config = {
    "apiKey": "YOUR_API_KEY_HERE",
    "authDomain": "YOUR_AUTH_DOMAIN_HERE",
    "databaseURL": "YOUR_DATABASE_URL_HERE",
    "projectId": "YOUR_PROJECT_ID_HERE",
    "storageBucket": "YOUR_STORAGE_BUCKET_HERE",
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Create a new Discord client
bot = hikari.gatewaybot()

# Define a command that the bot will respond to
@bot.command()
async def hello(ctx):
    # Respond to the command with a message
    await ctx.send("Hello, World!")

# Keep track of all users who join the server
@bot.event
async def on_member_join(event: hikari.MemberCreateEvent):
    # Add the user's Discord ID to the database
    db.child('guilds').child(event.guild_id).child("users").push({"discord_id": event.user_id})

async def is_duplicate(anylist):
    if type(anylist) != 'list':
        return("Error. Passed parameter is Not a list")
    if len(anylist) != len(set(anylist)):
        return True
    else:
        return False

# Function to keep track of message chains
async def track_message_chain(event: hikari.GuildMessageCreateEvent):
    # Get the guild ID, channel ID, user ID and message content
    guild_id = event.guild_id
    channel_id = event.channel_id
    author = event.author_id
    content = event.message_id

    # Declare counter
    counter = 0

    # If db does not have preivous meesage recorded AND no user is in the chain, record it to db
    if db.child('guilds').child(guild_id).child('channels').child(channel_id).child('previous_message') is None \
         and len(db.child('guilds').child(guild_id).child('channels').child(channel_id).child('usersInChain')) == 0: 

        await db.child('guilds').child(guild_id).child('channels').child(channel_id).child('usersInChain').push(author)
        await db.child('guilds').child(guild_id).child('channels').child(channel_id).child('previous_message').set(content)
        counter += 1
        
    # CASE COVERING THE START OF A CHAIN.
    # If the current content matches the previous message, and the user who sent the message is in NOT the chain user list, start the chain if the counter is <= 2.
    elif db.child('guilds').child(guild_id).child('channels').child(channel_id).child('previous_message') == content \
        and author not in db.child('guilds').child(guild_id).child('channels').child(channel_id).child('usersInChain') and \
        counter <= 2 :

        await db.child('guilds').child(guild_id).child('channels').child(channel_id).child('usersInChain').push(author)

        # Add number 1 emoji to previous message
        await db.child('guilds').child(guild_id).child('channels').child(channel_id).child('previous_message').add_reaction(f"\U003{counter - 1}")

        # Add number 2 moji to current message
        await db.child('guilds').child(guild_id).child('channels').child(channel_id).child(content).add_reaction(f"\U003{counter}")

    # CASE COVERING CONTINUATION OF A CHAIN SIZE LESS THAN 10.
    # If the current content matches the previous message, and the user who sent the message is in NOT the chain user list, add a reaction if counter is under two digits.
    elif db.child('guilds').child(guild_id).child('channels').child(channel_id).child('previous_message') == content \
        and author not in db.child('guilds').child(guild_id).child('channels').child(channel_id).child('usersInChain') and \
            2 < counter < 10:

        await db.child('guilds').child(guild_id).child('channels').child(channel_id).child('usersInChain').push(author)
        await db.child('guilds').child(guild_id).child('channels').child(channel_id).child(content).add_reaction(f"\U003{counter}")
        counter += 1


    # CASE COVERING CONTINUATION OF A CHAIN SIZE GREATER THAN 10
    # If the current content matches the previous message, and the user who sent the message is in NOT the chain user list
    # Split the digits of the chain counter into isolated number per digit, and add reaction of those respective digits in order.
    elif db.child('guilds').child(guild_id).child('channels').child(channel_id).child('previous_message') == content \
        and author not in db.child('guilds').child(guild_id).child('channels').child(channel_id).child('usersInChain') and \
            counter >= 10:

        await db.child('guilds').child(guild_id).child('channels').child(channel_id).child('usersInChain').push(author)

        digits = [(counter//(10**i))%10 for i in range(math.ceil(math.log(counter, 10)), -1, -1)][bool(math.log(counter,10)%1):]

        if is_duplicate(digits):
            
            await db.child('guilds').child(guild_id).child('channels').child(channel_id).child(content).add_reaction(f"\U0001F522")
            counter += 1
        else:
            for x in digits:
                await db.child('guilds').child(guild_id).child('channels').child(channel_id).child(content).add_reaction(f"\U003{x}")
                counter += 1

    # BREAK THE CHAIN, RESET ALL COUNTERS!!
    else: 
        counter = 0
        
        await db.child('guilds').child(guild_id).child('channels').child(channel_id).child('usersInChain').set([])
        
        await db.child('guilds').child(guild_id).child('channels').child(channel_id).child(content).add_reaction(f"\U0001F621")
    


        

    # Check if the current message is the same as the previous message
    previous_message = db.child("channels").child(channel_id).child("previous_message").get()
    if content == previous_message:
        # If it is, increment the message chain count
        message_chain_count = db.child("channels").child(channel_id).child("message_chain_count").get()
        message_chain_count += 1
        db.child("channels").child(channel_id).update({"message_chain_count": message_chain_count})
    else:
        # If it is not, reset the message chain count
        db.child("channels").child(channel_id).update({"message_chain_count": 0})

    # Update the previous message
    db.child("channels").child(channel_id).update({"previous_message": content})

#