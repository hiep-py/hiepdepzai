import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# --------------------- CẤU HÌNH TRÌNH DUYỆT ---------------------
options = Options()
options.add_argument("--headless")  
options.add_argument("--disable-extensions")
options.add_argument("--disable-notifications")
options.add_argument("--window-size=800,600")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

prefs = {"profile.default_content_setting_values": {"images": 2, "javascript": 1}}
options.add_experimental_option("prefs", prefs)

# --------------------- HÀM LẤY DỮ LIỆU ---------------------
def fetch_data():
    driver = webdriver.Chrome(options=options)
    URL = "https://aero.turbogames.io"
    driver.get(URL)
    
    wait = WebDriverWait(driver, 20)
    data_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[3]/div[3]/div[1]/div[1]')))
    print("🎯 Đã tìm thấy phần tử chứa dữ liệu!")

    while True:
        try:
            raw_text = data_element.text.strip()
            number_match = re.search(r"\d+(\.\d+)?", raw_text)

            if number_match:
                latest_value = float(number_match.group())
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Ghi vào file JSON
                data = {"value": latest_value, "timestamp": current_time}
                with open("data.json", "w") as file:
                    json.dump(data, file)

                print(f"📊 Dữ liệu mới: {latest_value} +|+ {current_time}")

            time.sleep(1)  # Cập nhật mỗi 0.5 giây

        except Exception as e:
            print(f"⚠ Lỗi: {e}")
            break

    driver.quit()

# Chạy chương trình
if __name__ == "__main__":
    fetch_data()
