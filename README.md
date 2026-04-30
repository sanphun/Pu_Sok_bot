# Telegram Security Bot

A Telegram bot that protects groups from suspicious files and links.

## Features

- 🔒 Block suspicious file types (exe, apk, bat, cmd, vbs, js, jar, etc.)
- 🔗 Detect and remove suspicious links
- ⚡ Auto-remove violating members from the group
- 📝 Configurable allowed file types
- 👥 Admin management commands

## Setup

1. Install dependencies:
```bash
pip install python-telegram-bot python-dotenv
```

2. Create a `.env` file with your bot token:
```
BOT_TOKEN=your_telegram_bot_token_here
```

3. Run the bot:
```bash
python bot.py
```

## Bot Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/allow <extension>` - Add allowed file extension
- `/block <extension>` - Add blocked file extension
- `/allowed` - List allowed file extensions
- `/blocked` - List blocked file extensions

## Configuration

Edit `config.py` to customize:
- Blocked file extensions
- Suspicious link patterns
- Warning messages

## Get Bot Token

1. Open Telegram and search for @BotFather
2. Send `/newbot` to create a new bot
3. Follow the instructions to get your bot token
4. Use the token in your `.env` file