import discord
from discord.ext import commands
from flask import Flask, request
import threading
import os

TOKEN = os.environ.get('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN')
CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID', '123456789012345678'))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
app = Flask(__name__)
message_id = None

@bot.event
async def on_ready():
    print(f'Bot ready: {bot.user}')

@app.route('/update', methods=['POST'])
def update():
    global message_id
    try:
        data = request.get_json()
        players = data.get('players', {})
        
        embed = discord.Embed(title="Player Levels", color=0x3498db)
        for username, level in players.items():
            embed.add_field(name=username, value=f"Level: {level}", inline=True)
        
        channel = bot.get_channel(CHANNEL_ID)
        
        async def send_or_edit():
            global message_id
            try:
                if message_id:
                    msg = await channel.fetch_message(message_id)
                    await msg.edit(embed=embed)
                else:
                    msg = await channel.send(embed=embed)
                    message_id = msg.id
            except:
                msg = await channel.send(embed=embed)
                message_id = msg.id
        
        bot.loop.create_task(send_or_edit())
        return 'ok'
    except Exception as e:
        print(f"Error: {e}")
        return 'error', 500

def run_flask():
    app.run(host='0.0.0.0', port=5000)

threading.Thread(target=run_flask).start()
bot.run(TOKEN) 
