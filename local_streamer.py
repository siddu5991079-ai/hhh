import os
import time
import subprocess
import urllib.parse
import traceback
from datetime import datetime, timezone, timedelta
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# --- SETTINGS ---
DEFAULT_URL = "https://crichdbest.com/player.php?id=starsp3"
# Aapka Dadocric wala link (Default target)
TARGET_WEBSITE = os.environ.get('TARGET_URL', "https://dadocric.st/player.php?id=willowextra")

# Apni Stream Key Yahan Dalein (OK.ru ke liye)
STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda" 
RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
DEFAULT_SLEEP = 45 * 60 
# ----------------

# Timezone setup (Pakistan Time)
PKT = timezone(timedelta(hours=5))

def get_link_with_headers():
    print(f"\n[🕵️‍♂️] Bot link dhoondne ja raha hai: {TARGET_WEBSITE}")
    
    options = webdriver.ChromeOptions()
    
    # --- LOCAL PC SETTINGS (HEADLESS BAND HAI) ---
    # Humne headless comment kar diya hai taake aapko browser open hota nazar aaye
    # options.add_argument('--headless=new') 
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # --- VIDEO AUTOPLAY FIX ---
    options.add_argument('--autoplay-policy=no-user-gesture-required')
    options.add_argument('--mute-audio')
    
    # Enable Logging
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    # --- ANTI-BOT BYPASS ---
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    seleniumwire_options = {'disable_encoding': True, 'connection_keep_alive': True}

    driver = None
    data = None

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            seleniumwire_options=seleniumwire_options,
            options=options
        )
        
        # JS Injection: Bot flag hide
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get(TARGET_WEBSITE)
        
        # ⏳ 15 seconds ka time taake ads skip hon aur player live ho
        print("[⏳] Chrome open ho gaya hai... Player load hone ka wait karein (15 sec)...") 
        time.sleep(15) 

        for request in driver.requests:
            if request.response:
                # Sirf .m3u8 pakrega
                if ".m3u8" in request.url:
                    headers = request.headers
                    data = {
                        "url": request.url,
                        "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
                        "cookie": headers.get('Cookie', ''),
                        "referer": headers.get('Referer', TARGET_WEBSITE) 
                    }
                    print(f"[✅] Link Found: {request.url[:60]}...")
                    break
        
        if not data:
            print("\n[🚨] WARNING: .m3u8 link nahi mila! Wajah dhoond rahe hain...")
            print(f"   -> Page Title: '{driver.title}'")

    except Exception as e:
        print(f"\n[💥] CRITICAL PYTHON ERROR:")
        print(traceback.format_exc())
    finally:
        # Link milne ke baad browser band ho jayega
        if driver: driver.quit()
    
    return data

def calculate_sleep_time(url):
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        expiry_ts = None
        
        if 'expires' in params: expiry_ts = int(params['expires'][0])
        elif 'e' in params: expiry_ts = int(params['e'][0])
            
        if expiry_ts:
            expiry_dt = datetime.fromtimestamp(expiry_ts, PKT)
            wake_up_dt = expiry_dt - timedelta(minutes=5)
            now_dt = datetime.now(PKT)
            seconds = (wake_up_dt - now_dt).total_seconds()
            
            print(f"[⏰] Expiry: {expiry_dt.strftime('%I:%M %p')}")
            print(f"[💤] Naya Link dhoondne ka time: {wake_up_dt.strftime('%I:%M %p')}")
            
            if seconds > 0: return seconds
            else: return 60
    except Exception as e:
        pass
    
    return DEFAULT_SLEEP

def start_stream(data):
    headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
    
    cmd = [
        "ffmpeg", "-re",
        "-loglevel", "error", # Sirf errors show karega
        "-headers", headers_cmd,
        "-i", data['url'],
        "-c:v", "libx264", "-preset", "ultrafast",
        "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
        "-vf", "scale=854:480", "-r", "25",
        "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
        "-f", "flv", RTMP_URL
    ]
    print("\n[⚙️] FFmpeg Streaming Engine Start ho raha hai...")
    
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 

def main():
    print("========================================")
    print("   🚀 LOCAL PC STREAMER STARTED")
    print("========================================")
    print(f"Target: {TARGET_WEBSITE}")
    
    end_time = time.time() + (6 * 60 * 60)
    current_process = None

    while time.time() < end_time:
        try:
            data = get_link_with_headers()
            
            if data:
                if current_process: current_process.terminate()
                
                current_process = start_stream(data)
                print("[🚀] BINGO! Stream OK.ru par live chali gayi hai!")
                
                sleep_seconds = calculate_sleep_time(data['url'])
                print(f"[zzz] FFmpeg background mein chal raha hai. Bot {int(sleep_seconds/60)} mins ke liye so raha hai...")
                
                waited = 0
                while waited < sleep_seconds:
                    time.sleep(10)
                    waited += 10
                    # Check if ffmpeg crashed
                    if current_process.poll() is not None:
                        exit_code = current_process.poll()
                        print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
                        break 
                
                print("[🔄] Link expire hone wala hai, naya link laa raha hoon...")
                if current_process: current_process.terminate()
            else:
                print("[❌] Link nahi mila. 1 min baad dobara koshish karega...")
                time.sleep(60)
                
        except Exception as main_e:
            print(f"\n[💥] MAIN LOOP ERROR:")
            print(traceback.format_exc())
            time.sleep(60)

if __name__ == "__main__":
    main()