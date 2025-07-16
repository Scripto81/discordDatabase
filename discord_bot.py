import discord
from discord.ext import commands
from flask import Flask, request
import threading
import os
import json

TOKEN = os.environ.get('DISCORD_BOT_TOKEN', 'YOUR_BOT_TOKEN')
CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID', '123456789012345678'))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
app = Flask(__name__)

# File storage functions
def save_players(players):
    """Save players data to JSON file"""
    try:
        with open('player_levels.json', 'w') as f:
            json.dump(players, f, indent=2)
        print(f"Saved {len(players)} players to file")
    except Exception as e:
        print(f"Error saving players: {e}")

def load_players():
    """Load players data from JSON file"""
    try:
        with open('player_levels.json', 'r') as f:
            players = json.load(f)
            print(f"Loaded {len(players)} players from file")
            return players
    except FileNotFoundError:
        print("No player data file found, starting fresh")
        return {}
    except Exception as e:
        print(f"Error loading players: {e}")
        return {}

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

@bot.command()
async def search(ctx, username: str):
    """Search for a player's level by username"""
    players = load_players()
    
    # Search for exact match first
    if username in players:
        player_data = players[username]
        embed = discord.Embed(title="Player Found", color=0x00ff00)
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="Display Name", value=player_data.get('displayName', 'N/A'), inline=True)
        embed.add_field(name="Level", value=player_data.get('level', 'N/A'), inline=True)
        embed.add_field(name="Account Age", value=f"{player_data.get('accountAge', 'N/A')} days", inline=True)
        embed.add_field(name="User ID", value=player_data.get('userId', 'N/A'), inline=True)
        await ctx.send(embed=embed)
        return
    
    # Search for partial matches
    matches = []
    username_lower = username.lower()
    for player_name, player_data in players.items():
        if username_lower in player_name.lower():
            matches.append((player_name, player_data))
    
    if matches:
        # Sort matches by level (highest first)
        matches.sort(key=lambda x: x[1].get('level', 0), reverse=True)
        
        embed = discord.Embed(title="Search Results", color=0x3498db)
        embed.add_field(name="Search Term", value=username, inline=False)
        
        # Show up to 10 matches
        for i, (player_name, player_data) in enumerate(matches[:10]):
            level = player_data.get('level', 'N/A')
            display_name = player_data.get('displayName', 'N/A')
            embed.add_field(name=f"Match {i+1}", value=f"{player_name} ({display_name}): Level {level}", inline=True)
        
        if len(matches) > 10:
            embed.set_footer(text=f"Showing 10 of {len(matches)} matches")
        
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Player Not Found", description=f"No players found matching '{username}'", color=0xff0000)
        await ctx.send(embed=embed)

@bot.command()
async def top(ctx, count: int = 10):
    """Show top players by level"""
    players = load_players()
    
    if not players:
        embed = discord.Embed(title="No Data", description="No player data available", color=0xff0000)
        await ctx.send(embed=embed)
        return
    
    # Sort by level (highest first)
    sorted_players = sorted(players.items(), key=lambda x: x[1].get('level', 0), reverse=True)
    
    embed = discord.Embed(title=f"Top {min(count, len(sorted_players))} Players", color=0x00ff00)
    
    for i, (username, player_data) in enumerate(sorted_players[:count]):
        level = player_data.get('level', 'N/A')
        display_name = player_data.get('displayName', 'N/A')
        account_age = player_data.get('accountAge', 'N/A')
        embed.add_field(name=f"#{i+1} {username}", value=f"Level {level} | {display_name} | {account_age} days", inline=False)
    
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
        
        new_players = data.get('players', {})
        print(f"5. Extracted new players: {new_players}")
        print(f"6. Number of new players: {len(new_players)}")
        
        print("7. Processing player data...")
        
        # Load existing players from file
        existing_players = load_players()
        print(f"8. Loaded {len(existing_players)} existing players from file")
        
        # Merge new players with existing players (keep higher levels)
        all_players = existing_players.copy()
        for username, new_data in new_players.items():
            if username not in all_players or new_data.get('level', 0) > all_players[username].get('level', 0):
                all_players[username] = new_data
                print(f"9. Updated {username}: Level {new_data.get('level', 'N/A')}")
        
        print(f"10. Total players after merge: {len(all_players)}")
        
        # Save updated players to file
        save_players(all_players)
        
        print("11. Data saved successfully")
        print("12. Returning success")
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
