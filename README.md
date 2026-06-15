# ⛏ Gram Network Auto Miner

Auto-mining bot untuk **Gram Network** Telegram Mini App.
Pakai **Telethon userbot** → generate initData fresh otomatis, tidak perlu refresh manual.

## Fitur
- 🔄 Auto generate initData setiap cycle (via Telethon)
- ⛏ Auto start mining tiap 4 jam
- 💰 Auto claim tokens setelah session selesai
- 🎁 Auto claim daily reward
- 📊 Logging ke file + console
- 🔄 Auto-restart on crash (systemd)

---

## Tutorial

### Step 1 — Clone Repo

```bash
git clone https://github.com/DevSelf12/gram-network-miner.git
cd gram-network-miner
```

### Step 2 — Install Dependencies

```bash
pip install telethon requests
```

> **VPS (Ubuntu/Debian):**
> ```bash
> apt update && apt install -y python3 python3-pip
> pip3 install telethon requests
> ```

### Step 3 — Get Telegram API Credentials

1. Buka **https://my.telegram.org/apps**
2. Login dengan nomor HP kamu
3. Klik **"Create new application"**
4. Isi form:
   - **App title:** `GramMiner` (bebas)
   - **Short name:** `gramminer` (bebas)
   - **Platform:** pilih `Android`
5. Klik **Create** → dapatkan **api_id** (angka) dan **api_hash** (string)

### Step 4 — Edit config.json

```json
{
  "api_id": 12345678,
  "api_hash": "abcdef1234567890abcdef1234567890",
  "phone": "+628xxxxxxxxxx",
  "bot_username": "gram_network_bot"
}
```

| Field | Isi dari |
|-------|----------|
| `api_id` | my.telegram.org → angka |
| `api_hash` | my.telegram.org → string |
| `phone` | Nomor HP yang dipake login Telegram |
| `bot_username` | Username bot Gram Network (default: `gram_network_bot`) |

### Step 5 — First Run (Login Telegram)

```bash
python3 miner.py
```

Pertama kali jalan, Telethon minta:
1. **Nomor HP** → masukkan nomor yang sama dengan config
2. **Kode verifikasi** → cek Telegram, masukkan 5 digit kode
3. **Password (jika ada)** → kalau 2FA aktif

Session tersimpan otomatis ke `gram_session.session`.
**Login cukup sekali** — selanjutnya bot jalan otomatis.

### Step 6 — Cek Hasil

Kalau berhasil, outputnya seperti ini:

```
✅ Telegram client connected!
🔄 Getting fresh initData...
✅ Got fresh initData from Telegram!
==================================================
👤 Rizvan Alhafizh | HCA (@rizvanbaihaqi)
💰 Balance: 10.80 GRM ($0.00)
⛏  Mining: Inactive
⚡ Rate: 0.20 GRM/hr | Power: 20.00 GH/s
🪙 Earned: 0.80 GRM
🔋 Energy: 100 / 100
⏰ Time Left: 00:00:00
==================================================
⛏  Starting mining...
✅ Mining started! Session: 4h
💤 Sleeping 4 hours...
```

---

## Deploy ke VPS (24/7)

### Option A — Manual (screen/tmux)

```bash
# Install tmux
apt install -y tmux

# Buat session
tmux new -s gram-miner

# Jalankan bot
cd /path/to/gram-network-miner
python3 miner.py

# Keluar dari tmux (bot tetap jalan): Ctrl+B, lalu D
# Balik ke session: tmux attach -t gram-miner
```

### Option B — Systemd Service (Recommended)

```bash
# Copy files ke VPS
scp -r gram-network-miner/ root@VPS_IP:/opt/gram-miner/

# SSH ke VPS
ssh root@VPS_IP
cd /opt/gram-miner

# Jalankan setup
bash setup_vps.sh

# Login sekali (masukkan kode verifikasi)
python3 miner.py

# Start service
systemctl start gram-miner

# Cek status
systemctl status gram-miner

# Cek log real-time
tail -f miner.log
```

> ⚠️ **Penting:** Login (`python3 miner.py`) harus dilakukan SEBELUM `systemctl start`, supaya session file tersimpan.

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `api_id` / `api_hash` salah | Cek ulang di https://my.telegram.org/apps |
| Session expired | Jalankan `python3 miner.py` ulang untuk login |
| Bot username beda | Cek username bot Gram Network, update `config.json` |
| Mining tidak mulai | Cek log: `tail -miner.log` — mungkin API berubah |
| VPS tidak bisa login | Login di local dulu, upload `gram_session.session` ke VPS |

---

## File Structure

```
gram-network-miner/
├── miner.py           # Bot utama
├── config.json        # Konfigurasi (api_id, api_hash, phone)
├── gram_session.session  # Session Telegram (auto-generated)
├── miner.log          # Log aktivitas
├── setup_vps.sh       # Setup VPS one-click
└── README.md          # Dokumentasi ini
```

## How It Works

```
┌─────────────┐    RequestWebView     ┌──────────────┐
│  Telethon   │ ──────────────────►  │   Telegram   │
│  Userbot    │ ◄──────────────────  │   Server     │
│             │   Fresh initData     └──────────────┘
└──────┬──────┘
       │ POST /api/start_mining.php
       ▼
┌─────────────┐
│   Gram      │
│   Network   │
│   API       │
└─────────────┘
       │
       ▼ (sleep 4 hours)
       │ POST /api/claim_mining.php
       ▼
   💰 Tokens claimed → repeat
```

## License

MIT
