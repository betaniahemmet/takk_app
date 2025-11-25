# TAKK Deployment Guide

This guide covers deploying the TAKK sign language app on Ubuntu Server with Nginx + Gunicorn.

## Prerequisites

- HP Elite Mini 600 G9 (or similar) with Ubuntu Server 24.04 installed
- SSH access to the server
- Server connected to your WiFi network with static IP

---

## 1. Initial Server Setup

### Update system
```bash
sudo apt update && sudo apt upgrade -y
```

### Install required packages
```bash
sudo apt install -y python3 python3-pip python3-venv nginx git
```

### Create dedicated user
```bash
sudo useradd -r -m -s /bin/bash takk
sudo usermod -aG www-data takk
```

---

## 2. Deploy Application Files

### Create directory structure
```bash
sudo mkdir -p /opt/takk
sudo mkdir -p /var/log/takk
sudo mkdir -p /var/run/takk
sudo chown -R takk:takk /opt/takk
sudo chown -R takk:takk /var/log/takk
sudo chown -R takk:takk /var/run/takk
```

### Copy your project
```bash
# From your development machine, copy files to server
scp -r takk_app/* takk@<server-ip>:/opt/takk/

# Or if you have Git repo:
# cd /opt/takk
# sudo -u takk git clone <your-repo-url> .
```

---

## 3. Setup Python Environment

### Create virtual environment
```bash
cd /opt/takk
sudo -u takk python3 -m venv venv
```

### Install Python dependencies
```bash
sudo -u takk /opt/takk/venv/bin/pip install --upgrade pip
sudo -u takk /opt/takk/venv/bin/pip install -r requirements.txt
```

---

## 4. Build React Frontend

### Install Node.js (if not already installed)
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### Build React app
```bash
cd /opt/takk/app/components
sudo -u takk npm install
sudo -u takk npm run build
```

This creates the production build in `/opt/takk/app/components/dist/`

---

## 5. Configure Environment

### Create production environment file
```bash
sudo -u takk cp /opt/takk/.env.example /opt/takk/.env.production
sudo -u takk nano /opt/takk/.env.production
```

### Edit `.env.production`:
```ini
FLASK_ENV=production
DEBUG=false
BASE_URL=http://<your-server-ip>
SANDBOX_MODE=false
```

---

## 6. Setup Gunicorn

### Copy gunicorn config
```bash
sudo cp gunicorn.conf.py /opt/takk/
sudo chown takk:takk /opt/takk/gunicorn.conf.py
```

### Test Gunicorn manually (optional)
```bash
cd /opt/takk
sudo -u takk venv/bin/gunicorn --config gunicorn.conf.py run:app
# Press Ctrl+C to stop
```

---

## 7. Setup Systemd Service

### Copy service file
```bash
sudo cp takk.service /etc/systemd/system/
```

### Enable and start service
```bash
sudo systemctl daemon-reload
sudo systemctl enable takk
sudo systemctl start takk
```

### Check status
```bash
sudo systemctl status takk
```

### View logs
```bash
sudo journalctl -u takk -f
```

---

## 8. Setup Nginx

### Copy nginx config
```bash
sudo cp nginx-takk.conf /etc/nginx/sites-available/takk
```

### Edit the config to set your IP
```bash
sudo nano /etc/nginx/sites-available/takk
# Change server_name to your server's IP or hostname
```

### Enable site
```bash
sudo ln -s /etc/nginx/sites-available/takk /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site
```

### Test nginx config
```bash
sudo nginx -t
```

### Restart nginx
```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 9. Set Static IP (Important!)

Your server needs a static IP on your WiFi network so users can always access it.

### Option A: Configure in your WiFi router
1. Log into your WiFi router admin panel
2. Find DHCP settings
3. Reserve IP for server's MAC address
4. Recommended IP: `192.168.1.100` (adjust to your network)

### Option B: Configure on Ubuntu Server
```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

Add/modify:
```yaml
network:
  version: 2
  renderer: networkd
  wifis:
    wlan0:
      dhcp4: no
      addresses:
        - 192.168.1.100/24  # Your static IP
      gateway4: 192.168.1.1  # Your router IP
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
      access-points:
        "YourWiFiName":
          password: "YourWiFiPassword"
```

Apply:
```bash
sudo netplan apply
```

---

## 10. Test Deployment

### From another device on the same WiFi:

Open browser and go to:
```
http://<server-ip>/
```

You should see the TAKK home page!

Test endpoints:
```
http://<server-ip>/api/health  # Should return {"ok": true}
http://<server-ip>/api/signs   # Should return list of signs
```

---

## 11. Monitoring & Maintenance

### Check service status
```bash
sudo systemctl status takk
sudo systemctl status nginx
```

### View logs
```bash
# Application logs
sudo journalctl -u takk -n 100 --no-pager

# Nginx access logs
sudo tail -f /var/log/nginx/takk-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/takk-error.log

# Gunicorn logs
sudo tail -f /var/log/takk/error.log
```

### Restart services after changes
```bash
# Restart Gunicorn
sudo systemctl restart takk

# Restart Nginx
sudo systemctl restart nginx

# Restart both
sudo systemctl restart takk nginx
```

### Update application
```bash
cd /opt/takk
sudo -u takk git pull  # If using Git
# Or copy new files with scp

# Rebuild React if needed
cd app/components
sudo -u takk npm run build

# Restart
sudo systemctl restart takk
```

---

## 12. Firewall (Optional but Recommended)

```bash
# Allow HTTP
sudo ufw allow 80/tcp

# Allow SSH (if you need remote access)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

---

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u takk -n 50

# Check if port 8000 is in use
sudo lsof -i :8000

# Check permissions
ls -la /opt/takk
```

### Nginx 502 Bad Gateway
```bash
# Check if Gunicorn is running
sudo systemctl status takk

# Check nginx error log
sudo tail -f /var/log/nginx/takk-error.log

# Test Gunicorn directly
cd /opt/takk
sudo -u takk venv/bin/python run.py
```

### Videos not loading
```bash
# Check media directory permissions
ls -la /opt/takk/media/

# Check nginx media location
sudo nano /etc/nginx/sites-available/takk
```

### Can't access from other devices
```bash
# Check if nginx is listening
sudo netstat -tlnp | grep :80

# Check firewall
sudo ufw status

# Test from server itself
curl http://localhost/api/health

# Verify static IP
ip addr show
```

---

## Performance Tuning

For 100 concurrent users, the default config should work fine. If you need more:

### Increase Gunicorn workers
Edit `/opt/takk/gunicorn.conf.py`:
```python
workers = 20  # Increase if needed
```

### Increase Nginx worker connections
Edit `/etc/nginx/nginx.conf`:
```nginx
events {
    worker_connections 2048;
}
```

---

## Quick Reference

### Useful Commands
```bash
# Service management
sudo systemctl start takk
sudo systemctl stop takk
sudo systemctl restart takk
sudo systemctl status takk

# View logs
sudo journalctl -u takk -f

# Test configs
sudo nginx -t
cd /opt/takk && venv/bin/python -c "from app import create_app; create_app()"

# Disk usage
df -h
du -sh /opt/takk/*
```

### Access URLs
```
http://<server-ip>/              # Home page
http://<server-ip>/game          # Levels
http://<server-ip>/dictionary    # Dictionary
http://<server-ip>/competition   # Competition
http://<server-ip>/feedback      # Feedback
http://<server-ip>/api/health    # Health check
```

---

## Security Checklist

- ✅ Running as non-root user (takk)
- ✅ Rate limiting enabled in Flask
- ✅ Path traversal protection
- ✅ Input validation on all endpoints
- ✅ Nginx security headers
- ⚠️ Consider HTTPS for production (not critical on local WiFi)

---

## Support

If you encounter issues:
1. Check logs: `sudo journalctl -u takk -n 100`
2. Test health endpoint: `curl http://localhost/api/health`
3. Verify file permissions: `ls -la /opt/takk`
4. Check network: `ip addr show` and `ping <server-ip>`

---

## Backup Strategy

### Weekly backup script
```bash
#!/bin/bash
# Save as /opt/takk/backup.sh

BACKUP_DIR="/home/takk/backups"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Backup data files
tar -czf $BACKUP_DIR/takk-data-$DATE.tar.gz \
    /opt/takk/catalog/ \
    /opt/takk/feedback.json

# Keep only last 4 weeks
find $BACKUP_DIR -name "takk-data-*.tar.gz" -mtime +28 -delete
```

Add to crontab:
```bash
sudo crontab -e
# Add: 0 2 * * 0 /opt/takk/backup.sh
```

---

Good luck with your deployment! 🎉