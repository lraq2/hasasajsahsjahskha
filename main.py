import os
import sqlite3
import requests
from telebot import TeleBot, types

# توكن البوت (تأكد من إضافته كمتغير بيئة إذا كنت تستخدم خدمات مثل Vercel)
TOKEN = os.getenv("TOKEN")  # ضع التوكن الخاص بك هنا إذا كنت تعمل محليًا
CHANNEL_LINK = "https://t.me/d_tt3"  # رابط القناة
bot = TeleBot(TOKEN)

# إعداد قاعدة البيانات
def setup_database():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        visit_count INTEGER DEFAULT 0,
        invite_count INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

# إضافة مستخدم جديد إلى قاعدة البيانات
def add_user(user_id, username):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

# تحديث عدد الزيارات أو الدعوات
def update_user_data(user_id, column):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {column} = {column} + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# استرجاع ترتيب الجترافي
def get_ranking(column):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT username, {column} FROM users ORDER BY {column} DESC LIMIT 10")
    ranking = cursor.fetchall()
    conn.close()
    return ranking

# التحقق من الاشتراك في القناة
def is_subscribed(user_id):
    try:
        check_url = f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id=@d_tt3&user_id={user_id}"
        response = requests.get(check_url).json()
        status = response.get('result', {}).get('status', '')
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

# بدء البوت
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"

    if not is_subscribed(user_id):
        bot.send_message(
            message.chat.id,
            f"⚠️ عذراً، يجب الاشتراك في القناة أولاً: [اضغط هنا]({CHANNEL_LINK})",
            parse_mode="Markdown"
        )
        return

    add_user(user_id, username)
    bot.send_message(
        message.chat.id,
        "مرحباً! 😊 اختر من القائمة: 👇",
        reply_markup=main_menu()
    )

# القائمة الرئيسية
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("👤 من زار ملفي الشخصي"),
        types.KeyboardButton("💌 الأشخاص الذين دعوتهم"),
        types.KeyboardButton("📈 ترتيب الجترافي"),
        types.KeyboardButton("❓ طريقة استخدام البوت"),
        types.KeyboardButton("📖 تعليمات وخطوات الدعوة")
    )
    return markup

# عرض عدد الزيارات
@bot.message_handler(func=lambda message: message.text == "👤 من زار ملفي الشخصي")
def profile_visits(message):
    user_id = message.from_user.id
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT visit_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    visit_count = result[0] if result else 0
    bot.send_message(message.chat.id, f"📊 عدد الأشخاص الذين زاروا ملفك: {visit_count}")

# عرض عدد الدعوات
@bot.message_handler(func=lambda message: message.text == "💌 الأشخاص الذين دعوتهم")
def invites(message):
    user_id = message.from_user.id
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT invite_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    invite_count = result[0] if result else 0
    bot.send_message(message.chat.id, f"📊 عدد الأشخاص الذين دعوتهم: {invite_count}")

# عرض ترتيب الجترافي
@bot.message_handler(func=lambda message: message.text == "📈 ترتيب الجترافي")
def show_ranking(message):
    ranking = get_ranking("visit_count")
    text = "🏆 ترتيب الجترافي:\n\n"
    for i, (username, score) in enumerate(ranking, 1):
        text += f"{i}. @{username} - {score} زيارة\n"
    bot.send_message(message.chat.id, text)

# شرح طريقة البوت
@bot.message_handler(func=lambda message: message.text == "❓ طريقة استخدام البوت")
def how_to_use(message):
    bot.send_message(
        message.chat.id,
        "✨ هذا البوت يساعدك في:\n"
        "- 👤 معرفة من زار ملفك الشخصي.\n"
        "- 💌 معرفة الأشخاص الذين دعوتهم.\n"
        "- 📈 مشاهدة ترتيبك بين الأعضاء.\n\n"
        "🚀 استمر بدعوة أصدقائك للحصول على ترتيب أعلى!"
    )

# تعليمات وخطوات الدعوة
@bot.message_handler(func=lambda message: message.text == "📖 تعليمات وخطوات الدعوة")
def instructions(message):
    bot.send_message(
        message.chat.id,
        f"🌟 **خطوات الدعوة والتفاعل مع البوت:**\n"
        "1️⃣ شارك رابط الدعوة الخاص بك مع أصدقائك.\n"
        "2️⃣ اجعلهم يشتركون في القناة الرسمية: [اضغط هنا]({CHANNEL_LINK}).\n"
        "3️⃣ عندما ينضم صديقك، ستزيد نقاط الدعوة لديك تلقائيًا.\n\n"
        "📊 كلما زادت نقاطك، ارتفع ترتيبك في الجترافي!",
        parse_mode="Markdown"
    )

# تشغيل البوت
if __name__ == "__main__":
    setup_database()
    bot.polling()
    
