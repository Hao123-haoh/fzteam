import requests
from bs4 import BeautifulSoup
import time
import threading
from flask import Flask

# --- PHẦN WEB SERVER ĐỂ RENDER KHÔNG LỖI ---
app = Flask('')

@app.route('/')
def home():
    return "Bot đang chạy..."

def run_web():
    app.run(host='0.0.0.0', port=8080)

# --- PHẦN BOT SĂN DEAL ---
TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url)

def check_deal():
    while True:
        try:
            # Ví dụ quét một trang deal (thay URL thật vào đây)
            print("Đang quét mã...")
            # Code quét dữ liệu của bạn ở đây...
            # if tìm thấy mã: send_telegram("Có mã mới!")
        except Exception as e:
            print(f"Lỗi: {e}")
        time.sleep(300) # Nghỉ 5 phút

# Chạy song song cả Web và Bot
if __name__ == "__main__":
    t = threading.Thread(target=check_deal)
    t.start()
    run_web()
