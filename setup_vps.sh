#!/bin/bash
# Gram Network Miner - VPS Setup
# Run: bash setup_vps.sh

set -e
INSTALL_DIR="$(pwd)"

echo "🚀 Setting up Gram Network Miner..."

# Install Python3 if needed
if ! command -v python3 &> /dev/null; then
    apt update && apt install -y python3 python3-pip
fi

# Install dependencies
pip3 install telethon requests --break-system-packages 2>/dev/null || pip3 install telethon requests

chmod +x miner.py

# Systemd service
cat > /etc/systemd/system/gram-miner.service << EOF
[Unit]
Description=Gram Network Auto Miner (Telethon)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
ExecStart=/usr/bin/python3 ${INSTALL_DIR}/miner.py
Restart=always
RestartSec=60
StandardOutput=append:${INSTALL_DIR}/miner.log
StandardError=append:${INSTALL_DIR}/miner.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gram-miner

echo ""
echo "✅ Installed!"
echo ""
echo "⚠️  FIRST RUN (to login Telegram):"
echo "   cd ${INSTALL_DIR} && python3 miner.py"
echo "   → Enter phone number + verification code"
echo "   → Session saved to gram_session.session"
echo ""
echo "   Then: systemctl start gram-miner"
echo ""
echo "   Logs:    tail -f ${INSTALL_DIR}/miner.log"
echo "   Status:  systemctl status gram-miner"
