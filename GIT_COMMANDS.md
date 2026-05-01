# Git Commands for Pu_Sok Bot

Complete Git commands to initialize the project and push to GitHub for Render.com deployment.

## 📋 Quick Command List

### 1. Initialize Git Repository
```bash
cd c:\Users\싼푼일반대글로벌교육리더십\Documents\TelegramBot
git init
```

### 2. Add All Files
```bash
git add .
```

### 3. Create Initial Commit
```bash
git commit -m "Initial commit: Pu_Sok - UYFC-PV Telegram Security Bot"
```

### 4. Create Main Branch (if needed)
```bash
git branch -M main
```

### 5. Add GitHub Remote Repository
```bash
git remote add origin https://github.com/YOUR_USERNAME/pu-sok-bot.git
```

### 6. Push to GitHub
```bash
git push -u origin main
```

---

## 📝 Detailed Step-by-Step Instructions

### STEP 1: Initialize Git
```powershell
# Open PowerShell or Command Prompt
# Navigate to project directory
cd "c:\Users\싼푼일반대글로벌교육리더십\Documents\TelegramBot"

# Initialize git repository
git init

# Output should show:
# Initialized empty Git repository in c:\Users\...\TelegramBot\.git\
```

### STEP 2: Verify Files
```powershell
# Check what files will be added
git status

# You should see:
# - bot.py
# - config.py
# - requirements.txt
# - Procfile
# - README.md
# - DEPLOYMENT_GUIDE.md
# - setup.py
# - .env.example
# - .gitignore
# - (any other files)
```

### STEP 3: Add All Files
```powershell
# Stage all files for commit
git add .

# Verify with:
git status

# Should show green "Changes to be committed:" with all files
```

### STEP 4: Create First Commit
```powershell
git commit -m "Initial commit: Pu_Sok - UYFC-PV Telegram Security Bot

- 3-strike warning system with automatic banning
- Dangerous file detection (.exe, .apk, etc.)
- URL/Link detection and removal
- Private DM warnings with group fallback
- Admin violation reports with forwarded messages
- Threading for responsive bot operation
- Khmer language support for UYFC-PV"
```

### STEP 5: Create Main Branch
```powershell
# If on 'master', rename to 'main'
git branch -M main

# Verify:
git branch
# Output: * main
```

### STEP 6: Create GitHub Repository

Visit: https://github.com/new

Fill in:
- **Repository name**: `pu-sok-bot`
- **Description**: Telegram Security Bot for UYFC-PV Prey Veng
- **Visibility**: Public or Private (your choice)
- **Initialize with README**: NO (we already have one)

Copy the HTTPS URL: `https://github.com/YOUR_USERNAME/pu-sok-bot.git`

### STEP 7: Add Remote Repository
```powershell
# Replace YOUR_USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/pu-sok-bot.git

# Verify:
git remote -v

# Output should show:
# origin  https://github.com/YOUR_USERNAME/pu-sok-bot.git (fetch)
# origin  https://github.com/YOUR_USERNAME/pu-sok-bot.git (push)
```

### STEP 8: Push to GitHub
```powershell
# Push main branch to GitHub
git push -u origin main

# First time may ask for authentication:
# Enter your GitHub username
# Enter your GitHub token (not password!)
#   → Go to https://github.com/settings/tokens
#   → Generate new token (classic)
#   → Select 'repo' scope
#   → Copy and paste when prompted

# Output:
# Enumerating objects: X, done.
# Counting objects: X%, done.
# ...
# To https://github.com/YOUR_USERNAME/pu-sok-bot.git
#  * [new branch]      main -> main
# Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## 🔄 Future Updates

After initial setup, use these commands for updates:

### Make Changes & Push
```bash
# Make edits to bot.py, config.py, etc.

# Check what changed
git status

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Update: Add more blocked file extensions"

# Push to GitHub
git push origin main
```

### Common Commit Messages
```bash
git commit -m "Feature: Add customizable file extensions"
git commit -m "Fix: Handle URL detection edge cases"
git commit -m "Update: Improve warning messages"
git commit -m "Docs: Update deployment instructions"
git commit -m "Refactor: Extract helper functions"
```

---

## 🐛 Common Issues & Solutions

### Issue: "fatal: not a git repository"
```bash
# Solution: Initialize git first
git init
```

### Issue: "fatal: 'origin' does not appear to be a 'git' repository"
```bash
# Solution: Add remote again
git remote add origin https://github.com/YOUR_USERNAME/pu-sok-bot.git
```

### Issue: "remote origin already exists"
```bash
# Solution: Remove and re-add
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/pu-sok-bot.git
```

### Issue: Authentication fails
```bash
# Solution: Use GitHub token instead of password
# 1. Go to https://github.com/settings/tokens
# 2. Click "Generate new token (classic)"
# 3. Select 'repo' scope
# 4. Copy token
# 5. Paste when Git asks for password (it says "password" but wants token)
```

### Issue: Files committed that shouldn't be (like .env)
```bash
# Remove file from git history
git rm --cached .env

# Add to .gitignore
echo ".env" >> .gitignore

# Commit removal
git add .
git commit -m "Remove: .env from tracking"
git push origin main
```

---

## 📊 Git Workflow Summary

```
Local Development
       ↓
git add .                  (Stage changes)
       ↓
git commit -m "..."        (Create snapshot)
       ↓
git push origin main       (Upload to GitHub)
       ↓
Render.com auto-deploys    (Bot updates live!)
```

---

## 🎯 Deployment Sequence

```
1. git init                                    ← Initialize repository
2. git add .                                   ← Add all files
3. git commit -m "Initial commit: ..."        ← Create first commit
4. git branch -M main                          ← Ensure main branch
5. git remote add origin <URL>                 ← Connect to GitHub
6. git push -u origin main                     ← Push to GitHub
7. Connect GitHub to Render.com                ← Deploy
8. Add environment variables (BOT_TOKEN, etc.) ← Configure
9. Click Deploy                                ← Live!
```

---

## ✅ Verification Checklist

After pushing to GitHub:

- [ ] Visit `https://github.com/YOUR_USERNAME/pu-sok-bot`
- [ ] Verify all files are visible
- [ ] `.env` file NOT in repository (only `.env.example`)
- [ ] `README.md` displays correctly
- [ ] File count matches local directory
- [ ] Recent commit visible in history

---

## 📚 Additional Git Commands

### View Commit History
```bash
git log
git log --oneline          # Short format
```

### View Changes Before Committing
```bash
git diff                   # Show changes
git diff --staged          # Show staged changes
```

### Undo Recent Changes
```bash
git restore <file>         # Undo changes in working directory
git restore --staged <file> # Unstage file
```

### Branches
```bash
git branch                 # List branches
git branch -a              # List all branches
git checkout -b feature    # Create new branch
git checkout main          # Switch to main
```

---

## 🎓 Learning Resources

- **Git Basics**: https://git-scm.com/book/en/v2/Getting-Started
- **GitHub Help**: https://docs.github.com/en
- **Render Deployment**: https://render.com/docs/deploy-from-github

---

## ❓ Still Having Issues?

1. **Check Git Installation**
   ```bash
   git --version
   ```

2. **Check Git Config**
   ```bash
   git config --list
   git config user.name "Your Name"
   git config user.email "your@email.com"
   ```

3. **Check Remote URL**
   ```bash
   git remote -v
   ```

---

**Ready to deploy! 🚀 Happy coding! 🤖**

ពូសុខ - សន្តិសុខយាម Telegram 🛡️
