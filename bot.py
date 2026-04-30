"""
Telegram Security Bot
Blocks suspicious files and links, removes violating members
"""

import os
import re
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ChatMemberHandler
)
from telegram.constants import ChatMemberStatus
import config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Custom blocked extensions (can be modified by admins)
custom_blocked = set()
custom_allowed = set()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(config.BOT_DESCRIPTION)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 មូលប្បដិធានីយ៍:

/start - ចាប់ផ្តើម bot
/help - បង្ហាញជំនួយនេះ
/allow <ext> - អនុញ្ញាតប្រភេទ file
/block <ext> - រារាំងប្រភេទ file
/allowed - បង្ហាញ្រភេទ file ដែលអនុញ្ញាត
/blocked - បង្ហាញប្រភេទ file ដែលរារាំង
"""
    await update.message.reply_text(help_text)


async def allow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /allow command to add allowed file extension"""
    if not context.args:
        await update.message.reply_text("⚠️ ប្រើប្រាស់: /allow <extension>\nExample: /allow pdf")
        return
    
    ext = context.args[0].lower().strip().replace('.', '')
    custom_allowed.add(ext)
    custom_blocked.discard(ext)
    
    await update.message.reply_text(f"✅ បានបន្ថែម {ext} ទៅបញ្ជីអនុញ្ញាត!")


async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /block command to add blocked file extension"""
    if not context.args:
        await update.message.reply_text("⚠️ ប្រើប្រាស់: /block <extension>\nExample: /block exe")
        return
    
    ext = context.args[0].lower().strip().replace('.', '')
    custom_blocked.add(ext)
    custom_allowed.discard(ext)
    
    await update.message.reply_text(f"🚫 បានបន្ថែម {ext} ទៅបញ្ជីរារាំង!")


async def allowed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show allowed file extensions"""
    all_allowed = config.ALLOWED_EXTENSIONS | custom_allowed
    await update.message.reply_text(
        f"📂 ប្រភេទ file អនុញ្ញាត:\n" + ", ".join(sorted(all_allowed))
    )


async def blocked_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show blocked file extensions"""
    all_blocked = config.BLOCKED_EXTENSIONS | custom_blocked
    await update.message.reply_text(
        f"🚫 ប្រភេទ file រារាំង:\n" + ", ".join(sorted(all_blocked))
    )


def get_all_blocked_extensions():
    """Get all blocked extensions including custom ones"""
    return config.BLOCKED_EXTENSIONS | custom_blocked


def is_suspicious_file(file_name: str) -> bool:
    """Check if file extension is suspicious"""
    if not file_name:
        return False
    
    # Get file extension
    ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
    
    # Check if extension is blocked
    all_blocked = get_all_blocked_extensions()
    
    # Check if explicitly allowed
    all_allowed = config.ALLOWED_EXTENSIONS | custom_allowed
    if ext in all_allowed:
        return False
    
    return ext in all_blocked


def is_suspicious_link(text: str) -> bool:
    """Check if text contains suspicious links"""
    if not text:
        return False
    
    text_lower = text.lower()
    for pattern in config.SUSPICIOUS_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    return False


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new members joining the group"""
    message = update.message
    new_members = message.new_chat_members
    
    for member in new_members:
        # Skip if it's the bot itself
        if member.id == context.bot.id:
            continue
        
        logger.info(f"New member joined: {member.name or member.username} (ID: {member.id})")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and check for suspicious content"""
    message = update.message
    
    # Only process in groups
    if message.chat.type == 'private':
        return
    
    user = message.from_user
    chat = message.chat
    
    # Check for documents/files
    if message.document:
        file_name = message.document.file_name or ""
        file_id = message.document.file_id
        
        if is_suspicious_file(file_name):
            logger.warning(f"Suspicious file detected from {user.name}: {file_name}")
            
            # Try to delete the message
            try:
                await message.delete()
                logger.info(f"Deleted suspicious file: {file_name}")
            except Exception as e:
                logger.error(f"Failed to delete message: {e}")
            
            # Try to remove the user from the group
            try:
                await context.bot.ban_chat_member(
                    chat_id=chat.id,
                    user_id=user.id
                )
                
                # Send warning message
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=config.WARNING_MESSAGE.format(
                        username=user.name or user.username or "Unknown",
                        file_type=file_name.split('.')[-1].upper()
                    )
                )
                
                logger.info(f"Removed user {user.name} for sending suspicious file")
                
            except Exception as e:
                logger.error(f"Failed to remove user: {e}")
                # Try to unban if ban failed
                try:
                    await context.bot.unban_chat_member(
                        chat_id=chat.id,
                        user_id=user.id
                    )
                except:
                    pass
    
    # Check for suspicious links
    if message.text or message.caption:
        text = message.text or message.caption
        
        if is_suspicious_link(text):
            logger.warning(f"Suspicious link detected from {user.name}: {text[:50]}...")
            
            # Try to delete the message
            try:
                await message.delete()
                logger.info("Deleted message with suspicious link")
            except Exception as e:
                logger.error(f"Failed to delete message: {e}")
            
            # Try to remove the user from the group
            try:
                await context.bot.ban_chat_member(
                    chat_id=chat.id,
                    user_id=user.id
                )
                
                # Send warning message
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=config.WARNING_MESSAGE.format(
                        username=user.name or user.username or "Unknown",
                        file_type="LINK"
                    )
                )
                
                logger.info(f"Removed user {user.name} for sending suspicious link")
                
            except Exception as e:
                logger.error(f"Failed to remove user: {e}")
                # Try to unban if ban failed
                try:
                    await context.bot.unban_chat_member(
                        chat_id=chat.id,
                        user_id=user.id
                    )
                except:
                    pass


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")


def main():
    """Main function to run the bot"""
    # Get bot token from environment variable
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        # Try to load from .env file
        from dotenv import load_dotenv
        load_dotenv()
        bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        logger.error("BOT_TOKEN not found! Please set BOT_TOKEN in .env file")
        print("Error: BOT_TOKEN not found!")
        print("Please create a .env file with BOT_TOKEN=your_token_here")
        return
    
    # Create the Application
    application = Application.builder().token(bot_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("allow", allow_command))
    application.add_handler(CommandHandler("block", block_command))
    application.add_handler(CommandHandler("allowed", allowed_command))
    application.add_handler(CommandHandler("blocked", blocked_command))
    
    # Add message handler for documents and links
    application.add_handler(MessageHandler(
        filters.Document.ALL | filters.TEXT,
        handle_message
    ))
    
    # Add new member handler
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        handle_new_member
    ))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Telegram Security Bot is starting...")
    print("Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=['message', 'edited_message'])


if __name__ == "__main__":
    main()