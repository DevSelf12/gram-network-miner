#!/usr/bin/env python3
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.contacts import ResolveUsernameRequest
import json

cfg = json.load(open("config.json"))
client = TelegramClient("gram_session", cfg["api_id"], cfg["api_hash"])

async def main():
    await client.start()
    
    # Try variations
    usernames = [
        "gram_network_bot",
        "gramnetwork_bot", 
        "GramNetworkBot",
        "gram_network_mining_bot",
        "gramnetwork",
        "gramnetworkbot",
        "Gram_Network_Bot",
        "gram_networkapp_bot",
        "gram_network",
    ]
    
    for u in usernames:
        try:
            result = await client(ResolveUsernameRequest(u))
            users = result.users
            if users:
                print(f"✅ @{u} → user_id={users[0].id}, first_name={users[0].first_name}")
            else:
                print(f"❌ @{u} → not found")
        except Exception as e:
            print(f"❌ @{u} → {e}")
    
    await client.disconnect()

asyncio.run(main())
\nEOF
