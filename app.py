import telebot
from telebot import types
from flask import Flask
import threading
import os
import json

TOKEN = "6556057870:AAFPx3CJpAcGt-MfKRoAo00SlAEQ26XSS-s"
ADMIN_ID = 6090612274 
bot = telebot.TeleBot(TOKEN)
app = Flask('')

DATA_FILE = "accounts.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def home():
    return "🚀 Bot Quản Lý Acc Game đang Online!"

# --- GIAO DIỆN TIN NHẮN ĐẸP ---

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.chat.id != ADMIN_ID: return
    
    # Tạo nút bấm Inline (nút dưới tin nhắn)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("➕ Thêm Acc", callback_data="add_prompt")
    btn2 = types.InlineKeyboardButton("📋 Danh Sách", callback_data="list_accs")
    btn3 = types.InlineKeyboardButton("🔍 Tìm Kiếm", callback_data="search_prompt")
    btn4 = types.InlineKeyboardButton("⚙️ Hướng Dẫn", callback_data="help")
    markup.add(btn1, btn2, btn3, btn4)

    welcome_msg = (
        "<b>╔════════════════╗</b>\n"
        "<b>    🎮 GAME ACCOUNT MANAGER    </b>\n"
        "<b>╚════════════════╝</b>\n\n"
        "👋 Chào mừng <b>Master</b> quay trở lại!\n"
        "Hệ thống lưu trữ đã sẵn sàng phục vụ."
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode='HTML', reply_markup=markup)

# Xử lý khi nhấn nút
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "add_prompt":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📝 <b>Nhập theo cú pháp:</b>\n<code>/add [tên game] [user] [pass]</code>", parse_mode='HTML')
    
    elif call.data == "list_accs":
        data = load_data()
        if not data:
            bot.answer_callback_query(call.id, "Kho trống!")
            return
        
        res = "📋 <b>DANH SÁCH TÀI KHOẢN</b>\n"
        res += "────────────────────\n"
        for i, a in enumerate(data):
            res += f"📌 {i+1}. <b>{a['game']}</b> | 👤 <code>{a['user']}</code>\n"
        
        # Thêm nút làm mới
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Làm mới", callback_data="list_accs"))
        bot.edit_message_text(res, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)

    elif call.data == "search_prompt":
        bot.send_message(call.message.chat.id, "🔍 <b>Nhập:</b> <code>/find [tên game]</code>", parse_mode='HTML')

# Lệnh Add đẹp hơn
@bot.message_handler(commands=['add'])
def add_process(message):
    if message.chat.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        new_acc = {"game": parts[1].upper(), "user": parts[2], "pass": parts[3]}
        data = load_data()
        data.append(new_acc)
        save_data(data)
        
        success_msg = (
            "✅ <b>THÊM THÀNH CÔNG</b>\n"
            "────────────────────\n"
            f"🎮 Game: <b>{parts[1].upper()}</b>\n"
            f"👤 User: <code>{parts[2]}</code>\n"
            "────────────────────\n"
            "<i>Dữ liệu đã được mã hóa và lưu trữ.</i>"
        )
        bot.send_message(message.chat.id, success_msg, parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ <b>Lỗi!</b> Sai cú pháp rồi Master ơi.")

# Lệnh Find đẹp hơn
@bot.message_handler(commands=['find'])
def find_process(message):
    game_name = message.text.replace("/find", "").strip().upper()
    data = load_data()
    results = [a for a in data if game_name in a['game']]
    
    if results:
        for a in results:
            find_msg = (
                f"✨ <b>KẾT QUẢ TÌM KIẾM: {a['game']}</b>\n"
                "────────────────────\n"
                f"👤 Tài khoản: <code>{a['user']}</code>\n"
                f"🔑 Mật khẩu:  <code>{a['pass']}</code>\n"
                "────────────────────\n"
                "<i>(Chạm vào User hoặc Pass để sao chép)</i>"
            )
            bot.send_message(message.chat.id, find_msg, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "❌ <b>Không tìm thấy!</b> Vui lòng kiểm tra lại tên game.")

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
