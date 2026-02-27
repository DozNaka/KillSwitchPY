# Python Port of xlzxq's Killswitch by Doz
# Perharps the most engineered lobby locker ever made like seriously, 
# it just stops some poor child from logining into a cracked server.
# Import
import discord, asyncio, re, json, os
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
DATA_FILE = "players_lobbed.json"

def load_players() -> list:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_players(players) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(players, f, indent=4)

playerList = load_players()

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

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=MY_GUILD)
        #self.tree.clear_commands(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready() -> None:
    print(f'[KILLSWITCH] Ready!\nLogged in as {client.user}')
    
    # Resume locking for players already in the JSON file
    print(f"Resuming sessions for: {', '.join(playerList) if playerList else 'None'}")
    for user in playerList:
        # Start the manager for each existing player
        if user not in active_tasks:
            active_tasks[user] = asyncio.create_task(bot_manager(user))


@client.tree.command()
@app_commands.describe(username='Username of the player you want to lobbylock')
async def lobbylock(interaction: discord.Interaction, username: str) -> None:
    """Lobby locks a player"""
    if len(playerList) >= amount:
        await interaction.response.send_message(f'You have exceeded the limit of {amount} players.')
    elif username in playerList:
        await interaction.response.send_message(f'`{username}` already exists!')
    else:
        playerList.append(username)
        save_players(playerList)
        
        active_tasks[username] = asyncio.create_task(bot_manager(username))
        
        await interaction.response.send_message(f'Now lobby locking `{username}`')


@client.tree.command()
@app_commands.describe(username='Username of the player you want to unlobbylock')
async def unlobbylock(interaction: discord.Interaction, username: str) -> None:
    """Unlobby locks a player"""
    if username in playerList:
        playerList.remove(username)
        save_players(playerList)
        
        if username in active_tasks:
            active_tasks[username].cancel()
            del active_tasks[username]
            
        await interaction.response.send_message(f'I have stopped lobby locking `{username}`')
    else:
        await interaction.response.send_message(f'`{username}` doesn\'t exist!')


@client.tree.command()
async def lobbylocklist(interaction: discord.Interaction) -> None:
    """List of people who are currently lobbylocked"""
    await interaction.response.send_message(f'List [{len(playerList)}]: `{",".join(playerList)}`')

active_tasks = {}
async def bot_manager(user) -> None:
    """Le funni"""
    try:
        while user in playerList:
            print(f'[KILLSWITCH] Starting session for {user}...')
            
            # Create the bot, duh
            bot = mineflayer.createBot({ 
                'host': serverIP,
                'port': port, 
                'username': user, 
                'version': version,
                'hideErrors': True # Shut up
            })
            # TODO: Add proxy? issue with that is that it adds delay. Best host it on a VPS.

            # Use a Future to wait for the bot to 'end'
            stop_event = asyncio.Event()

            @On(bot, 'login')
            def onJoin(this):
                print(f'[KILLSWITCH] {user} logged in.')
                asyncio.run_coroutine_threadsafe(
                    delayed_quit(bot, 110), client.loop
                )
                # Quit after some time to prevent triggering anti brute force. Change accordingly

            @On(bot, 'messagestr')
            def onChat(this, message, *rest):
                pass
                # Do anything you want here idk

            @On(bot, 'kicked')
            def onKick(this, reason, loggedIn):
                print(f'[KILLSWITCH] {user} was kicked: {reason}')
                # This is only needed for kick reasons regardless of session end.

            @On(bot, 'end')
            def onLeave(this, reason):
                print(f'[KILLSWITCH] {user} session ended: {reason}')
                # CLEANUP: Stop all listeners for this specific bot object
                bot.removeAllListeners()
                
                # Tell the manager: "This bot is done, start the next loop!"
                client.loop.call_soon_threadsafe(stop_event.set)

            # Wait for the bot to finish before looping
            try:
                await stop_event.wait()
            except asyncio.CancelledError:
                # When /unlobbylock is called, cancel the task. This will raise a CancelledError here.
                bot.quit()  # Attempt to quit the bot gracefully
                print(f'[KILLSWITCH] Forcefully stopped session for {user}')
                raise
            
            # Small delay to let GC work
            await asyncio.sleep(0.05)
            
    except asyncio.CancelledError:
        pass

async def delayed_quit(bot, delay) -> None:
    await asyncio.sleep(delay)
    try:
        bot.quit()
    except:
        pass

if __name__ == "__main__":
    try:
        client.run(TOKEN, log_handler=None)
    except KeyboardInterrupt:
        print('[KILLSWITCH] Exiting...')
        for task in active_tasks.values():
            task.cancel()
