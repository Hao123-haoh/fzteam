import requests
from bs4 import BeautifulSoup
import time
import threading
from flask import Flask
import os

# ==========================================
# CẤU HÌNH THÔNG SỐ (SỬA Ở ĐÂY)
# ==========================================
TOKEN = "6556057870:AAFPx3CJpAcGt-MfKRoAo00SlAEQ26XSS-s"
CHAT_ID = "6090612274"

# Danh sách nguồn quét
SOURCES = {
    "TikTok Shop (BlogGiamGia)": "https://bloggiamgia.vn/tiktok-shop",
    "Mã Hoàn Tiền (RioKupon)": "https://riokupon.com/ma-giam-gia-tiktok-shop",
}

# Cài đặt mặc định
config = {
    "keywords": ["0đ", "50%", "100k", "giảm", "voucher", "shopee"], # Shopee thêm cho vui
    "is_running": True
}

app = Flask('')

@app.route('/')
def home():
    status = "ON" if config["is_running"] else "OFF"
    return f"Bot Status: {status} | Keywords: {', '.join(config['keywords'])}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

# ==========================================
# TÍNH NĂNG 4: ĐIỀU KHIỂN QUA CHAT (XỬ LÝ LỆNH)
# ==========================================
def handle_commands():
    last_update_id = 0
    print("--- Hệ thống lắng nghe lệnh đã kích hoạt ---")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=20"
            response = requests.get(url, timeout=25).json()
            
            if "result" in response:
                for update in response["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        msg_text = update["message"]["text"].strip().lower()
                        user_id = str(update["message"]["chat"]["id"])

                        # Chỉ cho phép bạn điều khiển
                        if user_id == CHAT_ID:
                            if msg_text == "/start":
                                config["is_running"] = True
                                send_telegram("▶️ <b>Bot đã khởi động!</b> Đang săn deal...")
                            elif msg_text == "/pause":
                                config["is_running"] = False
                                send_telegram("⏸ <b>Bot đã tạm dừng.</b> Nhắn /start để chạy lại.")
                            elif msg_text == "/status":
                                tt = "Đang chạy 🔥" if config["is_running"] else "Đang ngủ 💤"
                                kw = ", ".join(config["keywords"])
                                send_telegram(f"📊 <b>TRẠNG THÁI BOT:</b>\n\n- Tình trạng: {tt}\n- Từ khóa: {kw}\n\n<i>Mẹo: Dùng /add [từ] để thêm từ khóa săn sale.</i>")
                            elif msg_text.startswith("/add"):
                                new_word = msg_text.replace("/add", "").strip()
                                if new_word:
                                    config["keywords"].append(new_word)
                                    send_telegram(f"✅ Đã thêm mục tiêu: <b>{new_word}</b>")
        except Exception as e:
            print(f"Lỗi lệnh: {e}")
        time.sleep(2)

# ==========================================
# TÍNH NĂNG 1 & 2: QUÉT ĐA NGUỒN & LỌC TỪ KHÓA
# ==========================================
def scrape_deals():
    processed_deals = set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("--- Hệ thống quét deal đã kích hoạt ---")
    
    while True:
        if config["is_running"]:
            for name, url in SOURCES.items():
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Tìm tiêu đề mã (Quét qua các tag phổ biến của web deal)
                    items = soup.find_all(['h3', 'h2', 'div'], class_=['coupon-title', 'coupon-name', 'deal-title', 'title'])
                    
                    for item in items:
                        deal_text = item.text.strip()
                        if not deal_text: continue
                        
                        # Lọc theo từ khóa (Tính năng 1)
                        if any(word in deal_text.lower() for word in config["keywords"]):
                            # Nếu deal này chưa từng được gửi
                            if deal_text not in processed_deals:
                                msg = f"<b>🔔 KÈO MỚI TỪ {name.upper()}:</b>\n\n🔥 <code>{deal_text}</code>\n\n🔗 Link: {url}"
                                send_telegram(msg)
                                processed_deals.add(deal_text)
                except Exception as e:
                    print(f"Lỗi quét {name}: {e}")
            
            # Xóa bớt bộ nhớ sau mỗi 100 deal để tránh nặng bot
            if len(processed_deals) > 100:
                processed_deals.clear()

        time.sleep(600) # Quét lại sau mỗi 10 phút

if __name__ == "__main__":
    # Khởi chạy luồng điều khiển
    t1 = threading.Thread(target=handle_commands, daemon=True)
    t1.start()
    
    # Khởi chạy luồng quét mã
    t2 = threading.Thread(target=scrape_deals, daemon=True)
    t2.start()
    
    # Khởi chạy Web Server cho Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
