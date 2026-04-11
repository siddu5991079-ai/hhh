import os
import time
import subprocess
import urllib.parse
import traceback
import requests
from datetime import datetime, timezone, timedelta
from DrissionPage import ChromiumPage, ChromiumOptions

# ==========================================
# ⚙️ MAIN SETTINGS (DYNAMIC FROM GITHUB)
# ==========================================
STREAM_ID = str(os.environ.get('STREAM_ID', '1'))

# 🔥 FILE 1 KA LOGIC: Bhalocast Links mapped with Server ID
BHALOCAST_LINKS = {
    '1': "https://bhalocast.com/atoplay.php?v=wextres&hello=m1lko&expires=123456",     # willowextra
    '2': "https://bhalocast.com/atoplay.php?v=ptvskpr&hello=m1lko&expires=123456",     # ptvskpr
    '3': "https://bhalocast.com/atoplay.php?v=star1kibich&hello=m1lko&expires=123456", # star1kibich
    '4': "https://bhalocast.com/penguin.php?v=ptvskpr&hello=m1lko&expires=123456"      # penguin
}

# Agar GitHub se URL nahi aata ya empty hai, toh File 1 ke Bhalocast links uthayega
DEFAULT_URL = BHALOCAST_LINKS.get(STREAM_ID, BHALOCAST_LINKS['1'])
TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# 🔥 FILE 1 KA LOGIC: Hardcoded Headers for Bhalocast Bypass
REFERER = "https://bhalocast.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

# --- Stream Keys Logic ---
MULTI_KEYS = {
    '1': os.environ.get('STREAM_KEY', '14136719122027_13152308497003_hnlk6em2e4'), # Default Key
    '2': '14136743566955_13152356600427_vmdsemtmo4', # 👈 Apni Stream 2 ki key
    '3': '14136762048107_13152392710763_22fobqpsdi',  # 👈 Apni Stream 3 ki key
    '4': '14136778563179_13152426265195_c5quhoj2vm'  # 👈 Apni Stream 4 ki key
}

STREAM_KEY = MULTI_KEYS.get(STREAM_ID, MULTI_KEYS['1'])
RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
# ------------------------------------------------

PROXY_IP = os.environ.get('PROXY_IP', '31.59.20.176')
PROXY_PORT = os.environ.get('PROXY_PORT', '6754')
PROXY_USER = os.environ.get('PROXY_USER', 'fzqdczzq')
PROXY_PASS = os.environ.get('PROXY_PASS', '5ex21twl07tx')
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"

# --- MANUAL MODE INPUTS ---
MANUAL_M3U8 = os.environ.get('MANUAL_M3U8', '').strip()
MANUAL_REFERER = os.environ.get('MANUAL_REFERER', '').strip()
MANUAL_ORIGIN = os.environ.get('MANUAL_ORIGIN', '').strip()

# --- CASE 2: RAW COMMAND INPUT ---
MANUAL_FFMPEG_CMD = os.environ.get('MANUAL_FFMPEG_CMD', '').strip()

DEFAULT_SLEEP = 45 * 60 
PKT = timezone(timedelta(hours=5))
# ==========================================

def trigger_next_run():
    print("\n" + "="*50)
    print(" ⏰ AUTO-RESTART TRIGGER ACTIVATED ⏰")
    print("="*50)
    print("[🔄] 5 Ghante 45 Minute poore ho gaye hain! Naya Bot chala raha hoon...")
    
    token = os.environ.get('GH_PAT')
    repo = os.environ.get('GITHUB_REPOSITORY') 
    branch = os.environ.get('GITHUB_REF_NAME', 'main')
    
    if not token or not repo:
        print("[❌] GH_PAT ya Repo Name nahi mila! Auto-Restart Fail ho gaya.")
        return

    url = f"https://api.github.com/repos/{repo}/actions/workflows/stream.yml/dispatches"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    data = {
        "ref": branch,
        "inputs": {
            "stream_id": STREAM_ID,
            "target_url": TARGET_WEBSITE,
            "stream_key": STREAM_KEY,
            "proxy_ip": PROXY_IP,
            "proxy_port": PROXY_PORT,
            "proxy_user": PROXY_USER,
            "proxy_pass": PROXY_PASS,
            "manual_m3u8": MANUAL_M3U8,
            "manual_referer": MANUAL_REFERER,
            "manual_origin": MANUAL_ORIGIN,
            "manual_ffmpeg_cmd": MANUAL_FFMPEG_CMD
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 204:
            print(f"[✅] SUCCESS! Nayi 'stream.yml' (Server {STREAM_ID}) background mein start ho gayi hai!")
        else:
            print(f"[❌] FAILED to start new bot. Status: {response.status_code}")
    except Exception as e:
        print(f"[💥] API Error: {e}")

def get_link_with_headers():
    """DrissionPage se M3U8 link extract karna (Bhalocast bypass ke sath)"""
    print(f"\n========================================")
    print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
    print(f"[🔍] [STEP 2] Proxy Set for Link Fetching: {PROXY_URL.split('@')[-1]}")
    
    opts = ChromiumOptions()
    opts.set_argument('--no-sandbox')
    opts.set_argument('--disable-dev-shm-usage')
    opts.set_argument('--disable-gpu')
    opts.set_argument('--autoplay-policy=no-user-gesture-required')
    opts.set_argument('--mute-audio')
    
    # Proxy Setup for DrissionPage
    opts.set_proxy(PROXY_URL)

    page = None
    data = None

    try:
        print(f"[⚙️] [STEP 3] Chromium Browser start ho raha hai (DrissionPage)...")
        page = ChromiumPage(addr_or_opts=opts)
        
        # M3U8 packets ko listen karna start karein
        page.listen.start('m3u8')
        
        print(f"[🌐] [STEP 5] Website open kar raha hoon...")
        page.get(TARGET_WEBSITE)
        
        print("[⏳] [STEP 6] Cloudflare Turnstile bypass wait... Scanning for .m3u8 (Max 90s)")
        
        start_time = time.time()
        
        # 90 seconds tak background requests check karna
        while time.time() - start_time < 90:
            for packet in page.listen.steps(count=1, timeout=3, gap=1):
                if packet:
                    items = packet if isinstance(packet, list) else [packet]
                    for p in items:
                        print(f"\n🎉 [BINGO] Cloudflare Bypassed! Link Mil Gaya: {p.url}")
                        
                        # DrissionPage ke original headers nikalne ki koshish
                        req_headers = {}
                        if hasattr(p, 'request') and hasattr(p.request, 'headers'):
                            req_headers = p.request.headers
                        
                        # File 1 wale Hardcoded Bhalocast Headers apply kar rahe hain
                        data = {
                            "url": p.url,
                            "ua": USER_AGENT,
                            "cookie": req_headers.get('Cookie', ''),
                            "referer": REFERER,
                            "origin": req_headers.get('Origin', '')
                        }
                        break
                if data: break
            if data: break
            
            elapsed = int(time.time() - start_time)
            if elapsed % 15 == 0 and elapsed > 0:
                print(f"  {elapsed}s elapsed...")

        if not data:
            print("\n[🚨] WARNING: .m3u8 link nahi mila! WAF ne block kiya ya wait time khatam.")
            
    except Exception as e:
        print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
        print(traceback.format_exc())
    finally:
        if page:
            print("[🧹] [STEP 8] Browser band kiya ja raha hai...")
            page.listen.stop()
            page.quit()
    
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
            
            print(f"[⏰] Asli Link Expiry Time: {expiry_dt.strftime('%I:%M %p')} PKT")
            print(f"[🛠️] Pre-Fetch Time: Bot {wake_up_dt.strftime('%I:%M %p')} par uthega.")
            
            if seconds > 0: return seconds
            else: return 60
    except Exception:
        pass
    return DEFAULT_SLEEP

#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
def start_stream(data):
    # File 1 wali format me Headers pass ho rahe hain FFmpeg ko
    headers_cmd = f"Referer: {data['referer']}\r\nUser-Agent: {data['ua']}\r\n"
    if data.get('cookie'):
        headers_cmd += f"Cookie: {data['cookie']}\r\n"
    if data.get('origin'):
        headers_cmd += f"Origin: {data['origin']}\r\n"
    
    print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai (360p ULTRA-LOW BANDWIDTH)...")
    cmd = [
        "ffmpeg", "-re",
        "-loglevel", "error", 
        "-fflags", "+genpts",  
        "-headers", headers_cmd,
        "-user_agent", data['ua'],  # Explicit user agent
        "-i", data['url'],
        "-c:v", "libx264", "-preset", "ultrafast",
        "-b:v", "300k", "-maxrate", "400k", "-bufsize", "800k", 
        "-vf", "scale=640:360", "-r", "20",                     
        "-c:a", "aac", "-b:a", "32k", "-ar", "44100",            
        "-async", "1",         
        "-f", "flv", RTMP_URL
    ]
    print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Slow Internet Optimized)")
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)

def main():
    print("========================================")
    print("   🚀 ULTIMATE ALL-IN-ONE STREAMER (DrissionPage Edition)")
    print(f"   📡 SELECTED SERVER ID: {STREAM_ID}")
    print("========================================")
    
    start_time = time.time()
    RESTART_TIME_LIMIT = (5 * 60 * 60) + (45 * 60) # 5h 45m
    end_time = start_time + (6 * 60 * 60)
    
    # ====================================================
    # 🔥 CASE 2: RAW FFMPEG COMMAND OVERRIDE LOGIC
    # ====================================================
    if MANUAL_FFMPEG_CMD:
        print("\n[🎯] ⚡ RAW FFMPEG COMMAND OVERRIDE ACTIVATED ⚡")
        print("Bot apni link-finding logic band kar raha hai aur direct aapki command chala raha hai...")
        
        next_run_triggered = False
        while time.time() < end_time:
            if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
                trigger_next_run()
                next_run_triggered = True

            print(f"\n[🎬] Executing Full Command: \n{MANUAL_FFMPEG_CMD[:150]}... (truncated for display)")
            
            try:
                current_process = subprocess.Popen(MANUAL_FFMPEG_CMD, shell=True)
                current_process.wait() 
            except Exception as e:
                print(f"[💥] Command Error: {e}")
                
            print("\n[⚠️] Command rukk gayi ya stream crash ho gayi. 10 second baad dobara try kar raha hoon...")
            time.sleep(10)
            
        return 
    # ====================================================

    current_process = None
    next_run_triggered = False
    is_manual_mode = bool(MANUAL_M3U8)

    if is_manual_mode:
        print("\n[🎯] ⚡ MANUAL M3U8 LINK ACTIVATED ⚡")
        data = {
            "url": MANUAL_M3U8,
            "referer": MANUAL_REFERER if MANUAL_REFERER else REFERER,
            "origin": MANUAL_ORIGIN,
            "ua": USER_AGENT,
            "cookie": ""
        }
    else:
        data = get_link_with_headers()

    while time.time() < end_time:
        try:
            if not data:
                print("\n[🔄] Link lene ja raha hoon...")
                data = get_link_with_headers()
                if not data:
                    print("\n[❌] Link nahi mila. 1 minute baad dobara koshish hogi...")
                    time.sleep(60)
                    continue

            if current_process: current_process.terminate()
            current_process = start_stream(data)
            print("\n[🚀] SUCCESS! Video feed OK.ru par live hai!")
            
            if is_manual_mode:
                sleep_seconds = 10 * 60 * 60
            else:
                sleep_seconds = calculate_sleep_time(data['url'])
                print(f"[zzz] AUTO MODE: Bot {int(sleep_seconds/60)} mins rest karega...")
            
            waited = 0
            crashed = False
            
            while waited < sleep_seconds:
                time.sleep(10)
                waited += 10
                
                if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
                    trigger_next_run()
                    next_run_triggered = True 
                    
                if current_process.poll() is not None:
                    exit_code = current_process.poll()
                    print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
                    crashed = True
                    break 
            
            if not is_manual_mode and not crashed:
                print("\n[🕵️‍♂️] PRE-FETCH MODE: Background mein naya link la raha hoon...")
                new_data = get_link_with_headers()
                if new_data:
                    print("\n[⚡] NAYA LINK READY! Millisecond swap kar raha hoon...")
                    data = new_data 
                else:
                    print("\n[⚠️] Pre-fetch fail! Purani stream ko natural crash hone tak chalne do...")
                    current_process.wait() 
                    data = None 
            elif crashed and not is_manual_mode:
                data = None 

        except Exception:
            print(f"\n[💥] MAIN LOOP ERROR:")
            print(traceback.format_exc())
            time.sleep(60)

if __name__ == "__main__":
    main()





































# ================ crichd website ney new update laya hai, jiss see below code m3u8 link ko capture nahey kar paa raha hai . iss liyee upper code mei iss problem koo fix karney k try kar rahey hai ========================





# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# import requests
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (DYNAMIC FROM GITHUB)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# # --- NAYA LOGIC: Number se Stream Key nikalna ---
# STREAM_ID = str(os.environ.get('STREAM_ID', '1'))

# MULTI_KEYS = {
#     '1': os.environ.get('STREAM_KEY', '14136719122027_13152308497003_hnlk6em2e4'), # Default Key
#     # '1': '13792808935019_12476172012139_mstifuzoo4',
#     '2': '14136743566955_13152356600427_vmdsemtmo4', # 👈 Apni Stream 2 ki key yahan dalein
#     '3': '14136762048107_13152392710763_22fobqpsdi',  # 👈 Apni Stream 3 ki key yahan dalein
#     '4': '14136778563179_13152426265195_c5quhoj2vm'
# }

# STREAM_KEY = MULTI_KEYS.get(STREAM_ID, MULTI_KEYS['1'])
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
# # ------------------------------------------------

# PROXY_IP = os.environ.get('PROXY_IP', '31.59.20.176')
# PROXY_PORT = os.environ.get('PROXY_PORT', '6754')
# PROXY_USER = os.environ.get('PROXY_USER', 'cjasfidu')
# PROXY_PASS = os.environ.get('PROXY_PASS', 'qhnyvm0qpf6p')
# PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"

# # --- MANUAL MODE INPUTS ---
# MANUAL_M3U8 = os.environ.get('MANUAL_M3U8', '').strip()
# MANUAL_REFERER = os.environ.get('MANUAL_REFERER', '').strip()
# MANUAL_ORIGIN = os.environ.get('MANUAL_ORIGIN', '').strip()

# # --- CASE 2: RAW COMMAND INPUT ---
# MANUAL_FFMPEG_CMD = os.environ.get('MANUAL_FFMPEG_CMD', '').strip()

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def trigger_next_run():
#     print("\n" + "="*50)
#     print(" ⏰ AUTO-RESTART TRIGGER ACTIVATED ⏰")
#     print("="*50)
#     print("[🔄] 5 Ghante 45 Minute poore ho gaye hain! Naya Bot chala raha hoon...")
    
#     token = os.environ.get('GH_PAT')
#     repo = os.environ.get('GITHUB_REPOSITORY') 
#     branch = os.environ.get('GITHUB_REF_NAME', 'main')
    
#     if not token or not repo:
#         print("[❌] GH_PAT ya Repo Name nahi mila! Auto-Restart Fail ho gaya.")
#         return

#     url = f"https://api.github.com/repos/{repo}/actions/workflows/stream.yml/dispatches"
    
#     headers = {
#         "Accept": "application/vnd.github.v3+json",
#         "Authorization": f"token {token}"
#     }
    
#     data = {
#         "ref": branch,
#         "inputs": {
#             "stream_id": STREAM_ID, # 👈 NAYA LOGIC: Auto-restart mein same Server ID dobara bhejega
#             "target_url": TARGET_WEBSITE,
#             "stream_key": STREAM_KEY,
#             "proxy_ip": PROXY_IP,
#             "proxy_port": PROXY_PORT,
#             "proxy_user": PROXY_USER,
#             "proxy_pass": PROXY_PASS,
#             "manual_m3u8": MANUAL_M3U8,
#             "manual_referer": MANUAL_REFERER,
#             "manual_origin": MANUAL_ORIGIN,
#             "manual_ffmpeg_cmd": MANUAL_FFMPEG_CMD
#         }
#     }
    
#     try:
#         response = requests.post(url, headers=headers, json=data)
#         if response.status_code == 204:
#             print(f"[✅] SUCCESS! Nayi 'stream.yml' (Server {STREAM_ID}) background mein start ho gayi hai!")
#         else:
#             print(f"[❌] FAILED to start new bot. Status: {response.status_code}")
#     except Exception as e:
#         print(f"[💥] API Error: {e}")

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy Set for Link Fetching: {PROXY_URL.split('@')[-1]}")
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {
#         'proxy': {'http': PROXY_URL, 'https': PROXY_URL, 'no_proxy': 'localhost,127.0.0.1'},
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai Proxy ke sath...")
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), seleniumwire_options=seleniumwire_options, options=options)
        
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon...")
#         driver.get(TARGET_WEBSITE)
        
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds wait...") 
#         for i in range(5, 0, -1):
#             time.sleep(1)
            
#         print("[✅] [STEP 7] Scanning network requests for .m3u8 token...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE),
#                         "origin": ""
#                     }
#                     print(f"\n🎉 [BINGO] Cloudflare Bypassed! Link Mil Gaya!")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: .m3u8 link nahi mila! WAF ne block kiya ya wait time kam tha.")
            
#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: 
#             print("[🧹] [STEP 8] Chrome Browser band kiya ja raha hai...")
#             driver.quit()
    
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Asli Link Expiry Time: {expiry_dt.strftime('%I:%M %p')} PKT")
#             print(f"[🛠️] Pre-Fetch Time: Bot {wake_up_dt.strftime('%I:%M %p')} par uthega.")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
#     return DEFAULT_SLEEP

# #,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
#     if data.get('origin'):
#         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai (360p ULTRA-LOW BANDWIDTH)...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-fflags", "+genpts",  
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "300k", "-maxrate", "400k", "-bufsize", "800k", 
#         "-vf", "scale=640:360", "-r", "20",                     
#         "-c:a", "aac", "-b:a", "32k", "-ar", "44100",           
#         "-async", "1",         
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Slow Internet Optimized)")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)

# def main():
#     print("========================================")
#     print("   🚀 ULTIMATE ALL-IN-ONE STREAMER")
#     print(f"   📡 SELECTED SERVER ID: {STREAM_ID}")
#     print("========================================")
    
#     start_time = time.time()
#     RESTART_TIME_LIMIT = (5 * 60 * 60) + (45 * 60) # 5h 45m
#     end_time = start_time + (6 * 60 * 60)
    
#     # ====================================================
#     # 🔥 CASE 2: RAW FFMPEG COMMAND OVERRIDE LOGIC
#     # ====================================================
#     if MANUAL_FFMPEG_CMD:
#         print("\n[🎯] ⚡ RAW FFMPEG COMMAND OVERRIDE ACTIVATED ⚡")
#         print("Bot apni link-finding logic band kar raha hai aur direct aapki command chala raha hai...")
        
#         next_run_triggered = False
#         while time.time() < end_time:
#             if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
#                 trigger_next_run()
#                 next_run_triggered = True

#             print(f"\n[🎬] Executing Full Command: \n{MANUAL_FFMPEG_CMD[:150]}... (truncated for display)")
            
#             try:
#                 current_process = subprocess.Popen(MANUAL_FFMPEG_CMD, shell=True)
#                 current_process.wait() 
#             except Exception as e:
#                 print(f"[💥] Command Error: {e}")
                
#             print("\n[⚠️] Command rukk gayi ya stream crash ho gayi. 10 second baad dobara try kar raha hoon...")
#             time.sleep(10)
            
#         return 
#     # ====================================================

#     current_process = None
#     next_run_triggered = False
#     is_manual_mode = bool(MANUAL_M3U8)

#     if is_manual_mode:
#         print("\n[🎯] ⚡ MANUAL M3U8 LINK ACTIVATED ⚡")
#         data = {
#             "url": MANUAL_M3U8,
#             "referer": MANUAL_REFERER,
#             "origin": MANUAL_ORIGIN,
#             "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
#             "cookie": ""
#         }
#     else:
#         data = get_link_with_headers()

#     while time.time() < end_time:
#         try:
#             if not data:
#                 print("\n[🔄] Link lene ja raha hoon...")
#                 data = get_link_with_headers()
#                 if not data:
#                     print("\n[❌] Link nahi mila. 1 minute baad dobara koshish hogi...")
#                     time.sleep(60)
#                     continue

#             if current_process: current_process.terminate()
#             current_process = start_stream(data)
#             print("\n[🚀] SUCCESS! Video feed OK.ru par live hai!")
            
#             if is_manual_mode:
#                 sleep_seconds = 10 * 60 * 60
#             else:
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] AUTO MODE: Bot {int(sleep_seconds/60)} mins rest karega...")
            
#             waited = 0
#             crashed = False
            
#             while waited < sleep_seconds:
#                 time.sleep(10)
#                 waited += 10
                
#                 if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
#                     trigger_next_run()
#                     next_run_triggered = True 
                    
#                 if current_process.poll() is not None:
#                     exit_code = current_process.poll()
#                     print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                     crashed = True
#                     break 
            
#             if not is_manual_mode and not crashed:
#                 print("\n[🕵️‍♂️] PRE-FETCH MODE: Background mein naya link la raha hoon...")
#                 new_data = get_link_with_headers()
#                 if new_data:
#                     print("\n[⚡] NAYA LINK READY! Millisecond swap kar raha hoon...")
#                     data = new_data 
#                 else:
#                     print("\n[⚠️] Pre-fetch fail! Purani stream ko natural crash hone tak chalne do...")
#                     current_process.wait() 
#                     data = None 
#             elif crashed and not is_manual_mode:
#                 data = None 

#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()









# ====================== multi stream logic added upper code,belwo code iss 100% valid for single match stream ====================================================================


# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# import requests
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (DYNAMIC FROM GITHUB)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# STREAM_KEY = os.environ.get('STREAM_KEY', '11523921485458_10535073221266_x3wpukcvda')
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# PROXY_IP = os.environ.get('PROXY_IP', '31.59.20.176')
# PROXY_PORT = os.environ.get('PROXY_PORT', '6754')
# PROXY_USER = os.environ.get('PROXY_USER', 'cjasfidu')
# PROXY_PASS = os.environ.get('PROXY_PASS', 'qhnyvm0qpf6p')
# PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"

# # --- MANUAL MODE INPUTS ---
# MANUAL_M3U8 = os.environ.get('MANUAL_M3U8', '').strip()
# MANUAL_REFERER = os.environ.get('MANUAL_REFERER', '').strip()
# MANUAL_ORIGIN = os.environ.get('MANUAL_ORIGIN', '').strip()

# # --- CASE 2: RAW COMMAND INPUT ---
# MANUAL_FFMPEG_CMD = os.environ.get('MANUAL_FFMPEG_CMD', '').strip()

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def trigger_next_run():
#     print("\n" + "="*50)
#     print(" ⏰ AUTO-RESTART TRIGGER ACTIVATED ⏰")
#     print("="*50)
#     print("[🔄] 5 Ghante 45 Minute poore ho gaye hain! Naya Bot chala raha hoon...")
    
#     token = os.environ.get('GH_PAT')
#     repo = os.environ.get('GITHUB_REPOSITORY') 
#     branch = os.environ.get('GITHUB_REF_NAME', 'main')
    
#     if not token or not repo:
#         print("[❌] GH_PAT ya Repo Name nahi mila! Auto-Restart Fail ho gaya.")
#         return

#     url = f"https://api.github.com/repos/{repo}/actions/workflows/stream.yml/dispatches"
    
#     headers = {
#         "Accept": "application/vnd.github.v3+json",
#         "Authorization": f"token {token}"
#     }
    
#     data = {
#         "ref": branch,
#         "inputs": {
#             "target_url": TARGET_WEBSITE,
#             "stream_key": STREAM_KEY,
#             "proxy_ip": PROXY_IP,
#             "proxy_port": PROXY_PORT,
#             "proxy_user": PROXY_USER,
#             "proxy_pass": PROXY_PASS,
#             "manual_m3u8": MANUAL_M3U8,
#             "manual_referer": MANUAL_REFERER,
#             "manual_origin": MANUAL_ORIGIN,
#             "manual_ffmpeg_cmd": MANUAL_FFMPEG_CMD # Nayi field ko bhi aage bhej raha hai
#         }
#     }
    
#     try:
#         response = requests.post(url, headers=headers, json=data)
#         if response.status_code == 204:
#             print("[✅] SUCCESS! Nayi 'stream.yml' background mein start ho gayi hai!")
#         else:
#             print(f"[❌] FAILED to start new bot. Status: {response.status_code}")
#     except Exception as e:
#         print(f"[💥] API Error: {e}")

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy Set for Link Fetching: {PROXY_URL.split('@')[-1]}")
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {
#         'proxy': {'http': PROXY_URL, 'https': PROXY_URL, 'no_proxy': 'localhost,127.0.0.1'},
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai Proxy ke sath...")
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), seleniumwire_options=seleniumwire_options, options=options)
        
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon...")
#         driver.get(TARGET_WEBSITE)
        
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds wait...") 
#         for i in range(5, 0, -1):
#             time.sleep(1)
            
#         print("[✅] [STEP 7] Scanning network requests for .m3u8 token...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE),
#                         "origin": ""
#                     }
#                     print(f"\n🎉 [BINGO] Cloudflare Bypassed! Link Mil Gaya!")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: .m3u8 link nahi mila! WAF ne block kiya ya wait time kam tha.")
            
#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: 
#             print("[🧹] [STEP 8] Chrome Browser band kiya ja raha hai...")
#             driver.quit()
    
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Asli Link Expiry Time: {expiry_dt.strftime('%I:%M %p')} PKT")
#             print(f"[🛠️] Pre-Fetch Time: Bot {wake_up_dt.strftime('%I:%M %p')} par uthega.")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
#     return DEFAULT_SLEEP

# #,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
#     if data.get('origin'):
#         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai (360p ULTRA-LOW BANDWIDTH)...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-fflags", "+genpts",  
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "300k", "-maxrate", "400k", "-bufsize", "800k", # 👈 Bitrate half kar diya
#         "-vf", "scale=640:360", "-r", "20",                     # 👈 360p aur 20 FPS kar diya
#         "-c:a", "aac", "-b:a", "32k", "-ar", "44100",           # 👈 Audio quality low kar di
#         "-async", "1",         
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Slow Internet Optimized)")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)



# # def start_stream(data):
# #     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
# #     if data.get('origin'):
# #         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
# #     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai (360p + STABLE KEYFRAMES)...")
# #     cmd = [
# #         "ffmpeg", "-re",
# #         "-loglevel", "error", 
# #         "-fflags", "+genpts+discardcorrupt",  # 👈 Kharab hone par corrupt data ko discard karega
# #         "-headers", headers_cmd,
# #         "-i", data['url'],
# #         "-c:v", "libx264", "-preset", "ultrafast",
# #         "-b:v", "300k", "-maxrate", "400k", "-bufsize", "800k",
# #         "-vf", "scale=640:360", "-r", "20",
# #         "-g", "40",                           # 👈 NAYA PARAMETER: Har 2 sec baad keyframe bhejega (20fps x 2 = 40). Yeh sync out nahi hone dega!
# #         "-c:a", "aac", "-b:a", "32k", "-ar", "44100",
# #         "-f", "flv", RTMP_URL
# #     ]
# #     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Bursting Fixed)")
# #     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)


# def main():
#     print("========================================")
#     print("   🚀 ULTIMATE ALL-IN-ONE STREAMER")
#     print("========================================")
    
#     start_time = time.time()
#     RESTART_TIME_LIMIT = (5 * 60 * 60) + (45 * 60) # 5h 45m
#     end_time = start_time + (6 * 60 * 60)
    
#     # ====================================================
#     # 🔥 CASE 2: RAW FFMPEG COMMAND OVERRIDE LOGIC
#     # ====================================================
#     if MANUAL_FFMPEG_CMD:
#         print("\n[🎯] ⚡ RAW FFMPEG COMMAND OVERRIDE ACTIVATED ⚡")
#         print("Bot apni link-finding logic band kar raha hai aur direct aapki command chala raha hai...")
        
#         next_run_triggered = False
#         while time.time() < end_time:
#             # Check for Auto-Restart in Raw Command mode
#             if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
#                 trigger_next_run()
#                 next_run_triggered = True

#             print(f"\n[🎬] Executing Full Command: \n{MANUAL_FFMPEG_CMD[:150]}... (truncated for display)")
            
#             try:
#                 # shell=True use kiya hai taake aapki command exactly wese hi chale jese terminal par chalti hai
#                 current_process = subprocess.Popen(MANUAL_FFMPEG_CMD, shell=True)
#                 current_process.wait() # Jab tak crash na ho chalne do
#             except Exception as e:
#                 print(f"[💥] Command Error: {e}")
                
#             print("\n[⚠️] Command rukk gayi ya stream crash ho gayi. 10 second baad dobara try kar raha hoon...")
#             time.sleep(10)
            
#         return # Raw command case yahan khatam ho jata hai
#     # ====================================================

#     current_process = None
#     next_run_triggered = False
#     is_manual_mode = bool(MANUAL_M3U8)

#     if is_manual_mode:
#         print("\n[🎯] ⚡ MANUAL M3U8 LINK ACTIVATED ⚡")
#         data = {
#             "url": MANUAL_M3U8,
#             "referer": MANUAL_REFERER,
#             "origin": MANUAL_ORIGIN,
#             "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
#             "cookie": ""
#         }
#     else:
#         data = get_link_with_headers()

#     while time.time() < end_time:
#         try:
#             if not data:
#                 print("\n[🔄] Link lene ja raha hoon...")
#                 data = get_link_with_headers()
#                 if not data:
#                     print("\n[❌] Link nahi mila. 1 minute baad dobara koshish hogi...")
#                     time.sleep(60)
#                     continue

#             if current_process: current_process.terminate()
#             current_process = start_stream(data)
#             print("\n[🚀] SUCCESS! Video feed OK.ru par live hai!")
            
#             if is_manual_mode:
#                 sleep_seconds = 10 * 60 * 60
#             else:
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] AUTO MODE: Bot {int(sleep_seconds/60)} mins rest karega...")
            
#             waited = 0
#             crashed = False
            
#             while waited < sleep_seconds:
#                 time.sleep(10)
#                 waited += 10
                
#                 if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
#                     trigger_next_run()
#                     next_run_triggered = True 
                    
#                 if current_process.poll() is not None:
#                     exit_code = current_process.poll()
#                     print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                     crashed = True
#                     break 
            
#             if not is_manual_mode and not crashed:
#                 print("\n[🕵️‍♂️] PRE-FETCH MODE: Background mein naya link la raha hoon...")
#                 new_data = get_link_with_headers()
#                 if new_data:
#                     print("\n[⚡] NAYA LINK READY! Millisecond swap kar raha hoon...")
#                     data = new_data 
#                 else:
#                     print("\n[⚠️] Pre-fetch fail! Purani stream ko natural crash hone tak chalne do...")
#                     current_process.wait() 
#                     data = None 
#             elif crashed and not is_manual_mode:
#                 data = None 

#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()



























    







# ======================================


# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# import requests
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (DYNAMIC FROM GITHUB)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# STREAM_KEY = os.environ.get('STREAM_KEY', '11523921485458_10535073221266_x3wpukcvda')
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# PROXY_IP = os.environ.get('PROXY_IP', '31.59.20.176')
# PROXY_PORT = os.environ.get('PROXY_PORT', '6754')
# PROXY_USER = os.environ.get('PROXY_USER', 'cjasfidu')
# PROXY_PASS = os.environ.get('PROXY_PASS', 'qhnyvm0qpf6p')
# PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"

# # --- MANUAL MODE INPUTS ---
# MANUAL_M3U8 = os.environ.get('MANUAL_M3U8', '').strip()
# MANUAL_REFERER = os.environ.get('MANUAL_REFERER', '').strip()
# MANUAL_ORIGIN = os.environ.get('MANUAL_ORIGIN', '').strip()

# # --- CASE 2: RAW COMMAND INPUT ---
# MANUAL_FFMPEG_CMD = os.environ.get('MANUAL_FFMPEG_CMD', '').strip()

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def trigger_next_run():
#     print("\n" + "="*50)
#     print(" ⏰ AUTO-RESTART TRIGGER ACTIVATED ⏰")
#     print("="*50)
#     print("[🔄] 5 Ghante 45 Minute poore ho gaye hain! Naya Bot chala raha hoon...")
    
#     token = os.environ.get('GH_PAT')
#     repo = os.environ.get('GITHUB_REPOSITORY') 
#     branch = os.environ.get('GITHUB_REF_NAME', 'main')
    
#     if not token or not repo:
#         print("[❌] GH_PAT ya Repo Name nahi mila! Auto-Restart Fail ho gaya.")
#         return

#     url = f"https://api.github.com/repos/{repo}/actions/workflows/stream.yml/dispatches"
    
#     headers = {
#         "Accept": "application/vnd.github.v3+json",
#         "Authorization": f"token {token}"
#     }
    
#     data = {
#         "ref": branch,
#         "inputs": {
#             "target_url": TARGET_WEBSITE,
#             "stream_key": STREAM_KEY,
#             "proxy_ip": PROXY_IP,
#             "proxy_port": PROXY_PORT,
#             "proxy_user": PROXY_USER,
#             "proxy_pass": PROXY_PASS,
#             "manual_m3u8": MANUAL_M3U8,
#             "manual_referer": MANUAL_REFERER,
#             "manual_origin": MANUAL_ORIGIN,
#             "manual_ffmpeg_cmd": MANUAL_FFMPEG_CMD # Nayi field ko bhi aage bhej raha hai
#         }
#     }
    
#     try:
#         response = requests.post(url, headers=headers, json=data)
#         if response.status_code == 204:
#             print("[✅] SUCCESS! Nayi 'stream.yml' background mein start ho gayi hai!")
#         else:
#             print(f"[❌] FAILED to start new bot. Status: {response.status_code}")
#     except Exception as e:
#         print(f"[💥] API Error: {e}")

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy Set for Link Fetching: {PROXY_URL.split('@')[-1]}")
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {
#         'proxy': {'http': PROXY_URL, 'https': PROXY_URL, 'no_proxy': 'localhost,127.0.0.1'},
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai Proxy ke sath...")
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), seleniumwire_options=seleniumwire_options, options=options)
        
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon...")
#         driver.get(TARGET_WEBSITE)
        
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds wait...") 
#         for i in range(5, 0, -1):
#             time.sleep(1)
            
#         print("[✅] [STEP 7] Scanning network requests for .m3u8 token...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE),
#                         "origin": ""
#                     }
#                     print(f"\n🎉 [BINGO] Cloudflare Bypassed! Link Mil Gaya!")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: .m3u8 link nahi mila! WAF ne block kiya ya wait time kam tha.")
            
#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: 
#             print("[🧹] [STEP 8] Chrome Browser band kiya ja raha hai...")
#             driver.quit()
    
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Asli Link Expiry Time: {expiry_dt.strftime('%I:%M %p')} PKT")
#             print(f"[🛠️] Pre-Fetch Time: Bot {wake_up_dt.strftime('%I:%M %p')} par uthega.")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
#     return DEFAULT_SLEEP



# # ===============================================================

# # def start_stream(data):
# #     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
# #     if data.get('origin'):
# #         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
# #     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
# #     cmd = [
# #         "ffmpeg", "-re",
# #         "-loglevel", "error", 
# #         "-fflags", "+genpts",  # Sync ke liye
# #         "-headers", headers_cmd,
# #         "-i", data['url'],
# #         "-c:v", "copy",        # 👈 YEH CHANGE KIYA: Original HD video direct aage bhejne ke liye
# #         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
# #         "-async", "1",         # Sync ke liye
# #         "-f", "flv", RTMP_URL
# #     ]
# #     print("[⚙️] [STEP 10] FFmpeg Stream HD Quality mein Launch ho rahi hai!")
# #     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)






#  ## 1st priotiy
# # def start_stream(data):
# #     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
# #     if data.get('origin'):
# #         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
# #     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
# #     cmd = [
# #         "ffmpeg", "-re",
# #         "-loglevel", "error", 
# #         "-fflags", "+genpts",  # Sync maintain rakhne ke liye
# #         "-headers", headers_cmd,
# #         "-i", data['url'],
        
# #         # 👇 YEH WAPIS ADD KIYA HAI: Video quality ko chota (480p) aur stabilize karne ke liye
# #         "-c:v", "libx264", "-preset", "ultrafast",
# #         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
# #         "-vf", "scale=854:480", "-r", "25",
        
# #         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
# #         "-async", "1",         # Audio ko video ke sath lock rakhne ke liye
# #         "-f", "flv", RTMP_URL
# #     ]
# #     print("[⚙️] [STEP 10] FFmpeg Stream 480p (Optimized) Quality mein Launch ho rahi hai!")
# #     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)









# # def start_stream(data):
# #     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
# #     if data.get('origin'):
# #         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
# #     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
# #     cmd = [
# #         "ffmpeg", "-re",
# #         "-loglevel", "error", 
# #         "-headers", headers_cmd,
# #         "-i", data['url'],
# #         "-c:v", "libx264", "-preset", "ultrafast",
# #         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
# #         "-vf", "scale=854:480", "-r", "25",
# #         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
# #         "-f", "flv", RTMP_URL
# #     ]
# #     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Direct GitHub Network par)")
# #     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 



# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
#     if data.get('origin'):
#         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-fflags", "+genpts",  # Sync maintain rakhne ke liye
#         "-headers", headers_cmd,
#         "-i", data['url'],
        
#         # 👇 YEH WAPIS ADD KIYA HAI: Video quality ko chota (480p) aur stabilize karne ke liye
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
        
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-async", "1",         # Audio ko video ke sath lock rakhne ke liye
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream 480p (Optimized) Quality mein Launch ho rahi hai!")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)



# # =========================================================



# def main():
#     print("========================================")
#     print("   🚀 ULTIMATE ALL-IN-ONE STREAMER")
#     print("========================================")
    
#     start_time = time.time()
#     RESTART_TIME_LIMIT = (5 * 60 * 60) + (45 * 60) # 5h 45m
#     end_time = start_time + (6 * 60 * 60)
    
#     # ====================================================
#     # 🔥 CASE 2: RAW FFMPEG COMMAND OVERRIDE LOGIC
#     # ====================================================
#     if MANUAL_FFMPEG_CMD:
#         print("\n[🎯] ⚡ RAW FFMPEG COMMAND OVERRIDE ACTIVATED ⚡")
#         print("Bot apni link-finding logic band kar raha hai aur direct aapki command chala raha hai...")
        
#         next_run_triggered = False
#         while time.time() < end_time:
#             # Check for Auto-Restart in Raw Command mode
#             if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
#                 trigger_next_run()
#                 next_run_triggered = True

#             print(f"\n[🎬] Executing Full Command: \n{MANUAL_FFMPEG_CMD[:150]}... (truncated for display)")
            
#             try:
#                 # shell=True use kiya hai taake aapki command exactly wese hi chale jese terminal par chalti hai
#                 current_process = subprocess.Popen(MANUAL_FFMPEG_CMD, shell=True)
#                 current_process.wait() # Jab tak crash na ho chalne do
#             except Exception as e:
#                 print(f"[💥] Command Error: {e}")
                
#             print("\n[⚠️] Command rukk gayi ya stream crash ho gayi. 10 second baad dobara try kar raha hoon...")
#             time.sleep(10)
            
#         return # Raw command case yahan khatam ho jata hai
#     # ====================================================

#     current_process = None
#     next_run_triggered = False
#     is_manual_mode = bool(MANUAL_M3U8)

#     if is_manual_mode:
#         print("\n[🎯] ⚡ MANUAL M3U8 LINK ACTIVATED ⚡")
#         data = {
#             "url": MANUAL_M3U8,
#             "referer": MANUAL_REFERER,
#             "origin": MANUAL_ORIGIN,
#             "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
#             "cookie": ""
#         }
#     else:
#         data = get_link_with_headers()

#     while time.time() < end_time:
#         try:
#             if not data:
#                 print("\n[🔄] Link lene ja raha hoon...")
#                 data = get_link_with_headers()
#                 if not data:
#                     print("\n[❌] Link nahi mila. 1 minute baad dobara koshish hogi...")
#                     time.sleep(60)
#                     continue

#             if current_process: current_process.terminate()
#             current_process = start_stream(data)
#             print("\n[🚀] SUCCESS! Video feed OK.ru par live hai!")
            
#             if is_manual_mode:
#                 sleep_seconds = 10 * 60 * 60
#             else:
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] AUTO MODE: Bot {int(sleep_seconds/60)} mins rest karega...")
            
#             waited = 0
#             crashed = False
            
#             while waited < sleep_seconds:
#                 time.sleep(10)
#                 waited += 10
                
#                 if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
#                     trigger_next_run()
#                     next_run_triggered = True 
                    
#                 if current_process.poll() is not None:
#                     exit_code = current_process.poll()
#                     print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                     crashed = True
#                     break 
            
#             if not is_manual_mode and not crashed:
#                 print("\n[🕵️‍♂️] PRE-FETCH MODE: Background mein naya link la raha hoon...")
#                 new_data = get_link_with_headers()
#                 if new_data:
#                     print("\n[⚡] NAYA LINK READY! Millisecond swap kar raha hoon...")
#                     data = new_data 
#                 else:
#                     print("\n[⚠️] Pre-fetch fail! Purani stream ko natural crash hone tak chalne do...")
#                     current_process.wait() 
#                     data = None 
#             elif crashed and not is_manual_mode:
#                 data = None 

#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()













# upper code mei video ko original ok.ru par sent keya mean HD
# ============================== 10000% 2 --- here sync problem ko teek karney k khosheh aab tu pata chalegy gaab internet slow huqaa ===========================
# agar neeche wallah code kaam n karey to pher yeh mrthod add karo ispar try karo

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
#     if data.get('origin'):
#         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-g", "50",                             # 👈 NAYA ADD KIYA: OK.ru ko sync ke liye har 2 sec baad Keyframe chahiye (25fps x 2 = 50)
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-af", "aresample=async=1",             # 👈 NAYA ADD KIYA: Modern aur safe Audio Sync filter
#         "-max_muxing_queue_size", "1024",       # 👈 NAYA ADD KIYA: Sync karte waqt FFmpeg ko buffer crash se bachane ke liye
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Direct GitHub Network par)")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)





# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# import requests
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (DYNAMIC FROM GITHUB)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# STREAM_KEY = os.environ.get('STREAM_KEY', '11523921485458_10535073221266_x3wpukcvda')
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# PROXY_IP = os.environ.get('PROXY_IP', '31.59.20.176')
# PROXY_PORT = os.environ.get('PROXY_PORT', '6754')
# PROXY_USER = os.environ.get('PROXY_USER', 'cjasfidu')
# PROXY_PASS = os.environ.get('PROXY_PASS', 'qhnyvm0qpf6p')
# PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"

# # --- MANUAL MODE INPUTS ---
# MANUAL_M3U8 = os.environ.get('MANUAL_M3U8', '').strip()
# MANUAL_REFERER = os.environ.get('MANUAL_REFERER', '').strip()
# MANUAL_ORIGIN = os.environ.get('MANUAL_ORIGIN', '').strip()

# # --- CASE 2: RAW COMMAND INPUT ---
# MANUAL_FFMPEG_CMD = os.environ.get('MANUAL_FFMPEG_CMD', '').strip()

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def trigger_next_run():
#     print("\n" + "="*50)
#     print(" ⏰ AUTO-RESTART TRIGGER ACTIVATED ⏰")
#     print("="*50)
#     print("[🔄] 5 Ghante 45 Minute poore ho gaye hain! Naya Bot chala raha hoon...")
    
#     token = os.environ.get('GH_PAT')
#     repo = os.environ.get('GITHUB_REPOSITORY') 
#     branch = os.environ.get('GITHUB_REF_NAME', 'main')
    
#     if not token or not repo:
#         print("[❌] GH_PAT ya Repo Name nahi mila! Auto-Restart Fail ho gaya.")
#         return

#     url = f"https://api.github.com/repos/{repo}/actions/workflows/stream.yml/dispatches"
    
#     headers = {
#         "Accept": "application/vnd.github.v3+json",
#         "Authorization": f"token {token}"
#     }
    
#     data = {
#         "ref": branch,
#         "inputs": {
#             "target_url": TARGET_WEBSITE,
#             "stream_key": STREAM_KEY,
#             "proxy_ip": PROXY_IP,
#             "proxy_port": PROXY_PORT,
#             "proxy_user": PROXY_USER,
#             "proxy_pass": PROXY_PASS,
#             "manual_m3u8": MANUAL_M3U8,
#             "manual_referer": MANUAL_REFERER,
#             "manual_origin": MANUAL_ORIGIN,
#             "manual_ffmpeg_cmd": MANUAL_FFMPEG_CMD # Nayi field ko bhi aage bhej raha hai
#         }
#     }
    
#     try:
#         response = requests.post(url, headers=headers, json=data)
#         if response.status_code == 204:
#             print("[✅] SUCCESS! Nayi 'stream.yml' background mein start ho gayi hai!")
#         else:
#             print(f"[❌] FAILED to start new bot. Status: {response.status_code}")
#     except Exception as e:
#         print(f"[💥] API Error: {e}")

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy Set for Link Fetching: {PROXY_URL.split('@')[-1]}")
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {
#         'proxy': {'http': PROXY_URL, 'https': PROXY_URL, 'no_proxy': 'localhost,127.0.0.1'},
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai Proxy ke sath...")
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), seleniumwire_options=seleniumwire_options, options=options)
        
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon...")
#         driver.get(TARGET_WEBSITE)
        
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds wait...") 
#         for i in range(5, 0, -1):
#             time.sleep(1)
            
#         print("[✅] [STEP 7] Scanning network requests for .m3u8 token...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE),
#                         "origin": ""
#                     }
#                     print(f"\n🎉 [BINGO] Cloudflare Bypassed! Link Mil Gaya!")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: .m3u8 link nahi mila! WAF ne block kiya ya wait time kam tha.")
            
#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: 
#             print("[🧹] [STEP 8] Chrome Browser band kiya ja raha hai...")
#             driver.quit()
    
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Asli Link Expiry Time: {expiry_dt.strftime('%I:%M %p')} PKT")
#             print(f"[🛠️] Pre-Fetch Time: Bot {wake_up_dt.strftime('%I:%M %p')} par uthega.")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
#     return DEFAULT_SLEEP

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
#     if data.get('origin'):
#         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-fflags", "+genpts",  # 👈 YEH ADD KIYA HAI (Naye timestamps generate karne ke liye)
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-async", "1",         # 👈 YEH ADD KIYA HAI (Audio ko video ke sath force lock karne ke liye)
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Direct GitHub Network par)")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)

# def main():
#     print("========================================")
#     print("   🚀 ULTIMATE ALL-IN-ONE STREAMER")
#     print("========================================")
    
#     start_time = time.time()
#     RESTART_TIME_LIMIT = (5 * 60 * 60) + (45 * 60) # 5h 45m
#     end_time = start_time + (6 * 60 * 60)
    
#     # ====================================================
#     # 🔥 CASE 2: RAW FFMPEG COMMAND OVERRIDE LOGIC
#     # ====================================================
#     if MANUAL_FFMPEG_CMD:
#         print("\n[🎯] ⚡ RAW FFMPEG COMMAND OVERRIDE ACTIVATED ⚡")
#         print("Bot apni link-finding logic band kar raha hai aur direct aapki command chala raha hai...")
        
#         next_run_triggered = False
#         while time.time() < end_time:
#             # Check for Auto-Restart in Raw Command mode
#             if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
#                 trigger_next_run()
#                 next_run_triggered = True

#             print(f"\n[🎬] Executing Full Command: \n{MANUAL_FFMPEG_CMD[:150]}... (truncated for display)")
            
#             try:
#                 # shell=True use kiya hai taake aapki command exactly wese hi chale jese terminal par chalti hai
#                 current_process = subprocess.Popen(MANUAL_FFMPEG_CMD, shell=True)
#                 current_process.wait() # Jab tak crash na ho chalne do
#             except Exception as e:
#                 print(f"[💥] Command Error: {e}")
                
#             print("\n[⚠️] Command rukk gayi ya stream crash ho gayi. 10 second baad dobara try kar raha hoon...")
#             time.sleep(10)
            
#         return # Raw command case yahan khatam ho jata hai
#     # ====================================================

#     current_process = None
#     next_run_triggered = False
#     is_manual_mode = bool(MANUAL_M3U8)

#     if is_manual_mode:
#         print("\n[🎯] ⚡ MANUAL M3U8 LINK ACTIVATED ⚡")
#         data = {
#             "url": MANUAL_M3U8,
#             "referer": MANUAL_REFERER,
#             "origin": MANUAL_ORIGIN,
#             "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
#             "cookie": ""
#         }
#     else:
#         data = get_link_with_headers()

#     while time.time() < end_time:
#         try:
#             if not data:
#                 print("\n[🔄] Link lene ja raha hoon...")
#                 data = get_link_with_headers()
#                 if not data:
#                     print("\n[❌] Link nahi mila. 1 minute baad dobara koshish hogi...")
#                     time.sleep(60)
#                     continue

#             if current_process: current_process.terminate()
#             current_process = start_stream(data)
#             print("\n[🚀] SUCCESS! Video feed OK.ru par live hai!")
            
#             if is_manual_mode:
#                 sleep_seconds = 10 * 60 * 60
#             else:
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] AUTO MODE: Bot {int(sleep_seconds/60)} mins rest karega...")
            
#             waited = 0
#             crashed = False
            
#             while waited < sleep_seconds:
#                 time.sleep(10)
#                 waited += 10
                
#                 if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
#                     trigger_next_run()
#                     next_run_triggered = True 
                    
#                 if current_process.poll() is not None:
#                     exit_code = current_process.poll()
#                     print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                     crashed = True
#                     break 
            
#             if not is_manual_mode and not crashed:
#                 print("\n[🕵️‍♂️] PRE-FETCH MODE: Background mein naya link la raha hoon...")
#                 new_data = get_link_with_headers()
#                 if new_data:
#                     print("\n[⚡] NAYA LINK READY! Millisecond swap kar raha hoon...")
#                     data = new_data 
#                 else:
#                     print("\n[⚠️] Pre-fetch fail! Purani stream ko natural crash hone tak chalne do...")
#                     current_process.wait() 
#                     data = None 
#             elif crashed and not is_manual_mode:
#                 data = None 

#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()



















# ============ 10000% 1 --- oprimize command hai lekin bas ok.ru mei video and audio sync nahey ho rhey jab internet slow hu tab ==============================


# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# import requests
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (DYNAMIC FROM GITHUB)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# STREAM_KEY = os.environ.get('STREAM_KEY', '11523921485458_10535073221266_x3wpukcvda')
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# PROXY_IP = os.environ.get('PROXY_IP', '31.59.20.176')
# PROXY_PORT = os.environ.get('PROXY_PORT', '6754')
# PROXY_USER = os.environ.get('PROXY_USER', 'cjasfidu')
# PROXY_PASS = os.environ.get('PROXY_PASS', 'qhnyvm0qpf6p')
# PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"

# # --- MANUAL MODE INPUTS ---
# MANUAL_M3U8 = os.environ.get('MANUAL_M3U8', '').strip()
# MANUAL_REFERER = os.environ.get('MANUAL_REFERER', '').strip()
# MANUAL_ORIGIN = os.environ.get('MANUAL_ORIGIN', '').strip()

# # --- CASE 2: RAW COMMAND INPUT ---
# MANUAL_FFMPEG_CMD = os.environ.get('MANUAL_FFMPEG_CMD', '').strip()

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def trigger_next_run():
#     print("\n" + "="*50)
#     print(" ⏰ AUTO-RESTART TRIGGER ACTIVATED ⏰")
#     print("="*50)
#     print("[🔄] 5 Ghante 45 Minute poore ho gaye hain! Naya Bot chala raha hoon...")
    
#     token = os.environ.get('GH_PAT')
#     repo = os.environ.get('GITHUB_REPOSITORY') 
#     branch = os.environ.get('GITHUB_REF_NAME', 'main')
    
#     if not token or not repo:
#         print("[❌] GH_PAT ya Repo Name nahi mila! Auto-Restart Fail ho gaya.")
#         return

#     url = f"https://api.github.com/repos/{repo}/actions/workflows/stream.yml/dispatches"
    
#     headers = {
#         "Accept": "application/vnd.github.v3+json",
#         "Authorization": f"token {token}"
#     }
    
#     data = {
#         "ref": branch,
#         "inputs": {
#             "target_url": TARGET_WEBSITE,
#             "stream_key": STREAM_KEY,
#             "proxy_ip": PROXY_IP,
#             "proxy_port": PROXY_PORT,
#             "proxy_user": PROXY_USER,
#             "proxy_pass": PROXY_PASS,
#             "manual_m3u8": MANUAL_M3U8,
#             "manual_referer": MANUAL_REFERER,
#             "manual_origin": MANUAL_ORIGIN,
#             "manual_ffmpeg_cmd": MANUAL_FFMPEG_CMD # Nayi field ko bhi aage bhej raha hai
#         }
#     }
    
#     try:
#         response = requests.post(url, headers=headers, json=data)
#         if response.status_code == 204:
#             print("[✅] SUCCESS! Nayi 'stream.yml' background mein start ho gayi hai!")
#         else:
#             print(f"[❌] FAILED to start new bot. Status: {response.status_code}")
#     except Exception as e:
#         print(f"[💥] API Error: {e}")

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy Set for Link Fetching: {PROXY_URL.split('@')[-1]}")
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {
#         'proxy': {'http': PROXY_URL, 'https': PROXY_URL, 'no_proxy': 'localhost,127.0.0.1'},
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai Proxy ke sath...")
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), seleniumwire_options=seleniumwire_options, options=options)
        
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon...")
#         driver.get(TARGET_WEBSITE)
        
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds wait...") 
#         for i in range(5, 0, -1):
#             time.sleep(1)
            
#         print("[✅] [STEP 7] Scanning network requests for .m3u8 token...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE),
#                         "origin": ""
#                     }
#                     print(f"\n🎉 [BINGO] Cloudflare Bypassed! Link Mil Gaya!")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: .m3u8 link nahi mila! WAF ne block kiya ya wait time kam tha.")
            
#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: 
#             print("[🧹] [STEP 8] Chrome Browser band kiya ja raha hai...")
#             driver.quit()
    
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Asli Link Expiry Time: {expiry_dt.strftime('%I:%M %p')} PKT")
#             print(f"[🛠️] Pre-Fetch Time: Bot {wake_up_dt.strftime('%I:%M %p')} par uthega.")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
#     return DEFAULT_SLEEP

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
#     if data.get('origin'):
#         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Direct GitHub Network par)")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 

# def main():
#     print("========================================")
#     print("   🚀 ULTIMATE ALL-IN-ONE STREAMER")
#     print("========================================")
    
#     start_time = time.time()
#     RESTART_TIME_LIMIT = (5 * 60 * 60) + (45 * 60) # 5h 45m
#     end_time = start_time + (6 * 60 * 60)
    
#     # ====================================================
#     # 🔥 CASE 2: RAW FFMPEG COMMAND OVERRIDE LOGIC
#     # ====================================================
#     if MANUAL_FFMPEG_CMD:
#         print("\n[🎯] ⚡ RAW FFMPEG COMMAND OVERRIDE ACTIVATED ⚡")
#         print("Bot apni link-finding logic band kar raha hai aur direct aapki command chala raha hai...")
        
#         next_run_triggered = False
#         while time.time() < end_time:
#             # Check for Auto-Restart in Raw Command mode
#             if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
#                 trigger_next_run()
#                 next_run_triggered = True

#             print(f"\n[🎬] Executing Full Command: \n{MANUAL_FFMPEG_CMD[:150]}... (truncated for display)")
            
#             try:
#                 # shell=True use kiya hai taake aapki command exactly wese hi chale jese terminal par chalti hai
#                 current_process = subprocess.Popen(MANUAL_FFMPEG_CMD, shell=True)
#                 current_process.wait() # Jab tak crash na ho chalne do
#             except Exception as e:
#                 print(f"[💥] Command Error: {e}")
                
#             print("\n[⚠️] Command rukk gayi ya stream crash ho gayi. 10 second baad dobara try kar raha hoon...")
#             time.sleep(10)
            
#         return # Raw command case yahan khatam ho jata hai
#     # ====================================================

#     current_process = None
#     next_run_triggered = False
#     is_manual_mode = bool(MANUAL_M3U8)

#     if is_manual_mode:
#         print("\n[🎯] ⚡ MANUAL M3U8 LINK ACTIVATED ⚡")
#         data = {
#             "url": MANUAL_M3U8,
#             "referer": MANUAL_REFERER,
#             "origin": MANUAL_ORIGIN,
#             "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
#             "cookie": ""
#         }
#     else:
#         data = get_link_with_headers()

#     while time.time() < end_time:
#         try:
#             if not data:
#                 print("\n[🔄] Link lene ja raha hoon...")
#                 data = get_link_with_headers()
#                 if not data:
#                     print("\n[❌] Link nahi mila. 1 minute baad dobara koshish hogi...")
#                     time.sleep(60)
#                     continue

#             if current_process: current_process.terminate()
#             current_process = start_stream(data)
#             print("\n[🚀] SUCCESS! Video feed OK.ru par live hai!")
            
#             if is_manual_mode:
#                 sleep_seconds = 10 * 60 * 60
#             else:
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] AUTO MODE: Bot {int(sleep_seconds/60)} mins rest karega...")
            
#             waited = 0
#             crashed = False
            
#             while waited < sleep_seconds:
#                 time.sleep(10)
#                 waited += 10
                
#                 if (time.time() - start_time) > RESTART_TIME_LIMIT and not next_run_triggered:
#                     trigger_next_run()
#                     next_run_triggered = True 
                    
#                 if current_process.poll() is not None:
#                     exit_code = current_process.poll()
#                     print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                     crashed = True
#                     break 
            
#             if not is_manual_mode and not crashed:
#                 print("\n[🕵️‍♂️] PRE-FETCH MODE: Background mein naya link la raha hoon...")
#                 new_data = get_link_with_headers()
#                 if new_data:
#                     print("\n[⚡] NAYA LINK READY! Millisecond swap kar raha hoon...")
#                     data = new_data 
#                 else:
#                     print("\n[⚠️] Pre-fetch fail! Purani stream ko natural crash hone tak chalne do...")
#                     current_process.wait() 
#                     data = None 
#             elif crashed and not is_manual_mode:
#                 data = None 

#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()





































































































































































# =====================n(iss below code mei api hai 2000% correct) upper waley mei default full ffmpeg command ko teek karn hai =============

# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# import requests
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (DYNAMIC FROM GITHUB)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# STREAM_KEY = os.environ.get('STREAM_KEY', '11523921485458_10535073221266_x3wpukcvda')
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# PROXY_IP = os.environ.get('PROXY_IP', '31.59.20.176')
# PROXY_PORT = os.environ.get('PROXY_PORT', '6754')
# PROXY_USER = os.environ.get('PROXY_USER', 'cjasfidu')
# PROXY_PASS = os.environ.get('PROXY_PASS', 'qhnyvm0qpf6p')
# PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"

# # --- MANUAL MODE INPUTS ---
# MANUAL_M3U8 = os.environ.get('MANUAL_M3U8', '').strip()
# MANUAL_REFERER = os.environ.get('MANUAL_REFERER', '').strip()
# MANUAL_ORIGIN = os.environ.get('MANUAL_ORIGIN', '').strip()

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def trigger_next_run():
#     print("\n" + "="*50)
#     print(" ⏰ AUTO-RESTART TRIGGER ACTIVATED ⏰")
#     print("="*50)
#     print("[🔄] 5 Ghante 45 Minute poore ho gaye hain! Naya Bot chala raha hoon...")
    
#     token = os.environ.get('GH_PAT')
#     repo = os.environ.get('GITHUB_REPOSITORY') 
#     branch = os.environ.get('GITHUB_REF_NAME', 'main')
    
#     if not token or not repo:
#         print("[❌] GH_PAT ya Repo Name nahi mila! Auto-Restart Fail ho gaya.")
#         print("[⚠️] Kripya GitHub Secrets mein 'GH_PAT' add karein.")
#         return

#     url = f"https://api.github.com/repos/{repo}/actions/workflows/stream.yml/dispatches"
    
#     headers = {
#         "Accept": "application/vnd.github.v3+json",
#         "Authorization": f"token {token}"
#     }
    
#     data = {
#         "ref": branch,
#         "inputs": {
#             "target_url": TARGET_WEBSITE,
#             "stream_key": STREAM_KEY,
#             "proxy_ip": PROXY_IP,
#             "proxy_port": PROXY_PORT,
#             "proxy_user": PROXY_USER,
#             "proxy_pass": PROXY_PASS,
#             "manual_m3u8": MANUAL_M3U8,
#             "manual_referer": MANUAL_REFERER,
#             "manual_origin": MANUAL_ORIGIN
#         }
#     }
    
#     try:
#         response = requests.post(url, headers=headers, json=data)
#         if response.status_code == 204:
#             print("[✅] SUCCESS! Nayi 'stream.yml' background mein start ho gayi hai!")
#             print("[✅] Yeh current bot 15 minute baad automatically band ho jayega.")
#         else:
#             print(f"[❌] FAILED to start new bot. Status: {response.status_code}, Response: {response.text}")
#     except Exception as e:
#         print(f"[💥] API Error: {e}")

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy Set for Link Fetching: {PROXY_URL.split('@')[-1]}")
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {
#         'proxy': {'http': PROXY_URL, 'https': PROXY_URL, 'no_proxy': 'localhost,127.0.0.1'},
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai Proxy ke sath...")
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), seleniumwire_options=seleniumwire_options, options=options)
        
#         print(f"[🕵️‍♂️] [STEP 4] Anti-Bot JS Scripts inject ho rahi hain...")
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon...")
#         driver.get(TARGET_WEBSITE)
        
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds ka wait start ho gaya hai...") 
#         for i in range(5, 0, -1):
#             time.sleep(1)
            
#         print("[✅] [STEP 7] Scanning network requests for .m3u8 token...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE),
#                         "origin": ""
#                     }
#                     print(f"\n🎉 [BINGO] Cloudflare Bypassed! Link Mil Gaya!")
#                     print(f"   🔗 URL: {request.url[:70]}...")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: .m3u8 link nahi mila! WAF ne block kiya ya wait time kam tha.")
            
#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: 
#             print("[🧹] [STEP 8] Chrome Browser band kiya ja raha hai...")
#             driver.quit()
    
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
#             # 5 minute pehle uthega naya link lane ke liye (Zero Downtime setup)
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Asli Link Expiry Time: {expiry_dt.strftime('%I:%M %p')}")
#             print(f"[🛠️] Pre-Fetch Time: Bot {wake_up_dt.strftime('%I:%M %p')} par uthega.")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
    
#     return DEFAULT_SLEEP

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
#     if data.get('origin'):
#         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Direct GitHub Network par)")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 

# def main():
#     print("========================================")
#     print("   🚀 ULTIMATE 24/7 STREAMER (V-FINAL)")
#     print("========================================")
    
#     start_time = time.time()
#     # 5 Hours and 45 Minutes limit for Auto-Restart
#     RESTART_TIME_LIMIT = (5 * 60 * 60) + (45 * 60) 
    
#     end_time = start_time + (6 * 60 * 60)
#     current_process = None
#     next_run_triggered = False

#     # --- DUAL MODE SETTINGS ---
#     is_manual_mode = bool(MANUAL_M3U8)
#     if is_manual_mode:
#         print("\n[🎯] ⚡ MANUAL OVERRIDE ACTIVATED ⚡")
#         print("Aapka diya hua link directly chala raha hoon...")
#         data = {
#             "url": MANUAL_M3U8,
#             "referer": MANUAL_REFERER,
#             "origin": MANUAL_ORIGIN,
#             "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
#             "cookie": ""
#         }
#     else:
#         data = get_link_with_headers()

#     while time.time() < end_time:
#         try:
#             if not data:
#                 print("\n[🔄] Link lene ja raha hoon...")
#                 data = get_link_with_headers()
#                 if not data:
#                     print("\n[❌] Link nahi mila. 1 minute baad dobara koshish hogi...")
#                     time.sleep(60)
#                     continue

#             if current_process: current_process.terminate()
#             current_process = start_stream(data)
#             print("\n[🚀] SUCCESS! Video feed OK.ru par live hai!")
            
#             if is_manual_mode:
#                 sleep_seconds = 10 * 60 * 60 # Manual Mode doesn't calculate sleep
#             else:
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] AUTO MODE: FFmpeg background mein chal raha hai. Bot {int(sleep_seconds/60)} mins rest karega...")
            
#             waited = 0
#             crashed = False
            
#             # THE REST & MONITORING LOOP
#             while waited < sleep_seconds:
#                 time.sleep(10)
#                 waited += 10
                
#                 # --- CHECK FOR AUTO-RESTART ---
#                 elapsed_time = time.time() - start_time
#                 if elapsed_time > RESTART_TIME_LIMIT and not next_run_triggered:
#                     trigger_next_run()
#                     next_run_triggered = True 
                    
#                 # --- CHECK IF FFMPEG CRASHED ---
#                 if current_process.poll() is not None:
#                     exit_code = current_process.poll()
#                     print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                     crashed = True
#                     break 
            
#             # ====================================================
#             # 🔥 ZERO-DOWNTIME PRE-FETCH LOGIC
#             # ====================================================
#             if not is_manual_mode and not crashed:
#                 print("\n[🕵️‍♂️] PRE-FETCH MODE: Viewers ko purani stream chal rahi hai. Background mein naya link la raha hoon...")
                
#                 new_data = get_link_with_headers()
                
#                 if new_data:
#                     print("\n[⚡] NAYA LINK READY! Purani feed kill kar ke naya millisecond swap kar raha hoon...")
#                     data = new_data 
#                 else:
#                     print("\n[⚠️] Pre-fetch fail! Purani stream ko natural crash hone tak chalne do...")
#                     current_process.wait() 
#                     data = None 
            
#             elif crashed and not is_manual_mode:
#                 data = None 

#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()










# ========= 2 upper waley mei key add kiya hai taaky github jab 6hour complete hu jaye to automaticte new 6 hour dee 


# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (DYNAMIC FROM GITHUB)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# STREAM_KEY = os.environ.get('STREAM_KEY', '11523921485458_10535073221266_x3wpukcvda')
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# PROXY_IP = os.environ.get('PROXY_IP', '31.59.20.176')
# PROXY_PORT = os.environ.get('PROXY_PORT', '6754')
# PROXY_USER = os.environ.get('PROXY_USER', 'cjasfidu')
# PROXY_PASS = os.environ.get('PROXY_PASS', 'qhnyvm0qpf6p')
# PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"

# # --- MANUAL MODE INPUTS ---
# MANUAL_M3U8 = os.environ.get('MANUAL_M3U8', '').strip()
# MANUAL_REFERER = os.environ.get('MANUAL_REFERER', '').strip()
# MANUAL_ORIGIN = os.environ.get('MANUAL_ORIGIN', '').strip()

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy Set for Link Fetching: {PROXY_URL.split('@')[-1]}")
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {
#         'proxy': {'http': PROXY_URL, 'https': PROXY_URL, 'no_proxy': 'localhost,127.0.0.1'},
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai...")
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), seleniumwire_options=seleniumwire_options, options=options)
        
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon: {TARGET_WEBSITE}")
#         driver.get(TARGET_WEBSITE)
        
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds wait start...") 
#         for i in range(5, 0, -1):
#             time.sleep(1)
            
#         print("[✅] [STEP 7] Scanning network requests...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE),
#                         "origin": ""
#                     }
#                     print(f"\n🎉 [BINGO] .m3u8 Link Mil Gaya: {request.url[:60]}...")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: .m3u8 link nahi mila!")
            
#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: driver.quit()
    
#     return data

# # =============================================

# def calculate_sleep_time(url):
#     try:
#         parsed = urllib.parse.urlparse(url)
#         params = urllib.parse.parse_qs(parsed.query)
#         expiry_ts = None
        
#         if 'expires' in params: expiry_ts = int(params['expires'][0])
#         elif 'e' in params: expiry_ts = int(params['e'][0])
            
#         if expiry_ts:
#             expiry_dt = datetime.fromtimestamp(expiry_ts, PKT)
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Link Expiry Time: {expiry_dt.strftime('%I:%M %p')}")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
    
#     return DEFAULT_SLEEP





# # ====================================================

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
#     if data.get('origin'):
#         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 

# def main():
#     print("========================================")
#     print("   🚀 ZERO-DOWNTIME HYBRID STREAMER")
#     print("========================================")
    
#     end_time = time.time() + (6 * 60 * 60)
#     current_process = None

#     # --- DUAL MODE SETTINGS ---
#     is_manual_mode = bool(MANUAL_M3U8)
#     if is_manual_mode:
#         print("\n[🎯] ⚡ MANUAL OVERRIDE ACTIVATED ⚡")
#         data = {
#             "url": MANUAL_M3U8,
#             "referer": MANUAL_REFERER,
#             "origin": MANUAL_ORIGIN,
#             "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
#             "cookie": ""
#         }
#     else:
#         data = get_link_with_headers()

#     while time.time() < end_time:
#         try:
#             if not data:
#                 print("\n[🔄] Naya link dhoondne ka cycle shuru ho raha hai...")
#                 data = get_link_with_headers()
#                 if not data:
#                     print("\n[❌] Link nahi mila. 1 minute baad dobara koshish hogi...")
#                     time.sleep(60)
#                     continue

#             # Stream yahan start hoti hai
#             if current_process: current_process.terminate()
#             current_process = start_stream(data)
#             print("\n[🚀] SUCCESS! Video feed OK.ru par live hai!")
            
#             if is_manual_mode:
#                 sleep_seconds = 10 * 60 * 60
#             else:
#                 sleep_seconds = calculate_sleep_time(data['url'])
            
#             waited = 0
#             crashed = False
#             while waited < sleep_seconds:
#                 time.sleep(10)
#                 waited += 10
#                 if current_process.poll() is not None:
#                     exit_code = current_process.poll()
#                     print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                     crashed = True
#                     break 
            
#             # ====================================================
#             # 🔥 ZERO-DOWNTIME PRE-FETCH LOGIC (The Magic Hack)
#             # ====================================================
#             if not is_manual_mode and not crashed:
#                 print("\n[🕵️‍♂️] PRE-FETCH MODE: Viewers ko stream nazar aa rahi hai. Background mein naya link laa raha hoon...")
                
#                 # Yeh function 20 seconds lega, lekin is doran FFmpeg purane link par video chala raha hoga!
#                 new_data = get_link_with_headers()
                
#                 if new_data:
#                     print("\n[⚡] NAYA LINK READY! Millisecond Swap kar raha hoon (Zero Downtime)...")
#                     data = new_data 
#                     # Loop ghoom kar wapis upar jayega, purani stream band hogi aur 0.1s mein nayi start ho jayegi!
#                 else:
#                     print("\n[⚠️] Pre-fetch fail! Purani stream ko natural crash hone tak chalne do...")
#                     current_process.wait() # Jab tak link zinda hai chalne do
#                     data = None # Phir shuru se dhoondega
            
#             elif crashed and not is_manual_mode:
#                 data = None # Crash ho gaya toh naya link laayega

#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()







# ======= 1


# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (DYNAMIC FROM GITHUB)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# STREAM_KEY = os.environ.get('STREAM_KEY', '11523921485458_10535073221266_x3wpukcvda')
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# PROXY_IP = os.environ.get('PROXY_IP', '31.59.20.176')
# PROXY_PORT = os.environ.get('PROXY_PORT', '6754')
# PROXY_USER = os.environ.get('PROXY_USER', 'cjasfidu')
# PROXY_PASS = os.environ.get('PROXY_PASS', 'qhnyvm0qpf6p')
# PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"

# # --- NAYA: MANUAL MODE INPUTS ---
# MANUAL_M3U8 = os.environ.get('MANUAL_M3U8', '').strip()
# MANUAL_REFERER = os.environ.get('MANUAL_REFERER', '').strip()
# MANUAL_ORIGIN = os.environ.get('MANUAL_ORIGIN', '').strip()

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy Set for Link Fetching: {PROXY_URL.split('@')[-1]}")
    
#     options = webdriver.ChromeOptions()
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     seleniumwire_options = {
#         'proxy': {'http': PROXY_URL, 'https': PROXY_URL, 'no_proxy': 'localhost,127.0.0.1'},
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai Proxy ke sath...")
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), seleniumwire_options=seleniumwire_options, options=options)
        
#         print(f"[🕵️‍♂️] [STEP 4] Anti-Bot JS Scripts inject ho rahi hain...")
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon: {TARGET_WEBSITE}")
#         driver.get(TARGET_WEBSITE)
        
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds ka wait start ho gaya hai...") 
#         for i in range(5, 0, -1):
#             time.sleep(1)
            
#         print("[✅] [STEP 7] 5 Seconds poore! Ab network requests scan kar raha hoon...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE),
#                         "origin": "" # Auto mode mein Origin blank rakhte hain
#                     }
#                     print(f"\n🎉 [BINGO] .m3u8 Link Mil Gaya!")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: 5 seconds poore hone ke bawajood .m3u8 link nahi mila!")
#             print(f"   -> Page Title: '{driver.title}'")

#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: 
#             print("[🧹] [STEP 8] Chrome Browser band kiya ja raha hai...")
#             driver.quit()
    
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Link Expiry Time: {expiry_dt.strftime('%I:%M %p')}")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
    
#     return DEFAULT_SLEEP

# def start_stream(data):
#     # NAYA: Origin Header ka hisaab lagaya gaya hai
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
#     if data.get('origin'):
#         headers_cmd += f"\r\nOrigin: {data['origin']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Direct GitHub Network par):")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 

# def main():
#     print("========================================")
#     print("   🚀 HYBRID STREAMER (MANUAL + AUTO)")
#     print("========================================")
    
#     end_time = time.time() + (6 * 60 * 60)
#     current_process = None

#     # --- DUAL MODE CHECKER ---
#     is_manual_mode = bool(MANUAL_M3U8)
#     if is_manual_mode:
#         print("\n[🎯] ⚡ MANUAL OVERRIDE ACTIVATED ⚡")
#         print("Bot ab link dhoondne ke bajaye seedha aapka diya hua link chalayega!")
#         manual_data = {
#             "url": MANUAL_M3U8,
#             "referer": MANUAL_REFERER,
#             "origin": MANUAL_ORIGIN,
#             "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
#             "cookie": ""
#         }

#     while time.time() < end_time:
#         try:
#             # Mode ke hisaab se data set karo
#             if is_manual_mode:
#                 data = manual_data
#             else:
#                 data = get_link_with_headers()
            
#             if data:
#                 if current_process: current_process.terminate()
                
#                 current_process = start_stream(data)
#                 print("\n[🚀] SUCCESS! Video feed OK.ru par send hona shuru ho gayi hai!")
                
#                 if is_manual_mode:
#                     print("[zzz] MANUAL MODE: Bot 10 ghante ke liye so raha hai. Expire hone par wapis yahi link retry karega.")
#                     sleep_seconds = 10 * 60 * 60 # Manual mode mein expiry check nahi hoti
#                 else:
#                     sleep_seconds = calculate_sleep_time(data['url'])
#                     print(f"[zzz] AUTO MODE: Bot {int(sleep_seconds/60)} mins ke liye rest mode mein ja raha hai...")
                
#                 waited = 0
#                 while waited < sleep_seconds:
#                     time.sleep(10)
#                     waited += 10
#                     if current_process.poll() is not None:
#                         exit_code = current_process.poll()
#                         print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                         if is_manual_mode:
#                             print("[🔄] MANUAL MODE: Watchman ne bahar nikala hai, lekin main dobara issi ticket (link) par andar ja raha hoon...")
#                         break 
                
#                 if not is_manual_mode:
#                     print("\n[🔄] AUTO MODE: Naya link dhoondne ka cycle dobara shuru ho raha hai...")
#                 if current_process: current_process.terminate()
#             else:
#                 print("\n[❌] Link dhoondne ka process fail ho gaya. 1 minute baad dobara koshish hogi...")
#                 time.sleep(60)
                
#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()





























































































































































































































# ============ 100% good =================================




# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (DYNAMIC FROM GITHUB)
# # ==========================================
# # Target Website (GitHub Input se aayegi)
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# # 1️⃣ DYNAMIC STREAM KEY
# STREAM_KEY = os.environ.get('STREAM_KEY', '11523921485458_10535073221266_x3wpukcvda')
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# # 2️⃣ DYNAMIC PROXY MAKER (Sirf Link Fetching ke liye)
# PROXY_IP = os.environ.get('PROXY_IP', '31.59.20.176')
# PROXY_PORT = os.environ.get('PROXY_PORT', '6754')
# PROXY_USER = os.environ.get('PROXY_USER', 'cjasfidu')
# PROXY_PASS = os.environ.get('PROXY_PASS', 'qhnyvm0qpf6p')

# # Yahan code khud proxy ka format bana lega
# PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_IP}:{PROXY_PORT}"

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy (Link Fetching): {PROXY_IP}:{PROXY_PORT}")
    
#     options = webdriver.ChromeOptions()
    
#     # --- GITHUB ACTIONS DISPLAY SETTINGS ---
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
    
#     # --- VIDEO AUTOPLAY FIX ---
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
    
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
#     # --- ANTI-BOT BYPASS ---
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     # --- PROXY INJECTION (Sirf Selenium ke liye) ---
#     seleniumwire_options = {
#         'proxy': {
#             'http': PROXY_URL,
#             'https': PROXY_URL,
#             'no_proxy': 'localhost,127.0.0.1'
#         },
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai Proxy ke sath...")
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             seleniumwire_options=seleniumwire_options,
#             options=options
#         )
        
#         print(f"[🕵️‍♂️] [STEP 4] Anti-Bot JS Scripts inject ho rahi hain...")
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon...")
#         driver.get(TARGET_WEBSITE)
        
#         # ⏳ STRICT 5 SECONDS WAIT
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds ka wait start ho gaya hai...") 
#         for i in range(5, 0, -1):
#             print(f"      ⏳ Wait: {i} seconds baqi...")
#             time.sleep(1)
            
#         print("[✅] [STEP 7] 5 Seconds poore! Ab network requests scan kar raha hoon...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE) 
#                     }
#                     print(f"\n🎉 [BINGO] .m3u8 Link Mil Gaya!")
#                     print(f"   🔗 URL: {request.url[:80]}...")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: 5 seconds poore hone ke bawajood .m3u8 link nahi mila!")
#             print(f"   -> Page Title: '{driver.title}'")

#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: 
#             print("[🧹] [STEP 8] Chrome Browser band kiya ja raha hai...")
#             driver.quit()
    
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Link Expiry Time: {expiry_dt.strftime('%I:%M %p')} (PKT)")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
    
#     return DEFAULT_SLEEP

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
        
#         # ⚠️ MASTER HACK: FFmpeg Proxy ke baghair chal raha hai (Free Data) ⚠️
        
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Direct GitHub Network par):")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 

# def main():
#     print("========================================")
#     print("   🚀 SMART DYNAMIC STREAMER (V4)")
#     print("========================================")
    
#     end_time = time.time() + (6 * 60 * 60)
#     current_process = None

#     while time.time() < end_time:
#         try:
#             data = get_link_with_headers()
            
#             if data:
#                 if current_process: current_process.terminate()
                
#                 current_process = start_stream(data)
#                 print("\n[🚀] SUCCESS! Video feed OK.ru par send hona shuru ho gayi hai!")
                
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] FFmpeg direct data fetch kar raha hai. Bot {int(sleep_seconds/60)} mins ke liye rest mode mein ja raha hai...")
                
#                 waited = 0
#                 while waited < sleep_seconds:
#                     time.sleep(10)
#                     waited += 10
#                     if current_process.poll() is not None:
#                         exit_code = current_process.poll()
#                         print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                         break 
                
#                 print("\n[🔄] Naya link dhoondne ka cycle dobara shuru ho raha hai...")
#                 if current_process: current_process.terminate()
#             else:
#                 print("\n[❌] Link dhoondne ka process fail ho gaya. 1 minute baad dobara koshish hogi...")
#                 time.sleep(60)
                
#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()




# ========= temporary fix with find link with proxy and when link find then use github default own (very good Alhamdullah) =======================


# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (YAHAN APNI DETAILS DALEIN)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# # 1️⃣ APNI FRESH OK.RU STREAM KEY YAHAN DALEIN
# # STREAM_KEY = "NAYI_STREAM_KEY_YAHAN_DALEIN"
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda"  # <-- NAYA: OK.ru Stream Key
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# # 2️⃣ APNI WEBSHARE PROXY YAHAN DALEIN 
# # Yeh sirf link fetch karne (KB's) mein use hogi
# # PROXY_URL = "http://shafi_user:pass1234@185.199.229.156:80"
# PROXY_URL = "http://cjasfidu:qhnyvm0qpf6p@31.59.20.176:6754"  # <-- NAYA: Proxy URL for Selenium (Link Fetching Only)

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy Set for Link Fetching: {PROXY_URL.split('@')[-1]}")
    
#     options = webdriver.ChromeOptions()
    
#     # --- GITHUB ACTIONS DISPLAY SETTINGS ---
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
    
#     # --- VIDEO AUTOPLAY FIX ---
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
    
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
#     # --- ANTI-BOT BYPASS ---
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     # --- PROXY INJECTION (Sirf Selenium ke liye) ---
#     seleniumwire_options = {
#         'proxy': {
#             'http': PROXY_URL,
#             'https': PROXY_URL,
#             'no_proxy': 'localhost,127.0.0.1'
#         },
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai Proxy ke sath...")
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             seleniumwire_options=seleniumwire_options,
#             options=options
#         )
        
#         print(f"[🕵️‍♂️] [STEP 4] Anti-Bot JS Scripts inject ho rahi hain...")
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon: {TARGET_WEBSITE}")
#         driver.get(TARGET_WEBSITE)
        
#         # ⏳ STRICT 5 SECONDS WAIT
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds ka wait start ho gaya hai...") 
#         for i in range(5, 0, -1):
#             print(f"      ⏳ Wait: {i} seconds baqi...")
#             time.sleep(1)
            
#         print("[✅] [STEP 7] 5 Seconds poore! Ab network requests scan kar raha hoon...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE) 
#                     }
#                     print(f"\n🎉 [BINGO] .m3u8 Link Mil Gaya!")
#                     print(f"   🔗 URL: {request.url[:80]}...")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: 5 seconds poore hone ke bawajood .m3u8 link nahi mila!")
#             print(f"   -> Page Title: '{driver.title}'")

#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: 
#             print("[🧹] [STEP 8] Chrome Browser band kiya ja raha hai...")
#             driver.quit()
    
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Link Expiry Time: {expiry_dt.strftime('%I:%M %p')}")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
    
#     return DEFAULT_SLEEP

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
        
#         # ⚠️ MASTER HACK: FFmpeg ki proxy band kar di gayi hai! ⚠️
#         # Ab stream direct GitHub ke internet se download hogi
        
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Direct GitHub Network par):")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 

# def main():
#     print("========================================")
#     print("   🚀 SMART SPLIT-ROUTING STREAMER")
#     print("========================================")
    
#     # ⚠️ STREAM KEY CHECKER ⚠️
#     if "NAYI_STREAM_KEY" in STREAM_KEY:
#         print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#         print("❌ ERROR: Aapne abhi tak OK.ru ki nayi Stream Key nahi dali!")
#         print("❌ Line Number 18 par ja kar asli key update karein.")
#         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
#         time.sleep(10)
#         return 
    
#     end_time = time.time() + (6 * 60 * 60)
#     current_process = None

#     while time.time() < end_time:
#         try:
#             data = get_link_with_headers()
            
#             if data:
#                 if current_process: current_process.terminate()
                
#                 current_process = start_stream(data)
#                 print("\n[🚀] SUCCESS! Video feed OK.ru par send hona shuru ho gayi hai!")
                
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] FFmpeg direct data fetch kar raha hai (Proxy safe hai). Bot {int(sleep_seconds/60)} mins ke liye rest mode mein ja raha hai...")
                
#                 waited = 0
#                 while waited < sleep_seconds:
#                     time.sleep(10)
#                     waited += 10
#                     if current_process.poll() is not None:
#                         exit_code = current_process.poll()
#                         print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                         print("[🔍] Reason: Shayad m3u8 link par IP-Lock hai aur direct download allowed nahi hai.")
#                         break 
                
#                 print("\n[🔄] Naya link dhoondne ka cycle dobara shuru ho raha hai...")
#                 if current_process: current_process.terminate()
#             else:
#                 print("\n[❌] Link dhoondne ka process fail ho gaya. 1 minute baad dobara koshish hogi...")
#                 time.sleep(60)
                
#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()


























































# ===== temporary fix with proxy =========================

# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (YAHAN APNI DETAILS DALEIN)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# # 1️⃣ APNI FRESH OK.RU STREAM KEY YAHAN DALEIN
# # STREAM_KEY = "NAYI_STREAM_KEY_YAHAN_DALEIN"
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda"  # <-- NAYA: OK.ru Stream Key
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# # 2️⃣ APNI WEBSHARE PROXY YAHAN DALEIN 
# # Format: "http://username:password@ip_address:port"
# # PROXY_URL = "http://shafi_user:pass1234@185.199.229.156:80"
# PROXY_URL = "http://cjasfidu:qhnyvm0qpf6p@185.199.229.156:80"  # <-- NAYA: Proxy URL for Selenium and FFmpeg

# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def get_link_with_headers():
#     print(f"\n========================================")
#     print(f"[🔍] [STEP 1] Target URL Set: {TARGET_WEBSITE}")
#     print(f"[🔍] [STEP 2] Proxy Set: {PROXY_URL.split('@')[-1]} (Hiding credentials)")
    
#     options = webdriver.ChromeOptions()
    
#     # --- GITHUB ACTIONS DISPLAY SETTINGS ---
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
    
#     # --- VIDEO AUTOPLAY FIX ---
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
    
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
#     # --- ANTI-BOT BYPASS ---
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     # --- PROXY INJECTION ---
#     seleniumwire_options = {
#         'proxy': {
#             'http': PROXY_URL,
#             'https': PROXY_URL,
#             'no_proxy': 'localhost,127.0.0.1'
#         },
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         print(f"[⚙️] [STEP 3] Chrome Browser start ho raha hai Proxy ke sath...")
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             seleniumwire_options=seleniumwire_options,
#             options=options
#         )
        
#         print(f"[🕵️‍♂️] [STEP 4] Anti-Bot JS Scripts inject ho rahi hain...")
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         print(f"[🌐] [STEP 5] Website open kar raha hoon: {TARGET_WEBSITE}")
#         driver.get(TARGET_WEBSITE)
        
#         # ⏳ STRICT 5 SECONDS WAIT
#         print("[⏳] [STEP 6] Website load ho gayi! 5 Seconds ka wait start ho gaya hai...") 
#         for i in range(5, 0, -1):
#             print(f"      ⏳ Wait: {i} seconds baqi...")
#             time.sleep(1)
            
#         print("[✅] [STEP 7] 5 Seconds poore! Ab network requests scan kar raha hoon...")

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE) 
#                     }
#                     print(f"\n🎉 [BINGO] .m3u8 Link Mil Gaya!")
#                     print(f"   🔗 URL: {request.url[:80]}...")
#                     print(f"   🛡️ Referer: {data['referer']}")
#                     print(f"   🍪 Cookie Set: {'Yes' if data['cookie'] else 'No'}")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: 5 seconds poore hone ke bawajood .m3u8 link nahi mila!")
#             print(f"   -> Page Title: '{driver.title}'")
#             print("   -> 💡 Tip: Agar title 'Just a moment' hai toh Proxy WAF mein fail ho gayi. Agar title normal hai, toh 5 seconds player ke liye kam par gaye.")

#     except Exception as e:
#         print(f"\n[💥] PYTHON SCRIPT ERROR (Browser Crash):")
#         print(traceback.format_exc())
#     finally:
#         if driver: 
#             print("[🧹] [STEP 8] Chrome Browser band kiya ja raha hai...")
#             driver.quit()
    
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Link Expiry Time: {expiry_dt.strftime('%I:%M %p')}")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
    
#     return DEFAULT_SLEEP

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
    
#     print("\n[🎬] [STEP 9] FFmpeg Command tayyar ki ja rahi hai...")
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-http_proxy", PROXY_URL,  
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     print("[⚙️] [STEP 10] FFmpeg Stream Launch ho rahi hai! (Errors honge toh neechay aayenge):")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 

# def main():
#     print("========================================")
#     print("   🚀 ULTRA-DEBUG GITHUB STREAMER")
#     print("========================================")
    
#     # ⚠️ STREAM KEY CHECKER ⚠️
#     if "NAYI_STREAM_KEY" in STREAM_KEY:
#         print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#         print("❌ ERROR: Aapne abhi tak OK.ru ki nayi Stream Key nahi dali!")
#         print("❌ Line Number 18 par ja kar asli key update karein.")
#         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
#         time.sleep(10)
#         return # Code ko yahin rok do taake crash na ho
    
#     end_time = time.time() + (6 * 60 * 60)
#     current_process = None

#     while time.time() < end_time:
#         try:
#             data = get_link_with_headers()
            
#             if data:
#                 if current_process: current_process.terminate()
                
#                 current_process = start_stream(data)
#                 print("\n[🚀] SUCCESS! Video feed OK.ru par send hona shuru ho gayi hai!")
                
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] FFmpeg chal raha hai. Bot {int(sleep_seconds/60)} mins ke liye rest mode mein ja raha hai...")
                
#                 waited = 0
#                 while waited < sleep_seconds:
#                     time.sleep(10)
#                     waited += 10
#                     if current_process.poll() is not None:
#                         exit_code = current_process.poll()
#                         print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                         print("[🔍] Reason: Shayad m3u8 link expire ho gaya hai ya proxy ne connection tor diya hai.")
#                         break 
                
#                 print("\n[🔄] Naya link dhoondne ka cycle dobara shuru ho raha hai...")
#                 if current_process: current_process.terminate()
#             else:
#                 print("\n[❌] Link dhoondne ka process fail ho gaya. 1 minute baad dobara koshish hogi...")
#                 time.sleep(60)
                
#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()

















# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # ==========================================
# # ⚙️ MAIN SETTINGS (YAHAN APNI DETAILS DALEIN)
# # ==========================================
# DEFAULT_URL = "https://dadocric.st/player.php?id=willowextra"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# # 1️⃣ APNI FRESH OK.RU STREAM KEY YAHAN DALEIN
# # STREAM_KEY = "NAYI_STREAM_KEY_YAHAN_DALEIN"
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda"  # <-- NAYA: OK.ru Stream Key
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"

# # 2️⃣ APNI WEBSHARE PROXY YAHAN DALEIN 
# # Format: "http://username:password@ip_address:port"
# # PROXY_URL = "http://cjasfidu:qhnyvm0qpf6p@31.59.20.176:6754"
# PROXY_URL = "http://cjasfidu:qhnyvm0qpf6p@31.59.20.176:6754"  # <-- NAYA: Proxy URL for Selenium and FFmpeg


# DEFAULT_SLEEP = 45 * 60 
# PKT = timezone(timedelta(hours=5))
# # ==========================================

# def get_link_with_headers():
#     print(f"\n[🕵️‍♂️] Bot link dhoondne ja raha hai via PROXY: {TARGET_WEBSITE}")
    
#     options = webdriver.ChromeOptions()
    
#     # --- GITHUB ACTIONS DISPLAY SETTINGS ---
#     # Headless band hai kyunke hum GitHub par 'xvfb' (fake screen) use kar rahe hain
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
    
#     # --- VIDEO AUTOPLAY FIX ---
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
    
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
#     # --- ANTI-BOT BYPASS ---
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

#     # --- PROXY INJECTION FOR SELENIUM ---
#     seleniumwire_options = {
#         'proxy': {
#             'http': PROXY_URL,
#             'https': PROXY_URL,
#             'no_proxy': 'localhost,127.0.0.1'
#         },
#         'disable_encoding': True, 
#         'connection_keep_alive': True
#     }

#     driver = None
#     data = None

#     try:
#         # Browser proxy ke sath open ho raha hai
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             seleniumwire_options=seleniumwire_options,
#             options=options
#         )
        
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         driver.get(TARGET_WEBSITE)
        
#         print("[⏳] Page loading & Player Autoplay (15 sec wait)...") 
#         time.sleep(15) 

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE) 
#                     }
#                     print(f"[✅] Link Found: {request.url[:60]}...")
#                     break
                    
#         if not data:
#             print("\n[🚨] WARNING: .m3u8 link nahi mila! Wajah dhoond rahe hain...")
#             print(f"   -> Page Title: '{driver.title}'")

#     except Exception as e:
#         print(f"\n[💥] PYTHON ERROR:")
#         print(traceback.format_exc())
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Expiry: {expiry_dt.strftime('%I:%M %p')}")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception:
#         pass
    
#     return DEFAULT_SLEEP

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
    
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", 
#         "-http_proxy", PROXY_URL,  # <-- NAYA: FFmpeg bhi ab proxy use karega
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     print("\n[⚙️] FFmpeg Streaming Engine Start ho raha hai via Proxy...")
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 

# def main():
#     print("========================================")
#     print("   🚀 GITHUB ACTIONS STREAMER STARTED")
#     print("========================================")
    
#     end_time = time.time() + (6 * 60 * 60)
#     current_process = None

#     while time.time() < end_time:
#         try:
#             data = get_link_with_headers()
            
#             if data:
#                 if current_process: current_process.terminate()
                
#                 current_process = start_stream(data)
#                 print("[🚀] BINGO! Stream OK.ru par live chali gayi hai!")
                
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] FFmpeg background mein chal raha hai. Bot {int(sleep_seconds/60)} mins ke liye so raha hai...")
                
#                 waited = 0
#                 while waited < sleep_seconds:
#                     time.sleep(10)
#                     waited += 10
#                     if current_process.poll() is not None:
#                         exit_code = current_process.poll()
#                         print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                         break 
                
#                 print("[🔄] Link expire hone wala hai, naya link laa raha hoon...")
#                 if current_process: current_process.terminate()
#             else:
#                 print("[❌] Link nahi mila. 1 min baad dobara koshish karega...")
#                 time.sleep(60)
                
#         except Exception:
#             print(f"\n[💥] MAIN LOOP ERROR:")
#             print(traceback.format_exc())
#             time.sleep(60)

# if __name__ == "__main__":
#     main()







# import os
# import time
# import subprocess
# import urllib.parse
# import traceback
# from datetime import datetime, timezone, timedelta
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# # --- SETTINGS ---
# DEFAULT_URL = "https://crichdbest.com/player.php?id=starsp3"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# # Apni Stream Key Yahan Dalein
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda" 
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
# DEFAULT_SLEEP = 45 * 60 
# # ----------------

# # Timezone setup
# PKT = timezone(timedelta(hours=5))

# def get_link_with_headers():
#     print(f"\n[🕵️‍♂️] Bot link dhoondne ja raha hai: {TARGET_WEBSITE}")
    
#     options = webdriver.ChromeOptions()
    
#     # --- GITHUB ACTIONS (HEADLESS) STEALTH SETTINGS ---
#     options.add_argument('--headless=new')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')
    
#     # --- VIDEO AUTOPLAY FIX (Taake player khud chal pare) ---
#     options.add_argument('--autoplay-policy=no-user-gesture-required')
#     options.add_argument('--mute-audio')
    
#     # Enable Browser Console Logging (Taake debugging asaan ho)
#     options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
#     # --- ANTI-BOT BYPASS ---
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
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
        
#         # JS Injection: Bot flag ko false karo
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         driver.get(TARGET_WEBSITE)
        
#         # ⏳ 15 seconds ka time taake ads skip hon aur player m3u8 fetch kare
#         print("[⏳] Page loading & Player Autoplay (15 sec)...") 
#         time.sleep(15) 

#         for request in driver.requests:
#             if request.response:
#                 # Sirf .m3u8 pakrega
#                 if ".m3u8" in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', TARGET_WEBSITE) 
#                     }
#                     print(f"[✅] Link Found: {request.url[:60]}...")
#                     break
        
#         # DIAGNOSTIC PRINT: Agar link nahi mila toh kyun nahi mila?
#         if not data:
#             print("\n[🚨] WARNING: .m3u8 link nahi mila! Debug info neechay hai:")
#             print(f"   -> Page Title: '{driver.title}'")
#             print(f"   -> Current URL: {driver.current_url}")
            
#             # WAF / Captcha Detection
#             if "Just a moment" in driver.title or "Cloudflare" in driver.title or "Access Denied" in driver.title:
#                 print("   -> 🛑 WAF/CLOUDFLARE BLOCK: Website ne bot detect kar liya hai!")
#             else:
#                 print("   -> 🔎 Check: Shayad 15 seconds wait time bhi player ke liye kam raha.")
            
#             # Print Javascript Console Errors
#             print("   -> 📜 Browser Console Logs:")
#             try:
#                 logs = driver.get_log('browser')
#                 error_found = False
#                 for entry in logs:
#                     if entry['level'] == 'SEVERE' or 'error' in entry['message'].lower():
#                         print(f"      [JS Error]: {entry['message'][:150]}...")
#                         error_found = True
#                 if not error_found:
#                     print("      (Koi Javascript error nahi mila)")
#             except Exception as log_e:
#                 print(f"      Log read error: {log_e}")

#     except Exception as e:
#         # Full Traceback print karega taake line number pata chalay
#         print(f"\n[💥] CRITICAL PYTHON ERROR:")
#         print(traceback.format_exc())
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
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             print(f"[⏰] Expiry: {expiry_dt.strftime('%I:%M %p')}")
#             print(f"[💤] Restart Time: {wake_up_dt.strftime('%I:%M %p')}")
            
#             if seconds > 0: return seconds
#             else: return 60
#     except Exception as e:
#         print(f"[⚠️] Time Calculate Error: {e}")
#         pass
    
#     return DEFAULT_SLEEP

# def start_stream(data):
#     headers_cmd = f"User-Agent: {data['ua']}\r\nReferer: {data['referer']}\r\nCookie: {data['cookie']}"
    
#     cmd = [
#         "ffmpeg", "-re",
#         "-loglevel", "error", # FFmpeg sirf critical errors print karega
#         "-headers", headers_cmd,
#         "-i", data['url'],
#         "-c:v", "libx264", "-preset", "ultrafast",
#         "-b:v", "600k", "-maxrate", "800k", "-bufsize", "1200k",
#         "-vf", "scale=854:480", "-r", "25",
#         "-c:a", "aac", "-b:a", "64k", "-ar", "44100",
#         "-f", "flv", RTMP_URL
#     ]
#     print("\n[⚙️] FFmpeg Streaming Engine Started...")
    
#     return subprocess.Popen(cmd, stdout=subprocess.DEVNULL) 

# def main():
#     print("=== DYNAMIC STREAMER STARTED ===")
#     print(f"Target: {TARGET_WEBSITE}")
    
#     end_time = time.time() + (6 * 60 * 60)
#     current_process = None

#     while time.time() < end_time:
#         try:
#             data = get_link_with_headers()
            
#             if data:
#                 if current_process: current_process.terminate()
                
#                 current_process = start_stream(data)
#                 print("[🚀] Stream Started to OK.ru!")
                
#                 sleep_seconds = calculate_sleep_time(data['url'])
#                 print(f"[zzz] Sleeping for {int(sleep_seconds/60)} mins...")
                
#                 waited = 0
#                 while waited < sleep_seconds:
#                     time.sleep(10)
#                     waited += 10
#                     # FFmpeg Crash Detector
#                     if current_process.poll() is not None:
#                         exit_code = current_process.poll()
#                         print(f"\n[⚠️] FFmpeg Stream Crashed! (Exit Code: {exit_code})")
#                         print("[🔍] Upar error log check karein ke FFmpeg kyun ruka.")
#                         break 
                
#                 print("[🔄] Refreshing Link...")
#                 if current_process: current_process.terminate()
#             else:
#                 print("[❌] Failed to get link. Retrying in 1 min...")
#                 time.sleep(60)
                
#         except Exception as main_e:
#             print(f"\n[💥] MAIN LOOP CRASHED:")
#             print(traceback.format_exc())
#             print("[🔄] 1 minute baad dobara try kar raha hoon...")
#             time.sleep(60)

# if __name__ == "__main__":
#     main()












# =====================   referrer: https://pipcast.cc/  ================================


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
# DEFAULT_URL = "https://crichdbest.com/player.php?id=starsp3"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# # Apni Stream Key Yahan Dalein
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda" 
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
# DEFAULT_SLEEP = 45 * 60 
# # ----------------

# # Timezone setup
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
        
#         # Wait time set to 5 seconds
#         print("[⏳] Page loading (5 sec)...") 
#         time.sleep(5) 

#         for request in driver.requests:
#             if request.response:
#                 if ".m3u8" in request.url and "google" not in request.url:
#                     headers = request.headers
#                     data = {
#                         "url": request.url,
#                         "ua": headers.get('User-Agent', ''),
#                         "cookie": headers.get('Cookie', ''),
#                         "referer": headers.get('Referer', 'https://pipcast.cc/')
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
            
#             # Expiry buffer set to 5 minutes
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
            
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             # Time format set to AM/PM
#             print(f"[⏰] Expiry: {expiry_dt.strftime('%I:%M %p')}")
#             print(f"[💤] Restart Time: {wake_up_dt.strftime('%I:%M %p')}")
            
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
    
#     # Run for 6 hours
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
#                 # Check if ffmpeg crashed
#                 if current_process.poll() is not None:
#                     print("[⚠️] Stream Crash! Restarting...")
#                     break 
            
#             print("[🔄] Refreshing Link...")
#             if current_process: current_process.terminate()
#         else:
#             print("[❌] Failed. Retry in 1 min.")
#             time.sleep(5)

# if __name__ == "__main__":
#     main()













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
# DEFAULT_URL = "https://crichdbest.com/player.php?id=starsp3"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# # Apni Stream Key Yahan Dalein
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda" 
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
# DEFAULT_SLEEP = 45 * 60 
# # ----------------

# # Timezone setup
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
        
#         # Wait time set to 5 seconds
#         print("[⏳] Page loading (5 sec)...") 
#         time.sleep(5) 

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
            
#             # Expiry buffer set to 5 minutes
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
            
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             # Time format set to AM/PM
#             print(f"[⏰] Expiry: {expiry_dt.strftime('%I:%M %p')}")
#             print(f"[💤] Restart Time: {wake_up_dt.strftime('%I:%M %p')}")
            
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
    
#     # --- TASK: Run for 15 hours ---
#     end_time = time.time() + (15 * 60 * 60) # 15 hours * 60 mins * 60 secs
    
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
#                 # Check if ffmpeg crashed
#                 if current_process.poll() is not None:
#                     print("[⚠️] Stream Crash! Restarting...")
#                     break 
            
#             print("[🔄] Refreshing Link...")
#             if current_process: current_process.terminate()
#         else:
#             print("[❌] Failed. Retry in 1 min.")
#             time.sleep(5)

# if __name__ == "__main__":
#     main()












# ======= upper walay ko 6housr see change karky 15hours tak karleya github =============================




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
# DEFAULT_URL = "https://crichdbest.com/player.php?id=starsp3"
# TARGET_WEBSITE = os.environ.get('TARGET_URL', DEFAULT_URL)

# # Apni Stream Key Yahan Dalein
# STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda" 
# RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
# DEFAULT_SLEEP = 45 * 60 
# # ----------------

# # Timezone setup
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
        
#         # --- TASK 2: Wait time reduced to 5 seconds ---
#         print("[⏳] Page loading (5 sec)...") 
#         time.sleep(5) 

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
            
#             # --- TASK 1: Expiry buffer changed to 5 minutes ---
#             wake_up_dt = expiry_dt - timedelta(minutes=5)
            
#             now_dt = datetime.now(PKT)
#             seconds = (wake_up_dt - now_dt).total_seconds()
            
#             # --- TASK 3: Time format changed to 12-hour AM/PM ---
#             print(f"[⏰] Expiry: {expiry_dt.strftime('%I:%M %p')}")
#             print(f"[💤] Restart Time: {wake_up_dt.strftime('%I:%M %p')}")
            
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
    
#     # Run for 6 hours
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
#                 # Check if ffmpeg crashed
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
