import requests
from bs4 import BeautifulSoup
import time
import threading
from flask import Flask
import os

# --- CẤU HÌNH ---
TOKEN = "6556057870:AAFPx3CJpAcGt-MfKRoAo00SlAEQ26XSS-s"
CHAT_ID = "6090612274"
SOURCE_URL = "https://bloggiamgia.vn/tiktok-shop" # Nguồn săn mã

app = Flask('')

@app.route('/')
def home():
    return "Bot Săn Deal TikTok đang chạy 24/7 trên Render!"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Lỗi gửi tin nhắn: {e}")

def scrape_deals():
    processed_deals = set() # Lưu các mã đã gửi để không bị lặp
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("Bot bắt đầu quét deal...")
    
    while True:
        try:
            response = requests.get(SOURCE_URL, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tìm các thẻ chứa tiêu đề mã giảm giá
            # Cấu trúc này có thể thay đổi tùy trang web, đây là ví dụ cho bloggiamgia
            items = soup.find_all('h3', class_='coupon-title') 
            
            for item in items:
                deal_text = item.text.strip()
                
                if deal_text not in processed_deals:
                    # Gửi thông báo về Telegram
                    msg = f"<b>🚀 MÃ MỚI XUẤT HIỆN:</b>\n\n📌 <i>{deal_text}</i>\n\n🔗 Xem ngay: {SOURCE_URL}"
                    send_telegram(msg)
                    
                    # Lưu vào bộ nhớ để không báo lại mã cũ
                    processed_deals.add(deal_text)
                    
            # Giới hạn bộ nhớ tránh đầy RAM
            if len(processed_deals) > 100:
                processed_deals.clear()

        except Exception as e:
            print(f"Lỗi khi quét: {e}")
            
        time.sleep(600) # Quét lại sau mỗi 10 phút (tránh bị chặn IP)

if __name__ == "__main__":
    threading.Thread(target=scrape_deals, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
