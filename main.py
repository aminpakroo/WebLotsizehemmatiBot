
import logging
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
from messages import get_random_tip, get_random_psychology
from checklist_handler import start_checklist, handle_checklist_response

logging.basicConfig(level=logging.INFO)

USERS_FILE = 'users.json'

try:
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

def save_users():
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    first_name = update.effective_user.first_name

    if user_id not in users:
        users[user_id] = {
            "name": first_name,
            "visits": 1,
            "state": None
        }
        msg = f"سلام {first_name} 👋\nبه ربات مدیریت سرمایه آکادمی فارکس همتی خوش اومدی 💹"
    else:
        users[user_id]['visits'] += 1
        msg = f"خوش برگشتی {first_name} عزیز 🌟\nبار {users[user_id]['visits']} هست که به ما سر زدی!"

    save_users()

    keyboard = [
        [KeyboardButton("🎯 محاسبه لات سایز")],
        [KeyboardButton("📋 چک‌لیست معامله گری")],
        [KeyboardButton("🎓 پیام آموزشی امروز")],
        [KeyboardButton("📢 عضویت در کانال")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(msg, reply_markup=reply_markup)

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = str(update.effective_user.id)

    if text == "🎯 محاسبه لات سایز":
        await update.message.reply_text("لطفاً موجودی حسابت به دلار رو وارد کن:")
        users[user_id]['state'] = 'awaiting_balance'

    elif text == "📋 چک‌لیست معامله گری":
        await start_checklist(update, context, users, save_users)

    elif text == "🎓 پیام آموزشی امروز":
        tip = get_random_tip()
        psych = get_random_psychology()
        await update.message.reply_text(f"📚 {tip}\n🧠 {psych}")

    elif text == "📢 عضویت در کانال":
        await update.message.reply_text("📲 برای دریافت آموزش‌ها و تحلیل‌ها عضو کانال شوید:\nhttps://t.me/AcademyHemmati")

    elif users.get(user_id, {}).get('state') == 'awaiting_balance':
        try:
            balance = float(text)
            users[user_id]['balance'] = balance
            users[user_id]['state'] = 'awaiting_risk'
            await update.message.reply_text("درصد ریسک مورد نظرت رو وارد کن (مثلاً 2):")
        except:
            await update.message.reply_text("❗ لطفاً عدد معتبر وارد کن")

    elif users.get(user_id, {}).get('state') == 'awaiting_risk':
        try:
            risk = float(text)
            users[user_id]['risk'] = risk
            users[user_id]['state'] = 'awaiting_sl'
            await update.message.reply_text("مقدار حد ضرر (به پیپ) رو وارد کن:")
        except:
            await update.message.reply_text("❗ لطفاً عدد معتبر وارد کن")

    elif users.get(user_id, {}).get('state') == 'awaiting_sl':
        try:
            sl = float(text)
            balance = users[user_id]['balance']
            risk = users[user_id]['risk']
            risk_amount = balance * (risk / 100)
            lot_size = round(risk_amount / (sl * 10), 2)
            msg = f"✅ لات سایز مناسب: {lot_size} لاته\n(براساس {risk}% ریسک روی {balance}$ و SL: {sl} پیپ)"
            if risk >= 5:
                msg += "\n⚠️ ریسک بالاست! حتماً مطمئن باش از تصمیم‌ت."
            await update.message.reply_text(msg)
            users[user_id]['state'] = None
        except:
            await update.message.reply_text("❗ مقدار وارد شده نادرسته، دوباره تلاش کن")

    elif users.get(user_id, {}).get('state', '').startswith('checklist_'):
        await handle_checklist_response(update, context, users, save_users)

    else:
        await update.message.reply_text("لطفاً یکی از گزینه‌ها رو از منوی پایین انتخاب کن ✅")

if __name__ == '__main__':
    app = ApplicationBuilder().token("8065124749:AAH1viTOHcqh8JyHkCYWTetvIfM0Cs8ImRM").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running via Webhook...")
    app.run_webhook(listen="0.0.0.0", port=8080, url_path="8065124749:AAH1viTOHcqh8JyHkCYWTetvIfM0Cs8ImRM",
                    webhook_url="https://yourrenderdomain.onrender.com/8065124749:AAH1viTOHcqh8JyHkCYWTetvIfM0Cs8ImRM")
