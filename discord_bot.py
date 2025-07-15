import discord
from discord.ext import commands
from flask import Flask, request
import threading
import os

TOKEN = os.environ.get('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN')
CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID', '123456789012345678'))  # Replace with your channel ID

bot = commands.Bot(command_prefix='!')
app = Flask(__name__)
message_id = None
player_levels = {}

@bot.event
def on_ready():
    print(f'Logged in as {bot.user}')

@app.route('/update', methods=['POST'])
def update():
    global message_id, player_levels
    data = request.json
    player_levels = data.get('players', {})
    embed = discord.Embed(title="Player Levels Database", color=0x3498db)
    for user, level in player_levels.items():
        embed.add_field(name=user, value=f"Level: {level}", inline=True)
    channel = bot.get_channel(CHANNEL_ID)
    async def send_or_edit():
        global message_id
        if message_id:
            try:
                msg = await channel.fetch_message(message_id)
                await msg.edit(embed=embed)
            except Exception:
                msg = await channel.send(embed=embed)
                message_id = msg.id
        else:
            msg = await channel.send(embed=embed)
            message_id = msg.id
    bot.loop.create_task(send_or_edit())
    return 'ok'

def run_flask():
    app.run(host='0.0.0.0', port=5000)

threading.Thread(target=run_flask).start()
bot.run(TOKEN) 
