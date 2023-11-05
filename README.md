# <p align="center">Killswitch</p>
<p align="center">A discord bot to manage "lobby locking" accounts.</p>

## How it works
Killswitch works by connecting the chosen player to a certain server of your choice, then staying there. It doesn't login or anything. It also auto reconnects if it happens to get kicked.

Killswitch also has a bypass for servers who may have patched this in a way, its done by disconnecting manually after a certain amount of time instead of waiting to be kicked.
## How to setup / use
To use Killswitch, you will need to:

 1. Make a Discord bot (if you havent already) - https://discord.com/developers/
 2. Download [Node.JS => 18](https://nodejs.org/) and [Python3](https://www.python.org/downloads/) (if you havent already)
 3. Download required imports by doing `pip install -r requirements.txt` (you will need discord.py and javascript)
 4. Replace `GUILD_ID` and `TOKEN` with your own
 5. Set your `serverIP`, `version` and `amount` (amount is the amount of people you can lobby lock from 1 ip at a time)
 6. Run `python main.py`