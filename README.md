# 🤖 KinkSheet Discord Bot Setup Guide

A Discord bot for matching people based on questionnaire responses with MongoDB integration.

---

## 📋 Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- MongoDB Atlas account (free tier works)
- Age-gated Discord server (18+)

---

## 🚀 Installation Steps

### 1. Install Python Dependencies

```bash
pip install discord.py pymongo python-dotenv requests beautifulsoup4
```

Or use requirements.txt:

```bash
pip install -r requirements.txt
```

---

### 2. Create Your Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** and name it
3. Go to **"Bot"** tab and click **"Add Bot"**
4. Enable these **Privileged Gateway Intents**:
   - ✅ Message Content Intent
   - ✅ Server Members Intent (optional)
5. Click **"Reset Token"** and copy your bot token
6. Go to **OAuth2 > URL Generator**:
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Manage Messages`, `Add Reactions`, `Read Message History`
7. Copy the generated URL and invite the bot to your server

---

### 3. Setup MongoDB Atlas

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account and cluster
3. Click **"Connect"** on your cluster
4. Choose **"Connect your application"**
5. Copy the connection string (looks like `mongodb+srv://...`)
6. Replace `<password>` with your database password
7. Replace `<dbname>` with `dating_bot`

Example:
```
mongodb+srv://myuser:mypassword123@cluster0.abc123.mongodb.net/dating_bot?retryWrites=true&w=majority
```

---

### 4. Create Your .env File

Create a file named `.env` in your project folder:

```bash
# Discord Bot Configuration
DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/dating_bot?retryWrites=true&w=majority
```

**⚠️ IMPORTANT:** 
- Never commit your `.env` file to GitHub
- Add `.env` to your `.gitignore` file

---

### 5. Project Structure

Your folder should look like this:

```
kinksheet-bot/
├── .env                          # Your secrets (don't share!)
├── .gitignore                    # Add .env to this
├── discord_bot.py                # Main Discord bot
├── kinksheet_scraper.py          # Question scraper
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🎮 Usage

### Step 1: Import Questions

Run the scraper to populate your database:

```bash
python kinksheet_scraper.py
```

**Options:**
- `1` - Automatic scraping from kinksheet.com
- `2` - Alternative scraping method
- `3` - Manual entry (copy/paste questions)
- `4` - Export questions to file
- `5` - View database stats

### Step 2: Start the Bot

```bash
python discord_bot.py
```

You should see:
```
🤖 Starting bot...
📊 Connected to MongoDB: dating_bot
📋 Questions available: 150
Bot is now running!
```

---

## 📝 Discord Commands

### 👤 User Commands

| Command | Description |
|---------|-------------|
| `!start` | Take the questionnaire |
| `!profile [@user]` | View someone's profile |
| `!matches` | Find your top 5 matches |
| `!compare @user` | Compare profiles with someone |
| `!retake` | Delete profile and start over |
| `!leaderboard` | See all profiles |
| `!listq [category]` | View questions (optional filter) |
| `!help` | Show all commands |

### 👑 Admin Commands (Requires Administrator Permission)

| Command | Description |
|---------|-------------|
| `!addq <category> <question>` | Add a question |
| `!removeq <id>` | Remove a question by ID |
| `!categories` | View all categories |

**Examples:**
```
!addq BDSM Do you enjoy impact play?
!addq Roleplay Are you interested in fantasy scenarios?
!removeq 15
!listq BDSM
```

---

## 🎨 Response Options

When taking the questionnaire, users react with:

- 🔵 **Favorite** (4 points) - You love this!
- 🟢 **Like** (3 points) - You enjoy this
- 🟡 **Interested** (2 points) - Open to this
- 🔴 **No** (1 point) - Not for you

---

## 🔒 Security Best Practices

1. **Never share your `.env` file**
2. **Add `.env` to `.gitignore`:**
   ```
   .env
   __pycache__/
   *.pyc
   ```
3. **Restrict admin commands** to trusted users
4. **Enable age-gate** on your Discord server
5. **Set up proper NSFW channels**
6. **Review Discord's Community Guidelines**

---

## 🛠️ Troubleshooting

### Bot won't start

```bash
❌ DISCORD_BOT_TOKEN not found in .env file!
```
**Solution:** Check that your `.env` file exists and has the correct token.

---

### MongoDB connection error

```bash
ServerSelectionTimeoutError
```
**Solution:** 
- Check your internet connection
- Verify MongoDB Atlas IP whitelist (allow 0.0.0.0/0 for testing)
- Confirm connection string is correct

---

### Bot doesn't respond to commands

**Solution:**
- Check "Message Content Intent" is enabled in Discord Developer Portal
- Verify bot has proper permissions in your server
- Make sure bot is online (green status)

---

### No questions in database

```bash
📋 Questions available: 0
```
**Solution:** Run the scraper first:
```bash
python kinksheet_scraper.py
```

---

## 📊 Database Collections

Your MongoDB will have these collections:

| Collection | Purpose |
|------------|---------|
| `profiles` | User questionnaire responses |
| `questions` | All questions with categories |
| `categories` | Question categories |

---

## 🔄 Updating Questions

### Add Questions Manually
```bash
!addq <category> <question>
```

### Bulk Import
Use the scraper's manual mode (option 3):
```bash
python kinksheet_scraper.py
# Choose option 3
# Paste questions in format: question text | category
```

### Export Current Questions
```bash
python kinksheet_scraper.py
# Choose option 4
# Questions saved to kinksheet_questions.txt
```

---

## 📈 Features

✅ Age-gated questionnaire system  
✅ MongoDB database storage  
✅ Compatibility matching algorithm  
✅ Beautiful Discord embeds  
✅ Category-based organization  
✅ Profile comparison  
✅ Top 5 matches display  
✅ Leaderboard system  
✅ Admin controls  
✅ Automatic question scraping  
✅ Manual question entry  

---

## 🤝 Support

For issues or questions:
1. Check this README first
2. Review error messages carefully
3. Verify `.env` configuration
4. Test MongoDB connection
5. Check Discord bot permissions

---

## ⚖️ Legal & Ethics

- ✅ For private server use only
- ✅ 18+ age-gated required
- ✅ Respect user privacy
- ✅ Follow Discord TOS
- ✅ Educational/creative writing purposes
- ❌ Do not use for commercial purposes

---

## 📜 License

For private, non-commercial use only.

---

**Made with 💜 for creative writing communities**
