# Configuration for Telegram Security Bot

# File extensions to block (suspicious files)
BLOCKED_EXTENSIONS = {
    'exe', 'apk', 'bat', 'cmd', 'vbs', 'js', 'jar', 'scr', 'pif', 'msi',
    'com', 'hta', 'wsf', 'wsh', 'ps1', 'sh', 'bash', 'elf', 'bin',
    'dll', 'sys', 'ocx', 'reg', 'inf', 'ini'  # Potentially dangerous
}

# File extensions that are always allowed
ALLOWED_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg',  # Images
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',  # Documents
    'txt', 'md', 'csv', 'json', 'xml', 'zip', 'rar',  # Common files
    'mp3', 'mp4', 'avi', 'mkv', 'mov', 'wav', 'flac',  # Media
    'html', 'css', 'py', 'java', 'c', 'cpp', 'h', 'ts', 'js'  # Code
}

# Suspicious URL patterns
SUSPICIOUS_PATTERNS = [
    r'bit\.ly/',
    r't\.ly/',
    r'tinyurl\.com/',
    r'goo\.gl/',
    r'shorturl\.',
    r't\.me/',
    r'telegram\.me/',
    r'wa\.me/',
    r'chat\.whatsapp\.com',
    r'discord\.gg/',
    r'discord\.com/invite/',
]

# Warning message when member is removed
WARNING_MESSAGE = """
⚠️ ប្រតិកម្ម!

{username} ត្រូវបានដកចេញពីក្រុមភ្លាមៗ ដោយសារបានបំពានគោលការណ៍សុវត្ថិភាព:
- ផ្ញើឯកសារ {file_type} គួរឱ្យសង្ស័យ
- ឬ ផ្ញើតំណរភ្ជាប់គួរសង្ស័យ

📋 ច្បាប់ក្រុម: ការផ្ញើឯកសារ ឬ តំណរភ្ជាប់គួរសង្ស័យ ត្រូវបានហាមឃាត់!
"""

# Bot description
BOT_DESCRIPTION = """
🔒 Telegram Security Bot

ម៉ាស៊ីនស្រាវជ្រាវសុវត្ថិភាពក្រុម:
- ការពារឯកសារគួរសង្ស័យ (exe, apk, etc.)
- ការពារតំណរភ្ជាប់គួរសង្ស័យ
- ដកចេញសាមាជិកដែលបំពាន
"""