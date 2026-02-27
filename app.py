import requests
from bs4 import BeautifulSoup
import time
import threading
from flask import Flask, render_template_string, request, redirect, url_for
import os
import re

# --- CẤU HÌNH ---
TOKEN = "6556057870:AAFPx3CJpAcGt-MfKRoAo00SlAEQ26XSS-s"
CHAT_ID = "6090612274"

target_config = {
    "item_name": "canxi nano",
    "max_price": 180000,
    "is_running": True,
    "last_check": "Chưa kiểm tra",
    "total_found": 0
}

app = Flask('')

# --- GIAO DIỆN WEB HIỆN ĐẠI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Hunter Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
        .card { border-radius: 15px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .btn-tiktok { background: #ff0050; color: white; font-weight: bold; border-radius: 10px; }
        .header { background: #000; color: #fff; padding: 20px; border-radius: 0 0 20px 20px; margin-bottom: 30px; }
    </style>
</head>
<body>
    <div class="header text-center">
        <h2>🚀 TIKTOK SHOP HUNTER</h2>
    </div>
    <div class="container">
        <div class="row g-4 justify-content-center">
            <div class="col-md-6">
                <div class="card p-4">
                    <form action="/update" method="POST">
                        <div class="mb-3">
                            <label class="form-label font-weight-bold">Món đồ cần săn:</label>
                            <input type="text" name="item" class="form-control" value="{{ config.item_name }}">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Giá trần (đ):</label>
                            <input type="number" name="price" class="form-control" value="{{ config.max_price }}">
                        </div>
                        <button type="submit" class="btn btn-tiktok w-100">CẬP NHẬT MỤC TIÊU</button>
                    </form>
                </div>
                <div class="card mt-4 p-3 text-center">
                    <p class="mb-1">Trạng thái: <strong class="text-success">ONLINE</strong></p>
                    <p class="mb-0 text-muted small">Cập nhật lúc: {{ config.last_check }}</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, config=target_config)

@app.route('/update', methods=['POST'])
def update():
    target_config['item_name'] = request.form.get('item')
    target_config['max_price'] = int(request.form.get('price'))
    send_telegram(f"✅ <b>Đã cập nhật từ Web:</b> Săn <b>{target_config['item_name']}</b> dưới <b>{target_config['max_price']:,}đ</b>")
    return redirect(url_for('home'))

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
                                send_telegram(f"<b>🎯 TÌM THẤY DEAL ĐÚNG Ý:</b>\n\n📦 {item.text.strip()}\n💰 Giá: {price:,}đ\n\n👉 Mở TikTok ngay!")
                                processed_deals.add(title)
            except: pass
        time.sleep(300)

# ĐÃ SỬA LỖI TÁCH TÊN CÓ DẤU CÁCH
def handle_commands():
    last_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}&timeout=20"
            res = requests.get(url, timeout=25).json()
            for up in res.get("result", []):
                last_id = up["update_id"]
                txt = up["message"]["text"].lower()
                
                if "/san" in txt:
                    # Tách lấy phần số cuối cùng làm giá, còn lại là tên
                    parts = txt.replace("/san", "").strip().split()
                    if len(parts) >= 2:
                        price = int(parts[-1]) # Số cuối cùng là giá
                        item = " ".join(parts[:-1]) # Các chữ phía trước là tên
                        target_config["item_name"] = item
                        target_config["max_price"] = price
                        send_telegram(f"✅ <b>Đã nhận lệnh săn:</b> {item} - dưới {price:,}đ")
        except: pass
        time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=scrape_tiktok_deals, daemon=True).start()
    threading.Thread(target=handle_commands, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
