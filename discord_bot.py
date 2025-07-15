import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import os

TOKEN = os.environ.get('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN')
CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID', '123456789012345678'))  # Replace with your channel ID

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
app = Flask(__name__)
message_id = None
player_levels = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@app.route('/update', methods=['POST'])
def update():
    global message_id, player_levels
    
    # Check content type
    if not request.is_json:
        print(f"Received non-JSON request. Content-Type: {request.content_type}")
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        player_levels = data.get('players', {})
        
        embed = discord.Embed(title="Player Levels Database", color=0x3498db)
        for user, level in player_levels.items():
            embed.add_field(name=user, value=f"Level: {level}", inline=True)
        
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            return jsonify({"error": "Channel not found"}), 404
        
        async def send_or_edit():
            global message_id
            if message_id:
                try:
                    msg = await channel.fetch_message(message_id)
                    await msg.edit(embed=embed)
                    print(f"Updated message {message_id}")
                except Exception as e:
                    print(f"Failed to update message: {e}")
                    msg = await channel.send(embed=embed)
                    message_id = msg.id
                    print(f"Sent new message {message_id}")
            else:
                msg = await channel.send(embed=embed)
                message_id = msg.id
                print(f"Sent new message {message_id}")
        
        bot.loop.create_task(send_or_edit())
        return jsonify({"success": True, "players_count": len(player_levels)})
        
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

def run_flask():
    app.run(host='0.0.0.0', port=5000)

threading.Thread(target=run_flask).start()
bot.run(TOKEN) 
