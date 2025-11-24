import discord
from discord.ext import commands
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv('MONGODB_URI')
if not MONGO_URI:
    raise ValueError("❌ MONGODB_URI not found in .env file!")

client = MongoClient(MONGO_URI)
db = client['dating_bot']
profiles = db['profiles']
questions_db = db['questions']

# Bot setup
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ DISCORD_BOT_TOKEN not found in .env file!")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Reaction emojis with values
REACTIONS = {
    '🔵': 4,  # Favorite
    '🟢': 3,  # Like
    '🟡': 2,  # Interested
    '🔴': 1   # No
}

REACTION_NAMES = {
    '🔵': 'Favorite',
    '🟢': 'Like',
    '🟡': 'Interested',
    '🔴': 'No'
}

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    # Initialize questions if not exist
    if questions_db.count_documents({}) == 0:
        print("No questions found. Use !addq to add questions.")

# =============== ADMIN COMMANDS ===============

@bot.command(name='addq')
@commands.has_permissions(administrator=True)
async def add_question(ctx, category: str, *, question: str):
    """Add a question to the questionnaire (Admin only)
    Usage: !addq <category> <question>
    Example: !addq Fantasy Do you enjoy roleplay scenarios?
    """
    question_count = questions_db.count_documents({})
    
    questions_db.insert_one({
        'question_id': question_count + 1,
        'question': question,
        'category': category,
        'created_at': datetime.utcnow()
    })
    
    # Update categories collection
    categories_db.update_one(
        {'name': category},
        {'$set': {'name': category, 'updated_at': datetime.utcnow()}},
        upsert=True
    )
    
    embed = discord.Embed(
        title="✅ Question Added",
        description=f"**Question #{question_count + 1}** | Category: *{category}*\n{question}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='removeq')
@commands.has_permissions(administrator=True)
async def remove_question(ctx, question_id: int):
    """Remove a question by ID (Admin only)"""
    result = questions_db.delete_one({'question_id': question_id})
    
    if result.deleted_count > 0:
        # Reorder question IDs
        questions = list(questions_db.find().sort('question_id', 1))
        for idx, q in enumerate(questions, 1):
            questions_db.update_one({'_id': q['_id']}, {'$set': {'question_id': idx}})
        
        await ctx.send(f"✅ Question #{question_id} removed and IDs reordered!")
    else:
        await ctx.send(f"❌ Question #{question_id} not found!")

@bot.command(name='listq')
async def list_questions(ctx, category: str = None):
    """List all questions, optionally filtered by category"""
    query = {'category': category} if category else {}
    questions = list(questions_db.find(query).sort('question_id', 1))
    
    if not questions:
        await ctx.send("❌ No questions available. Ask an admin to add some with `!addq`")
        return
    
    # Get all categories
    categories = questions_db.distinct('category')
    
    embed = discord.Embed(
        title=f"📋 Questionnaire - {category if category else 'All Categories'}",
        description=f"Available categories: {', '.join(categories)}\nUse `!listq <category>` to filter",
        color=discord.Color.blue()
    )
    
    # Group by category
    current_category = None
    for q in questions:
        q_category = q.get('category', 'General')
        if q_category != current_category:
            current_category = q_category
            embed.add_field(
                name=f"\n━━━ {current_category} ━━━",
                value="",
                inline=False
            )
        
        embed.add_field(
            name=f"Q{q['question_id']}",
            value=q['question'],
            inline=False
        )
    
    embed.set_footer(text=f"Total: {len(questions)} questions")
    await ctx.send(embed=embed)

# =============== USER COMMANDS ===============

@bot.command(name='start')
async def start_questionnaire(ctx):
    """Start the dating questionnaire"""
    questions = list(questions_db.find().sort('question_id', 1))
    
    if not questions:
        await ctx.send("❌ No questions available yet! Ask an admin to add some.")
        return
    
    # Check if user already has a profile
    existing = profiles.find_one({'user_id': ctx.author.id})
    if existing:
        embed = discord.Embed(
            title="⚠️ Profile Exists",
            description="You already have a profile! Use `!retake` to start over or `!profile` to view your results.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return
    
    # Welcome message
    welcome = discord.Embed(
        title="💕 Welcome to the Dating Questionnaire!",
        description=f"Hey {ctx.author.mention}! Let's find your perfect match!\n\n"
                   f"You'll answer **{len(questions)} questions** by reacting with:\n\n"
                   f"🔵 **Favorite** - You love this!\n"
                   f"🟢 **Like** - You enjoy this\n"
                   f"🟡 **Interested** - Open to this\n"
                   f"🔴 **No** - Not for you\n\n"
                   f"Take your time! ⏱️ 60 seconds per question.",
        color=discord.Color.purple()
    )
    await ctx.send(embed=welcome)
    
    responses = {}
    
    # Ask each question
    current_category = None
    for q in questions:
        q_category = q.get('category', 'General')
        
        # Show category header if it changed
        if q_category != current_category:
            current_category = q_category
            category_embed = discord.Embed(
                title=f"📂 Category: {current_category}",
                description="Answer the following questions in this category",
                color=discord.Color.from_rgb(138, 43, 226)  # Blue violet
            )
            await ctx.send(embed=category_embed)
        
        embed = discord.Embed(
            title=f"Question {q['question_id']} of {len(questions)}",
            description=f"**{q['question']}**",
            color=discord.Color.from_rgb(255, 105, 180)  # Hot pink
        )
        embed.add_field(
            name="React with:",
            value="🔵 Favorite | 🟢 Like | 🟡 Interested | 🔴 No",
            inline=False
        )
        embed.set_footer(text=f"Category: {q_category}")
        
        msg = await ctx.send(embed=embed)
        
        # Add reactions
        for emoji in REACTIONS.keys():
            await msg.add_reaction(emoji)
        
        # Wait for reaction
        def check(reaction, user):
            return (user == ctx.author and 
                   str(reaction.emoji) in REACTIONS.keys() and 
                   reaction.message.id == msg.id)
        
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            emoji = str(reaction.emoji)
            responses[q['question_id']] = {
                'question': q['question'],
                'emoji': emoji,
                'value': REACTIONS[emoji],
                'name': REACTION_NAMES[emoji]
            }
        except:
            await ctx.send("⏱️ Time's up! Skipping this question...")
            responses[q['question_id']] = {
                'question': q['question'],
                'category': q.get('category', 'General'),
                'emoji': '❓',
                'value': 0,
                'name': 'Skipped'
            }
    
    # Save profile
    profile = {
        'user_id': ctx.author.id,
        'username': str(ctx.author),
        'discriminator': ctx.author.discriminator,
        'responses': responses,
        'created_at': datetime.utcnow(),
        'match_count': 0
    }
    
    profiles.insert_one(profile)
    
    # Show profile
    await show_profile(ctx, ctx.author.id)
    
    # Find matches
    await find_matches(ctx, ctx.author.id)

@bot.command(name='retake')
async def retake_questionnaire(ctx):
    """Retake the questionnaire (deletes old profile)"""
    result = profiles.delete_one({'user_id': ctx.author.id})
    
    if result.deleted_count > 0:
        await ctx.send("✅ Your old profile has been deleted! Use `!start` to begin again.")
    else:
        await ctx.send("❌ You don't have a profile yet. Use `!start` to create one!")

@bot.command(name='profile')
async def view_profile(ctx, member: discord.Member = None):
    """View your profile or someone else's"""
    target = member or ctx.author
    await show_profile(ctx, target.id)

async def show_profile(ctx, user_id):
    """Display a user's profile"""
    profile = profiles.find_one({'user_id': user_id})
    
    if not profile:
        await ctx.send("❌ This user hasn't completed the questionnaire yet!")
        return
    
    user = await bot.fetch_user(user_id)
    
    embed = discord.Embed(
        title=f"💝 {profile['username']}'s Dating Profile",
        description="Here's what they're looking for:",
        color=discord.Color.magenta()
    )
    
    # Add avatar
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    
    # Show responses grouped by category
    categories_shown = {}
    for q_id, resp in sorted(profile['responses'].items(), key=lambda x: int(x[0])):
        category = resp.get('category', 'General')
        
        if category not in categories_shown:
            categories_shown[category] = []
        
        categories_shown[category].append(resp)
    
    # Add fields by category
    for category, responses in categories_shown.items():
        category_text = "\n".join([
            f"{resp['emoji']} {resp['question']} - *{resp['name']}*"
            for resp in responses
        ])
        
        embed.add_field(
            name=f"📂 {category}",
            value=category_text,
            inline=False
        )
    
    completed_date = profile['created_at'].strftime('%B %d, %Y')
    embed.set_footer(text=f"Profile completed on {completed_date} • {profile.get('match_count', 0)} matches found")
    
    await ctx.send(embed=embed)

@bot.command(name='matches')
async def show_matches(ctx):
    """Find and show your best matches"""
    await find_matches(ctx, ctx.author.id)

async def find_matches(ctx, user_id):
    """Calculate and display top matches"""
    user_profile = profiles.find_one({'user_id': user_id})
    
    if not user_profile:
        await ctx.send("❌ Complete the questionnaire first with `!start`!")
        return
    
    all_profiles = list(profiles.find({'user_id': {'$ne': user_id}}))
    
    if not all_profiles:
        embed = discord.Embed(
            title="💔 No Matches Yet",
            description="You're the first one here! Share the questionnaire with others to find matches.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Calculate compatibility scores
    matches = []
    
    for other_profile in all_profiles:
        compatibility = calculate_compatibility(user_profile, other_profile)
        matches.append({
            'profile': other_profile,
            'score': compatibility
        })
    
    # Sort by compatibility
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Update match count
    profiles.update_one(
        {'user_id': user_id},
        {'$set': {'match_count': len(matches)}}
    )
    
    # Show top 5 matches
    embed = discord.Embed(
        title="💕 Your Top Matches!",
        description=f"Found {len(matches)} potential matches. Here are your best:",
        color=discord.Color.from_rgb(255, 20, 147)  # Deep pink
    )
    
    for idx, match in enumerate(matches[:5], 1):
        other = match['profile']
        score = match['score']
        
        # Get compatible answers count
        common = sum(1 for q_id in user_profile['responses'] 
                    if q_id in other['responses'] and 
                    user_profile['responses'][q_id]['value'] == other['responses'][q_id]['value'])
        
        medal = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][idx-1]
        
        embed.add_field(
            name=f"{medal} {other['username']} - {score}% Compatible",
            value=f"✨ {common} identical answers\n💫 Use `!profile @{other['username']}` to see their profile",
            inline=False
        )
    
    embed.set_footer(text="Compatibility is based on answer similarity • Use !compare @user to see details")
    
    await ctx.send(embed=embed)

def calculate_compatibility(profile1, profile2):
    """Calculate compatibility percentage between two profiles"""
    total_questions = 0
    matching_score = 0
    
    for q_id in profile1['responses']:
        if q_id in profile2['responses']:
            total_questions += 1
            val1 = profile1['responses'][q_id]['value']
            val2 = profile2['responses'][q_id]['value']
            
            # Calculate similarity (0-100)
            if val1 == val2:
                matching_score += 100  # Perfect match
            else:
                # Closer values = higher score
                difference = abs(val1 - val2)
                matching_score += max(0, 100 - (difference * 33))
    
    if total_questions == 0:
        return 0
    
    return round(matching_score / total_questions)

@bot.command(name='compare')
async def compare_profiles(ctx, member: discord.Member):
    """Compare your profile with another user"""
    if member.id == ctx.author.id:
        await ctx.send("❌ You can't compare with yourself!")
        return
    
    user_profile = profiles.find_one({'user_id': ctx.author.id})
    other_profile = profiles.find_one({'user_id': member.id})
    
    if not user_profile:
        await ctx.send("❌ You need to complete the questionnaire first!")
        return
    
    if not other_profile:
        await ctx.send(f"❌ {member.mention} hasn't completed the questionnaire yet!")
        return
    
    compatibility = calculate_compatibility(user_profile, other_profile)
    
    embed = discord.Embed(
        title=f"💞 Compatibility Analysis",
        description=f"**{ctx.author.name}** vs **{member.name}**\n\n"
                   f"Overall Compatibility: **{compatibility}%**",
        color=discord.Color.gold() if compatibility >= 70 else discord.Color.orange()
    )
    
    # Show question-by-question comparison
    for q_id in sorted(user_profile['responses'].keys(), key=int):
        if q_id in other_profile['responses']:
            your_resp = user_profile['responses'][q_id]
            their_resp = other_profile['responses'][q_id]
            
            match = "✅" if your_resp['value'] == their_resp['value'] else "❌"
            
            embed.add_field(
                name=f"{match} {your_resp['question']}",
                value=f"You: {your_resp['emoji']} {your_resp['name']}\n"
                      f"Them: {their_resp['emoji']} {their_resp['name']}",
                inline=False
            )
    
    await ctx.send(embed=embed)

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    """Show users with most completed profiles"""
    all_profiles = list(profiles.find().sort('created_at', -1).limit(10))
    
    if not all_profiles:
        await ctx.send("❌ No profiles yet!")
        return
    
    embed = discord.Embed(
        title="🏆 Dating Pool Leaderboard",
        description="Most recent profiles:",
        color=discord.Color.gold()
    )
    
    for idx, profile in enumerate(all_profiles, 1):
        completed = len([r for r in profile['responses'].values() if r['value'] > 0])
        total = len(profile['responses'])
        
        embed.add_field(
            name=f"{idx}. {profile['username']}",
            value=f"📊 {completed}/{total} answered • {profile.get('match_count', 0)} matches",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='categories')
async def show_categories(ctx):
    """Show all question categories"""
    categories = list(categories_db.find())
    
    if not categories:
        await ctx.send("❌ No categories yet!")
        return
    
    embed = discord.Embed(
        title="📂 Question Categories",
        description="Available categories in the questionnaire:",
        color=discord.Color.teal()
    )
    
    for cat in categories:
        count = questions_db.count_documents({'category': cat['name']})
        embed.add_field(
            name=cat['name'],
            value=f"{count} questions",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    """Show all commands"""
    embed = discord.Embed(
        title="💝 Dating Questionnaire Bot",
        description="Find your perfect match!",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="👤 User Commands",
        value="`!start` - Take the questionnaire\n"
              "`!profile [@user]` - View a profile\n"
              "`!matches` - Find your matches\n"
              "`!compare @user` - Compare with someone\n"
              "`!retake` - Retake questionnaire\n"
              "`!leaderboard` - See all profiles\n"
              "`!listq` - View all questions",
        inline=False
    )
    
    embed.add_field(
        name="👑 Admin Commands",
        value="`!addq <category> <question>` - Add a question\n"
              "`!removeq <id>` - Remove a question\n"
              "`!categories` - View all categories",
        inline=False
    )
    
    embed.add_field(
        name="🎨 Answer Options",
        value="🔵 **Favorite** (4 pts) - You love this!\n"
              "🟢 **Like** (3 pts) - You enjoy this\n"
              "🟡 **Interested** (2 pts) - Open to this\n"
              "🔴 **No** (1 pt) - Not for you",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Run bot
if __name__ == "__main__":
    try:
        print("🤖 Starting bot...")
        print(f"📊 Connected to MongoDB: {db.name}")
        print(f"📋 Questions available: {questions_db.count_documents({})}")
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        print("💡 Make sure your .env file is configured correctly!")
