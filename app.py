import telebot
from telebot import types
from flask import Flask
import threading
import os
import json

# --- CẤU HÌNH ---
TOKEN = "6556057870:AAFPx3CJpAcGt-MfKRoAo00SlAEQ26XSS-s"
ADMIN_ID = 6090612274 
bot = telebot.TeleBot(TOKEN)
app = Flask('')

DATA_FILE = "accounts.json"

# --- HÀM HỖ TRỢ DỮ LIỆU ---
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
    return "🚀 Game Manager Bot is Online!"

# --- THIẾT KẾ GIAO DIỆN TIN NHẮN ---

def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ Thêm Acc", callback_data="add"),
        types.InlineKeyboardButton("📋 Danh Sách", callback_data="list"),
        types.InlineKeyboardButton("🔍 Tìm Kiếm", callback_data="search"),
        types.InlineKeyboardButton("🗑️ Xóa Acc", callback_data="delete")
    )
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.chat.id != ADMIN_ID: return
    
    welcome_text = (
        "<b>╔════════════════════╗</b>\n"
        "<b>    🎮 QUẢN LÝ TÀI KHOẢN GAME    </b>\n"
        "<b>╚════════════════════╝</b>\n\n"
        "👋 Chào mừng Master <b>Hảo</b>!\n"
        "Hệ thống lưu trữ đã sẵn sàng phục vụ.\n"
        "<i>Vui lòng chọn chức năng dưới đây:</i>"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=get_main_menu())

# Xử lý các nút bấm Inline
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    bot.answer_callback_query(call.id)
    
    if call.data == "add":
        msg = "📝 <b>Gửi thông tin theo mẫu:</b>\n<code>/add [tên game] [user] [pass]</code>"
        bot.send_message(call.message.chat.id, msg, parse_mode='HTML')
        
    elif call.data == "list":
        data = load_data()
        if not data:
            bot.send_message(call.message.chat.id, "📭 <b>Kho trống!</b> Hãy thêm acc trước.")
            return
        
        res = "<b>📋 DANH SÁCH TÀI KHOẢN HIỆN CÓ</b>\n"
        res += "━━━━━━━━━━━━━━━━━━\n"
        for i, a in enumerate(data):
            res += f"📌 {i+1}. <b>{a['game']}</b> | 👤 <code>{a['user']}</code>\n"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Quay lại", callback_data="start_over"))
        bot.edit_message_text(res, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)

    elif call.data == "search":
        bot.send_message(call.message.chat.id, "🔍 <b>Nhập lệnh:</b> <code>/find [tên game]</code>", parse_mode='HTML')

    elif call.data == "start_over":
        welcome(call.message)

# Lệnh Add với tin nhắn phản hồi đẹp
@bot.message_handler(commands=['add'])
def process_add(message):
    if message.chat.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        game, user, pwd = parts[1].upper(), parts[2], parts[3]
        
        data = load_data()
        data.append({"game": game, "user": user, "pass": pwd})
        save_data(data)
        
        success_msg = (
            "✅ <b>THÊM THÀNH CÔNG!</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🎮 Game: <b>{game}</b>\n"
            f"👤 User: <code>{user}</code>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "<i>Dữ liệu đã được lưu trữ an toàn.</i>"
        )
        bot.send_message(message.chat.id, success_msg, parse_mode='HTML', reply_markup=get_main_menu())
    except:
        bot.reply_to(message, "❌ <b>Lỗi!</b> Cú pháp đúng: /add game user pass")

# Lệnh Find với định dạng copy nhanh
@bot.message_handler(commands=['find'])
def process_find(message):
    if message.chat.id != ADMIN_ID: return
    game_search = message.text.replace("/find", "").strip().upper()
    data = load_data()
    results = [a for a in data if game_search in a['game']]
    
    if results:
        for a in results:
            find_res = (
                f"✨ <b>KẾT QUẢ: {a['game']}</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👤 Tài khoản: <code>{a['user']}</code>\n"
                f"🔑 Mật khẩu:  <code>{a['pass']}</code>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "<i>(Chạm vào nội dung để Copy nhanh)</i>"
            )
            bot.send_message(message.chat.id, find_res, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "❌ <b>Không tìm thấy!</b> Vui lòng kiểm tra lại tên game.")

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # Khởi động Bot trong luồng riêng
    threading.Thread(target=run_bot).start()
    # Chạy Flask Server trên cổng Render cung cấp
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
