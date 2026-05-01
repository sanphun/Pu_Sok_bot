"""
Pu_Sok - Telegram Security Guard Bot (pyTelegramBotAPI)
A strict but funny security guard at UYFC-PV, Prey Veng
Persona: Speaks as an older Cambodian uncle (ក្មួយ)

Features:
- Monitors group messages for dangerous files (.exe, .apk) and URLs/links
- 3-Strike Warning System with automatic banning
- Reports violations to specific admin with forwarded messages
- Sends private DM warnings, or posts in group with auto-delete after 10s if DM fails
- Welcomes new members with warnings about rules
"""

import telebot
from telebot import types
import os
import re
import logging
import threading
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
import config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize bot with token
BOT_TOKEN = config.BOT_TOKEN
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not found! Please set BOT_TOKEN in .env file")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# ============================================
# DATA STRUCTURES
# ============================================

# Track user violations: {user_id: warning_count}
# This implements the 3-strike system
user_warnings = {}

# Track custom blocked/allowed extensions (for admin customization)
custom_blocked = set()
custom_allowed = set()


# ============================================
# HEALTH CHECK SERVER (for Render port detection)
# ============================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks"""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')
    
    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass


def start_health_server():
    """Start health check HTTP server on port 5000"""
    try:
        port = int(os.getenv('PORT', 5000))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"🌐 Health check server running on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start health server: {e}")


# ============================================
# HELPER FUNCTIONS
# ============================================

def is_dangerous_file(file_name: str) -> bool:
    """
    Check if file extension is dangerous (.exe, .apk, etc.)
    Returns: (is_dangerous, extension)
    """
    if not file_name:
        return False, ""
    
    try:
        ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
        
        # Check if explicitly allowed first
        all_allowed = config.ALLOWED_EXTENSIONS | custom_allowed
        if ext in all_allowed:
            return False, ext
        
        # Check if blocked
        all_blocked = config.BLOCKED_EXTENSIONS | custom_blocked
        if ext in all_blocked:
            return True, ext
        
        return False, ext
    except:
        return False, ""


def contains_url(text: str) -> bool:
    """
    Detect if text contains any URL or link
    Returns: True if URL detected
    """
    if not text:
        return False
    
    # URL regex pattern
    url_pattern = r'https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+'
    return bool(re.search(url_pattern, text, re.IGNORECASE))


def get_violation_type(message) -> str:
    """
    Determine the type of violation based on message content
    """
    if message.document:
        ext = message.document.file_name.split('.')[-1].upper() if '.' in message.document.file_name else 'FILE'
        return f"ឯកសារ .{ext}"
    
    if message.photo or message.video or message.audio or message.animation:
        caption = message.caption or ""
        if contains_url(caption):
            return "Link/URL"
    
    if message.text and contains_url(message.text):
        return "Link/URL"
    
    return "ឯកសារ/Link"


def send_warning_to_user(user_id: int, first_name: str, warning_count: int, violation_type: str, chat_id: int) -> bool:
    """
    Try to send private DM warning to user.
    If it fails, post warning in group and delete after 10 seconds using threading.
    
    THREADING EXPLANATION:
    - The delete_after_delay() function runs in a separate thread
    - This allows the bot to continue processing other messages
    - After 10 seconds, it deletes the warning message to keep the group chat clean
    - daemon=True means the thread is terminated when main program exits
    
    Args:
        user_id: User's Telegram ID
        first_name: User's first name for message
        warning_count: Current warning count (1-3)
        violation_type: Type of violation (e.g., "ឯកសារ .EXE")
        chat_id: Group chat ID (for fallback)
    
    Returns:
        True if DM sent successfully, False if fallback to group
    """
    warning_msg = config.WARNING_TEXT.format(
        first_name=first_name,
        violation_type=violation_type,
        warning_count=warning_count
    )
    
    try:
        # Try to send private DM
        bot.send_message(user_id, warning_msg)
        logger.info(f"✅ DM warning sent to {first_name} (ID: {user_id}) - Warning {warning_count}/3")
        return True
    except Exception as e:
        # DM failed - post in group and auto-delete after 10 seconds
        logger.warning(f"❌ DM failed for {first_name} (ID: {user_id}): {str(e)}")
        logger.info(f"📢 Posting warning in group instead (will auto-delete after 10s)")
        
        try:
            group_warning = f"@{first_name}\n\n{warning_msg}"
            msg = bot.send_message(chat_id, group_warning)
            
            # Use threading to delete message after 10 seconds
            # This keeps the chat clean while still notifying the user
            def delete_after_delay():
                try:
                    import time
                    time.sleep(10)
                    bot.delete_message(chat_id, msg.message_id)
                    logger.info(f"🗑️ Auto-deleted group warning message after 10s")
                except:
                    pass
            
            thread = threading.Thread(target=delete_after_delay, daemon=True)
            thread.start()
            
            return False
        except Exception as group_error:
            logger.error(f"Failed to post group warning: {group_error}")
            return False


def report_to_admin(user_id: int, first_name: str, warning_count: int, violation_type: str, message: types.Message):
    """
    Send violation report to specific admin with forwarded message as proof.
    Uses HTML formatting for better readability.
    """
    if not config.SPECIFIC_ADMIN_ID or config.SPECIFIC_ADMIN_ID == 0:
        logger.warning("⚠️ SPECIFIC_ADMIN_ID not configured!")
        return
    
    try:
        # Forward the original violating message to admin
        bot.forward_message(config.SPECIFIC_ADMIN_ID, message.chat.id, message.message_id)
        
        # Send formatted report
        report = config.ADMIN_REPORT.format(
            first_name=first_name,
            user_id=user_id,
            violation_type=violation_type,
            warning_count=warning_count
        )
        bot.send_message(config.SPECIFIC_ADMIN_ID, report)
        
        logger.info(f"📧 Admin report sent - {first_name} violation {warning_count}/3")
    except Exception as e:
        logger.error(f"Failed to send admin report: {e}")




# ============================================
# MESSAGE HANDLERS
# ============================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle /start command"""
    bot.reply_to(message, config.BOT_DESCRIPTION)
    logger.info(f"User {message.from_user.first_name} started bot")


@bot.message_handler(commands=['help'])
def handle_help(message):
    """Handle /help command"""
    help_text = """📖 មូលប្បដិធានីយ៍ ពូសុខ:

/start - ចាប់ផ្តើម
/help - ជំនួយនេះ
/stats - ស្ថានភាពព្រមាន (ក្មួយគ្រាន់)
/clear_warnings - ដកថ្ងាយឆ្ងាយព្រមាន (មេក្រុបគ្រាន់)
/allow `ext` - អនុញ្ញាតឯកសារ (មេក្រុបគ្រាន់)
/block `ext` - រារាំងឯកសារ (មេក្រុបគ្រាន់)"""
    bot.reply_to(message, help_text)




@bot.message_handler(commands=['stats'])
def handle_stats(message):
    """Show warning statistics (group admins only)"""
    if message.chat.type == 'private':
        return
    
    # Check if user is admin
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ['creator', 'administrator']:
            bot.reply_to(message, "❌ មេក្រុបតែប៉ុណ្ណោះ!")
            return
    except:
        bot.reply_to(message, "❌ មិនអាចផ្ទៀងផ្ទាត់សិទ្ធិ!")
        return
    
    if not user_warnings:
        bot.reply_to(message, "📊 មិនមានក្មួយលួច ពូសុខលម្អិត!")
        return
    
    stats = "📊 ស្ថានភាពព្រមាន:\n\n"
    for uid, count in user_warnings.items():
        stats += f"ID {uid}: ⚠️ {count}/3\n"
    
    bot.reply_to(message, stats)


@bot.message_handler(commands=['clear_warnings'])
def handle_clear_warnings(message):
    """Clear a user's warnings (admin only)"""
    if message.chat.type == 'private':
        return
    
    # Check if user is admin
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ['creator', 'administrator']:
            bot.reply_to(message, "❌ មេក្រុបតែប៉ុណ្ណោះ!")
            return
    except:
        bot.reply_to(message, "❌ មិនអាចផ្ទៀងផ្ទាត់សិទ្ធិ!")
        return
    
    if not message.reply_to_message or not message.reply_to_message.from_user:
        bot.reply_to(message, "⚠️ ឆ្លើយលើឯកសារក្មួយដែលត្រូវបង្ហាញលម្អិត")
        return
    
    user_id = message.reply_to_message.from_user.id
    if user_id in user_warnings:
        del user_warnings[user_id]
        bot.reply_to(message, f"✅ បានលុបព្រមាននៃក្មួយ {message.reply_to_message.from_user.first_name}")
    else:
        bot.reply_to(message, "❌ ក្មួយនេះមិនមានព្រមាន!")


@bot.message_handler(commands=['allow'])
def handle_allow(message):
    """Allow a file extension (admin only)"""
    if message.chat.type == 'private':
        return
    
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ['creator', 'administrator']:
            bot.reply_to(message, "❌ មេក្រុបតែប៉ុណ្ណោះ!")
            return
    except:
        bot.reply_to(message, "❌ មិនអាចផ្ទៀងផ្ទាត់សិទ្ធិ!")
        return
    
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(message, "⚠️ ប្រើប្រាស់: /allow pdf\nឧទាហរណ៍: /allow docx")
        return
    
    ext = args[0].lower().replace('.', '')
    if not ext.isalnum() or len(ext) > 10:
        bot.reply_to(message, "❌ ឈ្មោះ extension មិនត្រឹមត្រូវ!")
        return
    
    custom_allowed.add(ext)
    custom_blocked.discard(ext)
    bot.reply_to(message, f"✅ បានអនុញ្ញាត .{ext}")


@bot.message_handler(commands=['block'])
def handle_block(message):
    """Block a file extension (admin only)"""
    if message.chat.type == 'private':
        return
    
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ['creator', 'administrator']:
            bot.reply_to(message, "❌ មេក្រុបតែប៉ុណ្ណោះ!")
            return
    except:
        bot.reply_to(message, "❌ មិនអាចផ្ទៀងផ្ទាត់សិទ្ធិ!")
        return
    
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(message, "⚠️ ប្រើប្រាស់: /block exe\nឧទាហរណ៍: /block bat")
        return
    
    ext = args[0].lower().replace('.', '')
    if not ext.isalnum() or len(ext) > 10:
        bot.reply_to(message, "❌ ឈ្មោះ extension មិនត្រឹមត្រូវ!")
        return
    
    custom_blocked.add(ext)
    custom_allowed.discard(ext)
    bot.reply_to(message, f"🚫 បានរារាំង .{ext}")





@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    """Welcome new members with rules"""
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            # Bot itself joined
            bot.send_message(message.chat.id, "✅ ពូសុខមកលើការយាមរក្សាសន្តិសុខ!")
            continue
        
        welcome_msg = config.WELCOME_TEXT.format(first_name=member.first_name or "ក្មួយ")
        bot.send_message(message.chat.id, welcome_msg)
        logger.info(f"👋 Welcomed {member.first_name} to group")


@bot.message_handler(content_types=['document', 'photo', 'video', 'audio', 'animation', 'text'])
def handle_message(message):
    """
    Main message handler - checks for violations.
    
    VIOLATION DETECTION:
    1. Dangerous files (.exe, .apk)
    2. URLs/Links in captions or text
    
    3-STRIKE WARNING SYSTEM EXPLANATION:
    - Track violations in user_warnings dictionary: {user_id: count}
    - First violation: warning count = 1/3, send DM warning
    - Second violation: warning count = 2/3, send DM warning
    - Third violation: warning count = 3/3, ban user and remove from dictionary
    - Reset counter after ban so user can be monitored again if re-joins
    
    ACTION ON VIOLATION:
    1. Delete the message silently
    2. Increment user warning counter
    3. Send private warning (or group warning with auto-delete)
    4. Report to admin with forwarded message
    5. Ban if warning count reaches 3
    """
    
    # Only process group messages
    if message.chat.type == 'private':
        return
    
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Unknown"
    violation_type = None
    
    # ============================================
    # VIOLATION DETECTION
    # ============================================
    
    # Check for dangerous files
    if message.document:
        is_dangerous, ext = is_dangerous_file(message.document.file_name)
        if is_dangerous:
            violation_type = f"ឯកសារ .{ext.upper()}"
            logger.warning(f"🚨 Dangerous file from {first_name}: {message.document.file_name}")
    
    # Check for URLs in captions or text
    if not violation_type:
        text_to_check = message.caption or message.text or ""
        if contains_url(text_to_check):
            violation_type = "Link/URL"
            logger.warning(f"🚨 Suspicious link from {first_name}: {text_to_check[:50]}...")
    
    # ============================================
    # PROCESS VIOLATION
    # ============================================
    
    if violation_type:
        try:
            # 1. DELETE THE MESSAGE SILENTLY
            bot.delete_message(message.chat.id, message.message_id)
            logger.info(f"🗑️ Deleted message from {first_name}")
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
        
        # 2. INCREMENT WARNING COUNTER (3-STRIKE SYSTEM)
        if user_id not in user_warnings:
            user_warnings[user_id] = 0
        
        user_warnings[user_id] += 1
        warning_count = user_warnings[user_id]
        logger.info(f"⚠️ {first_name} warning {warning_count}/3")
        
        # 3. SEND WARNING TO USER (private DM or group with auto-delete)
        # Note: We use threading here to prevent blocking the main bot loop
        def send_warning_thread():
            try:
                send_warning_to_user(user_id, first_name, warning_count, violation_type, message.chat.id)
            except Exception as e:
                logger.error(f"Error in warning thread: {e}")
        
        warning_thread = threading.Thread(target=send_warning_thread, daemon=True)
        warning_thread.start()
        
        # 4. REPORT TO ADMIN WITH FORWARDED MESSAGE
        report_to_admin(user_id, first_name, warning_count, violation_type, message)
        
        # 5. BAN USER IF REACHED 3 WARNINGS
        if warning_count >= 3:
            try:
                bot.ban_chat_member(message.chat.id, user_id)
                ban_msg = config.BAN_TEXT.format(first_name=first_name)
                bot.send_message(message.chat.id, ban_msg)
                logger.info(f"🚫 Banned {first_name} after 3 warnings")
                
                # Reset warnings for this user
                del user_warnings[user_id]
            except Exception as e:
                logger.error(f"Failed to ban user: {e}")


# ============================================
# ERROR HANDLER & FALLBACK
# ============================================

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Fallback handler for any other messages"""
    pass


# ============================================
# MAIN
# ============================================

def main():
    """Start the bot"""
    print("=" * 60)
    print("🤖 Pu_Sok - Telegram Security Bot Starting...")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Bot Token: {'✓ Configured' if BOT_TOKEN else '✗ Missing!'}")
    print(f"👮 Admin ID: {config.SPECIFIC_ADMIN_ID if config.SPECIFIC_ADMIN_ID != 0 else '⚠️  Not Set'}")
    print("=" * 60)
    print("Press Ctrl+C to stop the bot")
    print("=" * 60)
    
    logger.info("✅ Bot started successfully")
    
    # Start health check server in background thread
    server_thread = threading.Thread(target=start_health_server, daemon=True)
    server_thread.start()
    
    try:
        # Start polling
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("\n✋ Bot stopped")
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        raise


if __name__ == "__main__":
    main()

