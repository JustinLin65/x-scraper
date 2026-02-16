import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- 設定區 ---
OUTPUT_FILE = "x_members_list.txt"  # 匯出的檔案名稱
SCROLL_PAUSE_TIME = 2.5             # 每次捲動後等待的時間（秒），建議 2-3 秒較安全

def main():
    # 1. 初始化瀏覽器
    chrome_options = Options()
    # 增加一些偽裝設定，避免被輕易偵測為機器人
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 2. 先前往 X 首頁
        driver.get("https://x.com/login")
        
        print("\n" + "="*60)
        print("【手動操作步驟】")
        print("1. 請在彈出的瀏覽器中完成登入。")
        print("2. 手動導覽至你想抓取的「社群成員名單」或「跟隨者名單」頁面。")
        print("3. 確認名單已顯示在螢幕上。")
        print("4. 回到這裡（終端機），按下 [Enter] 開始自動抓取。")
        print("="*60)
        
        input(">>> 已準備就緒？按下 [Enter] 開始抓取...")

        print("程序啟動中... 請勿關閉瀏覽器視窗。")
        
        user_ids = set()
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # 3. 抓取目前畫面上的所有 ID
            # X 的 ID 結構通常在 span 內且以 @ 開頭
            elements = driver.find_elements(By.TAG_NAME, "span")
            
            before_count = len(user_ids)
            for el in elements:
                try:
                    text = el.text.strip()
                    if text.startswith("@") and len(text) > 1:
                        user_ids.add(text)
                except:
                    continue
            
            # 顯示進度
            if len(user_ids) > before_count:
                print(f"目前累計抓取：{len(user_ids)} 個帳號...")

            # 4. 執行捲動
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

            # 5. 檢查高度是否有變化（判斷是否到最底）
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # 為了保險起見，再多等一下並捲動一次，避免網路延遲造成的假性見底
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                if driver.execute_script("return document.body.scrollHeight") == last_height:
                    print("\n[通知] 已偵測到頁面底部或內容不再更新。")
                    break
            last_height = new_height

        # 6. 儲存至 TXT
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            # 排序後存檔
            sorted_list = sorted(list(user_ids))
            for uid in sorted_list:
                f.write(uid + "\n")

        print("-" * 30)
        print(f"任務完成！")
        print(f"總共抓取人數：{len(user_ids)}")
        print(f"檔案儲存路徑：{OUTPUT_FILE}")
        print("-" * 30)

    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
    
    finally:
        # 詢問是否關閉瀏覽器
        stay_open = input("任務結束，是否關閉瀏覽器？(y/n): ").lower()
        if stay_open == 'y':
            driver.quit()

if __name__ == "__main__":
    main()