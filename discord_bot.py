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
    print(f'Bot is in {len(bot.guilds)} servers')
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id})')

@bot.event
async def on_guild_join(guild):
    print(f'Bot joined server: {guild.name}')
    # Try to send a welcome message to the first available channel
    for channel in guild.text_channels:
        try:
            await channel.send(f"🎉 **Player Levels Bot is now online!**\n\nI'll automatically update player levels from your Roblox game.\n\n**Commands:**\n`!status` - Check bot status\n`!channel` - Set update channel\n`!test` - Test the bot")
            break
        except:
            continue

@bot.command()
async def status(ctx):
    """Check bot status and permissions"""
    embed = discord.Embed(title="Bot Status", color=0x00ff00)
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Channel ID", value=CHANNEL_ID, inline=True)
    
    # Check channel permissions
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        embed.add_field(name="Target Channel", value=f"#{channel.name}", inline=True)
        embed.add_field(name="Can Send Messages", value="✅" if channel.permissions_for(bot.user).send_messages else "❌", inline=True)
        embed.add_field(name="Can Manage Messages", value="✅" if channel.permissions_for(bot.user).manage_messages else "❌", inline=True)
    else:
        embed.add_field(name="Target Channel", value="❌ Not found", inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def test(ctx):
    """Test the bot by sending a test embed"""
    embed = discord.Embed(title="Test Message", description="Bot is working! 🎉", color=0x00ff00)
    await ctx.send(embed=embed)

@app.route('/update', methods=['POST'])
def update():
    global message_id
    try:
        print("Received POST request to /update")
        data = request.get_json()
        print(f"Received data: {data}")
        players = data.get('players', {})
        print(f"Players: {players}")
        
        embed = discord.Embed(title="Player Levels", color=0x3498db)
        embed.set_footer(text=f"Last updated: {len(players)} players")
        
        for username, level in players.items():
            embed.add_field(name=username, value=f"Level: {level}", inline=True)
        
        channel = bot.get_channel(CHANNEL_ID)
        print(f"Channel found: {channel}")
        
        if not channel:
            print(f"ERROR: Channel {CHANNEL_ID} not found!")
            return 'Channel not found', 404
        
        if not channel.permissions_for(bot.user).send_messages:
            print(f"ERROR: Bot doesn't have permission to send messages in channel {CHANNEL_ID}")
            return 'No permission to send messages', 403
        
        async def send_or_edit():
            global message_id
            try:
                if message_id:
                    print(f"Trying to update message {message_id}")
                    msg = await channel.fetch_message(message_id)
                    await msg.edit(embed=embed)
                    print("Message updated successfully")
                else:
                    print("Sending new message")
                    msg = await channel.send(embed=embed)
                    message_id = msg.id
                    print(f"New message sent with ID: {message_id}")
            except Exception as e:
                print(f"Error in send_or_edit: {e}")
                msg = await channel.send(embed=embed)
                message_id = msg.id
                print(f"Fallback message sent with ID: {message_id}")
        
        bot.loop.create_task(send_or_edit())
        return 'ok'
    except Exception as e:
        print(f"Error in update route: {e}")
        return 'error', 500

def run_flask():
    app.run(host='0.0.0.0', port=5000)

threading.Thread(target=run_flask).start()
bot.run(TOKEN) 
