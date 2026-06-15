#!/usr/bin/env python3
"""
Gram Network Auto Miner - with Auto initData Refresh
=====================================================
Uses Telethon userbot to generate fresh Telegram initData on demand.
No manual refresh needed!

Setup:
  1. pip3 install telethon requests
  2. Get API credentials: https://my.telegram.org/apps
  3. Fill config.json
  4. python3 miner.py  (first run asks for phone + code)
"""

import requests
import json
import time
import sys
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from telethon import TelegramClient, functions, types
from urllib.parse import quote, unquote

# ── Paths ───────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
LOG_FILE = SCRIPT_DIR / "miner.log"

# ── Logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("gram-miner")

# ── Gram Network API ────────────────────────────────────────────────
BASE_URL = "https://app.gramnetwork.online/api"
SESSION_SECONDS = 4 * 3600  # 4 hours

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://app.gramnetwork.online",
    "Referer": "https://app.gramnetwork.online/",
}


def load_config():
    if not CONFIG_FILE.exists():
        log.error("config.json not found!")
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        return json.load(f)


async def get_fresh_initdata(client, bot_username="gramnetwork_bot"):
    """
    Get fresh initData by requesting WebApp view from Telegram.
    """
    try:
        from telethon.tl.functions.messages import RequestWebViewRequest
        from telethon.tl.functions.contacts import ResolveUsernameRequest
        from telethon.tl.types import InputUser

        # Resolve bot username to get proper InputUser
        result = await client(ResolveUsernameRequest(bot_username))
        users = result.users
        if not users:
            log.error(f"Could not resolve bot @{bot_username}")
            return None

        bot_user = users[0]
        bot_input = await client.get_input_entity(bot_user.id)

        # Get peer as InputPeer for the chat
        peer = await client.get_input_entity(bot_user.id)

        log.info(f"Resolved @{bot_username} → user_id={bot_user.id}")

        r = await client(RequestWebViewRequest(
            peer=peer,
            bot=bot_input,
            platform="android",
            from_bot_menu=False,
            url="https://app.gramnetwork.online/",
        ))

        url = r.url
        log.info(f"WebView URL: {url[:300]}...")

        if "tgWebAppData=" in url:
            raw = url.split("tgWebAppData=")[1]
            if "&tgWebAppVersion=" in raw:
                raw = raw.split("&tgWebAppVersion=")[0]
            init_data = unquote(raw)
            log.info("✅ Got fresh initData from Telegram!")
            log.info(f"initData length: {len(init_data)}")
            log.info(f"Has hash: {'hash=' in init_data}")
            log.info(f"Has signature: {'signature=' in init_data}")
            log.info(f"initData tail: ...{init_data[-200:]}")
            return init_data
        else:
            log.error(f"Could not extract initData from URL: {url[:100]}")
            return None

    except Exception as e:
        log.error(f"Failed to get initData: {type(e).__name__}: {e}")
        return None


def api_call(method, endpoint, init_data):
    """Make API call to Gram Network."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        if method == "GET":
            r = requests.get(f"{url}?initData={quote(init_data, safe='')}", headers=HEADERS, timeout=30)
        else:
            r = requests.post(url, headers=HEADERS, data=f"initData={quote(init_data, safe='')}", timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError:
        log.error(f"{method} {endpoint} → HTTP {r.status_code}: {r.text[:200]}")
        return None
    except Exception as e:
        log.error(f"{method} {endpoint} → {e}")
        return None


def fmt_time(seconds):
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def print_status(user):
    if not user:
        return
    log.info("=" * 50)
    log.info(f"👤 {user.get('first_name', 'N/A')} (@{user.get('username', 'N/A')})")
    log.info(f"💰 Balance: {user.get('total_balance', 0)} GRM (${user.get('usd_balance', 0)})")
    log.info(f"⛏  Mining: {user.get('mining_status', 'N/A')}")
    log.info(f"⚡ Rate: {user.get('mining_rate', 0)} GRM/hr | Power: {user.get('mining_power', 0)} GH/s")
    log.info(f"🪙 Earned: {user.get('tokens_earned', 0)} GRM")
    log.info(f"🔋 Energy: {user.get('energy', 'N/A')}")
    log.info(f"⏰ Time Left: {fmt_time(user.get('time_left', 0))}")
    log.info("=" * 50)


async def main():
    cfg = load_config()

    # ── Init Telethon ───────────────────────────────────────────────
    api_id = cfg["api_id"]
    api_hash = cfg["api_hash"]
    phone = cfg["phone"]
    bot_username = cfg.get("bot_username", "gramnetwork_bot")

    session_file = SCRIPT_DIR / "gram_session"
    password = cfg.get("password", None)
    client = TelegramClient(str(session_file), api_id, api_hash)

    # Login with proper 2FA handling
    await client.connect()
    if not await client.is_user_authorized():
        log.info(f"📱 Sending code to {phone}...")
        await client.send_code_request(phone)
        code = input("🔢 Enter the code you received: ")
        try:
            await client.sign_in(phone, code)
        except Exception as e:
            if "password" in str(e).lower() or "TwoStepVerificationError" in type(e).__name__:
                if password:
                    log.info("🔑 Using 2FA password from config...")
                    await client.sign_in(password=password)
                else:
                    log.info("🔑 2FA required. Enter your Telegram cloud password:")
                    pw = input("Password: ")
                    await client.sign_in(password=pw)
                    log.info("💡 Tip: add \"password\" to config.json so you don't need to type it again.")
            else:
                raise

    me = await client.get_me()
    log.info(f"✅ Logged in as {me.first_name} (@{me.username})")

    # ── Main loop ───────────────────────────────────────────────────
    while True:
        # Get fresh initData each cycle
        log.info("🔄 Getting fresh initData...")
        init_data = await get_fresh_initdata(client, bot_username)

        if not init_data:
            log.error("Failed to get initData. Retrying in 5 minutes...")
            await asyncio.sleep(300)
            continue

        # Get user data
        data = api_call("GET", "get_user_data.php", init_data)
        if not data or not data.get("success"):
            log.error(f"API error: {data}")
            await asyncio.sleep(300)
            continue

        user = data["user"]
        print_status(user)

        # Claim daily reward
        daily = api_call("POST", "claim_daily.php", init_data)
        if daily and daily.get("success"):
            log.info(f"🎁 Daily reward claimed!")

        mining_status = user.get("mining_status", "").lower()

        if mining_status == "active" or user.get("time_left", 0) > 0:
            # Wait for current session to finish
            time_left = user.get("time_left", 0)
            log.info(f"⛏  Mining active. Waiting {fmt_time(time_left)}...")

            await asyncio.sleep(min(time_left + 30, SESSION_SECONDS))

            # Claim
            log.info("💰 Claiming tokens...")
            claim = api_call("POST", "claim_mining.php", init_data)
            if claim and claim.get("success"):
                log.info(f"✅ Claimed!")
            else:
                log.info(f"⚠️  Claim: {claim}")
        else:
            # Start new session
            log.info("⛏  Starting mining...")
            result = api_call("POST", "start_mining.php", init_data)
            if result and result.get("success"):
                log.info(f"✅ Mining started! Session: 4h")
            else:
                log.info(f"⚠️  Start result: {result}")

            # Wait full session
            log.info(f"💤 Sleeping 4 hours...")
            await asyncio.sleep(SESSION_SECONDS)

            # Get fresh initData for claim
            init_data = await get_fresh_initdata(client, bot_username)
            if init_data:
                claim = api_call("POST", "claim_mining.php", init_data)
                if claim and claim.get("success"):
                    log.info(f"✅ Claimed after session!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("👋 Stopped")