#!/usr/bin/env python3
"""Test Gram Network API from VPS"""
import requests
from urllib.parse import unquote, quote
from telethon import TelegramClient
from telethon.tl.functions.messages import RequestWebViewRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
import json, asyncio

cfg = json.load(open("config.json"))
BASE_URL = "https://app.gramnetwork.online/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://app.gramnetwork.online",
    "Referer": "https://app.gramnetwork.online/",
}

async def main():
    # Connect
    client = TelegramClient("gram_session", cfg["api_id"], cfg["api_hash"])
    await client.start()
    me = await client.get_me()
    print(f"Logged in as: {me.first_name} (@{me.username})")
    
    # Resolve bot
    result = await client(ResolveUsernameRequest(cfg.get("bot_username", "gramnetwork_bot")))
    bot_user = result.users[0]
    bot_input = await client.get_input_entity(bot_user.id)
    peer = await client.get_input_entity(bot_user.id)
    print(f"Bot: @{bot_user.username} (id={bot_user.id})")
    
    # Get WebView
    r = await client(RequestWebViewRequest(
        peer=peer, bot=bot_input, platform="android",
        from_bot_menu=False, url="https://app.gramnetwork.online/"
    ))
    url = r.url
    
    # Extract initData
    raw = url.split("tgWebAppData=")[1]
    if "&tgWebAppVersion=" in raw:
        raw = raw.split("&tgWebAppVersion=")[0]
    init_data = unquote(raw)
    
    print(f"initData length: {len(init_data)}")
    print(f"Has hash: {'hash=' in init_data}")
    
    # Test 1: quote encoded
    api_url = f"{BASE_URL}/get_user_data.php?initData={quote(init_data, safe='')}"
    print(f"\nURL length: {len(api_url)}")
    
    r1 = requests.get(api_url, headers=HEADERS, timeout=30)
    print(f"Test 1 (quote): HTTP {r1.status_code}")
    print(f"  Response: {r1.text[:300]}")
    
    # Test 2: requests params
    r2 = requests.get(f"{BASE_URL}/get_user_data.php", params={"initData": init_data}, headers=HEADERS, timeout=30)
    print(f"\nTest 2 (params): HTTP {r2.status_code}")
    print(f"  Response: {r2.text[:300]}")
    
    # Test 3: minimal headers
    r3 = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    print(f"\nTest 3 (minimal headers): HTTP {r3.status_code}")
    print(f"  Response: {r3.text[:300]}")
    
    await client.disconnect()

asyncio.run(main())

