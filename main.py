import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- 設定區 ---
SCROLL_STEP = 700      # 每次捲動的像素
WAIT_PER_STEP = 2.5    # 每一小步等待時間

# 自動抓取目前電腦使用者的桌面路徑
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
OUTPUT_FILE = os.path.join(desktop_path, "x_followers_final.txt")
MAX_BOTTOM_RETRIES = 3 # 偵測到底部後，再多嘗試幾次才放棄

def main():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=chrome_options)
    
    user_ids = set()
    
    try:
        driver.get("https://x.com")
        print("\n" + "="*60)
        print("【操作指引】")
        print("1. 請手動完成登入並導覽至名單頁面。")
        print("2. 回到這裡按下 [Enter] 開始執行。")
        print("3. 執行中若想「手動停止並存檔」，請隨時按下 [Ctrl + C]。")
        print("="*60)
        input(">>> 準備好後按下 [Enter]...")

        last_position = 0
        bottom_retry_count = 0
        
        # 使用 try...except 包裹迴圈，以便捕捉 Ctrl+C
        try:
            while True:
                # 1. 執行碎步捲動
                current_position = last_position + SCROLL_STEP
                driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(WAIT_PER_STEP)

                # 2. 抓取 ID
                elements = driver.find_elements(By.TAG_NAME, "span")
                new_finds = 0
                for el in elements:
                    try:
                        text = el.text.strip()
                        if text.startswith("@") and len(text) > 1:
                            if text not in user_ids:
                                user_ids.add(text)
                                new_finds += 1
                    except:
                        continue
                
                if new_finds > 0:
                    print(f"目前累計：{len(user_ids)} 人（新增 {new_finds} 人）")
                    bottom_retry_count = 0 # 只要有抓到新人，重置底部計數器
                
                # 3. 底部偵測邏輯優化
                actual_position = driver.execute_script("return window.pageYOffset;")
                max_scroll = driver.execute_script("return document.body.scrollHeight - window.innerHeight;")
                
                if actual_position >= max_scroll - 10: # 容許 10 像素誤差
                    bottom_retry_count += 1
                    print(f"偵測到疑似底部 ({bottom_retry_count}/{MAX_BOTTOM_RETRIES})...")
                    time.sleep(3) # 給予更多載入時間
                    
                    if bottom_retry_count >= MAX_BOTTOM_RETRIES:
                        print("確認抵達底部，自動結束抓取。")
                        break
                
                last_position = actual_position

        except KeyboardInterrupt:
            print("\n\n[偵測到手動中斷] 正在停止抓取並準備存檔...")

    except Exception as e:
        print(f"程式執行異常: {e}")

    finally:
        # 4. 存檔邏輯（無論是自動結束還是手動中斷，都會執行到這裡）
        if user_ids:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for uid in sorted(list(user_ids)):
                    f.write(uid + "\n")
            print("-" * 30)
            print(f"任務結束！")
            print(f"總計抓取不重複人數：{len(user_ids)}")
            print(f"檔案已儲存至：{OUTPUT_FILE}")
            print("-" * 30)
        else:
            print("未抓取到任何資料。")
        
        driver.quit()

if __name__ == "__main__":
    main()