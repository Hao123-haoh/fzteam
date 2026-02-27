import requests
from bs4 import BeautifulSoup
import time
import threading
from flask import Flask
import os
import re

TOKEN = "6556057870:AAFPx3CJpAcGt-MfKRoAo00SlAEQ26XSS-s"
CHAT_ID = "6090612274"

# Cấu hình mục tiêu săn
target_config = {
    "item_name": "tai nghe", # Thay bằng món bạn muốn, vd: 'son', 'op lung'
    "max_price": 50000,      # Giá cao nhất bạn muốn mua (50k)
    "is_running": True
}

app = Flask('')

@app.route('/')
def home():
    return f"Bot TikTok Shop: {'ON' if target_config['is_running'] else 'OFF'} | Đang săn: {target_config['item_name']} < {target_config['max_price']}đ"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def extract_price(text):
    # Tìm số trong chuỗi (vd: "99.000đ" -> 99000)
    nums = re.findall(r'\d+', text.replace('.', '').replace(',', ''))
    if nums:
        price = int(nums[0])
        # Nếu tiêu đề ghi "99k" thì nhân 1000
        if 'k' in text.lower() and price < 1000:
            price *= 1000
        return price
    return None

def scrape_tiktok_deals():
    processed_deals = set()
    source_url = "https://bloggiamgia.vn/tiktok-shop"
    
    while True:
        if target_config['is_running']:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(source_url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Tìm các khung chứa deal
                items = soup.find_all(['h3', 'div'], class_=['coupon-title', 'deal-info'])
                
                for item in items:
                    title = item.text.strip().lower()
                    
                    # KIỂM TRA 1: Có đúng món đồ không?
                    if target_config['item_name'].lower() in title:
                        price = extract_price(title)
                        
                        # KIỂM TRA 2: Giá có rẻ hơn mức mong muốn không?
                        if price and price <= target_config['max_price']:
                            if title not in processed_deals:
                                msg = f"<b>🎯 KÈO TIKTOK SHOP ĐÚNG Ý:</b>\n\n📦 {item.text.strip()}\n💰 Giá tìm thấy: {price:,}đ\n\n👉 Mở TikTok săn ngay!"
                                send_telegram(msg)
                                processed_deals.add(title)
            except Exception as e:
                print(f"Lỗi quét: {e}")
        
        time.sleep(300) # 5 phút quét một lần

# Luồng nhận lệnh điều khiển
def handle_commands():
    last_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}"
            res = requests.get(url).json()
            for up in res.get("result", []):
                last_id = up["update_id"]
                txt = up["message"]["text"].lower()
                
                if "/san" in txt: # Lệnh mới: /san [tên] [giá]
                    parts = txt.split()
                    if len(parts) >= 3:
                        target_config["item_name"] = parts[1]
                        target_config["max_price"] = int(parts[2])
                        send_telegram(f"✅ Đã nhận lệnh! Bot sẽ săn <b>{parts[1]}</b> với giá dưới <b>{parts[2]}đ</b>")
        except: pass
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=scrape_tiktok_deals, daemon=True).start()
    threading.Thread(target=handle_commands, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
