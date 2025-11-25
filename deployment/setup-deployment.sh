#!/bin/bash
# setup-deployment.sh - Setup TAKK deployment files on the server
# Run this script on the EliteDesk after copying the project files

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "TAKK Deployment Setup Script"
echo -e "==========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root or with sudo${NC}"
    echo "Usage: sudo bash setup-deployment.sh"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    echo -e "${RED}Error: run.py not found${NC}"
    echo "Please run this script from the /opt/takk directory"
    exit 1
fi

DEPLOY_DIR="deployment"

# Check if deployment directory exists
if [ ! -d "$DEPLOY_DIR" ]; then
    echo -e "${RED}Error: deployment/ directory not found${NC}"
    echo "Make sure deployment files are in /opt/takk/deployment/"
    exit 1
fi

echo -e "${YELLOW}This script will:${NC}"
echo "  1. Copy Gunicorn config to /opt/takk/"
echo "  2. Copy Nginx config to /etc/nginx/sites-available/"
echo "  3. Copy systemd service to /etc/systemd/system/"
echo "  4. Set proper permissions"
echo "  5. Enable the service"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${BLUE}Starting setup...${NC}"
echo ""

# 1. Copy Gunicorn config
echo -n "Copying Gunicorn config... "
if cp "$DEPLOY_DIR/gunicorn.conf.py" /opt/takk/gunicorn.conf.py; then
    chown takk:takk /opt/takk/gunicorn.conf.py
    chmod 644 /opt/takk/gunicorn.conf.py
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

# 2. Copy requirements.txt
echo -n "Copying requirements.txt... "
if cp "$DEPLOY_DIR/requirements.txt" /opt/takk/requirements.txt; then
    chown takk:takk /opt/takk/requirements.txt
    chmod 644 /opt/takk/requirements.txt
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

# 3. Copy Nginx config
echo -n "Copying Nginx config... "
if cp "$DEPLOY_DIR/nginx-takk.conf" /etc/nginx/sites-available/takk; then
    chmod 644 /etc/nginx/sites-available/takk
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

# 4. Enable Nginx site
echo -n "Enabling Nginx site... "
if ln -sf /etc/nginx/sites-available/takk /etc/nginx/sites-enabled/takk; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

# 5. Remove default Nginx site
if [ -L /etc/nginx/sites-enabled/default ]; then
    echo -n "Removing default Nginx site... "
    rm /etc/nginx/sites-enabled/default
    echo -e "${GREEN}✓${NC}"
fi

# 6. Test Nginx config
echo -n "Testing Nginx config... "
if nginx -t 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    echo ""
    echo -e "${YELLOW}Nginx config test failed. Running test again to show errors:${NC}"
    nginx -t
    exit 1
fi

# 7. Copy systemd service
echo -n "Copying systemd service... "
if cp "$DEPLOY_DIR/takk.service" /etc/systemd/system/takk.service; then
    chmod 644 /etc/systemd/system/takk.service
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

# 8. Reload systemd
echo -n "Reloading systemd... "
if systemctl daemon-reload; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

# 9. Enable takk service
echo -n "Enabling takk service... "
if systemctl enable takk; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
fi

# 10. Create log directories
echo -n "Creating log directories... "
mkdir -p /var/log/takk
mkdir -p /var/run/takk
chown -R takk:takk /var/log/takk
chown -R takk:takk /var/run/takk
echo -e "${GREEN}✓${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "Setup Complete! ✓"
echo -e "==========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Install Python dependencies:"
echo -e "   ${BLUE}sudo -u takk /opt/takk/venv/bin/pip install -r requirements.txt${NC}"
echo ""
echo "2. Build React frontend:"
echo -e "   ${BLUE}cd /opt/takk/app/components && sudo -u takk npm run build${NC}"
echo ""
echo "3. Edit Nginx config with your server IP:"
echo -e "   ${BLUE}sudo nano /etc/nginx/sites-available/takk${NC}"
echo "   (Change server_name to your IP address)"
echo ""
echo "4. Start services:"
echo -e "   ${BLUE}sudo systemctl start takk${NC}"
echo -e "   ${BLUE}sudo systemctl restart nginx${NC}"
echo ""
echo "5. Check status:"
echo -e "   ${BLUE}sudo systemctl status takk${NC}"
echo -e "   ${BLUE}sudo systemctl status nginx${NC}"
echo ""
echo "6. View logs:"
echo -e "   ${BLUE}sudo journalctl -u takk -f${NC}"
echo ""
echo -e "${GREEN}Your deployment files are now in place!${NC}"
echo ""