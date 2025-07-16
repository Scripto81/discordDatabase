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
        # Check permissions more safely
        try:
            permissions = channel.permissions_for(ctx.guild.me)
            embed.add_field(name="Can Send Messages", value="✅" if permissions.send_messages else "❌", inline=True)
            embed.add_field(name="Can Manage Messages", value="✅" if permissions.manage_messages else "❌", inline=True)
        except:
            embed.add_field(name="Permissions", value="❌ Error checking", inline=True)
    else:
        embed.add_field(name="Target Channel", value="❌ Not found", inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def test(ctx):
    """Test the bot by sending a test embed"""
    embed = discord.Embed(title="Test Message", description="Bot is working! 🎉", color=0x00ff00)
    await ctx.send(embed=embed)

@app.route('/')
def home():
    return 'Bot is running! Use /update for POST requests.'

@app.route('/update', methods=['POST'])
def update():
    global message_id
    print("=== STARTING UPDATE ROUTE ===")
    print("A. Route function called")
    try:
        print("B. Entered try block")
        print("1. Received POST request to /update")
        print(f"2. Request headers: {dict(request.headers)}")
        print(f"3. Request content type: {request.content_type}")
        
        data = request.get_json()
        print(f"4. Parsed JSON data: {data}")
        
        if not data:
            print("ERROR: No JSON data received")
            return 'No data received', 400
        
        players = data.get('players', {})
        print(f"5. Extracted players: {players}")
        print(f"6. Number of players: {len(players)}")
        
        embed = discord.Embed(title="Player Levels", color=0x3498db)
        embed.set_footer(text=f"Last updated: {len(players)} players")
        
        print("7. Creating embed fields...")
        for username, level in players.items():
            embed.add_field(name=username, value=f"Level: {level}", inline=True)
            print(f"   - Added {username}: Level {level}")
        
        print("8. Getting channel...")
        channel = bot.get_channel(CHANNEL_ID)
        print(f"9. Channel found: {channel}")
        print(f"10. Channel ID: {CHANNEL_ID}")
        
        if not channel:
            print(f"ERROR: Channel {CHANNEL_ID} not found!")
            return 'Channel not found', 404
        
        print("11. Channel exists, checking permissions...")
        # Check permissions more safely
        try:
            permissions = channel.permissions_for(channel.guild.me)
            print(f"12. Permissions check successful")
            if not permissions.send_messages:
                print(f"ERROR: Bot doesn't have permission to send messages in channel {CHANNEL_ID}")
                return 'No permission to send messages', 403
        except Exception as e:
            print(f"Warning: Could not check permissions: {e}")
            # Continue anyway, let Discord handle the error if it occurs
        
        print("13. Starting async send/edit function...")
        async def send_or_edit():
            global message_id
            try:
                print(f"14. Inside async function, message_id: {message_id}")
                if message_id:
                    print(f"15. Trying to update message {message_id}")
                    msg = await channel.fetch_message(message_id)
                    await msg.edit(embed=embed)
                    print("16. Message updated successfully")
                else:
                    print("17. Sending new message")
                    msg = await channel.send(embed=embed)
                    message_id = msg.id
                    print(f"18. New message sent with ID: {message_id}")
            except Exception as e:
                print(f"19. Error in send_or_edit: {e}")
                print(f"20. Trying fallback - sending new message")
                msg = await channel.send(embed=embed)
                message_id = msg.id
                print(f"21. Fallback message sent with ID: {message_id}")
        
        print("22. Creating task...")
        bot.loop.create_task(send_or_edit())
        print("23. Task created successfully")
        print("24. Returning success")
        return 'ok'
    except Exception as e:
        print(f"ERROR in update route: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return 'error', 500
    except:
        print("ERROR: Unknown exception occurred")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return 'unknown error', 500

def run_flask():
    app.run(host='0.0.0.0', port=5000)

threading.Thread(target=run_flask).start()
bot.run(TOKEN) 
