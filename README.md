# ⛏ Gram Network Auto Miner (Auto Refresh)

Auto-mining bot untuk Gram Network Telegram Mini App.
**Tidak perlu refresh initData manual** — pakai Telethon userbot.

## Fitur
- 🔄 Auto generate initData fresh tiap cycle (via Telethon)
- ⛏ Auto start mining tiap 4 jam
- 💰 Auto claim tokens
- 🎁 Auto claim daily reward
- 📊 Logging ke file + console
- 🔄 Auto-restart on crash (systemd)

## Setup

### 1. Get Telegram API Credentials
1. Buka https://my.telegram.org/apps
2. Login nomor HP kamu
3. Buat app → dapatkan **api_id** dan **api_hash**

### 2. Edit config.json
```json
{
  "api_id": 12345678,
  "api_hash": "abcdef1234567890abcdef1234567890",
  "phone": "+628xxxxxxxxxx",
  "bot_username": "gram_network_bot"
}
```

### 3. First Run (Login)
```bash
python3 miner.py
# → Enter phone number
# → Enter verification code dari Telegram
# → Session tersimpan di gram_session.session
```

### 4. Deploy ke VPS
```bash
# Upload semua file + gram_session.session ke VPS
scp -r gram-network-miner/ root@VPS:/opt/gram-miner/

# Setup
ssh root@VPS
cd /opt/gram-miner
bash setup_vps.sh
systemctl start gram-miner
```

## Kenapa Pakai Telethon?

| Lama (manual)        | Baru (Telethon)           |
|---------------------|---------------------------|
| Refresh initData tiap hari | Auto generate sendiri |
| Buka browser manual | Tanpa browser              |
| Expire ~24 jam      | Selalu fresh               |

## Troubleshooting
- **Session expired**: Login ulang `python3 miner.py`
- **Bot username beda**: Cek username bot Gram Network di config
- **Logs**: `tail -f miner.log`
