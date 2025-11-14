# Deployment Files Organization Guide

## 📁 How to Organize

### Step 1: Create deployment folder in your project

On your **development computer**:

```bash
cd takk_app/
mkdir deployment
```

### Step 2: Move deployment files into the folder

```bash
mv gunicorn.conf.py deployment/
mv nginx-takk.conf deployment/
mv takk.service deployment/
mv requirements.txt deployment/
mv deployment-check.sh deployment/
mv setup-deployment.sh deployment/
mv DEPLOYMENT.md deployment/
mv DEPLOYMENT-PREP.md deployment/
```

### Step 3: Make scripts executable

```bash
chmod +x deployment/setup-deployment.sh
chmod +x deployment/deployment-check.sh
```

### Step 4: Add to Git (optional but recommended)

```bash
git add deployment/
git commit -m "Add deployment configuration files"
```

## 🚀 How to Deploy

### On Your Dev Computer:

1. **Transfer project to server**:

```bash
# Option A: Using scp
scp -r takk_app/ user@server-ip:/home/user/

# Option B: Using rsync (faster, skips unchanged files)
rsync -avz --exclude 'node_modules' --exclude '__pycache__' \
    takk_app/ user@server-ip:/home/user/takk_app/

# Option C: Using Git
# Push to Git repo, then clone on server
```

### On The Server (EliteDesk):

2. **Move to production location**:

```bash
sudo mv /home/user/takk_app /opt/takk
sudo chown -R takk:takk /opt/takk
```

3. **Run setup script**:

```bash
cd /opt/takk
sudo bash deployment/setup-deployment.sh
```

This script will:
- ✅ Copy all config files to correct locations
- ✅ Set proper permissions
- ✅ Enable services
- ✅ Verify Nginx config
- ✅ Create log directories

4. **Follow the on-screen instructions** to:
- Install Python dependencies
- Build React app
- Configure server IP in Nginx
- Start services

## 📋 Your Final Project Structure

```
takk_app/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── leaderboard.py
│   └── components/
│       ├── src/
│       └── dist/          # Created by npm run build
├── catalog/
│   ├── manifest.json
│   ├── distractors.json
│   └── leaderboard.json
├── media/
│   ├── signs/
│   └── ui/
├── deployment/            # ← All deployment files here
│   ├── gunicorn.conf.py
│   ├── nginx-takk.conf
│   ├── takk.service
│   ├── requirements.txt
│   ├── setup-deployment.sh
│   ├── deployment-check.sh
│   ├── DEPLOYMENT.md
│   └── DEPLOYMENT-PREP.md
├── run.py
├── .env.development
├── .env.production
└── README.md
```

## 🔄 Updating After Changes

### If you update deployment configs:

**On dev computer:**
```bash
# Edit config
nano deployment/nginx-takk.conf

# Commit changes
git commit -am "Update nginx config"
```

**On server:**
```bash
# Pull changes (if using Git)
cd /opt/takk
sudo -u takk git pull

# Re-run setup script
sudo bash deployment/setup-deployment.sh

# Restart services
sudo systemctl restart takk nginx
```

### If you update application code:

**On server:**
```bash
cd /opt/takk

# Pull/copy new code
sudo -u takk git pull

# Rebuild React if frontend changed
cd app/components
sudo -u takk npm run build

# Restart Flask app
sudo systemctl restart takk
```

## 🧪 Testing

After setup, test from any device on your WiFi:

```bash
# On your dev computer or phone
./deployment/deployment-check.sh 192.168.1.100
```

Or manually:
- Browser: `http://192.168.1.100/`
- API test: `http://192.168.1.100/api/health`

## 📦 What Goes Where

| File | Development | Production |
|------|-------------|------------|
| gunicorn.conf.py | `deployment/` | `/opt/takk/` |
| nginx-takk.conf | `deployment/` | `/etc/nginx/sites-available/` |
| takk.service | `deployment/` | `/etc/systemd/system/` |
| requirements.txt | `deployment/` | `/opt/takk/` |
| setup-deployment.sh | `deployment/` | Run from `/opt/takk/` |
| deployment-check.sh | `deployment/` | Run from anywhere |

## 🎯 Quick Commands Reference

```bash
# Setup (first time only)
sudo bash deployment/setup-deployment.sh

# Install Python deps
sudo -u takk /opt/takk/venv/bin/pip install -r requirements.txt

# Build React
cd /opt/takk/app/components && sudo -u takk npm run build

# Start services
sudo systemctl start takk
sudo systemctl start nginx

# Check status
sudo systemctl status takk
sudo systemctl status nginx

# View logs
sudo journalctl -u takk -f

# Restart after changes
sudo systemctl restart takk
```

## ✨ Benefits of This Organization

1. **Clean separation** - Dev files stay separate from production configs
2. **Version controlled** - All configs tracked in Git
3. **Easy deployment** - One script does everything
4. **Portable** - Deploy to multiple servers with same configs
5. **Maintainable** - Clear where everything lives

---

**You're all set!** Keep deployment files in the `deployment/` folder, and use `setup-deployment.sh` to deploy them to the server.