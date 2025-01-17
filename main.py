from flask import Flask, request, jsonify
import sqlite3
import requests

app = Flask(__name__)

# توكن البوت ورابط القناة
TOKEN = "7818149231:AAE7myiU3_omboOmq2YDlQBd5x0luMiSXO0"
CHANNEL_LINK = "https://t.me/d_tt3"

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

# إضافة مستخدم جديد
def add_user(user_id, username):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

# تحديث البيانات
def update_user_data(user_id, column):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {column} = {column} + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# استرجاع ترتيب المستخدمين
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

# نقطة البداية (اختبار)
@app.route("/")
def home():
    return jsonify({"message": "مرحباً! البوت يعمل على Vercel!"})

# استرجاع ترتيب المستخدمين
@app.route("/ranking", methods=["GET"])
def ranking():
    column = request.args.get("column", "visit_count")
    ranking_data = get_ranking(column)
    return jsonify({"ranking": ranking_data})

# استقبال بيانات من Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data and "message" in data:
        user_id = data["message"]["from"]["id"]
        username = data["message"]["from"].get("username", "Unknown")
        add_user(user_id, username)
    return jsonify({"status": "success"})

# إعداد قاعدة البيانات عند تشغيل التطبيق
if name == "__main__":
    setup_database()
    app.run(debug=True)