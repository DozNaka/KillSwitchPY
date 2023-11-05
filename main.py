# Import
import discord, threading
from discord import app_commands
from javascript import require, On
# JS
mineflayer = require('mineflayer')

# Config
serverIP = "" # Put the target minecraft server here
port = 25565
version = "1.8"
amount = 10
# -----
playerList = [] # Do not edit

# Bot config
TOKEN = "" # Put your Discord bot token here
GUILD_ID = 746147163163328613 # Replace with your server id
CHANNEL_ID = 746147164090269768 # Replace with your channel id
# -----

MY_GUILD = discord.Object(id=GUILD_ID)


class MyClient(discord.Client):

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        #self.tree.clear_commands(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'[KILLSWITCH] Ready!\nLogged in as {client.user} (ID: {client.user.id})')


@client.tree.command()
@app_commands.describe(username='Username of the player you want to lobbylock')
async def lobbylock(interaction: discord.Interaction, username: str):
    """Lobby locks a player"""
    user = username
    if (len(playerList) > amount):
        await interaction.response.send_message(f'You have exceeded the limit of {amount} players.')
    elif (user in playerList):
        await interaction.response.send_message(f'{user} already exists!')
    else:
        playerList.append(user)
        initBot(user)
        await interaction.response.send_message(f'Now lobby locking `{username}`')


@client.tree.command()
@app_commands.describe(username='Username of the player you want to unlobbylock')
async def unlobbylock(interaction: discord.Interaction, username: str):
    """Unlobby locks a player"""
    user = username
    if (user in playerList):
        playerList.pop(playerList.index(user))
        await interaction.response.send_message(f'I have stopped lobby locking `{username}`')
    else:
        await interaction.response.send_message(f'{user} doesnt exist!')


@client.tree.command()
async def lobbylocklist(interaction: discord.Interaction):
    """List of people who are currently lobbylocked"""
    await interaction.response.send_message(f'List [{len(playerList)}]: {",".join(playerList)}')


# the funni begins
def initBot(user):
    # Check if the player is in the list
    if (user in playerList):
        bot = mineflayer.createBot({ 
            'host': serverIP,
            'port': port, 
            'username': user, 
            'version': version,
            'hideErrors': True
        })

        # Alert console that the player has logged on
        @On(bot, 'login')
        def onJoin(this):
            print(f'[KILLSWITCH] {user} has logged in.')
            # This is a part of the bypass, if you want to use this and change the time it waits before disconnecting, change "110" to whatever you like (in seconds)
            # If you don't want the bypass then comment out the t or remove it entirely
            t = threading.Timer(110.0, bot.quit)
            t.start()

        # Attempt to reconnect the player when they are disconnected
        @On(bot, 'end')
        def onLeave(this, reason):
            print(f'[KILLSWITCH] {user} has disconnected. Reconnecting...')
            initBot(user)
    else:
        # Alert console that the player is no longer being lobby locked
        print(f'[KILLSWITCH] {user} is no longer being lobbylocked.')


client.run(TOKEN, log_handler=None)