import requests
from bs4 import BeautifulSoup
import time
import threading
from flask import Flask, render_template_string
import os
import re

# --- CẤU HÌNH ---
TOKEN = "6556057870:AAFPx3CJpAcGt-MfKRoAo00SlAEQ26XSS-s"
CHAT_ID = "6090612274"

target_config = {
    "item_name": "canxi nano d3",
    "max_price": 180000,
    "is_running": True,
    "last_check": "Chưa có dữ liệu"
}

app = Flask('')

@app.route('/')
def home():
    return f"<h3>Bot TikTok Hunter đang chạy!</h3><p>Mục tiêu: {target_config['item_name']} - Giá: {target_config['max_price']:,}đ</p>"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def scrape_tiktok_deals():
    processed_deals = set()
    while True:
        if target_config['is_running']:
            try:
                target_config['last_check'] = time.strftime("%H:%M:%S")
                res = requests.get("https://bloggiamgia.vn/tiktok-shop", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                items = soup.find_all(['h3', 'div'], class_=['coupon-title', 'deal-info'])
                for item in items:
                    title = item.text.strip().lower()
                    if target_config['item_name'].lower() in title:
                        nums = re.findall(r'\d+', title.replace('.', '').replace(',', ''))
                        if nums:
                            price = int(nums[0])
                            if 'k' in title and price < 1000: price *= 1000
                            if price <= target_config['max_price'] and title not in processed_deals:
                                send_telegram(f"<b>🎯 ĐÃ TÌM THẤY DEAL:</b>\n\n📦 {item.text.strip()}\n💰 Giá: {price:,}đ")
                                processed_deals.add(title)
            except: pass
        time.sleep(300)

# XỬ LÝ LỆNH MENU TELEGRAM
def handle_commands():
    last_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}&timeout=20"
            res = requests.get(url, timeout=25).json()
            for up in res.get("result", []):
                last_id = up["update_id"]
                if "message" not in up or "text" not in up["message"]: continue
                
                txt = up["message"]["text"].lower().strip()
                
                if txt == "/status":
                    send_telegram(f"📊 <b>TRẠNG THÁI:</b>\n- Đang săn: {target_config['item_name']}\n- Giá dưới: {target_config['max_price']:,}đ")
                
                elif txt.startswith("/san"):
                    # Tách tên và giá (Hỗ trợ tên có dấu cách như Canxi Nano D3)
                    parts = txt.replace("/san", "").strip().split()
                    if len(parts) >= 2:
                        try:
                            price = int(parts[-1]) # Lấy số cuối cùng làm giá
                            item = " ".join(parts[:-1]) # Phần còn lại là tên
                            target_config["item_name"] = item
                            target_config["max_price"] = price
                            send_telegram(f"✅ <b>Đã nhận lệnh săn:</b>\n📦 {item}\n💰 Dưới {price:,}đ")
                        except:
                            send_telegram("⚠️ Lỗi: Giá phải là số. VD: /san canxi 180000")
        except: pass
        time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=scrape_tiktok_deals, daemon=True).start()
    threading.Thread(target=handle_commands, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
