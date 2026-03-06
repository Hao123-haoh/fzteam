import telebot
from telebot import types
from flask import Flask
import threading
import os
import json
import time

# --- CẤU HÌNH ---
TOKEN = "6556057870:AAFPx3CJpAcGt-MfKRoAo00SlAEQ26XSS-s"
ADMIN_ID = 6090612274 
bot = telebot.TeleBot(TOKEN, threaded=False)
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
    return "🌐 Premium Account Manager with Image Support is Online!"

# --- GIAO DIỆN PREMIUM ---

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ THÊM ACC + 📸", callback_data="add_guide"),
        types.InlineKeyboardButton("📋 KHO ACC", callback_data="list"),
        types.InlineKeyboardButton("🔍 TÌM KIẾM", callback_data="search"),
        types.InlineKeyboardButton("⚙️ HỆ THỐNG", callback_data="sys")
    )
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.chat.id != ADMIN_ID: return
    
    welcome_text = (
        "<b>◈━━━━━━━ CONFIG ━━━━━━━◈</b>\n"
        "<b>   🤖 PREMIUM ACCOUNT MANAGER   </b>\n"
        "<b>◈━━━━━━━━━━━━━━━━━━━━━◈</b>\n\n"
        "👋 Chào mừng <b>Master Hảo</b>,\n"
        "Hệ thống đã sẵn sàng lưu trữ Media.\n\n"
        "📊 <i>Status: Running 🟢</i>\n"
        "🖼 <i>Media Support: Active ✅</i>"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=main_menu())

# Xử lý lệnh thêm Acc kèm Ảnh
@bot.message_handler(content_types=['photo'])
def handle_photo_add(message):
    if message.chat.id != ADMIN_ID: return
    if message.caption and message.caption.startswith('/add'):
        try:
            # Cú pháp: /add [Game] [User] [Pass] (viết trong phần chú thích ảnh)
            parts = message.caption.split()
            game, user, pwd = parts[1].upper(), parts[2], parts[3]
            
            # Lấy file_id của ảnh để lưu
            file_id = message.photo[-1].file_id
            
            data = load_data()
            data.append({"game": game, "user": user, "pass": pwd, "image": file_id})
            save_data(data)
            
            bot.reply_to(message, f"✅ <b>ĐÃ LƯU: {game}</b>\n(Kèm hình ảnh minh họa)", parse_mode='HTML')
        except:
            bot.reply_to(message, "⚠️ <b>LỖI:</b> Hãy ghi chú thích ảnh theo mẫu:\n<code>/add Game User Pass</code>", parse_mode='HTML')

# Xử lý tìm kiếm và hiển thị ảnh
@bot.message_handler(commands=['find'])
def find_acc(message):
    if message.chat.id != ADMIN_ID: return
    game_search = message.text.replace("/find", "").strip().upper()
    data = load_data()
    results = [a for a in data if game_search in a['game']]
    
    if results:
        for a in results:
            info = (
                f"🎮 <b>GAME: {a['game']}</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👤 User: <code>{a['user']}</code>\n"
                f"🔑 Pass: <code>{a['pass']}</code>\n"
                "━━━━━━━━━━━━━━━━━━"
            )
            if "image" in a and a['image']:
                bot.send_photo(message.chat.id, a['image'], caption=info, parse_mode='HTML')
            else:
                bot.send_message(message.chat.id, info, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "❌ Không tìm thấy!")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "add_guide":
        msg = "📸 <b>CÁCH THÊM ACC CÓ ẢNH:</b>\n\n1. Chọn ảnh muốn gửi.\n2. Ở phần <b>'Thêm chú thích'</b>, gõ:\n<code>/add Game User Pass</code>\n3. Nhấn gửi!"
        bot.send_message(call.message.chat.id, msg, parse_mode='HTML')
    elif call.data == "list":
        data = load_data()
        res = "📋 <b>DANH SÁCH ACC:</b>\n"
        for i, a in enumerate(data):
            res += f"{i+1}. <b>{a['game']}</b> - <code>{a['user']}</code>\n"
        bot.send_message(call.message.chat.id, res, parse_mode='HTML')
    bot.answer_callback_query(call.id)

def run_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    # Tự động nhận diện Port trên Render
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
