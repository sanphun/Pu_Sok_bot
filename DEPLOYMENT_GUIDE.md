# 🚀 Pu_Sok Bot - Deployment Guide (Render.com)

This guide shows how to deploy Pu_Sok security bot on Render.com for 24/7 monitoring.

## Prerequisites

1. ✅ GitHub Account (https://github.com)
2. ✅ Render Account (https://render.com)
3. ✅ Telegram Bot Token (from @BotFather)
4. ✅ Your Admin Telegram ID

## Step 1: Initialize Git Repository

```bash
cd TelegramBot

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Pu_Sok Bot - UYFC-PV Security Guard"

# Create main branch
git branch -M main
```

## Step 2: Push to GitHub

### Option A: New Repository
```bash
# Create new repository on GitHub.com
# Go to https://github.com/new
# Create repo name: "pu-sok-bot"
# Copy the HTTPS URL

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/pu-sok-bot.git

# Push to GitHub
git push -u origin main
```

### Option B: Existing Repository
```bash
git remote add origin https://github.com/YOUR_USERNAME/existing-repo.git
git push -u origin main
```

## Step 3: Deploy on Render.com

### 3.1 Connect GitHub to Render
1. Go to https://render.com
2. Sign up or log in
3. Click **New** → **Web Service**
4. Click **Connect GitHub**
5. Authorize Render to access your GitHub
6. Select the **pu-sok-bot** repository

### 3.2 Configure Web Service

Fill in the following:

| Setting | Value |
|---------|-------|
| **Name** | pu-sok-bot |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python bot.py` |
| **Instance Type** | Free (or Starter) |

### 3.3 Add Environment Variables

Click **Environment** and add:

| Key | Value | Example |
|-----|-------|---------|
| `BOT_TOKEN` | Your Telegram bot token | `123456:ABC-DEF1234ghIkl-zyx...` |
| `SPECIFIC_ADMIN_ID` | Your Telegram ID | `987654321` |

**Getting your Telegram ID:**
- Send `/start` to [@userinfobot](https://t.me/userinfobot)
- It will show your ID

### 3.4 Deploy

1. Click **Create Web Service**
2. Render will start building (~2-3 minutes)
3. Wait for status: **Live** (green checkmark)
4. Check logs to see bot running

## Step 4: Verify Deployment

### Check Bot Status
```
Logs should show:
✅ Bot started successfully
🔑 Bot Token: ✓ Configured
👮 Admin ID: 987654321
============================================================
```

### Test in Telegram Group
1. Add Pu_Sok bot to your group
2. Send a test file `.exe` or URL
3. Bot should:
   - Delete the message
   - Send warning to user
   - Report to admin

## Step 5: Git Workflow (Updates)

### Making Changes Locally
```bash
# Make edits to bot.py or config.py

# Stage changes
git add .

# Commit
git commit -m "Add new feature: block more extensions"

# Push to GitHub
git push origin main
```

Render will **automatically redeploy** when you push!

### Monitor Deployment
- Go to Render dashboard
- Click your service
- View real-time logs
- See deployment status

## 🔒 Security Checklist

- [ ] `.env` file is in `.gitignore` (don't commit secrets!)
- [ ] `.env.example` exists (without secrets)
- [ ] Bot token is kept secret
- [ ] Admin ID is private
- [ ] All code is reviewed before push

## ⚙️ Environment Variables Explained

### `BOT_TOKEN`
- Telegram bot authentication token
- Get from [@BotFather](https://t.me/botfather)
- Format: `123456:ABCDefghIjKlmnoPqrsTuvWxyz`

### `SPECIFIC_ADMIN_ID`
- Your Telegram user ID (receives violation reports)
- Get from [@userinfobot](https://t.me/userinfobot)
- Format: `123456789` (just numbers)

## 🚨 Troubleshooting

### Bot Status: "Build Failed"
```
Check logs for errors:
1. Click service
2. Scroll to "Logs"
3. Look for error messages
4. Common: missing requirements, Python syntax error
```

### Bot Status: "Query Timeout"
- Bot crashed or hung
- Check logs for errors
- Redeploy: Click "Manual Deploy" → "Latest Commit"

### Bot not responding in group
1. Check it's added to group
2. Check it has message delete permissions
3. Verify `BOT_TOKEN` is correct
4. Restart: Go to Render dashboard → Click service → "Restart Service"

### Can't send admin reports
- Verify `SPECIFIC_ADMIN_ID` is correct
- Admin must have started bot first (DM limitation)
- Check bot has permission to send messages

## 📊 Monitoring

### View Real-time Logs
1. Render Dashboard → Your Service
2. Scroll to "Logs" section
3. Refresh to see updates

### Typical Log Output
```
🤖 Pu_Sok - Telegram Security Bot Starting...
✅ Bot started successfully
👋 Welcomed [User] to group
🚨 Dangerous file from [User]: malware.exe
🗑️ Deleted message from [User]
✅ DM warning sent to [User] - Warning 1/3
📧 Admin report sent - [User] violation 1/3
```

## 🔄 Continuous Deployment

### Automatic Updates
1. Make local changes
2. `git push origin main`
3. Render detects change
4. Auto-builds and deploys (~2-3 min)
5. Bot updates live!

### Rollback (if needed)
```bash
# Revert last commit locally
git revert HEAD

# Push to deploy previous version
git push origin main
```

## 💾 Backup & Maintenance

### Database (if added later)
- Store in external database (MongoDB, PostgreSQL)
- Update connection string in `.env`

### Regular Updates
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Test locally
python bot.py

# Commit and push
git add requirements.txt
git commit -m "Update: dependencies"
git push origin main
```

## 🎓 Advanced: Custom Domain (Optional)

If you want custom domain instead of render.onrender.com:
1. Purchase domain (Namecheap, GoDaddy, etc.)
2. Render Dashboard → Service Settings
3. Add custom domain
4. Point DNS to Render nameservers

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **pyTelegramBotAPI**: https://github.com/eternnoir/pyTelegramBotAPI
- **Telegram Bot API**: https://core.telegram.org/bots/api

---

**Deployed on Render.com with ❤️ for UYFC-PV**

ពូសុខ - សន្តិសុខយាម 24/7 🛡️
