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

# Track user violations: {user_id: count}
user_violations = {}


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
    user = update.message.from_user
    chat = update.message.chat
    
    # Check if user is admin
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ['creator', 'administrator']:
            await update.message.reply_text("❌ អភិមន្ត្រីតែប៉ុណ្ណោះដែលអាចប្រើបានលម្អិត!")
            return
    except Exception:
        await update.message.reply_text("❌ មិនអាចផ្ទៀងផ្ទាត់សិទ្ធិ!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ ប្រើប្រាស់: /allow <extension>\nExample: /allow pdf")
        return
    
    ext = context.args[0].lower().strip().replace('.', '')
    # Validate extension (alphanumeric only)
    if not ext.isalnum() or len(ext) > 10:
        await update.message.reply_text("❌ ឈ្មោះ extension មិនត្រឹមត្រូវ! ប្រើតែលេខ និងអក្សរ (ផ្ដាច់ 10 អក្សរ)")
        return
    
    custom_allowed.add(ext)
    custom_blocked.discard(ext)
    
    await update.message.reply_text(f"✅ បានបន្ថែម .{ext} ទៅបញ្ជីអនុញ្ញាត!")


async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /block command to add blocked file extension"""
    user = update.message.from_user
    chat = update.message.chat
    
    # Check if user is admin
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ['creator', 'administrator']:
            await update.message.reply_text("❌ អភិមន្ត្រីតែប៉ុណ្ណោះដែលអាចប្រើបានលម្អិត!")
            return
    except Exception:
        await update.message.reply_text("❌ មិនអាចផ្ទៀងផ្ទាត់សិទ្ធិ!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ ប្រើប្រាស់: /block <extension>\nExample: /block exe")
        return
    
    ext = context.args[0].lower().strip().replace('.', '')
    # Validate extension (alphanumeric only)
    if not ext.isalnum() or len(ext) > 10:
        await update.message.reply_text("❌ ឈ្មោះ extension មិនត្រឹមត្រូវ! ប្រើតែលេខ និងអក្សរ (ផ្ដាច់ 10 អក្សរ)")
        return
    
    custom_blocked.add(ext)
    custom_allowed.discard(ext)
    
    await update.message.reply_text(f"🚫 បានបន្ថែម .{ext} ទៅបញ្ជីរារាំង!")


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


async def send_private_warning(bot, user_id: int, username: str, violation_type: str, violation_count: int):
    """Send a private warning message to a user
    
    Args:
        bot: The Telegram bot instance
        user_id: The user's ID to send the message to
        username: The user's username/name for logging
        violation_type: Description of what rule was broken
        violation_count: Current violation count (1-3)
    
    Returns:
        True if message was sent successfully, False otherwise
    """
    try:
        warning_text = f"""⚠️ ការព្រមាន!

អ្នកបានផ្ញើរ{violation_type}ដែលរារាំង

📊 ស្ថានភាព: ការព្រមាន {violation_count}/3
"""
        if violation_count < 3:
            warning_text += f"\n⏳ ឱកាសដែលនៅសល់: {3 - violation_count} ដង\n\nប្រសិនបើលើសពីការព្រមាន 3 ដង អ្នកនឹងត្រូវលុបចេញពីក្រុម។"
        else:
            warning_text += "\n\n⛔ ⚠️ ការព្រមាន្ល៉ាចុងក្រោយ!\n\nប្រសិនបើអ្នកបានផ្ញើរលម្អិតលម្អូលម្ដងទៀត អ្នកនឹងត្រូវលុបចេញពីក្រុមលេខ!"
        
        await bot.send_message(
            chat_id=user_id,
            text=warning_text
        )
        logger.info(f"✅ Sent private warning to {username} (ID: {user_id}): violation {violation_count}/3")
        return True
        
    except Exception as send_error:
        # Log detailed error information
        error_msg = str(send_error)
        logger.warning(f"❌ Could not send private DM to {username} (ID: {user_id})")
        logger.warning(f"   Error: {error_msg}")
        logger.warning(f"   → User must start bot first or may have privacy settings blocking messages")
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
    violation_type = None
    
    # Check for documents/files
    if message.document:
        file_name = message.document.file_name or ""
        
        if is_suspicious_file(file_name):
            violation_type = f"ឯកសារ: {file_name.split('.')[-1].upper()}"
            logger.warning(f"Suspicious file detected from {user.name}: {file_name}")
    
    # Check for suspicious captions on any media (photo, video, audio, animation, document)
    if not violation_type:
        caption = message.caption or message.text
        if caption and is_suspicious_link(caption):
            # Identify media type
            if message.photo:
                violation_type = "រូបភាពដែលមានតំណរគួរសង្ស័យ"
            elif message.video:
                violation_type = "វីដេអូដែលមានតំណរគួរសង្ស័យ"
            elif message.audio:
                violation_type = "ឯកសារសូត្របាទដែលមានតំណរគួរសង្ស័យ"
            elif message.animation:
                violation_type = "ចលនាដែលមានតំណរគួរសង្ស័យ"
            else:
                violation_type = "តំណរភ្ជាប់គួរសង្ស័យ"
            
            logger.warning(f"Suspicious link in {violation_type} from {user.name}: {caption[:50]}...")
    
    # Process violation if found
    if violation_type:
        # Delete the message
        try:
            await message.delete()
            logger.info(f"Deleted suspicious content: {violation_type}")
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
        
        # Track violation
        if user.id not in user_violations:
            user_violations[user.id] = 0
        
        user_violations[user.id] += 1
        violation_count = user_violations[user.id]
        
        # Send detailed warning to user (private message only)
        await send_private_warning(
            bot=context.bot,
            user_id=user.id,
            username=user.username or user.first_name or "Unknown",
            violation_type=violation_type,
            violation_count=violation_count
        )
        
        # Remove user if violation count reaches 3
        if violation_count >= 3:
            try:
                await context.bot.ban_chat_member(
                    chat_id=chat.id,
                    user_id=user.id
                )
                
                # Notify group
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=f"🚫 {user.name or user.username or 'Unknown'} ត្រូវលុបចេញពីក្រុមលើសពីការព្រមាន 3 ដង។"
                )
                
                logger.info(f"Removed user {user.name} after 3 violations")
                
                # Reset violation count
                del user_violations[user.id]
                
            except Exception as e:
                logger.error(f"Failed to remove user: {e}")


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
    
    # Add message handler for documents, media, and text
    application.add_handler(MessageHandler(
        filters.Document.ALL | filters.TEXT | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.ANIMATION,
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
    # Print startup message for Render health check
    print("=" * 50)
    print("🤖 Telegram Security Bot Starting...")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔗 Bot token: " + ("✓ Configured" if os.getenv('BOT_TOKEN') else "✗ Missing!"))
    print("=" * 50)
    main()