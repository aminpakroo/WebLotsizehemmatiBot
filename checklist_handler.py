from telegram import Update
from telegram.ext import ContextTypes

questions = [
    "آیا پلن معاملاتی‌ت مشخصه؟",
    "دلیل ورودت چیه؟ (تحلیل تکنیکال / فاندامنتال / فقط حس؟)",
    "آیا ورودت با روند هست؟",
    "نسبت ریسک به ریوارد حداقل 1:2 هست؟",
    "حد ضرر و حد سود مشخص شده؟",
    "درصد ریسک به‌درستی محاسبه شده؟",
    "از نظر احساسی در آرامش هستی؟",
    "خبر اقتصادی مهمی در راه نیست؟",
    "بعد از ورود، به پلنت پایبند می‌مونی؟"
]

async def start_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE, users: dict, save_func):
    user_id = str(update.effective_user.id)
    users[user_id]['state'] = 'checklist_0'
    users[user_id]['checklist'] = []
    await update.message.reply_text("✅ بزن بریم! به هر سوال با ✅ یا ❌ جواب بده:")
    await update.message.reply_text(questions[0])
    save_func()

async def handle_checklist_response(update: Update, context: ContextTypes.DEFAULT_TYPE, users: dict, save_func):
    user_id = str(update.effective_user.id)
    state = users[user_id]['state']
    index = int(state.split('_')[1])

    answer = update.message.text.strip()
    if answer not in ['✅', '❌']:
        await update.message.reply_text("لطفاً فقط با ✅ یا ❌ جواب بده 🙏")
        return

    users[user_id]['checklist'].append(answer)
    index += 1

    if index < len(questions):
        users[user_id]['state'] = f'checklist_{index}'
        await update.message.reply_text(questions[index])
    else:
        users[user_id]['state'] = None
        positives = users[user_id]['checklist'].count('✅')

        if positives >= len(questions) - 2:
            await update.message.reply_text("🌟 وضعیتت عالیه! همه‌چی آمادست برای ورود 👌")
        else:
            await update.message.reply_text("⚠️ بعضی موارد رعایت نشده. شاید بهتر باشه فعلاً وارد معامله نشی!")

        del users[user_id]['checklist']

    save_func()
