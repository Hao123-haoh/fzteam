
# 🔐 Bảo vệ bằng mật khẩu
PASSWORD = "fzteam123"  # Có thể thay bằng bất kỳ mật khẩu nào bạn muốn
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    pwd = st.text_input("🔒 Nhập mật khẩu để sử dụng:", type="password")
    if pwd == PASSWORD:
        st.session_state["authenticated"] = True
        st.experimental_rerun()
    else:
        st.stop()

# 🎨 Tự động đổi theme theo thời gian (dark từ 18h đến 6h)
hour = datetime.now().hour
theme_style = '''
<style>
body, .stApp {
    background-color: ''' + ("#0e1117" if hour >= 18 or hour <= 6 else "#ffffff") + ''';
    color: ''' + ("#f0f0f0" if hour >= 18 or hour <= 6 else "#000000") + ''';
}
</style>
'''
st.markdown(theme_style, unsafe_allow_html=True)


import streamlit as st
import requests
import re

# CSS hiệu ứng động
st.markdown('\n<style>\n/* Hiệu ứng chữ nhấp nháy màu gradient */\n@keyframes gradientText {\n    0% { background-position: 0% 50%; }\n    50% { background-position: 100% 50%; }\n    100% { background-position: 0% 50%; }\n}\n.fz-banner {\n    font-family: monospace;\n    font-weight: bold;\n    font-size: 14px;\n    background: linear-gradient(270deg, #ff4b4b, #f9d423, #00ffcc, #1e90ff);\n    background-size: 600% 600%;\n    -webkit-background-clip: text;\n    -webkit-text-fill-color: transparent;\n    animation: gradientText 6s ease infinite;\n    white-space: pre;\n}\n</style>\n\n<style>\n/* Fade-in hiệu ứng khi hiển thị kết quả */\n.fade-in {\n    animation: fadeIn 1s ease-in-out forwards;\n    opacity: 0;\n}\n@keyframes fadeIn {\n    to {\n        opacity: 1;\n    }\n}\n/* Nút hiệu ứng hover */\n.stButton > button {\n    background: linear-gradient(45deg, #ff4b4b, #ffb347);\n    color: white;\n    font-weight: bold;\n    transition: transform 0.2s, box-shadow 0.3s;\n}\n.stButton > button:hover {\n    transform: scale(1.05);\n    box-shadow: 0 0 10px rgba(255, 75, 75, 0.7);\n}\n</style>\n<script>\nconst observer = new MutationObserver(function (mutations) {\n    for (let mutation of mutations) {\n        for (let node of mutation.addedNodes) {\n            if (node.nodeType === 1) {\n                if (node.innerText.includes("Kết nối thành công") || node.innerText.includes("Lỗi")) {\n                    node.classList.add("fade-in");\n                }\n            }\n        }\n    }\n});\nobserver.observe(document.body, {{ childList: true, subtree: true }});\n</script>\n', unsafe_allow_html=True)

banner = """
███████╗███████╗    ████████╗███████╗ █████╗ ███╗   ███╗
╚══███╔╝╚══███╔╝    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
  ███╔╝   ███╔╝        ██║   █████╗  ███████║██╔████╔██║
 ███╔╝   ███╔╝         ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║
███████╗███████╗       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
╚══════╝╚══════╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
"""

st.set_page_config(page_title="FZ TEAM Messenger", page_icon="💬", layout="centered")
st.components.v1.html('\n<audio id="successSound" src="https://www.soundjay.com/buttons/sounds/button-3.mp3" preload="auto"></audio>\n<script>\nfunction playSuccessSound() {\n    document.getElementById(\'successSound\').play();\n}\n</script>\n\n<audio id="errorSound" src="https://www.soundjay.com/buttons/sounds/button-10.mp3" preload="auto"></audio>\n<script>\nfunction playErrorSound() {\n    document.getElementById(\'errorSound\').play();\n}\n</script>\n', height=0)
st.markdown(f"<div class='fz-banner'>{banner}</div>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🔐 Kết nối", "📜 Lịch sử", "📤 Xuất dữ liệu"])
with tab1:
    st.title("💬 Nanh Messenger Tool")
st.markdown("### Tự động lấy thông tin Facebook từ cookie")

class NanhMessenger:
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.user_id = self.get_user_id()
        self.fb_dtsg = None
        self.headers = self._init_headers()
        self._get_fb_dtsg()

    def get_user_id(self) -> str:
        try:
            return re.search(r"c_user=(\d+)", self.cookie).group(1)
        except Exception:
            raise ValueError("❌ Cookie không hợp lệ: Không tìm thấy c_user")

    def _init_headers(self) -> dict:
        return {
            'Cookie': self.cookie,
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/122.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/avif,image/webp,image/apng,*/*;q=0.8'
            ),
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Upgrade-Insecure-Requests': '1',
        }

    def _get_fb_dtsg(self):
        try:
            urls = [
                "https://www.facebook.com",
                "https://mbasic.facebook.com",
                "https://m.facebook.com"
            ]
            for url in urls:
                res = requests.get(url, headers=self.headers)
                if res.status_code != 200:
                    raise ValueError("⚠️ Cookie có thể đã hết hạn hoặc không hợp lệ (mã trạng thái: " + str(res.status_code) + ")")
                match = re.search(r'name="fb_dtsg" value="(.*?)"', res.text)
                if not match:
                    match = re.search(r'"token":"(.*?)"', res.text)
                if match:
                    self.fb_dtsg = match.group(1)
                    return
            raise ValueError("⚠️ Cookie giả hoặc không lấy được fb_dtsg. Vui lòng thử cookie khác.")
        except Exception as e:
            raise Exception("❌ Lỗi khi truy vấn Facebook: " + str(e))

cookie_input = st.text_area("🔐 Dán cookie Facebook tại đây:", height=150)
    if "history" not in st.session_state:
        st.session_state["history"] = []

    if st.button("🚀 Kết nối"):
    with st.spinner("Đang xử lý..."):
        st.markdown('''
<style>
/* Loading spinner đẹp */
.lds-ring {
  display: inline-block;
  position: relative;
  width: 80px;
  height: 80px;
}
.lds-ring div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 64px;
  height: 64px;
  margin: 8px;
  border: 6px solid #f93;
  border-radius: 50%;
  animation: lds-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  border-color: #f93 transparent transparent transparent;
}
.lds-ring div:nth-child(1) {
  animation-delay: -0.45s;
}
.lds-ring div:nth-child(2) {
  animation-delay: -0.3s;
}
.lds-ring div:nth-child(3) {
  animation-delay: -0.15s;
}
@keyframes lds-ring {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

<div class="lds-ring"><div></div><div></div><div></div><div></div></div>
''', unsafe_allow_html=True)
        try:
            nm = NanhMessenger(cookie=cookie_input)
            st.success("✅ Kết nối thành công!")
        st.session_state["history"].append({"user_id": nm.user_id, "fb_dtsg": nm.fb_dtsg})
        import json
with open("fzteam_history.json", "w", encoding="utf-8") as f:
    json.dump(st.session_state["history"], f, ensure_ascii=False, indent=2)
st.components.v1.html("<script>playSuccessSound();</script>", height=0)
            st.code(f"User ID: {nm.user_id}", language="python")
            st.code(f"fb_dtsg: {nm.fb_dtsg}", language="python")
        except Exception as e:
            st.error(f"❌ Lỗi: {e}")
st.components.v1.html("<script>playErrorSound();</script>", height=0)


with tab2:
    st.subheader("📜 Lịch sử cookie đã dùng")
    if st.session_state["history"]:
        for i, item in enumerate(st.session_state["history"], 1):
            st.markdown(f"**{i}. User ID:** `{item['user_id']}`  
🔑 fb_dtsg: `{item['fb_dtsg']}`")
    else:
        st.info("Chưa có dữ liệu lịch sử.")


import json
with tab3:
    st.subheader("📤 Xuất dữ liệu")
    if st.session_state["history"]:
        export_btn = st.button("📥 Tải file JSON")
        if export_btn:
            export_data = json.dumps(st.session_state["history"], indent=2)
            st.download_button("📄 Tải xuống lịch sử", data=export_data, file_name="fzteam_history.json", mime="application/json")
    else:
        st.info("Không có dữ liệu để xuất.")
