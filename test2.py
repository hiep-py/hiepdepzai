from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import time
import re
from datetime import datetime

app = Flask(__name__)  # Khởi tạo Flask



# --------------------- CẤU HÌNH TRÌNH DUYỆT ---------------------
options = Options()
options.add_argument("--headless")  # Chạy ẩn trình duyệt
options.add_argument("--disable-extensions")  # Tắt tiện ích mở rộng
options.add_argument("--disable-notifications")  # Tắt thông báo
options.add_argument("--window-size=800,600")  # Cỡ cửa sổ trình duyệt
options.add_argument("--no-sandbox")  # Chạy không sandbox (cần thiết trên Linux)
options.add_argument("--disable-dev-shm-usage")  # Giảm tiêu thụ bộ nhớ trên Linux
options.add_argument("--log-level=3")  # Ẩn các log không cần thiết

# ⚡ Tắt tải ảnh để giảm băng thông
prefs = {
    "profile.default_content_setting_values": {
        "images": 2,
        "javascript": 1,
        "geolocation": 2,
        "notifications": 2,
    }
}
options.add_experimental_option("prefs", prefs)

# Biến lưu dữ liệu mới nhất
latest_data = {"value": None, "timestamp": None}

# --------------------- HÀM CẬP NHẬT DỮ LIỆU ---------------------
def update_data():
    global latest_data
    
    while True:
        try:
            # Khởi động trình duyệt
            driver = webdriver.Chrome(options=options)
            URL = "https://aero.turbogames.io"
            driver.get(URL)
            
            # Đợi phần tử xuất hiện
            wait = WebDriverWait(driver, 10)
            data_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[3]/div[3]/div[1]/div[1]')))
            print("🎯 Đã tìm thấy phần tử chứa dữ liệu!")

            while True:
                try:
                    raw_text = data_element.text.strip()  # Lấy dữ liệu thô
                    
                    # 🔍 Lọc số đầu tiên từ dữ liệu bằng regex
                    number_match = re.search(r"\d+(\.\d+)?", raw_text)

                    if number_match:
                        latest_value = float(number_match.group())  # Chuyển thành số thực
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # Chỉ cập nhật nếu dữ liệu thay đổi
                        if latest_value != latest_data["value"]:
                            latest_data["value"] = latest_value
                            latest_data["timestamp"] = current_time

                            # Ghi vào file
                            with open("data.txt", "a") as file:
                                file.write(f"{latest_value} +|+ {current_time}\n")

                            print(f"📊 Dữ liệu mới: {latest_value} +|+ {current_time}")

                    time.sleep(1)  # Tránh vòng lặp quá nhanh
                except Exception as e:
                    print(f"⚠ Lỗi trong vòng lặp: {e}")
                    break  # Nếu lỗi liên tục, khởi động lại trình duyệt

            driver.quit()  # Đóng trình duyệt sau mỗi vòng lặp
            time.sleep(2)  # Chờ trước khi chạy lại
        except Exception as e:
            print(f"❌ Lỗi khởi động Selenium: {e}")
            time.sleep(5)  # Chờ lâu hơn nếu có lỗi nghiêm trọng

# --------------------- API ENDPOINT ---------------------
@app.route('/', methods=['GET'])
def get_data():
    return jsonify(latest_data)  # Trả về dữ liệu mới nhất dưới dạng JSON

# --------------------- CHẠY API & CẬP NHẬT LIÊN TỤC ---------------------
if __name__ == '__main__':
    # Tạo luồng chạy Selenium liên tục
    threading.Thread(target=update_data, daemon=True).start()
    
    # Chạy Flask API
    app.run(host='0.0.0.0', port=5000, debug=False)
