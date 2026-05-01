# Configuration for Pu_Sok - Telegram Security Bot (pyTelegramBotAPI)
# Bot Persona: Strict but funny security guard at UYFC-PV, Prey Veng

import os
from dotenv import load_dotenv

load_dotenv()

# Get from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
SPECIFIC_ADMIN_ID = int(os.getenv('SPECIFIC_ADMIN_ID', '0'))  # Replace with actual admin ID

# Dangerous file extensions to block (.exe, .apk, etc.)
BLOCKED_EXTENSIONS = {
    'exe', 'apk', 'bat', 'cmd', 'vbs', 'jar', 'scr', 'pif', 'msi',
    'com', 'hta', 'wsf', 'wsh', 'ps1', 'sh', 'bash', 'elf', 'bin',
    'dll', 'sys', 'ocx', 'reg', 'inf', 'zip'  # Potentially dangerous
}

# Allowed file extensions (optional - for customization)
ALLOWED_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',  # Images
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',  # Documents
    'txt', 'md', 'csv', 'json', 'xml',  # Common files
    'mp3', 'mp4', 'avi', 'mkv', 'mov', 'wav', 'flac',  # Media
}

# ============ KHMER MESSAGES ============

# Admin report when violation is detected
ADMIN_REPORT = """ជម្រាបសួរមេ! ពូសុខរាយការណ៍ប្រាប់៖
👤 ក្មួយឈ្មោះ៖ {first_name} (ID: <code>{user_id}</code>)
⚠️ លួចផ្ញើ៖ {violation_type}
📊 ព្រមានលើកទី៖ {warning_count}/3
👇 ឯកសារភស្តុតាងពូ Forward មកខាងលើនេះស្រាប់មេ!"""

# Warning message sent to user
WARNING_TEXT = """នែ៎ក្មួយ {first_name}! ពូប្រាប់ហើយថានៅស្នាក់ការយើងហាមផ្ញើ {violation_type}។ នេះពូកត់ឈ្មោះទុក ព្រមានលើកទី {warning_count}/3 ហើយណា៎។ បើគ្រប់ ៣ដង ពូអូសកចេញពីគ្រុបហើយ កុំថាពូសុខកាច!"""

# Ban message (when user reaches 3 warnings)
BAN_TEXT = """ឆុយ! ប្រាប់មិនស្តាប់! អាណិតណាស់ក្មួយ {first_name} ត្រូវបានពូសុខអូសកចេញពីគ្រុបបាត់ហើយ ដោយសារព្រមាន៣ដងហើយនៅតែរឹងក។"""

# Welcome message for new members
WELCOME_TEXT = """សួស្តីក្មួយ {first_name}! ពូឈ្មោះ ពូសុខ ជាសន្តិសុខយាមនៅទីស្នាក់ការ ววយក ខេត្តព្រៃវែង។ មុនចូលគ្រុបដោះស្បែកជើងផងក្មួយ... អាហ្នឹងពូនិយាយលេងទេ! ស្វាគមន៍មកកាន់គ្រុប! អានច្បាប់ផង កុំផ្ញើ Link ឬ File មេរោគផ្តេសផ្តាសប្រយ័ត្នពូទាត់ចេញណា៎!"""

# Bot description
BOT_DESCRIPTION = """🔒 ពូសុខ - សន្តិសុខយាម UYFC-PV

ពូឈ្មោះ ពូសុខ ជាសន្តិសុខយាមឆឺងក្នុងទីស្នាក់ការនិងក្នុងក្រុប Telegram
- ហាមផ្ញើឯកសារគ្រោះថ្នក់ (.exe, .apk)
- ហាមផ្ញើ Link / URL
- ព្រមាន 3 ដង ហើយគេចេញ"""
