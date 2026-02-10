# FILE: streamer.py
import time
import json
import subprocess
import os
import sys

# --- SETTINGS ---
DATA_FILE = "stream_data.json"
STREAM_KEY = "11523921485458_10535073221266_x3wpukcvda"
RTMP_URL = f"rtmp://vsu.okcdn.ru/input/{STREAM_KEY}"
# ----------------

def start_ffmpeg(data):
    print("\n[🚀] Starting NEW Stream...")
    
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
    
    # Process start karo (Output dikhana hai to stdout=None rakho)
    return subprocess.Popen(cmd)

def main():
    print("========================================")
    print("   WORKER BOT: Waiting for Superman...")
    print("========================================")

    current_process = None
    last_timestamp = 0

    while True:
        try:
            # Check karo kya file exist karti hai?
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        time.sleep(1)
                        continue # Agar file abhi likhi ja rahi hai to wait karo

                # KYA NAYA DATA AAYA HAI?
                if data['timestamp'] != last_timestamp:
                    print(f"\n[⚡] UPDATE DETECTED! (New Link Found)")
                    
                    # 1. Purana band karo
                    if current_process:
                        print("[ox] Stopping Old Stream...")
                        current_process.terminate()
                        current_process.wait()
                    
                    # 2. Naya chalao
                    current_process = start_ffmpeg(data)
                    last_timestamp = data['timestamp']
                
                # Agar process crash ho gaya ho to restart karo
                if current_process and current_process.poll() is not None:
                    print("[⚠️] Stream Crash hui thi. Restarting same link...")
                    current_process = start_ffmpeg(data)

            else:
                print("[...] Waiting for data file...", end="\r")

        except Exception as e:
            print(f"[Error] {e}")

        # Har 5 second baad file check karo
        time.sleep(5)

if __name__ == "__main__":
    main()













# =========== 200% correct hai yeh code link extract karta hai website see ====================



# import os
# import subprocess

# def clear_screen():
#     os.system('cls' if os.name == 'nt' else 'clear')

# def main():
#     clear_screen()
#     print("========================================")
#     print("   FFMPEG STREAM GENERATOR (V4 - BASH FIX)")
#     print("========================================")
    
#     # 1. Inputs
#     m3u8_link = input("\n[?] M3U8 Link paste karein: ").strip().replace('\n', '').replace('\r', '')
#     referer = input("[?] Referer Link (e.g., https://bhalocast.com): ").strip().replace('\n', '').replace('\r', '')
#     origin = input("[?] Origin Link (e.g., https://bhalocast.com): ").strip().replace('\n', '').replace('\r', '')
    
#     if not m3u8_link:
#         print("Error: Link khali nahi ho sakta!")
#         return

#     # Default Key
#     stream_key = "11523921485458_10535073221266_x3wpukcvda"
    
#     # 2. Data/Quality Selection
#     print("\n----------------------------------------")
#     print("DATA OPTIMIZATION (Slow Internet ke liye)")
#     print("1. HAAN: Data chota karo (480p, Low Bitrate)")
#     print("2. NAHI: Original Quality (High Data)")
#     choice = input("Apna option chunein (1/2): ").strip()

#     # --- CONSTRUCTION ZONE ---
    
#     # User Agent
#     ua_part1 = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#     ua_part2 = "AppleWebKit/537.36 (KHTML, like Gecko) "
#     ua_part3 = "Chrome/120.0.0.0 Safari/537.36"
#     user_agent = ua_part1 + ua_part2 + ua_part3
    
#     # Headers (Bash Syntax)
#     headers = f"$'Origin: {origin}\\r\\nReferer: {referer}'"
    
#     # Quality Settings
#     if choice == '1':
#         video_settings = "-c:v libx264 -preset ultrafast -b:v 600k -maxrate 800k -bufsize 1200k -vf \"scale=854:480\" -r 25"
#         audio_settings = "-c:a aac -b:a 64k -ar 44100"
#         print("\n[+] Mode: Low Data (Optimized)")
#     else:
#         video_settings = "-c copy"
#         audio_settings = ""
#         print("\n[+] Mode: Original Quality")

#     # Command Construction
#     parts = [
#         "ffmpeg -re",
#         f"-headers {headers}",
#         f"-user_agent \"{user_agent}\"",
#         f"-i \"{m3u8_link}\"",
#         video_settings,
#         audio_settings,
#         f"-f flv \"rtmp://vsu.okcdn.ru/input/{stream_key}\""
#     ]
    
#     raw_command = " ".join(parts)
#     final_command = raw_command.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')

#     # 4. Result
#     print("\n========================================")
#     print("COMMAND READY!")
#     print("========================================")
#     print(final_command)
#     print("========================================")
    
#     run_now = input("\n[?] Kya main is command ko abhi RUN kar dun? (y/n): ")
#     if run_now.lower() == 'y':
#         print("\n[+] Starting Stream via BASH... (Ab chalega!)")
#         # FIX: Force execution through /bin/bash to support special headers
#         subprocess.run(final_command, shell=True, executable='/bin/bash')
#     else:
#         print("Okay.")

# if __name__ == "__main__":
#     main()