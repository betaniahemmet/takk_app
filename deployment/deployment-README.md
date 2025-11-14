# TAKK Deployment Files

This folder contains all configuration files needed to deploy TAKK to production.

## 📋 Files

| File | Purpose |
|------|---------|
| `gunicorn.conf.py` | Gunicorn web server configuration |
| `nginx-takk.conf` | Nginx reverse proxy configuration |
| `takk.service` | Systemd service definition |
| `requirements.txt` | Python production dependencies |
| `setup-deployment.sh` | Automated setup script ⭐ |
| `deployment-check.sh` | Verify deployment is working |
| `DEPLOYMENT.md` | Complete step-by-step guide |
| `DEPLOYMENT-PREP.md` | Pre-deployment checklist |
| `DEPLOYMENT-ORGANIZATION.md` | How to organize these files |

## 🚀 Quick Start

### 1. Transfer project to server
```bash
scp -r takk_app/ user@server-ip:/home/user/
```

### 2. Move to production directory
```bash
ssh user@server-ip
sudo mv /home/user/takk_app /opt/takk
sudo chown -R takk:takk /opt/takk
```

### 3. Run setup script
```bash
cd /opt/takk
sudo bash deployment/setup-deployment.sh
```

### 4. Follow on-screen instructions
The script will tell you what to do next!

## 📖 Documentation

- **First time deploying?** Read `DEPLOYMENT.md`
- **Want to organize files?** Read `DEPLOYMENT-ORGANIZATION.md`  
- **Ready to deploy?** Run `setup-deployment.sh`
- **Need to verify?** Run `deployment-check.sh`

## 💡 Usage

### Development
Keep these files in your `deployment/` folder. They don't affect development.

### Production  
Run `setup-deployment.sh` to copy files to their correct system locations.

## 🔧 Customization

Before deploying, edit:
- `nginx-takk.conf` - Set your server IP in `server_name`
- `.env.production` - Set your production environment variables

## ✅ After Setup

Verify everything works:
```bash
./deployment/deployment-check.sh <your-server-ip>
```

---

**Need help?** Check `DEPLOYMENT.md` for detailed instructions.