# TAKK — Production Deployment Guide

Target platform: HP Elite Mini 600 G9 · Ubuntu Server 24.04 · public domain with HTTPS

---

## Table of Contents

1. [Server Prerequisites](#1-server-prerequisites)
2. [Deploy Application Files](#2-deploy-application-files)
3. [Python Environment & Dependencies](#3-python-environment--dependencies)
4. [Build React Frontend](#4-build-react-frontend)
5. [Environment Variables](#5-environment-variables)
6. [Systemd Service](#6-systemd-service)
7. [Nginx — HTTP Configuration](#7-nginx--http-configuration)
8. [SSL/HTTPS with Let's Encrypt](#8-sslhttps-with-lets-encrypt)
9. [DNS Configuration](#9-dns-configuration)
10. [SSH Key Authentication](#10-ssh-key-authentication)
11. [Firewall & Fail2ban](#11-firewall--fail2ban)
12. [Post-Deployment Testing Checklist](#12-post-deployment-testing-checklist)
13. [Rollback Procedure](#13-rollback-procedure)
14. [Ongoing Maintenance](#14-ongoing-maintenance)

---

## 1. Server Prerequisites

### OS

Ubuntu Server 24.04 LTS (minimal install, no GUI needed).

### System packages

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    python3 python3-pip python3-venv \
    nginx \
    redis-server \
    git \
    curl \
    certbot python3-certbot-nginx \
    ufw
```

### Node.js (for building the React frontend)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Verify:
```bash
node --version   # should be v20.x
npm --version
python3 --version
nginx -v
redis-server --version
```

### Dedicated service user

```bash
sudo useradd -r -m -s /bin/bash takk
sudo usermod -aG www-data takk
```

### Directory structure

```bash
sudo mkdir -p /opt/takk
sudo mkdir -p /var/log/takk
sudo mkdir -p /var/run/takk
sudo chown -R takk:takk /opt/takk /var/log/takk /var/run/takk
```

---

## 2. Deploy Application Files

### Option A — copy from dev machine (rsync)

```bash
# From your development machine:
rsync -avz --exclude venv --exclude node_modules --exclude __pycache__ \
    takk_app/ takk@<server-ip>:/opt/takk/
```

### Option B — Git

```bash
cd /opt/takk
sudo -u takk git clone <your-repo-url> .
```

### Enable and start Redis

```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
sudo systemctl status redis-server   # should show active (running)
```

---

## 3. Python Environment & Dependencies

```bash
cd /opt/takk

sudo -u takk python3 -m venv venv
sudo -u takk venv/bin/pip install --upgrade pip
sudo -u takk venv/bin/pip install -r deployment/requirements.txt
```

Verify:
```bash
sudo -u takk venv/bin/python -c "from app import create_app; create_app(); print('OK')"
```

---

## 4. Build React Frontend

```bash
cd /opt/takk/app/components

sudo -u takk npm install
sudo -u takk npm run build
```

The production build lands in `/opt/takk/app/components/dist/`. Nginx serves static files directly from there.

Verify:
```bash
ls /opt/takk/app/components/dist/   # should contain index.html and assets/
```

---

## 5. Environment Variables

Create the production env file (do **not** commit this file to git):

```bash
sudo -u takk cp /opt/takk/.env.production /opt/takk/.env.production.bak  # backup if it exists
sudo nano /opt/takk/.env.production
```

Required contents:

```ini
FLASK_ENV=production
DEBUG=False
BASE_URL=https://takk.betaniahemmet.se
SANDBOX_MODE=false

# Analytics dashboard password — change this from the default!
# Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
ANALYTICS_KEY=<strong-random-secret>

# Redis — localhost is fine if Redis is on the same machine
REDIS_URL=redis://localhost:6379
```

Set strict permissions:
```bash
sudo chmod 600 /opt/takk/.env.production
sudo chown takk:takk /opt/takk/.env.production
```

> **Security note:** The default `ANALYTICS_KEY=4242` in `.env.production` must be replaced
> with a strong secret before going live. The analytics dashboard at `/analytics` is the
> only thing protecting access to all usage data.

---

## 6. Systemd Service

```bash
# Copy the service file
sudo cp /opt/takk/deployment/takk.service /etc/systemd/system/takk.service

# Copy gunicorn config
sudo cp /opt/takk/deployment/gunicorn.conf.py /opt/takk/gunicorn.conf.py
sudo chown takk:takk /opt/takk/gunicorn.conf.py

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable takk
sudo systemctl start takk

# Verify
sudo systemctl status takk
```

Gunicorn listens on `127.0.0.1:8000` with 9 workers (tuned for the i3-12100T's 4 cores).

Check logs:
```bash
sudo journalctl -u takk -f
```

---

## 7. Nginx — HTTP Configuration

> Complete this step first (HTTP only), then add HTTPS in the next step.
> Certbot needs a working HTTP server to complete the ACME challenge.

```bash
sudo cp /opt/takk/deployment/nginx-takk.conf /etc/nginx/sites-available/takk

# Edit server_name to your real domain
sudo nano /etc/nginx/sites-available/takk
# Change:  server_name takk.local;
# To:      server_name takk.betaniahemmet.se;

sudo ln -s /etc/nginx/sites-available/takk /etc/nginx/sites-enabled/takk
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t            # must say "syntax is ok"
sudo systemctl enable nginx
sudo systemctl restart nginx
```

Quick smoke test (from the server itself):
```bash
curl -s http://localhost/api/health
# Expected: {"ok": true, ...}
```

---

## 8. SSL/HTTPS with Let's Encrypt

### Prerequisites

- Your domain's DNS A record must already point to this server's public IP (see §9).
- Port 80 must be reachable from the internet (certbot's HTTP-01 challenge).

### Obtain certificate

```bash
sudo certbot --nginx -d takk.betaniahemmet.se
```

Certbot will:
1. Verify domain ownership via HTTP-01 challenge
2. Issue the certificate to `/etc/letsencrypt/live/takk.betaniahemmet.se/`
3. Automatically rewrite your nginx config to add HTTPS and an HTTP→HTTPS redirect

### What the rewritten nginx config should look like

After certbot runs, verify `/etc/nginx/sites-available/takk` contains two server blocks:

```nginx
# HTTP → HTTPS redirect (certbot adds this)
server {
    listen 80;
    server_name takk.betaniahemmet.se;
    return 301 https://$host$request_uri;
}

# HTTPS (certbot adds ssl_certificate lines here)
server {
    listen 443 ssl;
    server_name takk.betaniahemmet.se;
    ssl_certificate     /etc/letsencrypt/live/takk.betaniahemmet.se/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/takk.betaniahemmet.se/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    # ... rest of your location blocks
}
```

Test and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Add HSTS header

Once HTTPS is confirmed working, add this to the HTTPS server block in your nginx config:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

Then reload nginx.

### Auto-renewal

Certbot installs a systemd timer automatically. Verify:
```bash
sudo systemctl status certbot.timer
sudo certbot renew --dry-run    # test renewal without actually renewing
```

Certificates renew automatically before they expire (90-day cycle).

---

## 9. DNS Configuration

You need an **A record** pointing your domain to the server's public IP.

| Type | Name                       | Value              | TTL  |
|------|----------------------------|--------------------|------|
| A    | takk.betaniahemmet.se      | `<public-ip>`      | 3600 |

Steps:
1. Find your server's public IP: `curl -s ifconfig.me`
2. Log in to your DNS provider (the registrar for `betaniahemmet.se`)
3. Add the A record above
4. Wait for propagation (usually minutes, up to 24 h)

Verify propagation:
```bash
dig takk.betaniahemmet.se +short   # should return your server's public IP
```

### If the server is behind NAT (router)

If the server is on a local network and you're using your router's public IP:

1. Configure **port forwarding** on the router: external 80 → server:80, external 443 → server:443
2. Point the DNS A record to the router's public IP
3. Consider setting a static local IP for the server (DHCP reservation or netplan)

---

## 10. SSH Key Authentication

Set this up **before** disabling password login, and test the key login in a second terminal
before closing your existing session.

### On your dev machine — generate a key pair (skip if you already have one)

```bash
ssh-keygen -t ed25519 -C "takk-server"
# Creates ~/.ssh/id_ed25519 (private) and ~/.ssh/id_ed25519.pub (public)
```

### Copy the public key to the server

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub takk@<server-ip>
# Or manually: cat ~/.ssh/id_ed25519.pub | ssh takk@<server-ip> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### Test key login (do this before the next step)

Open a **new terminal** and verify you can log in without a password:
```bash
ssh -i ~/.ssh/id_ed25519 takk@<server-ip>
```

### Harden SSH daemon

```bash
sudo nano /etc/ssh/sshd_config
```

Set or confirm these values:
```
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
```

Apply:
```bash
sudo systemctl reload sshd
```

Verify you can still log in from a new terminal before closing your current session.

---

## 11. Firewall & Fail2ban

### UFW

```bash
sudo ufw allow 22/tcp     # SSH — do this FIRST or you'll lock yourself out
sudo ufw allow 80/tcp     # HTTP (needed for certbot renewal)
sudo ufw allow 443/tcp    # HTTPS

sudo ufw enable
sudo ufw status
```

Redis (6379) and Gunicorn (8000) must **not** be opened — they only listen on localhost.

### Fail2ban

Fail2ban watches logs and temporarily bans IPs with too many failed attempts.

```bash
sudo apt install -y fail2ban
```

Create a local config (never edit the default `jail.conf` directly — it gets overwritten on upgrades):

```bash
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port    = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s

[nginx-http-auth]
enabled  = true
logpath  = /var/log/nginx/takk-error.log

[nginx-botsearch]
enabled  = true
logpath  = /var/log/nginx/takk-access.log
maxretry = 10
```

Enable and start:
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

Check status:
```bash
sudo fail2ban-client status
sudo fail2ban-client status sshd    # shows banned IPs for SSH jail
```

Unban an IP if needed:
```bash
sudo fail2ban-client set sshd unbanip <ip-address>
```

---

## 12. Post-Deployment Testing Checklist

Run these from a device outside the server after completing all steps.

### Infrastructure

- [ ] `curl -I https://takk.betaniahemmet.se` returns `200 OK` with `Strict-Transport-Security` header
- [ ] `curl -I http://takk.betaniahemmet.se` returns `301` redirect to HTTPS
- [ ] SSL certificate is valid: `echo | openssl s_client -connect takk.betaniahemmet.se:443 2>/dev/null | openssl x509 -noout -dates`
- [ ] SSH key login works: `ssh -i ~/.ssh/id_ed25519 takk@<server-ip>`
- [ ] Password login is rejected: `ssh -o PreferredAuthentications=password takk@<server-ip>` → `Permission denied`
- [ ] Fail2ban is running: `sudo fail2ban-client status` shows `sshd` jail active

### Application endpoints

```bash
BASE=https://takk.betaniahemmet.se

# Health
curl -s $BASE/api/health
# Expected: {"ok": true, "version": "..."}

# Signs list
curl -s $BASE/api/signs | python3 -m json.tool | head -20

# Levels
curl -s $BASE/api/levels

# Leaderboard
curl -s $BASE/api/scores

# Analytics (should reject without key)
curl -s $BASE/api/analytics
# Expected: {"error": "unauthorized"}

# Analytics with correct key
curl -s -H "X-Analytics-Key: <your-key>" $BASE/api/analytics
```

### Rate limiting

```bash
# Hit /api/analytics 6 times rapidly — the 6th should return 429
for i in {1..6}; do
    echo -n "Request $i: "
    curl -s -o /dev/null -w "%{http_code}" $BASE/api/analytics
    echo
done
```

### Frontend

- [ ] Home page loads and displays correctly
- [ ] `/game` — levels page loads, signs display with video
- [ ] `/dictionary` — dictionary page loads
- [ ] `/competition` — competition page loads
- [ ] Videos play (checks that `/media/` nginx alias and file permissions are correct)
- [ ] Feedback form submits without error

### Services on server

```bash
sudo systemctl status takk nginx redis-server
sudo journalctl -u takk -n 20 --no-pager   # no ERROR lines
sudo tail -20 /var/log/nginx/takk-error.log  # should be empty
```

---

## 13. Rollback Procedure

### Fast rollback (restart previous working state)

If you just deployed and something broke immediately:

```bash
# On the server — stop the broken service
sudo systemctl stop takk

# If deployed via git: revert to previous commit
cd /opt/takk
sudo -u takk git log --oneline -10    # find the last good commit hash
sudo -u takk git checkout <good-commit-hash>

# Rebuild frontend if JS changed
cd /opt/takk/app/components
sudo -u takk npm run build

# Reinstall Python deps if requirements changed
sudo -u takk /opt/takk/venv/bin/pip install -r deployment/requirements.txt

# Restart
sudo systemctl start takk
sudo systemctl status takk
```

### Rollback nginx config

```bash
# Certbot backs up the nginx config before modifying it
ls /etc/nginx/sites-available/   # look for takk.conf.certbot-* backup files

# Restore a backup
sudo cp /etc/nginx/sites-available/takk.conf.certbot-backup-<timestamp> \
        /etc/nginx/sites-available/takk
sudo nginx -t && sudo systemctl reload nginx
```

### If the service won't start at all

```bash
# Read the last 50 log lines
sudo journalctl -u takk -n 50 --no-pager

# Common causes:
#   - .env.production missing or wrong path
#   - Python import error (check venv/deps)
#   - Port 8000 already in use: sudo lsof -i :8000

# Test the app directly (outside gunicorn) to see Python errors
cd /opt/takk
sudo -u takk venv/bin/python run.py
```

### Full restore from backup

```bash
# Restore data files from backup (catalog, feedback)
BACKUP=/home/takk/backups/takk-data-<date>.tar.gz
sudo tar -xzf $BACKUP -C /

sudo systemctl restart takk
```

---

## 14. Ongoing Maintenance

### Deploying updates

```bash
cd /opt/takk

# Pull latest code
sudo -u takk git pull

# Rebuild frontend if React files changed
cd app/components
sudo -u takk npm run build
cd /opt/takk

# Reinstall Python deps if requirements changed
sudo -u takk venv/bin/pip install -r deployment/requirements.txt

# Reload gunicorn gracefully (zero downtime)
sudo systemctl reload takk
# If reload isn't enough:
sudo systemctl restart takk
```

### View logs

```bash
sudo journalctl -u takk -f                   # live app logs
sudo tail -f /var/log/nginx/takk-access.log  # nginx access
sudo tail -f /var/log/nginx/takk-error.log   # nginx errors
sudo tail -f /var/log/takk/error.log         # gunicorn errors
```

### Weekly backup (cron)

```bash
sudo crontab -e
# Add:
0 2 * * 0 tar -czf /home/takk/backups/takk-data-$(date +\%Y\%m\%d).tar.gz /opt/takk/catalog/ /opt/takk/feedback.json && find /home/takk/backups -name "takk-data-*.tar.gz" -mtime +28 -delete
```

### Cert renewal check

```bash
sudo certbot renew --dry-run
```

Certbot's systemd timer runs this automatically twice a day. No manual action needed unless dry-run shows errors.
