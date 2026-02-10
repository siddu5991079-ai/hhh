# FILE: superman.py
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import json
import os
import urllib.parse
from datetime import datetime, timezone, timedelta

# --- SETTINGS ---
TARGET_WEBSITE = "https://crichdbest.com/player.php?id=starsp3"
DATA_FILE = "stream_data.json"
DEFAULT_SLEEP = 20 * 60  # Agar expiry na mile to 20 min so jana
# ----------------

# --- TIMEZONE SETUP (Pakistan Standard Time) ---
PKT = timezone(timedelta(hours=5))

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def calculate_smart_sleep(url):
    """
    Yeh function Code 3 ki logic use karta hai.
    Link ka expiry time nikalta hai aur usme se 20 min minus karta hai.
    """
    try:
        # URL Parsing
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        expiry_ts = None
        
        # 1. Check 'expires' or 'e' parameter
        if 'expires' in params:
            expiry_ts = int(params['expires'][0])
        elif 'e' in params:
            expiry_ts = int(params['e'][0])
            
        if expiry_ts:
            # Unix Timestamp to PKT Datetime
            expiry_dt = datetime.fromtimestamp(expiry_ts, PKT)
            now_dt = datetime.now(PKT)
            
            # Expiry se 20 minute pehle ka time
            wake_up_dt = expiry_dt - timedelta(minutes=20)
            
            # Calculate Seconds to Sleep
            sleep_seconds = (wake_up_dt - now_dt).total_seconds()
            
            # Printing Info (Code 3 Style)
            print(f"\n{'-'*40}")
            print(f"📊 **SMART TIME CALCULATION (PKT)**")
            print(f"{'-'*40}")
            print(f"💀 Link Expire Hoga:  {expiry_dt.strftime('%I:%M:%S %p')}")
            print(f"⏰ Minus 20 Mins:     {wake_up_dt.strftime('%I:%M:%S %p')}")
            print(f"⌚ Abhi Time Hai:     {now_dt.strftime('%I:%M:%S %p')}")
            
            if sleep_seconds > 0:
                mins = int(sleep_seconds / 60)
                print(f"💤 Bot Soyega:        {mins} Minutes ({sleep_seconds:.0f} sec)")
                return sleep_seconds
            else:
                print(f"⚠️ Link already expired ya time bohot kam hai!")
                return 60 # Sirf 1 min so kar naya dhoondo
        else:
            print("⚠️ URL mein 'expires' parameter nahi mila.")
            return DEFAULT_SLEEP

    except Exception as e:
        print(f"⚠️ Calculation Error: {e}")
        return DEFAULT_SLEEP

def get_link_data():
    print(f"\n[🕵️‍♂️] Boss (Superman) Link dhoondne nikla hai...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    seleniumwire_options = {'disable_encoding': True, 'connection_keep_alive': True}

    driver = None
    found_data = None

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            seleniumwire_options=seleniumwire_options,
            options=options
        )
        
        driver.get(TARGET_WEBSITE)
        print("[⏳] Page loading (Wait 20 sec)...")
        time.sleep(20)

        print("[🔍] Scanning Network...")
        for request in driver.requests:
            if request.response:
                # Sirf m3u8 aur NO Google Ads
                if ".m3u8" in request.url and "google" not in request.url:
                    
                    headers = request.headers
                    found_data = {
                        "url": request.url,
                        "ua": headers.get('User-Agent', ''),
                        "cookie": headers.get('Cookie', ''),
                        "referer": headers.get('Referer', 'https://crichdbest.com/'),
                        "timestamp": time.time()
                    }
                    print(f"[✅] Link Mil Gaya!")
                    break
        
    except Exception as e:
        print(f"[⚠️] Browser Error: {e}")
    finally:
        if driver: driver.quit()
    
    return found_data

def main():
    clear_screen()
    print("========================================")
    print("   SUPERMAN: SMART TIMING EDITION")
    print("========================================")

    while True:
        data = get_link_data()
        
        sleep_time = DEFAULT_SLEEP # Default agar kuch fail ho jaye
        
        if data:
            # 1. File mein save karo (Taake Worker padh sake)
            with open(DATA_FILE, "w") as f:
                json.dump(data, f)
            print(f"[💾] Link saved to {DATA_FILE}")

            # 2. Smart Time Calculate karo
            sleep_time = calculate_smart_sleep(data['url'])
            
        else:
            print("[❌] Link nahi mila. 1 min baad dubara try karunga.")
            sleep_time = 60

        print(f"\n[zzz] Ab main {int(sleep_time/60)} minutes ke liye so raha hoon...")
        
        try:
            time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("\nUser stopped the bot.")
            break

if __name__ == "__main__":
    main()









# =========== 200% correct hai yeh code link extract karta hai website see ====================

# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# import time
# import subprocess
# import os

# # --- SETTINGS ---
# TARGET_WEBSITE = "https://crichdbest.com/player.php?id=starsp3"
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda"
# REFRESH_TIME = 60 * 60 
# # ----------------

# def clear_screen():
#     os.system('cls' if os.name == 'nt' else 'clear')

# def get_link_and_headers():
#     print(f"\n[🕵️‍♂️] Jasoos link aur headers dhoondne ja raha hai...")
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless=new') 
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {
#         'disable_encoding': True,
#         'connection_keep_alive': True
#     }

#     driver = None
#     found_data = None

#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             seleniumwire_options=seleniumwire_options,
#             options=options
#         )
        
#         driver.get(TARGET_WEBSITE)
#         print("[⏳] Page load... (Wait 20 sec)")
#         time.sleep(20)

#         print("[🔍] Scanning traffic...")
        
#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url and "google" not in request.url:
#                     print(f"\n[✅] LINK MIL GAYA!\n{request.url}")
                    
#                     # --- HEADERS CHORI KARNA (MAGIC STEP) ---
#                     # Hum wahi headers copy karenge jo browser ne use kiye
#                     headers = request.headers
#                     user_agent = headers.get('User-Agent', '')
#                     cookie = headers.get('Cookie', '')
#                     referer = headers.get('Referer', 'https://crichdbest.com/')
                    
#                     found_data = {
#                         "url": request.url,
#                         "ua": user_agent,
#                         "cookie": cookie,
#                         "referer": referer
#                     }
#                     print(f"[🔐] Headers Chori Kiye: UA={len(user_agent)} chars, Cookie={len(cookie)} chars")
#                     break
        
#     except Exception as e:
#         print(f"[⚠️] Error: {e}")
#     finally:
#         if driver:
#             driver.quit()
    
#     return found_data

# def start_ffmpeg_stream(data):
#     print("\n[🚀] FFmpeg Stream Start (Debug Mode On)...")
    
#     link = data['url']
#     ua = data['ua']
#     cookie = data['cookie']
#     referer = data['referer']
    
#     # Headers ko sahi format mein banana
#     headers_cmd = f"User-Agent: {ua}\r\nReferer: {referer}\r\nCookie: {cookie}"
    
#     cmd = [
#         "ffmpeg", "-re",
#         "-headers", headers_cmd,
#         "-i", link,
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
#     ]
    
#     # Yahan maine DEVNULL hata diya hai taake error dikhe
#     return subprocess.Popen(cmd)

# def main():
#     clear_screen()
#     print("========================================")
#     print("   V15: HEADER THIEF & DEBUGGER")
#     print("========================================")

#     while True:
#         data = get_link_and_headers()
        
#         if data:
#             process = start_ffmpeg_stream(data)
            
#             print(f"[zzz] Streaming... (Agar error aaya to niche dikhega)")
            
#             try:
#                 time.sleep(REFRESH_TIME)
#             except KeyboardInterrupt:
#                 process.terminate()
#                 break
            
#             print("\n[🔄] Refreshing...")
#             process.terminate()
#             process.wait()
            
#         else:
#             print("[❌] Link nahi mila! Retry in 1 min...")
#             time.sleep(60)

# if __name__ == "__main__":
#     main()











# ================================================


# # --- IMPORTS ---
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# import time
# import subprocess
# import os

# # --- SETTINGS ---
# TARGET_WEBSITE = "https://crichdbest.com/player.php?id=starsp3"
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda"
# REFRESH_TIME = 60 * 60  # Har 60 Minute baad naya link layega
# # ----------------

# def clear_screen():
#     os.system('cls' if os.name == 'nt' else 'clear')

# def get_magic_link():
#     print(f"\n[🕵️‍♂️] Jasoos (Selenium Wire) nikal raha hai link dhoondne...")
    
#     # --- BROWSER OPTIONS (CRASH FIXES) ---
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless=new') 
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     # Wire Options
#     seleniumwire_options = {
#         'disable_encoding': True,
#         'connection_keep_alive': True
#     }

#     driver = None
#     found_url = None

#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             seleniumwire_options=seleniumwire_options,
#             options=options
#         )
        
#         driver.get(TARGET_WEBSITE)
#         print("[⏳] Page load ho raha hai (Wait 20 sec)...")
#         time.sleep(20)

#         print("[🔍] Network traffic scan kar raha hoon...")
        
#         # --- TRAFFIC CHECK ---
#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     # Filter: Google Ads waghaira ko ignore karo
#                     if "google" not in request.url:
#                         found_url = request.url
#                         print(f"\n[✅] LINK MIL GAYA!\n{found_url}")
#                         break # Pehla link milte hi nikal jao
        
#     except Exception as e:
#         print(f"[⚠️] Error: {e}")
#     finally:
#         if driver:
#             driver.quit()
    
#     return found_url

# def start_ffmpeg_stream(m3u8_link):
#     print("\n[🚀] FFmpeg Stream Start kar raha hoon...")
    
#     # Headers bohot zaroori hain taake 'Session ID' valid rahe
#     headers = "Origin: https://crichdbest.com\r\nReferer: https://crichdbest.com/"
#     user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    
#     cmd = [
#         "ffmpeg", "-re",
#         "-headers", headers,
#         "-user_agent", user_agent,
#         "-i", m3u8_link,
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
#     ]
    
#     # Process return karo taake baad mein kill kar sakein
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# def main():
#     clear_screen()
#     print("========================================")
#     print("   FINAL AUTOMATION: DETECT & STREAM")
#     print("========================================")

#     while True:
#         # 1. Link Dhoondo
#         link = get_magic_link()
        
#         if link:
#             # 2. Stream Chalao
#             process = start_ffmpeg_stream(link)
            
#             print(f"[zzz] Stream chal rahi hai... {REFRESH_TIME/60} minute baad naya link launga.")
            
#             try:
#                 # Wait loop
#                 time.sleep(REFRESH_TIME)
#             except KeyboardInterrupt:
#                 print("\n[STOP] User ne band kar diya.")
#                 process.terminate()
#                 break
            
#             # 3. Time Up - Restart
#             print("\n[🔄] Time Up! Refreshing Link...")
#             process.terminate()
#             process.wait()
#             time.sleep(2) # Thoda saans lene do
            
#         else:
#             print("[❌] Link nahi mila! 1 minute baad dubara try karunga.")
#             time.sleep(60)

# if __name__ == "__main__":
#     main()














# import os
# import time
# import json
# import subprocess
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from webdriver_manager.chrome import ChromeDriverManager

# # --- SETTINGS ---
# TARGET_WEBSITE = "https://crichdbest.com/player.php?id=starsp3" 
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda"
# REFRESH_TIME = 50 * 60
# # ----------------

# def clear_screen():
#     os.system('cls' if os.name == 'nt' else 'clear')

# def get_link_via_network_logs():
#     print(f"\n[🕵️‍♂️] Bot Network Traffic check karne ja raha hai: {TARGET_WEBSITE}")
    
#     # 1. Enable Performance Logging (Network Sniffing)
#     options = Options()
#     options.add_argument("--headless=new") 
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--window-size=1920,1080")
#     options.add_argument("--remote-allow-origins=*")
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
#     # Capability set karna zaroori hai taake logs milein
#     options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

#     driver = None
#     try:
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=options)
        
#         driver.get(TARGET_WEBSITE)
        
#         print("[⏳] Page load aur Traffic capture ho raha hai... (Wait 25 sec)")
#         # Thoda zyada wait taake video load hona shuru ho jaye
#         time.sleep(25) 
        
#         # 2. Extract Performance Logs
#         logs = driver.get_log('performance')
        
#         print(f"[🔍] {len(logs)} Network requests scan kar raha hoon...")
        
#         found_link = None
        
#         for entry in logs:
#             log = json.loads(entry['message'])['message']
            
#             # Sirf Network Request check karo
#             if log['method'] == 'Network.requestWillBeSent':
#                 url = log['params']['request']['url']
                
#                 # Agar URL mein .m3u8 hai
#                 if ".m3u8" in url:
#                     found_link = url
#                     break # Pehla link milte hi ruk jao
        
#         if found_link:
#             print(f"[✅] NETWORK SE LINK MIL GAYA! \n{found_link[:60]}...")
#             return found_link
#         else:
#             print("[❌] Network logs mein m3u8 nahi mila.")
#             # Debug: Screenshot le lo taake pata chale screen par kya hai
#             driver.save_screenshot("debug_error.png")
#             print("[📸] Screenshot saved as 'debug_error.png' (Check files)")
#             return None
            
#     except Exception as e:
#         print(f"[⚠️] Bot Error: {e}")
#         return None
#     finally:
#         if driver:
#             driver.quit()

# def start_stream(m3u8_link):
#     print("[🚀] Streaming Start via FFmpeg...")
    
#     headers = "Origin: https://crichdbest.com\r\nReferer: https://crichdbest.com/"
    
#     cmd = [
#         "ffmpeg", "-re",
#         "-headers", headers,
#         "-i", m3u8_link,
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
#     ]
    
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# def main():
#     clear_screen()
#     print("========================================")
#     print("   NETWORK SNIFFER BOT (V10)")
#     print("========================================")

#     while True:
#         link = get_link_via_network_logs()
        
#         if link:
#             process = start_stream(link)
            
#             print(f"[zzz] Ab {REFRESH_TIME/60} minute baad naya link launga...")
#             try:
#                 time.sleep(REFRESH_TIME)
#             except KeyboardInterrupt:
#                 process.terminate()
#                 break
            
#             print("\n[🔄] Time Up! Refreshing...")
#             process.terminate()
#             process.wait()
#         else:
#             print("[:(] Link nahi mila. 1 minute baad dubara try karunga.")
#             time.sleep(60)

# if __name__ == "__main__":
    main()