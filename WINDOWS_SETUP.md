# NetBox Interface Migration Tool - Windows Setup Guide

## Prerequisites on Windows

### 1. Install Git for Windows

1. Download from: https://git-scm.com/download/win
2. Run the installer
3. Choose "Git Bash" during installation (recommended)
4. Restart your computer

**Verify installation:**

Open PowerShell or Command Prompt:

```powershell
git --version
```

Should show: `git version 2.x.x`

### 2. Install Python 3

1. Download from: https://www.python.org/downloads/
2. Run installer
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"

**Verify installation:**

```powershell
python --version
pip --version
```

### 3. Install Visual Studio Code (Optional but Recommended)

- Download: https://code.visualstudio.com/
- Extensions to install:
  - Python
  - Git Graph

---

## Clone the Repository

### Option A: Using GitHub (Recommended for Windows)

#### Step 1: Create GitHub Account

1. Go to https://github.com
2. Sign up for free account
3. Verify email

#### Step 2: Create New Repository on GitHub

1. Click **+** icon → **New repository**
2. Name: `netbox-interface-migration`
3. Description: "NetBox device and interface migration tool with filtering"
4. Choose **Public** or **Private**
5. Do NOT check "Initialize with README"
6. Click **Create repository**

#### Step 3: Upload Local Repository

On your Linux server (one time):

```bash
cd /home/grahama/netbox-interface-migration

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/netbox-interface-migration.git

# Rename branch
git branch -M main

# Push to GitHub
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username.**

#### Step 4: Clone on Windows

On your Windows PC, open **Git Bash** or **PowerShell**:

```powershell
cd Documents
git clone https://github.com/YOUR_USERNAME/netbox-interface-migration.git
cd netbox-interface-migration
```

---

### Option B: Using GitLab (Alternative)

Similar to GitHub:

1. Create account at https://gitlab.com
2. Create new project
3. On Linux server:
   ```bash
   git remote add origin https://gitlab.com/YOUR_USERNAME/netbox-interface-migration.git
   git push -u origin main
   ```
4. On Windows:
   ```powershell
   git clone https://gitlab.com/YOUR_USERNAME/netbox-interface-migration.git
   ```

---

## Windows Setup - Step by Step

### Step 1: Create Virtual Environment

Open **PowerShell** in your project directory:

```powershell
# Navigate to repository
cd netbox-interface-migration

# Create virtual environment
python -m venv netbox_env

# Activate it
.\netbox_env\Scripts\Activate.ps1
```

**If you get an error about execution policy:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then run the Activate command again.

### Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Configure the Script

Open `netbox_json_migration_advanced.py` in your editor (VS Code recommended):

```powershell
code netbox_json_migration_advanced.py
```

Find and update these lines (around line 350):

```python
# Configuration
NETBOX_URL = "https://nbupg.homelan.local"
API_TOKEN = "nbt_SA3YmWPeJzAv.<YOUR_FULL_TOKEN>"
VERIFY_SSL = False
```

### Step 4: Test Connection

```powershell
python netbox_json_migration_advanced.py export --help
```

Should show the help menu without errors.

---

## Using the Tool on Windows

### Export Example

```powershell
python netbox_json_migration_advanced.py export "dci" "" export.json --cabled
```

### Import Example

```powershell
python netbox_json_migration_advanced.py import export.json "lightedge-chaska" "dci"
```

### View Logs

```powershell
# List log files
dir netbox_migration_*.log

# View latest log
Get-Content (Get-ChildItem netbox_migration_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1)

# Or in PowerShell:
tail -f netbox_migration_*.log
```

---

## Git Workflow on Windows

### Check Status

```powershell
git status
```

### View History

```powershell
git log --oneline
git log --graph --decorate --all
```

### Make Changes and Commit

```powershell
# Edit file
code netbox_json_migration_advanced.py

# Check what changed
git diff

# Stage changes
git add netbox_json_migration_advanced.py

# Commit
git commit -m "Update: Add new feature or fix"

# Push to GitHub
git push
```

### View Recent Changes

```powershell
git show HEAD
git diff HEAD~1
```

### Create a Tag (for releases)

```powershell
git tag v1.0.0
git push origin v1.0.0
```

---

## Common Windows Tasks

### Open in File Explorer

```powershell
explorer .
```

### Run Python Script Directly

```powershell
python netbox_json_migration_advanced.py export "dci" "" export.json
```

### Activate Virtual Environment (if needed again)

```powershell
.\netbox_env\Scripts\Activate.ps1
```

### Deactivate Virtual Environment

```powershell
deactivate
```

---

## Troubleshooting on Windows

### Issue: "command not found: git"

**Solution:** Git not installed or not in PATH
- Reinstall Git for Windows
- Restart PowerShell/Command Prompt
- Restart computer if needed

### Issue: "Python: command not found"

**Solution:** Python not in PATH
- Reinstall Python
- During installation, CHECK "Add Python to PATH"
- Restart PowerShell

### Issue: Virtual environment not activating

**Solution:**

```powershell
# Try full path
& ".\netbox_env\Scripts\Activate.ps1"

# Or set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "Permission denied" when pushing to Git

**Solution:** Use Personal Access Token instead of password

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Select scopes: `repo`, `gist`
4. Copy token
5. When Git asks for password, paste the token

### Issue: Git asks for username/password repeatedly

**Solution:** Store credentials

```powershell
git config --global credential.helper wincred
```

Or use SSH (advanced):

```powershell
ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\id_rsa
# Then add public key to GitHub
```

---

## File Locations on Windows

```
C:\Users\YourUsername\Documents\netbox-interface-migration\
├── netbox_json_migration_advanced.py
├── README.md
├── SETUP.md
├── GIT_SETUP.md
├── WINDOWS_SETUP.md (this file)
├── requirements.txt
├── netbox_env\                    (virtual environment)
├── export*.json                   (your exports)
└── .git\                          (git history)
```

### Common Paths

```powershell
# Project root
cd C:\Users\YourUsername\Documents\netbox-interface-migration

# View project files
dir

# View hidden .git directory
dir -Force
```

---

## Using Git GUI Tools on Windows

### GitHub Desktop (Easiest for Beginners)

1. Download: https://desktop.github.com/
2. Install
3. Sign in with GitHub account
4. Click "Clone repository"
5. Select: `YOUR_USERNAME/netbox-interface-migration`
6. Click "Clone"

**No command line needed!**

### Visual Studio Code (Recommended)

1. Install VS Code: https://code.visualstudio.com/
2. Open repository folder
3. Click "Source Control" (left sidebar)
4. All git operations available in UI
5. Built-in terminal for Python

### TortoiseGit (Windows Explorer Integration)

1. Download: https://tortoisegit.org/
2. Install
3. Right-click folder → TortoiseGit → Clone
4. Enter repository URL

---

## Recommended Windows Workflow

### Using GitHub Desktop (Easiest)

```
1. Clone repository with GitHub Desktop
2. Make changes in VS Code
3. GitHub Desktop shows changes
4. Write commit message
5. Click "Commit to main"
6. Click "Push origin"
```

### Using VS Code (Recommended)

```
1. Open folder: File → Open Folder
2. Edit files
3. Source Control tab (left sidebar)
4. Click + to stage
5. Write message
6. Click ✓ to commit
7. Click ... → Push
```

### Using Command Line (Advanced)

```powershell
cd C:\path\to\repo
git add .
git commit -m "message"
git push
```

---

## Quick Start Checklist

- [ ] Git for Windows installed
- [ ] Python 3 installed (with PATH)
- [ ] GitHub account created
- [ ] Repository created on GitHub
- [ ] Repository cloned to Windows
- [ ] Virtual environment created: `python -m venv netbox_env`
- [ ] Virtual environment activated: `.\netbox_env\Scripts\Activate.ps1`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Script configured with API token
- [ ] Test connection works: `python netbox_json_migration_advanced.py export --help`
- [ ] First commit made and pushed: `git push`

---

## Next Steps

1. **If using GitHub Desktop:** Just click buttons, no command line needed
2. **If using VS Code:** Use the Source Control panel on the left
3. **If using command line:** See "Git Workflow on Windows" section above
4. **Share repository URL** with your team: `https://github.com/YOUR_USERNAME/netbox-interface-migration`

---

## File Sharing Alternative (No Git Required)

If you don't want to use Git, you can share files directly:

```powershell
# Copy file to network share
Copy-Item netbox_json_migration_advanced.py \\server\share\netbox-tools\

# Or email the script
# Or use Dropbox/OneDrive/Google Drive
```

But **Git is recommended** because it:
- Tracks all changes
- Easy to revert mistakes
- Collaborate with team
- Version control/history

---

**Questions? See README.md for full operator documentation.**
