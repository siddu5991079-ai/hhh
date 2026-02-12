import os
import time
import subprocess
import urllib.parse
from datetime import datetime, timezone, timedelta
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# --- SETTINGS ---
DEFAULT_URL = "https://crichdbest.com/player.php?id=starsp3"
TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# Apni Stream Key Yahan Dalein
STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda" 
RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
DEFAULT_SLEEP = 45 * 60 
# ----------------

# Timezone setup
PKT = timezone(timedelta(hours=5))

def get_link_with_headers():
    print(f"\n[🕵️‍♂️] Bot link dhoondne ja raha hai: {TARGET_WEBSITE}")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
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
        
        driver.get(TARGET_WEBSITE)
        
        # --- TASK 2: Wait time reduced to 5 seconds ---
        print("[⏳] Page loading (5 sec)...") 
        time.sleep(5) 

        for request in driver.requests:
            if request.response:
                if ".m3u8" in request.url and "google" not in request.url:
                    headers = request.headers
                    data = {
                        "url": request.url,
                        "ua": headers.get('User-Agent', ''),
                        "cookie": headers.get('Cookie', ''),
                        "referer": headers.get('Referer', 'https://crichdbest.com/')
                    }
                    print(f"[✅] Link Found: {request.url[:40]}...")
                    break
    except Exception as e:
        print(f"[⚠️] Link Finding Error: {e}")
    finally:
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
            
            # --- TASK 1: Expiry buffer changed to 5 minutes ---
            wake_up_dt = expiry_dt - timedelta(minutes=5)
            
            now_dt = datetime.now(PKT)
            seconds = (wake_up_dt - now_dt).total_seconds()
            
            # --- TASK 3: Time format changed to 12-hour AM/PM ---
            print(f"[⏰] Expiry: {expiry_dt.strftime('%I:%M %p')}")
            print(f"[💤] Restart Time: {wake_up_dt.strftime('%I:%M %p')}")
            
            if seconds > 0: return seconds
            else: return 60
            
    except:
        pass
    
    return DEFAULT_SLEEP

def start_stream(data):
    headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
    
    cmd = [
        "ffmpeg", "-re",
        "-headers", headers_cmd,
        "-i", data['url'],
        "-c:v", "libx264", "-preset", "ultrafast",
        "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
        "-vf", "scale=854:480", "-r", "25",
        "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
        "-f", "flv", RTMP_URL
    ]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    print("=== DYNAMIC STREAMER STARTED ===")
    print(f"Target: {TARGET_WEBSITE}")
    
    # Run for 6 hours
    end_time = time.time() + (6 * 60 * 60)
    current_process = None

    while time.time() < end_time:
        data = get_link_with_headers()
        
        if data:
            if current_process: current_process.terminate()
            
            current_process = start_stream(data)
            print("[🚀] Stream Started!")
            
            sleep_seconds = calculate_sleep_time(data['url'])
            print(f"[zzz] Sleeping for {int(sleep_seconds/60)} mins...")
            
            waited = 0
            while waited < sleep_seconds:
                time.sleep(10)
                waited += 10
                # Check if ffmpeg crashed
                if current_process.poll() is not None:
                    print("[⚠️] Stream Crash! Restarting...")
                    break 
            
            print("[🔄] Refreshing Link...")
            if current_process: current_process.terminate()
        else:
            print("[❌] Failed. Retry in 1 min.")
            time.sleep(60)

if __name__ == "__main__":
    main()








# ======== 500% correct hai =====================================

# import os
# import time
# import subprocess
# import urllib.parse
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # --- SETTINGS ---
# # Yahan hum GitHub se aaya hua link pakad rahe hain
# DEFAULT_URL = "https://crichdbest.com/player.php?id=starsp3"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# # Apni Stream Key Yahan Dalein
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda" 
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
# DEFAULT_SLEEP = 45 * 60 
# # ----------------


# PKT = timezone(timedelta(hours=5))

# def get_link_with_headers():
#     print(f"\n[🕵️‍♂️] Bot link dhoondne ja raha hai: {TARGET_WEBSITE}")
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless=new')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {'disable_encoding': True, 'connection_keep_alive': True}

#     driver = None
#     data = None

#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             seleniumwire_options=seleniumwire_options,
#             options=options
#         )
        
#         driver.get(TARGET_WEBSITE)
#         print("[⏳] Page loading (20 sec)...")
#         time.sleep(20)

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url and "google" not in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', ''),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', 'https://crichdbest.com/')
#                     }
#                     print(f"[✅] Link Found: {request.url[:40]}...")
#                     break
#     except Exception as e:
#         print(f"[⚠️] Link Finding Error: {e}")
#     finally:
#         if driver: driver.quit()
    
#     return data

# def calculate_sleep_time(url):
#     try:
#         parsed = urllib.parse.urlparse(url)
#         params = urllib.parse.parse_qs(parsed.query)
#         expiry_ts = None
        
#         if 'expires' in params: expiry_ts = int(params['expires'][0])
#         elif 'e' in params: expiry_ts = int(params['e'][0])
            
#         if expiry_ts:
#             expiry_dt = datetime.fromtimestamp(expiry_ts, PKT)
#             wake_up_dt = expiry_dt - timedelta(minutes=20)
#             now_dt = datetime.now(PKT)
            
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Expiry: {expiry_dt.strftime('%H:%M')}")
#             print(f"[💤] Restart Time: {wake_up_dt.strftime('%H:%M')}")
            
#             if seconds > 0: return seconds
#             else: return 60
            
#     except:
#         pass
    
#     return DEFAULT_SLEEP

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
    
#     cmd = [
#         "ffmpeg", "-re",
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# def main():
#     print("=== DYNAMIC STREAMER STARTED ===")
#     print(f"Target: {TARGET_WEBSITE}")
    
#     end_time = time.time() + (6 * 60 * 60)
#     current_process = None

#     while time.time() < end_time:
#         data = get_link_with_headers()
        
#         if data:
#             if current_process: current_process.terminate()
            
#             current_process = start_stream(data)
#             print("[🚀] Stream Started!")
            
#             sleep_seconds = calculate_sleep_time(data['url'])
#             print(f"[zzz] Sleeping for {int(sleep_seconds/60)} mins...")
            
#             waited = 0
#             while waited < sleep_seconds:
#                 time.sleep(10)
#                 waited += 10
#                 if current_process.poll() is not None:
#                     print("[⚠️] Stream Crash! Restarting...")
#                     break 
            
#             print("[🔄] Refreshing Link...")
#             if current_process: current_process.terminate()
#         else:
#             print("[❌] Failed. Retry in 1 min.")
#             time.sleep(60)

# if __name__ == "__main__":
#     main()
































































# ========== 300% correct hai bot correct in action but humey is ko dynamic link dena hu website k url jaahaa par video player hai ===================


# import os
# import time
# import subprocess
# import urllib.parse
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # --- SETTINGS ---
# # Jis page se link uthana hai
# TARGET_WEBSITE = "https://crichdbest.com/player.php?id=starsp3" 

# # Aapki OK.RU ki Key (Yahan apni wali daal lena agar change karni ho)
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda" 
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# # Agar link mein expiry na mile to 45 min baad refresh karega
# DEFAULT_SLEEP = 45 * 60 
# # ----------------

# # Pakistan Time Zone set kiya hai
# PKT = timezone(timedelta(hours=5))

# def get_link_with_headers():
#     print(f"\n[🕵️‍♂️] Bot link dhoondne ja raha hai...")
    
#     # Chrome Options (Taake server par crash na ho)
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless=new')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {'disable_encoding': True, 'connection_keep_alive': True}

#     driver = None
#     data = None

#     try:
#         # Browser Start
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             seleniumwire_options=seleniumwire_options,
#             options=options
#         )
        
#         driver.get(TARGET_WEBSITE)
#         print("[⏳] Page load ho raha hai (20 sec)...")
#         time.sleep(20) 

#         # Network Check
#         for request in driver.requests:
#             if request.response:
#                 # Sirf .m3u8 link uthao (Google Ads ko chorr kar)
#                 if ".m3u8" in request.url and "google" not in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', ''),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', 'https://crichdbest.com/')
#                     }
#                     print(f"[✅] Link Mil Gaya: {request.url[:40]}...")
#                     break
#     except Exception as e:
#         print(f"[⚠️] Link dhoondne mein error: {e}")
#     finally:
#         if driver: driver.quit()
    
#     return data

# def calculate_sleep_time(url):
#     # Yeh function check karega ke link kab expire hoga
#     try:
#         parsed = urllib.parse.urlparse(url)
#         params = urllib.parse.parse_qs(parsed.query)
#         expiry_ts = None
        
#         # Link mein expiry time dhoondo
#         if 'expires' in params: expiry_ts = int(params['expires'][0])
#         elif 'e' in params: expiry_ts = int(params['e'][0])
            
#         if expiry_ts:
#             expiry_dt = datetime.fromtimestamp(expiry_ts, PKT)
#             # Expiry se 20 minute pehle uthna hai
#             wake_up_dt = expiry_dt - timedelta(minutes=20)
#             now_dt = datetime.now(PKT)
            
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Link Expire Hoga: {expiry_dt.strftime('%H:%M')}")
#             print(f"[💤] Main Jagunga: {wake_up_dt.strftime('%H:%M')}")
            
#             if seconds > 0: return seconds
#             else: return 60 # Agar time guzar gaya to 1 min baad utho
            
#     except:
#         pass
    
#     return DEFAULT_SLEEP

# def start_stream(data):
#     # FFmpeg Command (Stream Start)
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
    
#     cmd = [
#         "ffmpeg", "-re",
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# def main():
#     print("=== FINAL ROBOT STARTED ===")
    
#     # 6 Ghante baad khud band ho jayega
#     end_time = time.time() + (6 * 60 * 60)
    
#     current_process = None

#     while time.time() < end_time:
#         data = get_link_with_headers()
        
#         if data:
#             # 1. Stream Chalao
#             if current_process:
#                 current_process.terminate() # Purani band karo
            
#             current_process = start_stream(data)
#             print("[🚀] Stream Start ho gayi hai!")
            
#             # 2. Time Calculate karo
#             sleep_seconds = calculate_sleep_time(data['url'])
#             print(f"[zzz] Ab main {int(sleep_seconds/60)} minute so raha hoon...")
            
#             # 3. Wait Loop (Jab tak time pura na ho ya stream crash na ho)
#             waited = 0
#             while waited < sleep_seconds:
#                 time.sleep(10)
#                 waited += 10
#                 # Check karo stream zinda hai ya nahi
#                 if current_process.poll() is not None:
#                     print("[⚠️] Stream Crash ho gayi! Dobara restart kar raha hoon...")
#                     break 
            
#             # 4. Refresh ka time ho gaya
#             print("[🔄] Refreshing...")
#             if current_process: current_process.terminate()
            
#         else:
#             print("[❌] Link nahi mila. 1 min baad dubara try karunga.")
#             time.sleep(60)

# if __name__ == "__main__":
#     main()