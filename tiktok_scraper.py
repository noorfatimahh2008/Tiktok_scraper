from fastapi import FastAPI
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv, os

app = FastAPI()

class TikTokRequest(BaseModel):
    url: str
    use_proxy: bool = False
    proxy_ip_port: str = ''

# Global driver variable
driver = None
proxy_applied = False

def init_driver(use_proxy: bool = False, proxy_ip_port: str = ""):
    global driver, proxy_applied

    if driver:
        try:
            driver.title  # test if driver is alive
            return driver
        except:
            print("[INFO] Old driver died. Reinitializing...")

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")

    if use_proxy and proxy_ip_port.strip() and not proxy_applied:
        options.add_argument(f'--proxy-server={proxy_ip_port}')
        proxy_applied = True
        print(f"[INFO] Proxy applied once: {proxy_ip_port}")
    elif proxy_applied:
        print("[INFO] Proxy already applied.")
    else:
        print("[INFO] No proxy used.")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_tiktok_data(url: str, use_proxy: bool = True, proxy_ip_port: str = ""):
    global driver
    driver = init_driver(use_proxy, proxy_ip_port)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 30)

        print("[INFO] Waiting for Like element...")
        like_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="main-content-video_detail"]/div/div[2]/div/div[1]/div[1]/div[4]/div[2]/button[1]/strong')
        ))
        print("[INFO] Waiting for Comment element...")
        comment_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="main-content-video_detail"]/div/div[2]/div/div[1]/div[1]/div[4]/div[2]/button[2]/strong')
        ))
        print("[INFO] Waiting for Favorite element...")
        favorite_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="main-content-video_detail"]/div/div[2]/div/div[1]/div[1]/div[4]/div[2]/div/button/strong')
        ))

        likes = like_elem.text
        comments = comment_elem.text
        favorites = favorite_elem.text

        print(f"[INFO] Scraped: Likes={likes}, Comments={comments}, Favorites={favorites}")

    except Exception as e:
        raise Exception("❌ Failed to extract data: " + str(e))
    driver.quit()
    # Save to CSV
    csv_file = 'tiktok_data.csv'
    file_exists = os.path.exists(csv_file)

    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['URL', 'Likes', 'Comments', 'Favorites'])
        writer.writerow([url, likes, comments, favorites])

    return {"url": url, "likes": likes, "comments": comments, "favorites": favorites}

@app.post("/scrape/")
def scrape_tiktok_video(request: TikTokRequest):
    try:
        data = scrape_tiktok_data(
            url=request.url,
            use_proxy=request.use_proxy,
            proxy_ip_port=request.proxy_ip_port
        )
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"[ERROR] {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
